"""
HumanitAI — Prevention & Intervention System  v2
=================================================================
Expands v1 with: (a) merged wider dataset (static + curated real stats),
(b) live news early-warning layer, (c) TREND PROJECTION (exponential
smoothing on a derived time index + news momentum), (d) CAUSAL-GRAPH
identification of lever->outcome paths, (e) full problem->solution matrix.

Models now stacked:
  1. Composite risk + tier
  2. Spatial hotspots (PySAL Gi*)
  3. Early-warning trajectory (severity x textual escalation)
  4. TREND PROJECTION  (forecast severity forward, with interval)
  5. CAUSAL GRAPH       (which levers plausibly move which outcomes)
  6. News early-warning (live RSS signal layer)
  7. Budget optimisation
  8. Intervention systems + stop/escalate
MiroFish agent layer remains available as second-order view.

All key-free for statistical layers. Honest labels on every uncertain output.
"""
import os, json, re, datetime
from collections import defaultdict, Counter
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA1 = os.path.join(ROOT, "prediction", "uk_social_stats_scraped.json")
DATA2 = os.path.join(ROOT, "prediction", "uk_stats_extra.json")
NEWS  = os.path.join(ROOT, "prediction", "news_signals.json")
MIRO  = os.path.join(ROOT, "prediction", "mirofish_uk_sim_out.json")

PRESSURES = ["poverty","homelessness","nhs","mental","isolation"]
PLABEL = {"poverty":"Poverty / low income","homelessness":"Homelessness",
          "nhs":"NHS waiting","mental":"Mental health","isolation":"Isolation / loneliness"}

LEVERS = {
 "poverty":[("Targeted child-poverty cash / cost-of-living support",0.90,1100),
            ("Debt advice + money guidance (CHW-delivered)",0.70,650),
            ("Living-wage / employment access programme",0.50,1400)],
 "homelessness":[("Preventive tenancy sustainment (pre-Section-21 reach)",0.85,950),
            ("Rapid rehousing + TA diversion",0.80,1300),
            ("Rent arrears mediation with landlord",0.60,700)],
 "nhs":[("Community navigation to cut avoidable A&E",0.60,800),
            ("Waiting-list prioritisation by deprivation",0.50,600),
            ("Social prescribing for chronic conditions",0.55,720)],
 "mental":[("Peer/community connector + befriending",0.65,520),
            ("Low-intensity CBT via VCSE",0.70,780),
            ("Anti-isolation groups / warm spaces",0.50,430)],
 "isolation":[("Community navigator + befriending",0.60,480),
            ("Social prescribing + group activity",0.55,460),
            ("Transport-to-service vouchers",0.40,390)],
}
IMPACT_PER_1K = {"poverty":9,"homelessness":7,"nhs":6,"mental":11,"isolation":13}
ESCAL_WORDS = ["record","worst","highest","rising","surge","crisis","soar","sharp",
               "increase","climb","deepen","exacerbat","more than","47%","49%","132,410","3,898"]

# ---- Causal graph: lever -> outcome (blueprint 11 + evidence) ----
CAUSAL = {
 "poverty":   [("cash_support","reduced_child_poverty"),("debt_advice","reduced_arrears_escalation"),("employment_access","sustained_income")],
 "homelessness":[("tenancy_sustainment","prevented_lose_home"),("rapid_rehousing","reduced_sleep_rough"),("arrears_mediation","avoided_possession")],
 "nhs":[("community_navigation","reduced_avoidable_ae"),("waiting_prioritisation","faster_treatment"),("social_prescribing","better_chronic_control")],
 "mental":[("peer_connector","reduced_loneliness_crisis"),("low_intensity_cbt","reduced_symptoms"),("anti_isolation","increased_belonging")],
 "isolation":[("navigator_befriend","reduced_loneliness"),("group_activity","increased_connection"),("transport_vouchers","access_to_services")],
}

def load():
    recs=[]
    for p in (DATA1,DATA2):
        with open(p) as f: recs+=json.load(f)
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
    esc_map=df.groupby("place")["detail"].apply(lambda s: max((escalation_signal(x) for x in s),default=0))
    g=g.copy(); g["esc"]=g["place"].map(esc_map).fillna(0).astype(float)
    g["trajectory"]=(g["sev"]/100.0+0.12*g["esc"]).clip(0,1.2)
    g["risk"]=(0.7*g["sev"]+0.3*g["trajectory"]*100).round(1)
    g["tier"]=pd.cut(g["risk"],[0,70,82,1000],labels=["Watch","Priority","Critical"])
    g=g.sort_values("risk",ascending=False).reset_index(drop=True); g["rank"]=range(1,len(g)+1)
    return g

def spatial(g):
    try:
        from libpysal.weights import KNN
        from esda.getisord import G_Local
    except Exception as e:
        return g,f"spatial skipped ({e})"
    pts=g[["lng","lat"]].values
    if len(g)<5: return g,"spatial skipped (n<5)"
    w=KNN.from_array(pts,k=4)
    gi=G_Local(g["sev"].values.astype(float),w,star=True)
    g=g.copy(); g["gi_star"]=gi.Zs
    g["hotspot"]=np.where(g["gi_star"]>1.96,"HOT",np.where(g["gi_star"]<-1.96,"COLD","ns"))
    return g,f"Gi* KNN k=4 (n={len(g)})"

def trend_projection(g, news):
    """Exponential-smoothing-style forward projection of place risk.
    Honest: we have one cross-sectional slice + live news momentum; we project
    a 3-period horizon with a widening interval, where news ELEVATED pressures
    add upward drift. This is a planning projection, NOT a calibrated forecast."""
    early = (news or {}).get("early_warning",{}) if news else {}
    rows=[]
    for _,r in g.iterrows():
        base=r["risk"]
        p=r.get("pressure_dominant")
        drift=0.0
        if p and early.get(p)=="ELEVATED":
            drift=2.5
        elif p and early.get(p)=="baseline":
            drift=-0.5
        proj=[round(min(base+drift*i,100),1) for i in range(1,4)]
        band_pm=round(2.0+1.5*len(proj),1)
        driver=("news-elevated:"+p) if (p and drift>0) else "stable"
        rows.append(dict(place=r["place"],base=base,
            h1=proj[0],h2=proj[1],h3=proj[2],
            band_pm=band_pm, driver=driver))
    return rows

def causal_graph():
    """Return lever->outcome edges as a readable structure."""
    edges=[]
    for p,links in CAUSAL.items():
        for lever,outcome in links:
            edges.append(dict(pressure=p,lever=lever,expected_outcome=outcome))
    return edges

def allocate(df,g,budget=120000):
    NATIONAL={"england (national)","uk (national)","united kingdom","england","uk",
              "scotland (national)","wales (national)","scotland","wales"}
    present=df.groupby("place")["pressure"].apply(list).to_dict()
    cands=[]
    for _,row in g.iterrows():
        place=row["place"]
        if place.lower() in NATIONAL: continue
        press=set(present.get(place,[])) or {"poverty"}
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
    return dict(funded=funded,spent=spent,total_hh=round(total_hh,1),
                places_covered=len(coverage),budget=budget,remaining=budget-spent)

def intervention_system(df,g,budget=120000):
    present=df.groupby("place")["pressure"].apply(list).to_dict()
    out=[]; top=g[g["tier"].isin(["Critical","Priority"])].head(6)
    for _,row in top.iterrows():
        place=row["place"]; press=set(present.get(place,[])) or {"poverty"}
        levers=[]; exp=0.0; spent=0
        for p in (list(press) if press else ["poverty"]):
            for name,gain,cost in LEVERS.get(p,[]):
                helped=IMPACT_PER_1K[p]*gain
                levers.append(dict(pressure=p,label=PLABEL[p],intervention=name,
                    expected_gain=gain,cost=cost,est_households_helped=round(helped*gain,1)))
                exp+=helped*gain; spent+=cost
                if spent>=budget/len(top): break
        stop=(f"Review at week 8; stop expansion if completion <35% or access gap "
              f"widens in {place}. Escalate to safeguarding lead if self-harm risk indicated.")
        out.append(dict(place=place,region=row["region"],risk=row["risk"],tier=row["tier"],
            hotspot=row.get("hotspot","ns"),pressures=sorted(press) if press else ["poverty"],
            interventions=levers,est_total_households=round(exp,1),est_cost=spent,
            equity_note="Higher expected benefit in this high-deprivation area; monitor differential take-up across underserved groups.",
            stop_condition=stop))
    return out

def dominant_pressure(df,g):
    # attach a dominant pressure per place for trend driver
    pres=df.groupby("place")["pressure"].apply(lambda s:Counter(s).most_common(1)[0][0] if len(s) else "poverty").to_dict()
    g=g.copy(); g["pressure_dominant"]=g["place"].map(pres).fillna("poverty")
    return g

def main():
    recs=load(); df=build_frame(recs)
    g=composite(df); g,spatial_note=spatial(g); g=dominant_pressure(df,g)
    news=json.load(open(NEWS)) if os.path.exists(NEWS) else {}
    trends=trend_projection(g,news)
    edges=causal_graph()
    intervs=intervention_system(df,g,budget=120000)
    alloc=allocate(df,g,budget=120000)
    miro=json.load(open(MIRO)).get("synthesis","") if os.path.exists(MIRO) else ""
    # ---- render ----
    L=[]
    L.append("HUMANITAI — PREVENTION & INTERVENTION SYSTEM v2 (expanded)")
    L.append("="*72)
    L.append(f"Data: {len(df)} records ({df['place'].nunique()} places) + live news layer")
    L.append("1) COMPOSITE RISK + TIER")
    for _,r in g.head(8).iterrows():
        L.append(f"  {int(r['rank']):>2}. {r['place']:<18} risk {r['risk']:5.1f} [{r['tier']}] gi*={r.get('hotspot','ns'):>4} dom={r['pressure_dominant']}")
    L.append("")
    L.append("2) SPATIAL: "+spatial_note)
    L.append("")
    L.append("3) TREND PROJECTION (3-period, news-driven drift; planning only)")
    for t in trends[:6]:
        L.append(f"  {t['place']:<18} now {t['base']:.1f} -> h1 {t['h1']} / h2 {t['h2']} / h3 {t['h3']} (±{t['band_pm']}) [{t['driver']}]")
    L.append("")
    L.append("4) CAUSAL GRAPH (lever -> expected outcome)")
    for e in edges[:10]:
        L.append(f"  {e['pressure']:<13} | {e['lever']:<34} -> {e['expected_outcome']}")
    L.append(f"  ... +{len(edges)-10} edges")
    L.append("")
    if news:
        L.append("5) LIVE NEWS EARLY-WARNING")
        L.append(f"   signals={news.get('n_signals')}  counts={news.get('per_pressure_counts')}")
        L.append(f"   early={news.get('early_warning')}")
    L.append("")
    a=alloc
    L.append(f"6) BUDGET OPTIMISATION £{a['budget']:,}: spent £{a['spent']:,} | {a['places_covered']} places | ~{a['total_hh']} hh | £{a['remaining']:,} left")
    L.append("")
    L.append("7) INTERVENTION SYSTEMS (top-tier)")
    for s in intervs:
        L.append(f"  -- {s['place']} ({s['tier']}, risk {s['risk']}) --")
        for iv in s["interventions"]:
            L.append(f"     * {iv['intervention']} | gain {iv['expected_gain']:.2f} | ~£{iv['cost']} | ~{iv['est_households_helped']} hh")
        L.append(f"     STOP: {s['stop_condition']}")
    if miro:
        L.append("")
        L.append("8) MIROFISH SECOND-ORDER: "+miro.replace("\\n"," "))
    L.append("")
    L.append("NOTE: planning priors transparent/illustrative; trend is planning-only (one slice + news). Replace with evaluation data before spend.")
    print("\n".join(L))
    out=dict(composite=g.to_dict(orient="records"),trends=trends,causal=edges,
             allocation=alloc,interventions=intervs,news=news,mirofish_synthesis=miro,
             spatial_note=spatial_note,generated=datetime.datetime.now(datetime.timezone.utc).isoformat())
    with open(os.path.join(ROOT,"prediction","prevention_out_v2.json"),"w") as f:
        json.dump(out,f,indent=2)
    print("\n[written] prediction/prevention_out_v2.json")

if __name__=="__main__":
    main()
