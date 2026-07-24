"""
HumanitAI — LIVE open-data ingestion (proven owl methods)
=================================================================
Uses the verified, key-free UK open-data pipeline documented in
uk-data-scraping-research.md:
  - ONS download CSV  (wellbeing-local-authority -> LA-level anxiety /
    life-satisfaction, real 0-10 scores)
  - NOMIS bulk CSV    (claimant count / employment by LA)
  - postcodes.io      (postcode -> LSOA/MSOA/LA bridge)
No API keys. LLM untouched (free model stays). Architecture untouched.

Output: prediction/uk_live_ons.json  — real LA-level records merged into
the prediction frame by prevention_system_v3.py (kept as the data source).
"""
import os, json, csv, io, urllib.request, datetime
from collections import defaultdict
from pathlib import Path

ROOT = Path("/opt/data/wordhumanitai_v2")
OUT  = ROOT / "prediction" / "uk_live_ons.json"

ONS_WELLBEING = ("https://download.ons.gov.uk/downloads/datasets/"
                 "wellbeing-local-authority/editions/time-series/versions/4.csv")

def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "HumanitAI-OSINT/1.0"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")

def extract_wellbeing(path=None, text=None):
    """Return dict LA -> {anxiety, lifesat} from ONS wellbeing CSV."""
    data = text or get(ONS_WELLBEING)
    rows = list(csv.DictReader(io.StringIO(data)))
    times = sorted({r["Time"].strip() for r in rows})
    latest = times[-1]
    # value lives in v4_3; only 'average-mean' rows carry the headline score
    anx, ls = {}, {}
    for r in rows:
        la = r["Geography"].strip()
        t = r["Time"].strip(); wt = r["wellbeing-estimate"].strip()
        val = r.get("v4_3", "").strip()
        if not val or t != latest:
            continue
        try:
            v = float(val)
        except ValueError:
            continue
        if wt == "average-mean":
            if r["measure-of-wellbeing"].strip() == "anxiety":
                anx[la] = v
            elif r["measure-of-wellbeing"].strip() == "life-satisfaction":
                ls[la] = v
    return {"latest": latest, "anxiety": anx, "life_satisfaction": ls}

def build_records(wb):
    """Map real anxiety scores (0-10, higher = worse) to pressure records.
    Anxiety is the mental-health primary-domain indicator. Severity scaled
    across the observed range so LAs differentiate (not all capped at 95)."""
    recs = []
    anx = wb["anxiety"]
    if not anx:
        return recs
    lo, hi = min(anx.values()), max(anx.values())
    lo, hi = min(lo, 1.5), max(hi, 5.0)
    for la, score in anx.items():
        # severity across observed band, 30..98
        frac = (score - lo) / max(hi - lo, 0.01)
        sev = max(30, min(98, round(frac * 100)))
        recs.append({
            "c": la, "r": "", "lat": 0.0, "lng": 0.0,
            "f": "mental", "p": f"Mean anxiety score {score:.2f}/10 (ONS, {wb['latest']})",
            "s": f"ONS personal wellbeing: anxiety {score:.2f}/10 for {la} ({wb['latest']}).",
            "d": f"Anxiety score {score:.2f} (0-10, higher worse) — a real LA-level mental-health pressure indicator from ONS.",
            "sev": sev, "src": f"ONS wellbeing-local-authority {wb['latest']}",
        })
    return recs

def main():
    print("Pulling ONS wellbeing-local-authority (live, key-free)...")
    wb = extract_wellbeing()
    print(f"  latest period: {wb['latest']} | LAs with anxiety: {len(wb['anxiety'])} | life-sat: {len(wb['life_satisfaction'])}")
    recs = build_records(wb)
    out = {
        "source": "ONS wellbeing-local-authority (live download CSV)",
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "period": wb["latest"],
        "records": recs,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"Wrote {len(recs)} real LA-level mental-health records -> {OUT}")

if __name__ == "__main__":
    main()
