import json, html, datetime
from pathlib import Path

ROOT = Path("/opt/data/wordhumanitai_v2")
d = json.loads((ROOT / "prediction" / "prevention_out_v3.json").read_text())
comp = d["composite"][:10]
trends = {t["place"]: t for t in d.get("trends", [])}
alloc = d["allocation"]
intervs = d["interventions"][:6]
edges = d.get("causal", [])
fs = d.get("fourth_space", {})
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
if len(edges)>12: causal_rows+='<tr><td colspan="3"><i>+%d more edges</i></td></tr>\n'%(len(edges)-12)

fs_spec=fs.get("spec",{})
fs_html=('<div class="fs"><div class="fsh">%s</div><div class="fsr">%s</div>'
    '<div class="fsm">Members/site: <b>%s</b> &middot; Expected loneliness reduced: <b>%s</b> &middot; SROI proxy: <b>x%s</b></div>'
    '<div class="fsm">Est. annual investment: <b>£%s</b> &rarr; est. social value: <b>£%s</b></div>'
    '<div class="fslev">%s</div></div>\n')%(
    esc(fs_spec.get("name","")), esc(fs_spec.get("rationale","")),
    fs.get("members_per_site",0), fs.get("expected_loneliness_reduced",0), fs.get("sroi_proxy",0),
    f"{fs.get('est_annual_investment',0):,}", f"{fs.get('est_social_value',0):,}",
    "".join('<li>%s (gain %.2f, ~£%s)</li>'%(esc(l[0]),l[1],f"{l[2]:,}") for l in fs_spec.get("levers",[])))

alloc_rows=""
for f in alloc["funded"][:16]:
    alloc_rows+=('<tr><td>%s</td><td>%s</td><td>%s</td><td>£%s</td><td>~%s</td></tr>\n'
        %(esc(f["place"]),esc(f["tier"]),esc(f["intervention"]),f"{f['cost']:,}",f["hh"]))
if len(alloc["funded"])>16: alloc_rows+='<tr><td colspan="5"><i>+%d more</i></td></tr>\n'%(len(alloc["funded"])-16)

intv=""
for s in intervs:
    ivs="".join('<li><b>%s</b> — gain %.2f, ~£%s</li>'
        %(esc(iv["intervention"]),iv["expected_gain"],f"{iv['cost']:,}") for iv in s["interventions"])
    intv+=('<div class="card"><div class="ch"><span class="ct %s">%s</span> %s <span class="cr">risk %s</span></div>'
        '<div class="cp">pressures: %s</div><ul>%s</ul>'
        '<div class="cstop"><b>Stop / escalate:</b> %s</div></div>\n'
        %(tier_cls(s["tier"]),s["tier"],esc(s["place"]),s["risk"],", ".join(esc(p) for p in s["pressures"]),ivs,esc(s["stop_condition"])))

nw = news.get("early_warning",{}) if news else {}
news_line = ("%d live signals &middot; early-warning %s"%(news.get("n_signals",0),nw)) if news else "news not run"

miro = d.get("mirofish_synthesis") or ""
miro_html = esc(miro).replace("\\n","<br>") if miro else "<i>run MiroFish layer</i>"

CSS="""
@page { size: A4; margin: 16mm 15mm; }
body { font-family:'Helvetica Neue',Arial,sans-serif; color:#1a1a1a; font-size:10pt; line-height:1.5; }
h1 { font-family:Georgia,serif; font-size:23pt; font-weight:700; margin:0 0 3pt; }
.sub { color:#5c5648; font-size:9.5pt; margin-bottom:12pt; }
.kick { font-size:8pt; letter-spacing:.18em; text-transform:uppercase; color:#007a68; font-weight:700; margin-bottom:6pt; }
h2 { font-family:Georgia,serif; font-size:13.5pt; font-weight:700; margin:17pt 0 6pt; border-bottom:2px solid #00bca3; padding-bottom:3pt; }
table { width:100%; border-collapse:collapse; margin:5pt 0; font-size:9pt; }
th { text-align:left; background:#f2efe6; color:#007a68; font-size:7.5pt; text-transform:uppercase; letter-spacing:.05em; padding:4pt 6pt; }
td { padding:4pt 6pt; border-bottom:1px solid #e7e1d3; }
tr:nth-child(even) td { background:#fbf9f4; }
.crit { color:#fff; background:#e11d0e; padding:1pt 5pt; border-radius:3pt; font-size:7.5pt; font-weight:700; }
.prio { color:#fff; background:#ff7a00; padding:1pt 5pt; border-radius:3pt; font-size:7.5pt; font-weight:700; }
.banner { background:#0a0a0a; color:#f4f1ea; padding:12pt 14pt; border-radius:7pt; display:flex; gap:22pt; margin:6pt 0; }
.banner .bn { font-family:Georgia,serif; font-size:16pt; font-weight:700; color:#fff; }
.banner .bl { font-size:7pt; text-transform:uppercase; letter-spacing:.1em; color:#9a958a; margin-top:2pt; }
.fs { border:2px solid #00bca3; border-radius:8pt; padding:11pt; margin:6pt 0; background:#f6fbfa; }
.fsh { font-family:Georgia,serif; font-size:12pt; font-weight:700; color:#007a68; }
.fsr { font-size:9pt; color:#3a352c; margin:4pt 0; }
.fsm { font-size:9pt; margin:2pt 0; }
.fslev { font-size:9pt; margin-top:5pt; }
.card { border:1px solid #e7e1d3; border-radius:6pt; padding:9pt; margin:6pt 0; page-break-inside:avoid; }
.ch { font-family:Georgia,serif; font-size:11pt; font-weight:700; }
.ct { color:#fff; background:#e11d0e; padding:1pt 5pt; border-radius:3pt; font-size:7pt; font-weight:700; margin-right:4pt; }
.cr { color:#5c5648; font-size:8.5pt; margin-left:4pt; }
.cp { color:#5c5648; font-size:8.5pt; margin:3pt 0; }
ul { margin:3pt 0 3pt 15pt; padding:0; } li { margin:1.5pt 0; font-size:9pt; }
.cstop { font-size:8.5pt; color:#5c5648; margin-top:5pt; padding-top:5pt; border-top:1px dashed #e7e1d3; }
.synth { background:#0a0a0a; color:#f4f1ea; border-radius:7pt; padding:12pt; margin-top:6pt; font-size:9.5pt; line-height:1.5; }
.synth b { color:#16e6c8; }
.note { font-size:7.5pt; color:#6b665b; margin-top:13pt; border-top:1px solid #e7e1d3; padding-top:7pt; }
.foot { font-size:7.5pt; color:#9a958a; }
"""

html_doc=f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="kick">HumanitAI · Prevention & Intervention System v3 · Architecture-Aligned</div>
<h1>Where to act, and what to build</h1>
<div class="sub">Two pillars. <b>Pillar 1 — Prediction:</b> models on existing UK open data to target help, with <b>mental health and ageing as the primary domains</b>. <b>Pillar 2 — 4th Space:</b> a physical/social venue (sauna, cold plunge, contrast therapy) that combats loneliness by bringing people together. This pack models both.</div>

<h2>1 — Composite risk, tier and 3-period trend</h2>
<table><tr><th>#</th><th>Place</th><th>Risk</th><th>Tier</th><th>Projected h1/h2/h3 (±band)</th></tr>{risk_rows}</table>

<h2>2 — Pillar 2: 4th Space model (flagship loneliness intervention)</h2>
{fs_html}

<h2>3 — Budget optimisation (£{alloc['budget']:,})</h2>
<div class="banner">
  <div><div class="bn">£{alloc['spent']:,}</div><div class="bl">deployed</div></div>
  <div><div class="bn">{alloc['places_covered']}</div><div class="bl">places covered</div></div>
  <div><div class="bn">~{alloc['total_hh']}</div><div class="bl">est. people helped</div></div>
  <div><div class="bn">£{alloc['remaining']:,}</div><div class="bl">unallocated</div></div>
</div>
<table><tr><th>Place</th><th>Tier</th><th>Intervention</th><th>Cost</th><th>~People</th></tr>{alloc_rows}</table>

<h2>4 — Causal graph: lever to expected outcome</h2>
<table><tr><th>Pressure</th><th>Lever</th><th>Expected outcome</th></tr>{causal_rows}</table>

<h2>5 — Intervention systems (top-tier places)</h2>
{intv}

<h2>6 — Live news early-warning</h2>
<div class="news" style="background:#f2efe6;border-left:3px solid #00bca3;padding:7pt 10pt;font-size:9pt;margin:6pt 0">{news_line}</div>

<h2>7 — Second-order: MiroFish agent reaction</h2>
<div class="synth">{miro_html}</div>

<div class="note">Mental health and ageing are the primary modelled domains per the CIC architecture; the 4th Space is the flagship loneliness-combat intervention. Priors are transparent and illustrative; trend projection is planning-only (one slice + live news momentum), not a calibrated forecast. Replace with local evaluation data before any spend. No individual-level inference. Aggregate place-level only.
<div class="foot">HumanitAI CIC · Community Intelligence Blueprint v1.0 · generated {datetime.date.today().isoformat()}</div></div>
</body></html>"""
(ROOT/"prediction"/"prevention_report_v3.html").write_text(html_doc)
print("html v3 written",len(html_doc),"bytes")
