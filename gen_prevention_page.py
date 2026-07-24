import json, html, os
from pathlib import Path

ROOT = Path("/opt/data/wordhumanitai_v2")
d = json.loads((ROOT / "prediction" / "prevention_out.json").read_text())
comp = d["composite"][:8]
alloc = d["allocation"]
intervs = d["interventions"][:6]

def tier_cls(t):
    return {"Critical": "crit", "Priority": "prio", "Watch": "watch"}.get(t, "watch")

risk_rows = ""
for r in comp:
    risk_rows += (
        f'<div class="rrow"><span class="rk">{int(r["rank"])}</span>'
        f'<span class="rp">{html.escape(r["place"])}</span>'
        f'<span class="rv">{r["risk"]:.1f}</span>'
        f'<span class="rt {tier_cls(r["tier"])}">{r["tier"]}</span>'
        f'<span class="rg">{html.escape(r["region"])}</span></div>\n'
    )

alloc_rows = ""
for f in alloc["funded"][:14]:
    alloc_rows += (
        f'<div class="arow"><span class="ap">{html.escape(f["place"])}</span>'
        f'<span class="ai">{html.escape(f["intervention"])}</span>'
        f'<span class="ac">£{f["cost"]:,}</span>'
        f'<span class="ah">~{f["hh"]} hh</span></div>\n'
    )
if len(alloc["funded"]) > 14:
    alloc_rows += f'<div class="amore">+{len(alloc["funded"]) - 14} more interventions</div>\n'

intv = ""
for s in intervs:
    ivs = "".join(
        f'<div class="iv"><b>{html.escape(iv["intervention"])}</b> — '
        f'gain {iv["expected_gain"]:.2f}, ~£{iv["cost"]:,}, ~{iv["est_households_helped"]} hh</div>'
        for iv in s["interventions"]
    )
    intv += (
        f'<div class="card"><div class="ch"><span class="ct {tier_cls(s["tier"])}">{s["tier"]}</span> '
        f'{html.escape(s["place"])} <span class="cr">risk {s["risk"]}</span></div>'
        f'<div class="cp">pressures: {", ".join(html.escape(p) for p in s["pressures"])}</div>'
        f'{ivs}'
        f'<div class="cmeta"><b>Equity:</b> {html.escape(s["equity_note"])}</div>'
        f'<div class="cstop"><b>Stop / escalate:</b> {html.escape(s["stop_condition"])}</div></div>\n'
    )

miro = d.get("mirofish_synthesis") or ""
miro_html = html.escape(miro).replace("\\n", "<br>") if miro else "<i>run MiroFish layer for second-order view</i>"

FONT = "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&amp;family=Inter:wght@400;500;600"

CSS = """
:root{--ivory:#FBF9F4;--ink:#070709;--dim:#5A554A;--teal:#00BCA3;--teal-deep:#007A68;--vermillion:#E11D0E;--amber:#FF7A00;--hair:#E4DDCC}
*{box-sizing:border-box;margin:0;padding:0}body{background:var(--ivory);color:var(--ink);font-family:Inter,system-ui,sans-serif;line-height:1.6}
.wrap{max-width:1000px;margin:0 auto;padding:0 28px 90px}header{padding:64px 28px 30px;max-width:1000px;margin:0 auto}
.kick{font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--teal-deep);display:flex;gap:12px;align-items:center;margin-bottom:14px}
.kick::before{content:"";width:26px;height:2px;background:var(--teal)}
h1{font-family:Fraunces,serif;font-size:clamp(2rem,5vw,3.2rem);font-weight:700;letter-spacing:-.02em}h1 .a{color:var(--teal)}
.meta{color:var(--dim);font-size:.9rem;margin-top:10px}h2{font-family:Fraunces,serif;font-size:1.6rem;font-weight:600;margin:54px 0 16px}
.rrow,.arow{display:grid;grid-template-columns:40px 1fr 70px 90px 1fr;gap:12px;align-items:center;padding:13px 0;border-top:1px solid var(--hair);font-size:.92rem}
.arow{grid-template-columns:1.1fr 2fr 90px 70px;gap:10px}.rk{color:var(--dim);font-weight:600}.rp{font-weight:600}
.rv{font-family:Fraunces,serif;font-size:1.2rem;font-weight:700}.rt{font-size:.66rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;border-radius:999px;padding:3px 10px;text-align:center;color:#fff}
.rt.crit{background:var(--vermillion)}.rt.prio{background:var(--amber)}.rt.watch{background:#888}.rg{color:var(--dim);font-size:.8rem}
.banner{background:#070709;color:#F4F1EA;border-radius:16px;padding:26px;margin:24px 0;display:flex;gap:40px;flex-wrap:wrap}
.banner div{font-family:Fraunces,serif}.banner .bn{font-size:2rem;font-weight:700;color:#fff;line-height:1}.banner .bl{font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;color:#9A958A;margin-top:6px}
.arow .ap{font-weight:600}.arow .ai{color:var(--dim)}.arow .ac{font-weight:600}.arow .ah{color:var(--teal-deep);font-weight:600;text-align:right}
.amore{padding:10px 0;color:var(--dim);font-size:.85rem}
.card{border:1px solid var(--hair);border-radius:14px;padding:20px;margin:14px 0;background:#fff}.ch{font-family:Fraunces,serif;font-size:1.15rem;font-weight:700}
.ct{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;border-radius:999px;padding:3px 9px;color:#fff;margin-right:8px;vertical-align:middle}.ct.crit{background:var(--vermillion)}.ct.prio{background:var(--amber)}
.cr{color:var(--dim);font-weight:400;font-size:.85rem;margin-left:8px}.cp{color:var(--dim);font-size:.82rem;margin:6px 0 10px}
.iv{padding:6px 0;border-top:1px solid var(--hair);font-size:.9rem}.cmeta,.cstop{font-size:.82rem;color:var(--dim);margin-top:10px;padding-top:10px;border-top:1px solid var(--hair)}
.cstop{border-top:1px dashed var(--hair)}.synth{background:#070709;color:#F4F1EA;border-radius:16px;padding:26px;margin-top:16px;font-size:.95rem;line-height:1.6}.synth b{color:var(--teal)}
.back{display:inline-block;margin-top:30px;color:var(--teal-deep);font-weight:600}.note{font-size:.78rem;color:var(--dim);margin-top:30px;border-top:1px solid var(--hair);padding-top:14px}
"""

page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>HumanitAI — Prevention and Intervention System</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link href="{FONT}" rel="stylesheet">
<style>{CSS}</style></head><body>
<header><div class="kick">Prevention and intervention system · multi-model</div>
<h1>Where to act, <span class="a">and what to do</span></h1>
<div class="meta">Built on HumanitAI's own UK pressure data. Six model layers: composite risk, spatial Gi*, early-warning trajectory, causal-lever scoring, budget optimisation, MiroFish agent reaction.</div></header>
<div class="wrap">
<h2>1 — Composite risk and tier</h2>{risk_rows}
<h2>2 — Budget optimisation (£{alloc['budget']:,})</h2>
<div class="banner">
  <div><div class="bn">£{alloc['spent']:,}</div><div class="bl">deployed</div></div>
  <div><div class="bn">{alloc['places_covered']}</div><div class="bl">places covered</div></div>
  <div><div class="bn">~{alloc['total_hh']}</div><div class="bl">est. households helped</div></div>
  <div><div class="bn">£{alloc['remaining']:,}</div><div class="bl">unallocated</div></div>
</div>{alloc_rows}
<h2>3 — Intervention systems (top-tier places)</h2>{intv}
<h2>4 — Second-order: MiroFish agent reaction</h2><div class="synth">{miro_html}</div>
<div class="note">Planning priors are transparent and illustrative; replace with local evaluation data before any spend. No individual-level inference. Aggregate place-level only.</div>
<a class="back" href="./">Back to HumanitAI</a></div></body></html>"""

(ROOT / "prevention.html").write_text(page)
print("written", len(page), "bytes")
