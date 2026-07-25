"""
HumanitAI — Prevention & Intervention System  v3 (architecture-aligned)
=================================================================
Per the CIC's actual architecture (two pillars):
  PILLAR 1  PREDICTION  — models on existing UK open data to target help.
             PRIMARY domains = MENTAL HEALTH + AGEING, plus other UK problems
             (poverty / homelessness / NHS / isolation).
  PILLAR 2  4TH SPACE    — combat loneliness & bring people together via a
             physical/social venue: sauna, cold plunge, contrast therapy.
             Modelled here as the flagship loneliness-combat intervention,
             with expected loneliness-reduction gain + SROI-style logic.

Models stacked:
  1. Composite risk + tier (mental-health & ageing weighted)
  2. Spatial hotspots (PySAL Gi*)
  3. Early-warning trajectory (severity x escalation text)
  4. Trend projection (news-driven drift)
  5. Causal graph (lever -> outcome)
  6. 4TH SPACE model (loneliness reduction + SROI proxy)
  7. Live news early-warning
  8. Budget optimisation
  9. Intervention systems + stop/escalate

All key-free for statistical layers. Honest labels throughout.
"""
import os, json, datetime
from collections import defaultdict, Counter
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA1 = os.path.join(ROOT, "prediction", "uk_social_stats_scraped.json")
DATA2 = os.path.join(ROOT, "prediction", "uk_stats_extra.json")
NEWS  = os.path.join(ROOT, "prediction", "news_signals.json")
MIRO  = os.path.join(ROOT, "prediction", "mirofish_uk_sim_out.json")

# Primary domains per architecture; weighted higher in composite risk.
PRIMARY = ["mental", "ageing"]
SECONDARY = ["poverty", "homelessness", "nhs", "isolation"]
PRESSURES = PRIMARY + SECONDARY
PLABEL = {"mental":"Mental health","ageing":"Ageing / older people",
          "poverty":"Poverty / low income","homelessness":"Homelessness",
          "nhs":"NHS waiting","isolation":"Isolation / loneliness"}
# architecture weighting: primary domains count more
WEIGHT = {"mental":1.4,"ageing":1.4,"poverty":1.0,"homelessness":1.0,"nhs":1.0,"isolation":1.0}

# Intervention levers (CHW + 5th space). gain = expected outcome lift (0-1), cost = £ per cohort.
LEVERS = {
 "mental":[("Community navigation to talking-therapy (VCSE)",0.70,780),
           ("Low-intensity CBT via VCSE",0.75,820),
           ("Peer support / befriending groups",0.65,520)],
 "ageing":[("Ageing-well connector + befriending",0.70,540),
           ("Fall-prevention + social club",0.60,610),
           ("Fuel-poverty + warm-space support",0.65,470)],
 "poverty":[("Targeted child-poverty cash / cost-of-living support",0.90,1100),
            ("Debt advice + money guidance (CHW-delivered)",0.70,650),
            ("Living-wage / employment access programme",0.50,1400)],
 "homelessness":[("Preventive tenancy sustainment (pre-Section-21 reach)",0.85,950),
            ("Rapid rehousing + TA diversion",0.80,1300),
            ("Rent arrears mediation with landlord",0.60,700)],
 "nhs":[("Community navigation to cut avoidable A&E",0.60,800),
            ("Waiting-list prioritisation by deprivation",0.50,600),
            ("Social prescribing for chronic conditions",0.55,720)],
 "isolation":[("Community navigator + befriending",0.60,480),
            ("Social prescribing + group activity",0.55,460),
            ("Transport-to-service vouchers",0.40,390)],
}
# 5TH SPACE — flagship loneliness-combat intervention (pillar 2): a CANAL BARGE
# A large, off-grid canal boat that travels the UK inland-waterway network and moors
# at the towns the forecast flags. Same loneliness-combat mission as the old fixed
# "4th Space" sauna, but mobile: it goes to the people instead of waiting for them.
FIFTH_SPACE = {
 "name":"5th Space — off-grid canal barge (mobile community venue)",
 "rationale":"A large canal barge, solar + lithium off-grid, that sails the UK canal/river network and moors at the towns the AI flags. It combats loneliness by arriving before the crisis — a warm room, on the water, with no postcode lottery. Models the CIC's pillar-2 delivery as a mobile venue.",
 "levers":[
   ("Canal-barge community mooring (subsidised, social sessions)",0.80,1800),
   ("Warm-room + contrast/wellbeing circle on board",0.78,1200),
   ("Intergenerational 5th-space sessions (ageing + youth)",0.72,1100),
 ],
 # illustrative planning proxies (replace with evaluation data before any spend):
 "loneliness_reduction":0.8,   # expected share of regular visitors reporting reduced loneliness
 "sessions_per_mooring":24,    # onboard sessions per mooring stop
 "capacity_per_mooring":60,    # people held per mooring / week at steady state
 "towns_per_year":12,          # approx towns reached/yr (4mph canals, 14-day CRT mooring limit)
 "reach_multiplier":12,        # rough x vs one fixed site (illustrative)
 "sroi_proxy":3.2,             # £ social value per £ invested (proxy; replace with eval)
}

IMPACT_PER_1K = {"mental":11,"ageing":10,"poverty":9,"homelessness":7,"nhs":6,"isolation":13}
ESCAL_WORDS = ["record","worst","highest","rising","surge","crisis","soar","sharp",
               "increase","climb","deepen","exacerbat","lonely","suicide","dementia","isolation"]

# Causal graph (lever -> expected outcome)
CAUSAL = {
 "mental":[("vcse_talking_therapy_nav","access_to_treatment"),("low_intensity_cbt","reduced_symptoms"),("peer_support","reduced_loneliness_crisis")],
 "ageing":[("ageing_connector","reduced_older_isolation"),("fall_prevention_club","reduced_falls_hospitalisation"),("warm_space","reduced_fuel_poverty")],
 "isolation":[("5th_space_barge","reduced_loneliness_connection"),("navigator_befriend","reduced_loneliness"),("group_activity","increased_belonging")],
 "poverty":[("cash_support","reduced_child_poverty"),("debt_advice","reduced_arrears_escalation")],
 "homelessness":[("tenancy_sustainment","prevented_lose_home"),("rapid_rehousing","reduced_sleep_rough")],
 "nhs":[("community_navigation","reduced_avoidable_ae"),("social_prescribing","better_chronic_control")],
}

def load():
    recs=[]
    for p in (DATA1,DATA2):
        with open(p) as f: recs+=json.load(f)
    # REAL live LA-level mental-health data (ONS wellbeing CSV) — primary domain
    live=os.path.join(ROOT,"prediction","uk_live_ons.json")
    if os.path.exists(live):
        recs+=json.load(open(live)).get("records",[])
    return recs

def escalation_signal(text):
    t=(text or "").lower()
    return min(sum(1 for w in ESCAL_WORDS if w in t),3)

def build_frame(recs):
    rows=[]
    for r in recs:
        rows.append(dict(place=r.get("c") or "?",region=r.get("r") or "",
            lat=float(r.get("lat") or 0),lng=float(r.get("lng") or 0),
            pressure=r.get("f") or "?",sev=float(r.get("sev") or 0),
            detail=(r.get("d") or r.get("s") or ""),src=r.get("src") or ""))
    return pd.DataFrame(rows)

def composite(df):
    g=df.groupby("place").agg(sev=("sev","mean"),region=("region","first"),
        lat=("lat","first"),lng=("lng","first"),n=("sev","count")).reset_index()
    # weighted severity: primary domains weighted
    wsum=df.groupby("place").apply(lambda x:(x["sev"]*x["pressure"].map(WEIGHT).fillna(1.0)).sum())
    wcnt=df.groupby("place").apply(lambda x:x["pressure"].map(WEIGHT).fillna(1.0).sum())
    wsev=(wsum/wcnt).round(1)
    g=g.copy(); g["wsev"]=g["place"].map(wsev.to_dict())
    esc_map=df.groupby("place")["detail"].apply(lambda s: max((escalation_signal(x) for x in s),default=0))
    g["esc"]=g["place"].map(esc_map).fillna(0).astype(float)
    g["trajectory"]=(g["wsev"]/100.0+0.12*g["esc"]).clip(0,1.2)
    g["risk"]=(0.7*g["wsev"]+0.3*g["trajectory"]*100).round(1)
    g["tier"]=pd.cut(g["risk"],[0,70,82,1000],labels=["Watch","Priority","Critical"])
    g=g.sort_values("risk",ascending=False).reset_index(drop=True); g["rank"]=range(1,len(g)+1)
    return g

def spatial(g):
    try:
        from libpysal.weights import KNN
        from esda.getisord import G_Local
    except Exception as e:
        return g,f"spatial skipped ({e})"
    geo = g[(g["lat"].abs()>0.01) & (g["lng"].abs()>0.01)]
    if len(geo)<5: return g,"spatial skipped (insufficient geocoded points)"
    pts=geo[["lng","lat"]].values
    if pts.std(axis=0).max() < 0.01: return g,"spatial skipped (no coordinates)"
    w=KNN.from_array(pts,k=4)
    gi=G_Local(geo["wsev"].values.astype(float),w,star=True)
    gg=geo.copy(); gg["gi_star"]=gi.Zs
    gg["hotspot"]=np.where(gg["gi_star"]>1.96,"HOT",np.where(gg["gi_star"]<-1.96,"COLD","ns"))
    # merge hotspot back
    g=g.copy(); g["hotspot"]="ns"
    g.loc[gg.index,"hotspot"]=gg["hotspot"].values
    return g,f"Gi* KNN k=4 (n={len(geo)} geocoded)"

def dominant_pressure(df,g):
    pres=df.groupby("place")["pressure"].apply(lambda s:Counter(s).most_common(1)[0][0] if len(s) else "mental").to_dict()
    g=g.copy(); g["pressure_dominant"]=g["place"].map(pres).fillna("mental")
    return g

def trend_projection(g,news):
    early=(news or {}).get("early_warning",{}) if news else {}
    rows=[]
    for _,r in g.iterrows():
        p=r.get("pressure_dominant"); base=r["risk"]; drift=0.0
        if p and early.get(p)=="ELEVATED": drift=2.5
        elif p and early.get(p)=="baseline": drift=-0.5
        proj=[round(min(base+drift*i,100),1) for i in range(1,4)]
        band_pm=round(2.0+1.5*len(proj),1)
        driver=("news-elevated:"+p) if (p and drift>0) else "stable"
        rows.append(dict(place=r["place"],base=base,h1=proj[0],h2=proj[1],h3=proj[2],band_pm=band_pm,driver=driver))
    return rows

def causal_graph():
    edges=[]
    for p,links in CAUSAL.items():
        for lever,outcome in links:
            edges.append(dict(pressure=p,lever=lever,expected_outcome=outcome))
    return edges

def fifth_space_model():
    fs=FIFTH_SPACE
    # expected users reached & loneliness reduction per mooring stop, steady state
    members=fs["capacity_per_mooring"]
    reduced=round(members*fs["loneliness_reduction"])
    annual_cost=fs["levers"][0][2]* (members//8 + 1)  # proxy cohort cost
    sroi_value=round(annual_cost*fs["sroi_proxy"])
    return dict(spec=fs,members_per_mooring=members,towns_per_year=fs["towns_per_year"],
                reach_multiplier=fs["reach_multiplier"],expected_loneliness_reduced=reduced,
                sroi_proxy=fs["sroi_proxy"],est_annual_investment=annual_cost,
                est_social_value=round(annual_cost*fs["sroi_proxy"]))

def allocate(df,g,budget=120000):
    NATIONAL={"england (national)","uk (national)","united kingdom","england","uk",
              "scotland (national)","wales (national)","scotland","wales"}
    present=df.groupby("place")["pressure"].apply(list).to_dict()
    cands=[]
    for _,row in g.iterrows():
        place=row["place"]
        if place.lower() in NATIONAL: continue
        press=set(present.get(place,[])) or {"mental"}
        for p in press:
            for name,gain,cost in LEVERS.get(p,[]):
                eff=(IMPACT_PER_1K[p]*gain)/max(cost,1)
                cands.append(dict(place=place,tier=row["tier"],pressure=p,
                    intervention=name,gain=gain,cost=cost,eff=eff,hh=round(IMPACT_PER_1K[p]*gain,1)))
    tr={"Critical":0,"Priority":1,"Watch":2}
    cands.sort(key=lambda c:(tr.get(c["tier"],3),-c["eff"]))
    funded,spent,total_hh,coverage=[],0.0,0.0,set()
    per=defaultdict(int); MAX=3
    for c in cands:
        if spent+c["cost"]>budget: continue
        if per[c["place"]]>=MAX: continue
        funded.append(c);spent+=c["cost"];total_hh+=c["hh"];coverage.add(c["place"]);per[c["place"]]+=1
    # ring-fence a 5th-space barge pilot from remaining budget
    fs_cost=FIFTH_SPACE["levers"][0][2]
    fs_funded=False
    if spent+fs_cost<=budget:
        funded.append(dict(place="PILOT: 5th Space barge",tier="Priority",pressure="isolation",
            intervention=FIFTH_SPACE["name"],gain=FIFTH_SPACE["loneliness_reduction"],
            cost=fs_cost,eff=IMPACT_PER_1K["isolation"]*FIFTH_SPACE["loneliness_reduction"]/fs_cost,
            hh=round(FIFTH_SPACE["capacity_per_mooring"]*FIFTH_SPACE["loneliness_reduction"],1)))
        spent+=fs_cost; total_hh+=round(FIFTH_SPACE["capacity_per_mooring"]*FIFTH_SPACE["loneliness_reduction"],1)
        coverage.add("5th Space"); fs_funded=True
    return dict(funded=funded,spent=spent,total_hh=round(total_hh,1),
                places_covered=len(coverage),budget=budget,remaining=budget-spent,
                fifth_space_funded=fs_funded)

def intervention_system(df,g,budget=120000):
    present=df.groupby("place")["pressure"].apply(list).to_dict()
    out=[]; top=g[g["tier"].isin(["Critical","Priority"])].head(6)
    for _,row in top.iterrows():
        place=row["place"]; press=set(present.get(place,[])) or {"mental"}
        levers=[]; exp=0.0; spent=0
        for p in (list(press) if press else ["mental"]):
            for name,gain,cost in LEVERS.get(p,[]):
                helped=IMPACT_PER_1K[p]*gain
                levers.append(dict(pressure=p,label=PLABEL[p],intervention=name,
                    expected_gain=gain,cost=cost,est_households_helped=round(helped*gain,1)))
                exp+=helped*gain; spent+=cost
                if spent>=budget/len(top): break
        out.append(dict(place=place,region=row["region"],risk=row["risk"],tier=row["tier"],
            hotspot=row.get("hotspot","ns"),pressures=sorted(press) if press else ["mental"],
            interventions=levers,est_total_households=round(exp,1),est_cost=spent,
            equity_note="Higher expected benefit in this high-need area; monitor differential take-up across older and isolated groups.",
            stop_condition=f"Review at week 8; stop expansion if completion <35% or access gap widens in {place}. Escalate to safeguarding lead if self-harm risk indicated."))
    return out

def main():
    recs=load(); df=build_frame(recs)
    g=composite(df); g,spatial_note=spatial(g); g=dominant_pressure(df,g)
    news=json.load(open(NEWS)) if os.path.exists(NEWS) else {}
    trends=trend_projection(g,news)
    edges=causal_graph()
    fs=fifth_space_model()
    intervs=intervention_system(df,g,budget=120000)
    alloc=allocate(df,g,budget=120000)
    miro=json.load(open(MIRO)).get("synthesis","") if os.path.exists(MIRO) else ""
    L=[]
    L.append("HUMANITAI — PREVENTION & INTERVENTION SYSTEM v3 (architecture-aligned)")
    L.append("="*72)
    L.append(f"Pillar1 PREDICTION (mental health + ageing primary) | Pillar2 5TH SPACE (canal barge)")
    L.append(f"Data: {len(df)} records ({df['place'].nunique()} places) + live news")
    L.append("1) COMPOSITE RISK + TIER (mental/ageing weighted)")
    for _,r in g.head(8).iterrows():
        L.append(f"  {int(r['rank']):>2}. {r['place']:<18} risk {r['risk']:5.1f} [{r['tier']}] dom={r['pressure_dominant']}")
    L.append("")
    L.append("2) SPATIAL: "+spatial_note)
    L.append("3) TREND (news drift): "+"; ".join(f"{t['place']}->{t['h3']}(±{t['band_pm']})" for t in trends[:4]))
    L.append("4) CAUSAL edges: "+str(len(edges))+" (mental/ageing/5th-space led)")
    L.append("")
    L.append("5) 5TH SPACE MODEL (pillar 2 flagship — mobile canal barge):")
    L.append(f"   {fs['spec']['name']}")
    L.append(f"   members/mooring {fs['members_per_mooring']} | towns/yr ~{fs['towns_per_year']} | reach x{fs['reach_multiplier']} vs fixed | expected loneliness reduced {fs['expected_loneliness_reduced']} | SROI proxy x{fs['sroi_proxy']}")
    L.append(f"   est annual investment £{fs['est_annual_investment']} -> social value £{fs['est_social_value']}")
    L.append("")
    if news:
        L.append("6) NEWS EARLY-WARNING: "+str(news.get("early_warning")))
    a=alloc
    L.append(f"7) BUDGET £{a['budget']:,}: spent £{a['spent']:,} | {a['places_covered']} places | ~{a['total_hh']} hh | 5thSpace funded={a['fifth_space_funded']}")
    L.append("8) INTERVENTION SYSTEMS:")
    for s in intervs:
        L.append(f"  -- {s['place']} ({s['tier']}, risk {s['risk']}) --")
        for iv in s["interventions"]:
            L.append(f"     * {iv['intervention']} | gain {iv['expected_gain']:.2f} | ~£{iv['cost']}")
    L.append("")
    L.append("NOTE: mental health + ageing are the primary modelled domains per architecture; 5th space (mobile canal barge) is the flagship loneliness intervention. Priors illustrative until replaced with evaluation data.")
    print("\n".join(L))
    out=dict(composite=g.to_dict(orient="records"),trends=trends,causal=edges,
             fifth_space=fs,allocation=alloc,interventions=intervs,news=news,
             mirofish_synthesis=miro,spatial_note=spatial_note,
             architecture="PREDICTION(mental/ageing primary)+5TH SPACE(canal barge)",
             generated=datetime.datetime.now(datetime.timezone.utc).isoformat())
    with open(os.path.join(ROOT,"prediction","prevention_out_v3.json"),"w") as f:
        json.dump(out,f,indent=2)
    print("\n[written] prediction/prevention_out_v3.json")

if __name__=="__main__":
    main()
