import json, html, datetime
from pathlib import Path

ROOT = Path("/opt/data/wordhumanitai_v2")
d = json.loads((ROOT / "prediction" / "prevention_out_v2.json").read_text())
comp = d["composite"][:10]
trends = {t["place"]: t for t in d.get("trends", [])}
alloc = d["allocation"]
intervs = d["interventions"][:6]
edges = d.get("causal", [])
news = d.get("news", {})

def tier_cls(t): return {"Critical":"crit","Priority":"prio","Watch":"watch"}.get(t,"watch")
def esc(s): return html.escape(str(s))

risk_rows=""
for r in comp:
    t=trends.get(r["place"],{})
    proj=f"{t.get('h1','-')}/{t.get('h2','-')}/{t.get('h3','-')} (±{t.get('band_pm','?')})" if t else "-"
    risk_rows+=('<tr><td>%d</td><td><b>%s</b></td><td>%.1f</td><td class="%s">%s</td><td>%s</td></tr>\n'
        %(int(r["rank"]),esc(r["place"]),r["risk"],tier_cls(r["tier"]),r["tier"],proj))

causal_rows=""
for e in edges[:12]:
    causal_rows+=('<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n'
        %(esc(e["pressure"]),esc(e["lever"]),esc(e["expected_outcome"])))
if len(edges)>12: causal_rows+='<tr><td colspan="3"><i>+%d more lever-outcome edges</i></td></tr>\n'%(len(edges)-12)

alloc_rows=""
for f in alloc["funded"][:16]:
    alloc_rows+=('<tr><td>%s</td><td>%s</td><td>%s</td><td>£%s</td><td>~%s</td></tr>\n'
        %(esc(f["place"]),esc(f["tier"]),esc(f["intervention"]),f"{f['cost']:,}",f["hh"]))
if len(alloc["funded"])>16: alloc_rows+='<tr><td colspan="5"><i>+%d more</i></td></tr>\n'%(len(alloc["funded"])-16)

intv=""
for s in intervs:
    ivs="".join('<li><b>%s</b> — gain %.2f, ~£%s, ~%s hh</li>'
        %(esc(iv["intervention"]),iv["expected_gain"],f"{iv['cost']:,}",iv["est_households_helped"]) for iv in s["interventions"])
    intv+=('<div class="card"><div class="ch"><span class="ct %s">%s</span> %s <span class="cr">risk %s</span></div>'
        '<div class="cp">pressures: %s</div><ul>%s</ul>'
        '<div class="cstop"><b>Stop / escalate:</b> %s</div></div>\n'
        %(tier_cls(s["tier"]),s["tier"],esc(s["place"]),s["risk"],", ".join(esc(p) for p in s["pressures"]),ivs,esc(s["stop_condition"])))

nw = news.get("early_warning",{}) if news else {}
news_line = ("%d live signals &middot; counts %s &middot; early-warning %s"
    %(news.get("n_signals",0), news.get("per_pressure_counts",{}), nw)) if news else "news layer not run"

miro = d.get("mirofish_synthesis") or ""
miro_html = esc(miro).replace("\\n","<br>") if miro else "<i>run MiroFish layer</i>"

# ---- 2026 UK CIC policy context (verified via GOV.UK, July 2026) ----
POLICY_2026 = [
 ("£2bn Rough Sleeping Strategy", "Landmark 2026 strategy (manifesto commitment to end rough sleeping): 2,400 long-term supported homes + prevention services. CICs can deliver prevention/transition support."),
 ("Ending Homelessness in Communities Fund", "Live 2026 prospectus open to VCSE/CICs for neighbourhood homelessness prevention and support."),
 ("Child Poverty Strategy 2025/26", "Published Dec 2025, updated July 2026. Prevention-focused; the two-child limit and benefit cap remain in place, so income-lift levers are limited and CIC prevention work fills the gap."),
 ("NHS 10-Year Health Plan 2025/26", "Shifts to neighbourhood health, same-day community care and social prescribing — explicit role for VCSE/CIC delivery partners."),
 ("No 10 North / regional mayors", "Prime Minister's office based in Manchester; regional mayors hold key housing and inequality briefs, opening direct CIC commissioning routes."),
]
policy_html=""
for name,desc in POLICY_2026:
    policy_html+=('<div class="prow"><span class="pname">%s</span><span class="pdesc">%s</span></div>\n'
        %(esc(name),esc(desc)))

CSS="""
@page { size: A4; margin: 16mm 15mm; }
body { font-family:'Helvetica Neue',Arial,sans-serif; color:#1a1a1a; font-size:10pt; line-height:1.5; }
h1 { font-family:Georgia,serif; font-size:24pt; font-weight:700; margin:0 0 3pt; }
.sub { color:#5c5648; font-size:9.5pt; margin-bottom:14pt; }
.kick { font-size:8pt; letter-spacing:.18em; text-transform:uppercase; color:#007a68; font-weight:700; margin-bottom:6pt; }
h2 { font-family:Georgia,serif; font-size:14pt; font-weight:700; margin:18pt 0 6pt; border-bottom:2px solid #00bca3; padding-bottom:3pt; }
table { width:100%; border-collapse:collapse; margin:5pt 0; font-size:9pt; }
th { text-align:left; background:#f2efe6; color:#007a68; font-size:7.5pt; text-transform:uppercase; letter-spacing:.05em; padding:4pt 6pt; }
td { padding:4pt 6pt; border-bottom:1px solid #e7e1d3; }
tr:nth-child(even) td { background:#fbf9f4; }
.crit { color:#fff; background:#e11d0e; padding:1pt 5pt; border-radius:3pt; font-size:7.5pt; font-weight:700; }
.prio { color:#fff; background:#ff7a00; padding:1pt 5pt; border-radius:3pt; font-size:7.5pt; font-weight:700; }
.banner { background:#0a0a0a; color:#f4f1ea; padding:12pt 14pt; border-radius:7pt; display:flex; gap:22pt; margin:6pt 0; }
.banner .bn { font-family:Georgia,serif; font-size:16pt; font-weight:700; color:#fff; }
.banner .bl { font-size:7pt; text-transform:uppercase; letter-spacing:.1em; color:#9a958a; margin-top:2pt; }
.card { border:1px solid #e7e1d3; border-radius:6pt; padding:9pt; margin:6pt 0; page-break-inside:avoid; }
.ch { font-family:Georgia,serif; font-size:11pt; font-weight:700; }
.ct { color:#fff; background:#e11d0e; padding:1pt 5pt; border-radius:3pt; font-size:7pt; font-weight:700; margin-right:4pt; }
.cr { color:#5c5648; font-size:8.5pt; margin-left:4pt; }
.cp { color:#5c5648; font-size:8.5pt; margin:3pt 0; }
ul { margin:3pt 0 3pt 15pt; padding:0; } li { margin:1.5pt 0; font-size:9pt; }
.cstop { font-size:8.5pt; color:#5c5648; margin-top:5pt; padding-top:5pt; border-top:1px dashed #e7e1d3; }
.synth { background:#0a0a0a; color:#f4f1ea; border-radius:7pt; padding:12pt; margin-top:6pt; font-size:9.5pt; line-height:1.5; }
.synth b { color:#16e6c8; }
.note { font-size:7.5pt; color:#6b665b; margin-top:14pt; border-top:1px solid #e7e1d3; padding-top:7pt; }
.foot { font-size:7.5pt; color:#9a958a; }
.news { background:#f2efe6; border-left:3px solid #00bca3; padding:7pt 10pt; font-size:9pt; margin:6pt 0; }
.policy { margin:6pt 0; }
.prow { padding:5pt 0; border-bottom:1px solid #e7e1d3; }
.pname { display:block; font-weight:700; color:#007a68; font-size:9.5pt; }
.pdesc { display:block; font-size:8.5pt; color:#3a352c; margin-top:2pt; }
"""

html_doc=f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="kick">Prevention and Intervention System v2 · Multi-Model · Expanded</div>
<h1>Where to act, and what to do</h1>
<div class="sub">HumanitAI CIC. Built on the organisation's own UK pressure data (40 records, 24 places) plus a live news early-warning layer. Eight stacked models: composite risk, spatial Gi*, early-warning trajectory, trend projection, causal graph, news signals, budget optimisation, intervention systems.</div>

<h2>1 — Composite risk, tier and 3-period trend</h2>
<table><tr><th>#</th><th>Place</th><th>Risk</th><th>Tier</th><th>Projected h1/h2/h3 (±band)</th></tr>{risk_rows}</table>

<h2>2 — Budget optimisation (£{alloc['budget']:,})</h2>
<div class="banner">
  <div><div class="bn">£{alloc['spent']:,}</div><div class="bl">deployed</div></div>
  <div><div class="bn">{alloc['places_covered']}</div><div class="bl">places covered</div></div>
  <div><div class="bn">~{alloc['total_hh']}</div><div class="bl">est. households helped</div></div>
  <div><div class="bn">£{alloc['remaining']:,}</div><div class="bl">unallocated</div></div>
</div>
<table><tr><th>Place</th><th>Tier</th><th>Intervention</th><th>Cost</th><th>~HH</th></tr>{alloc_rows}</table>

<h2>3 — Causal graph: lever to expected outcome</h2>
<table><tr><th>Pressure</th><th>Lever</th><th>Expected outcome</th></tr>{causal_rows}</table>

<h2>4 — Intervention systems (top-tier places)</h2>
{intv}

<h2>5 — Live news early-warning</h2>
<div class="news">{news_line}</div>

<h2>6 — 2026 UK CIC policy context (verified, GOV.UK)</h2>
<div class="policy">
{policy_html}
</div>

<h2>7 — Second-order: MiroFish agent reaction</h2>
<div class="synth">{miro_html}</div>

<div class="note">Planning priors are transparent and illustrative; trend projection is planning-only (one cross-sectional slice plus live news momentum), not a calibrated forecast. Replace with local evaluation data before any spend. No individual-level inference. Aggregate place-level only.
<div class="foot">HumanitAI CIC · Community Intelligence Blueprint v1.0 · generated {datetime.date.today().isoformat()}</div></div>
</body></html>"""
(ROOT/"prediction"/"prevention_report_v2.html").write_text(html_doc)
print("html v2 written",len(html_doc),"bytes")
