import json, html
from pathlib import Path

ROOT = Path("/opt/data/wordhumanitai_v2")
d = json.loads((ROOT / "prediction" / "prevention_out.json").read_text())
comp = d["composite"][:8]
alloc = d["allocation"]
intervs = d["interventions"][:6]

def tier_cls(t):
    return {"Critical": "crit", "Priority": "prio", "Watch": "watch"}.get(t, "watch")

def esc(s): return html.escape(str(s))

# Build HTML body
risk_rows = ""
for r in comp:
    risk_rows += (f'<tr><td>{int(r["rank"])}</td><td><b>{esc(r["place"])}</b></td>'
                  f'<td>{r["risk"]:.1f}</td><td class="{tier_cls(r["tier"])}">{r["tier"]}</td>'
                  f'<td>{esc(r["region"])}</td></tr>\n')

alloc_rows = ""
for f in alloc["funded"][:16]:
    alloc_rows += (f'<tr><td>{esc(f["place"])}</td><td>{esc(f["tier"])}</td>'
                   f'<td>{esc(f["intervention"])}</td><td>£{f["cost"]:,}</td>'
                   f'<td>~{f["hh"]}</td></tr>\n')
if len(alloc["funded"]) > 16:
    alloc_rows += f'<tr><td colspan="5"><i>+{len(alloc["funded"]) - 16} more interventions</i></td></tr>\n'

intv = ""
for s in intervs:
    ivs = "".join(f'<li><b>{esc(iv["intervention"])}</b> — gain {iv["expected_gain"]:.2f}, '
                  f'~£{iv["cost"]:,}, ~{iv["est_households_helped"]} hh</li>' for iv in s["interventions"])
    intv += (f'<div class="card"><div class="ch"><span class="ct {tier_cls(s["tier"])}">{s["tier"]}</span> '
             f'{esc(s["place"])} <span class="cr">risk {s["risk"]}</span></div>'
             f'<div class="cp">pressures: {", ".join(esc(p) for p in s["pressures"])}</div>'
             f'<ul>{ivs}</ul>'
             f'<div class="cmeta"><b>Equity:</b> {esc(s["equity_note"])}</div>'
             f'<div class="cstop"><b>Stop / escalate:</b> {esc(s["stop_condition"])}</div></div>\n')

miro = d.get("mirofish_synthesis") or ""
miro_html = esc(miro).replace("\\n", "<br>") if miro else "<i>run MiroFish layer for second-order view</i>"

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: 'Helvetica Neue', Arial, sans-serif; color:#1a1a1a; font-size:10.5pt; line-height:1.5; }
h1 { font-family: Georgia, 'Times New Roman', serif; font-size:26pt; font-weight:700; color:#0a0a0a; margin:0 0 4pt; }
.sub { color:#5c5648; font-size:10pt; margin-bottom:18pt; }
.kick { font-size:8pt; letter-spacing:.18em; text-transform:uppercase; color:#007a68; font-weight:700; margin-bottom:8pt; }
h2 { font-family: Georgia, serif; font-size:15pt; font-weight:700; color:#0a0a0a; margin:22pt 0 8pt; border-bottom:2px solid #00bca3; padding-bottom:4pt; }
table { width:100%; border-collapse:collapse; margin:6pt 0; font-size:9.5pt; }
th { text-align:left; background:#f2efe6; color:#007a68; font-size:8pt; text-transform:uppercase; letter-spacing:.06em; padding:5pt 7pt; }
td { padding:5pt 7pt; border-bottom:1px solid #e7e1d3; }
tr:nth-child(even) td { background:#fbf9f4; }
.crit { color:#fff; background:#e11d0e; padding:1pt 6pt; border-radius:3pt; font-size:8pt; font-weight:700; }
.prio { color:#fff; background:#ff7a00; padding:1pt 6pt; border-radius:3pt; font-size:8pt; font-weight:700; }
.watch { color:#fff; background:#888; padding:1pt 6pt; border-radius:3pt; font-size:8pt; font-weight:700; }
.banner { background:#0a0a0a; color:#f4f1ea; padding:14pt 16pt; border-radius:8pt; display:flex; gap:26pt; margin:8pt 0; }
.banner .bn { font-family:Georgia,serif; font-size:18pt; font-weight:700; color:#fff; }
.banner .bl { font-size:7pt; text-transform:uppercase; letter-spacing:.1em; color:#9a958a; margin-top:3pt; }
.card { border:1px solid #e7e1d3; border-radius:7pt; padding:11pt; margin:8pt 0; page-break-inside:avoid; }
.ch { font-family:Georgia,serif; font-size:12pt; font-weight:700; }
.ct { color:#fff; background:#e11d0e; padding:1pt 6pt; border-radius:3pt; font-size:7.5pt; font-weight:700; margin-right:5pt; }
.ct.prio { background:#ff7a00; }
.cr { color:#5c5648; font-size:9pt; margin-left:5pt; }
.cp { color:#5c5648; font-size:9pt; margin:4pt 0; }
ul { margin:4pt 0 4pt 16pt; padding:0; } li { margin:2pt 0; font-size:9.5pt; }
.cmeta,.cstop { font-size:9pt; color:#5c5648; margin-top:6pt; padding-top:6pt; border-top:1px solid #e7e1d3; }
.cstop { border-top:1px dashed #e7e1d3; }
.synth { background:#0a0a0a; color:#f4f1ea; border-radius:8pt; padding:14pt; margin-top:8pt; font-size:10pt; line-height:1.55; }
.synth b { color:#16e6c8; }
.note { font-size:8pt; color:#6b665b; margin-top:18pt; border-top:1px solid #e7e1d3; padding-top:8pt; }
.foot { font-size:8pt; color:#9a958a; margin-top:4pt; }
"""

html_doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="kick">Prevention and Intervention System · Multi-Model</div>
<h1>Where to act, and what to do</h1>
<div class="sub">HumanitAI CIC — built on the organisation's own UK community-pressure data.
Six model layers: composite risk · spatial Gi* · early-warning trajectory · causal-lever scoring · budget optimisation · MiroFish agent reaction.</div>

<h2>1 — Composite risk and tier</h2>
<table><tr><th>#</th><th>Place</th><th>Risk</th><th>Tier</th><th>Region</th></tr>{risk_rows}</table>

<h2>2 — Budget optimisation (£{alloc['budget']:,})</h2>
<div class="banner">
  <div><div class="bn">£{alloc['spent']:,}</div><div class="bl">deployed</div></div>
  <div><div class="bn">{alloc['places_covered']}</div><div class="bl">places covered</div></div>
  <div><div class="bn">~{alloc['total_hh']}</div><div class="bl">est. households helped</div></div>
  <div><div class="bn">£{alloc['remaining']:,}</div><div class="bl">unallocated</div></div>
</div>
<table><tr><th>Place</th><th>Tier</th><th>Intervention</th><th>Cost</th><th>~HH</th></tr>{alloc_rows}</table>

<h2>3 — Intervention systems (top-tier places)</h2>
{intv}

<h2>4 — Second-order: MiroFish agent reaction</h2>
<div class="synth">{miro_html}</div>

<div class="note">Planning priors are transparent and illustrative; replace with local evaluation data before any spend. No individual-level inference. Aggregate place-level only.
<div class="foot">HumanitAI CIC · Community Intelligence Blueprint v1.0 · generated {__import__('datetime').date.today().isoformat()}</div></div>
</body></html>"""

(ROOT / "prediction" / "prevention_report.html").write_text(html_doc)
print("html written", len(html_doc), "bytes")
