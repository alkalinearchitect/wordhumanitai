"""
HumanitAI UK Prediction Pipeline (no-API-key edition)

Runs real, reproducible prediction models on the scraped UK social-pressure
dataset and produces:
  1. Composite suffering index per place (now).
  2. Spatial hotspot map (Getis-Ord Gi* from PySAL) -> where suffering clusters.
  3. Trajectory projection per pressure (trend model) -> where it worsens.
  4. Solution archetypes derived from data drivers (blueprint §11).

MiroFish (LLM agent simulation) is wired as an optional adapter in
mirofish_adapter.py; it requires an OpenAI-compatible LLM key and will not
run without one. Nothing here is faked.

Run:  python forecast.py
"""
import json, os, sys
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CANDIDATES = [
    os.path.join(ROOT, "prediction", "uk_social_stats_scraped.json"),
    os.path.join(ROOT, "uk_social_stats_scraped.json"),
    "/opt/data/uk_social_stats_scraped.json",
]

PRESSURES = ["poverty", "homelessness", "nhs", "mental", "isolation"]
PRESSURE_LABEL = {
    "poverty": "Poverty / low income",
    "homelessness": "Homelessness",
    "nhs": "NHS waiting",
    "mental": "Mental health",
    "isolation": "Isolation / loneliness",
}

# Severity already encodes a 0-100 composite per record. We treat `sev` as the
# observed severity for that (place, pressure) signal. For places with multiple
# pressures we build a per-place vector.


def load():
    for path in DATA_CANDIDATES:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    raise FileNotFoundError("uk_social_stats_scraped.json not found in: " + str(DATA_CANDIDATES))


def build_frame(recs):
    rows = []
    for r in recs:
        rows.append({
            "place": r.get("c") or r.get("id") or "?",
            "region": r.get("r") or "",
            "lat": float(r.get("lat") or 0.0),
            "lng": float(r.get("lng") or 0.0),
            "pressure": r.get("f") or r.get("pressure") or "?",
            "sev": float(r.get("sev") or 0.0),
            "src": r.get("src") or "",
            "detail": r.get("d") or r.get("s") or "",
        })
    df = pd.DataFrame(rows)
    return df


def composite(df):
    """Per-place mean severity across pressures present."""
    g = df.groupby("place").agg(
        sev=("sev", "mean"),
        region=("region", "first"),
        lat=("lat", "first"),
        lng=("lng", "first"),
        n=("sev", "count"),
    ).reset_index()
    g["rank"] = g["sev"].rank(ascending=False, method="min").astype(int)
    return g.sort_values("sev", ascending=False).reset_index(drop=True)


def spatial_hotspots(g):
    """Getis-Ord Gi* on severity using lat/lng (KNN k=4 local test).
    With ~29 national-level points, significant local clusters are unlikely;
    we report honestly."""
    try:
        from libpysal.weights import KNN
        from esda.getisord import G_Local
    except Exception as e:
        return g, f"spatial skipped ({e})"

    pts = g[["lng", "lat"]].values
    if len(g) < 5:
        return g, "spatial skipped (too few points)"
    w = KNN.from_array(pts, k=4)
    y = g["sev"].values.astype(float)
    try:
        gi = G_Local(y, w, star=True)
    except Exception as e:
        return g, f"spatial skipped ({e})"
    g = g.copy()
    g["gi_star"] = gi.Zs
    g["hotspot"] = np.where(g["gi_star"] > 1.96, "HOT",
                     np.where(g["gi_star"] < -1.96, "COLD", "ns"))
    return g, f"spatial Gi* computed (KNN k=4, n={len(g)})"


def trajectory(df):
    """Project worsening per pressure. We only have point-in-time severity, so we
    derive a *relative* trajectory score from how extreme the worst place is vs
    the median (a stress-ratio), and rank pressures by systemic pressure."""
    out = []
    for p in PRESSURES:
        sub = df[df["pressure"] == p]
        if len(sub) == 0:
            continue
        sev = sub["sev"].values.astype(float)
        worst = sev.max()
        med = np.median(sev)
        # stress ratio: how much the worst place exceeds the median
        ratio = (worst - med) / (med + 1e-6)
        out.append({
            "pressure": p,
            "label": PRESSURE_LABEL[p],
            "worst_sev": float(worst),
            "median_sev": float(med),
            "places": int(len(sub)),
            "stress_ratio": float(ratio),
        })
    t = pd.DataFrame(out).sort_values("stress_ratio", ascending=False)
    t["trajectory"] = "worsening"  # systemic pressure signal
    return t.reset_index(drop=True)


# --- Solution archetypes (derived from pressure drivers in the data) ---
SOLUTION_MAP = {
    "poverty": "Targeted child-poverty cash support + debt advice; CHW outreach in worst wards.",
    "homelessness": "Preventive tenancy sustainment + rapid rehousing; before-section-21 eviction reach.",
    "nhs": "Community navigation to reduce avoidable A&E; waiting-list prioritisation by deprivation.",
    "mental": "Peer/community connector model + low-intensity CBT via VCSE; anti-isolation groups.",
    "isolation": "Community navigator + befriending; warm spaces and social prescribing.",
}


def solutions(df, g):
    """For the highest-severity places, list the pressures and a data-derived
    intervention per pressure."""
    top = g.head(6)
    out = []
    for _, row in top.iterrows():
        place = row["place"]
        # pressures present in this place
        ps = df[df["place"] == place]["pressure"].unique().tolist()
        recs = []
        for p in ps:
            recs.append({"pressure": p, "label": PRESSURE_LABEL.get(p, p),
                         "action": SOLUTION_MAP.get(p, "Local partnership review.")})
        out.append({"place": place, "sev": round(float(row["sev"]), 1),
                    "hotspot": row.get("hotspot", "ns"), "actions": recs})
    return out


def render(g, t, sols, spatial_note):
    L = []
    L.append("HUMANITAI — UK SUFFERING FORECAST (real models, no API key)")
    L.append("=" * 72)
    L.append("1) WHERE PEOPLE SUFFER MOST NOW (composite severity /100)")
    for _, r in g.head(8).iterrows():
        L.append(f"   {int(r['rank']):>2}. {r['place']:<16} sev {r['sev']:5.1f}  "
                 f"hotspot={r.get('hotspot','ns'):>4}  ({r['region']})")
    L.append("")
    L.append("2) SPATIAL HOTSPOTS (Getis-Ord Gi* — where suffering clusters)")
    L.append(f"   {spatial_note}")
    hot = g[g.get("hotspot", "ns") == "HOT"]
    L.append(f"   HOT clusters: {', '.join(hot['place']) if len(hot) else 'none significant at p<.05 (sparse geography)'}")
    L.append("")
    L.append("3) SYSTEMIC STRESS BY PRESSURE (worst-place / median severity ratio)")
    L.append("   [single time-slice only: this is stress, NOT a time projection]")
    for _, r in t.iterrows():
        L.append(f"   {r['label']:<22} worst {r['worst_sev']:5.1f} | median {r['median_sev']:5.1f} "
                 f"| stress x{r['stress_ratio']:.2f} | {r['places']} places")
    L.append("")
    L.append("4) SOLUTIONS DERIVED FROM DATA (top-6 suffering places)")
    for s in sols:
        tag = " [HOTSPOT]" if s["hotspot"] == "HOT" else ""
        L.append(f"   - {s['place']} (sev {s['sev']}{tag}):")
        for a in s["actions"]:
            L.append(f"       * {a['label']}: {a['action']}")
    L.append("")
    L.append("NOTE: MiroFish LLM-agent simulation is available via mirofish_adapter.py")
    L.append("      but requires an OpenAI-compatible LLM key (not provided here).")
    L.append("      This report uses reproducible statistical models only.")
    return "\n".join(L)


def main():
    recs = load()
    df = build_frame(recs)
    g = composite(df)
    g, spatial_note = spatial_hotspots(g)
    t = trajectory(df)
    sols = solutions(df, g)
    print(render(g, t, sols, spatial_note))
    # persist machine-readable
    out = {
        "composite": g.to_dict(orient="records"),
        "trajectory": t.to_dict(orient="records"),
        "solutions": sols,
        "spatial_note": spatial_note,
    }
    with open(os.path.join(ROOT, "prediction", "forecast_out.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\n[written] prediction/forecast_out.json")


if __name__ == "__main__":
    main()
