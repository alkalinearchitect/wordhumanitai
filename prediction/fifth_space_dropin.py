"""
fifth_space_dropin.py — PASTE-READY record for the mobile 5th Space canal barge.

Drop into prevention_system_v3.py to replace the fixed 4th Space intervention.

ALL NUMBERS ARE ILLUSTRATIVE PLANNING PROXIES — not measured outcomes.
Replace with 12-month pilot evaluation data before any funding/SIB case.
"""

# ── 1) Intervention record (replaces FOURTH_SPACE dict) ──────────────────────
FIFTH_SPACE_BARGE = {
    "id": "5th_space_barge",                      # data-model key (replaces 4th_space_contrast)
    "aliases": ["mobile_warm_space", "canal_community"],
    "name": "5th Space — mobile canal-barge community hub",
    "mode": "mobile",
    "rationale": ("A travelling community space that combats loneliness by sailing the canal "
                  "network to towns the prediction layer flags as tipping into crisis. Replaces "
                  "the fixed 4th Space sauna venue; trades per-site depth for geographic reach "
                  "and prevention timing."),
    "levers": [
        ("Barge drop-in warm space + brew (open sessions)", 0.55, 420),
        ("Guided group circle / peer connection on board", 0.58, 460),
        ("Intergenerational + signposting to local services", 0.60, 500),
    ],
    "loneliness_reduction": 0.55,   # lower than fixed 0.80: relationships can't deepen at one stop
    "sessions_per_stop": 18,        # over a 14-day mooring
    "capacity_per_session": 20,     # narrower than a fixed hall
    "stops_per_year": 15,           # 14-day mooring + ~2-day transit + lay-up  [illustrative]
    "people_reached_per_stop": 150, # cumulative unique visitors per stop        [illustrative]
    "regulars_per_stop": 45,        # form a recurring connection during the stop [illustrative]
    "sroi_proxy": 3.0,              # £ social value per £ invested (breadth > depth)
    "annual_operating_cost": 70000, # crew + fuel + mooring + maintenance        [illustrative]
    # ── mobile-only metrics the fixed model could not compute ──
    "miles_travelled_annual": 450,          # stops_per_year * ~30mi gap
    "reach_multiplier_vs_fixed_people": 37, # ~2250 unique / 60 fixed members
    "geo_reach_multiplier": 15,             # 15 towns / 1 postcode
    "connection_depth_index": 3,           # avg visits per regular
    "illustrative": True,
}

# ── 2) Model function (mirrors fourth_space_model()) ─────────────────────────
def fifth_space_model():
    fs = FIFTH_SPACE_BARGE
    annual_cost = fs["annual_operating_cost"]
    # annual unique reach across all stops
    annual_reach = fs["stops_per_year"] * fs["people_reached_per_stop"]
    # expected loneliness-reduced = regulars (depth) proxy, not shallow drop-ins
    expected_reduced = round(fs["stops_per_year"] * fs["regulars_per_stop"]
                             * fs["loneliness_reduction"])
    return dict(
        spec=fs,
        stops_per_year=fs["stops_per_year"],
        people_reached_per_stop=fs["people_reached_per_stop"],
        annual_unique_reach=annual_reach,
        regulars_per_stop=fs["regulars_per_stop"],
        expected_loneliness_reduced=expected_reduced,
        reach_multiplier_vs_fixed_people=fs["reach_multiplier_vs_fixed_people"],
        geo_reach_multiplier=fs["geo_reach_multiplier"],
        miles_travelled_annual=fs["miles_travelled_annual"],
        sroi_proxy=fs["sroi_proxy"],
        est_annual_investment=annual_cost,
        est_social_value=round(annual_cost * fs["sroi_proxy"]),
        illustrative=True,
    )

# ── 3) CAUSAL graph patch (replace in CAUSAL["isolation"]) ───────────────────
# OLD: ("4th_space_contrast","reduced_loneliness_connection")
# NEW:
CAUSAL_ISOLATION_PATCH = [
    ("5th_space_barge", "reduced_loneliness_connection"),
    ("5th_space_barge", "mobile_reach_connection"),
    ("navigator_befriend", "reduced_loneliness"),
    ("group_activity", "increased_belonging"),
]

# ── 4) allocate() patch note ─────────────────────────────────────────────────
# The barge is ONE mobile asset, not "≤3 per place". Add a mobile branch:
#   fs_cost = FIFTH_SPACE_BARGE["annual_operating_cost"]
#   fund once; tag each stop with its prediction-flagged town; do NOT use per-place loop.
#   track crisis_priority_hit_rate = stops_in_critical_or_priority_towns / stops_per_year

if __name__ == "__main__":
    import json
    print(json.dumps(fifth_space_model(), indent=2))
