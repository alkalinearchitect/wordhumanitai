# Re-Modelling the Loneliness Intervention: Fixed 4th Space → Mobile 5th Space Canal Barge

**Role:** Impact & Model Economist
**Date:** 2026-07-25
**Subject:** Re-model of the pillar-2 loneliness-combat intervention for a MOBILE canal-barge "5th Space" replacing the FIXED "4th Space" sauna venue.
**Status:** All figures are **illustrative planning proxies** (`[bracketed]`), NOT measured outcomes. Replace with evaluation data before any funding case.

---

## 1. What changes when the venue moves

| Dimension | Fixed 4th Space (old) | Mobile 5th Space barge (new) |
|---|---|---|
| Footprint | One postcode, permanent | ~15 towns/yr, transient |
| Relationship depth | High (steady 60 members) | Lower per stop (barge leaves) |
| Reach breadth | 1 community | Many communities, crisis-targeted |
| Capital/opex shape | Low opex, venue-bound | Higher opex, movable asset |
| Prediction linkage | None (fixed location) | Direct — sails to towns the AI flags as tipping into crisis |

**Core economic insight:** mobility trades *per-person depth* for *geographic breadth and prevention timing*. The fixed model's SROI proxy (x3.2) measured depth at one site. The mobile model must add **reach metrics** the fixed model literally cannot compute, and **spread** the social value across far more people and places.

---

## 2. Reach maths (mobile)

All inputs `[illustrative planning proxies]`:

- **Operating window:** 365 − winter lay-up `[~90 d]` − maintenance/crew leave `[~35 d]` ≈ **`[240 operating days/yr]`**
- **Per-stop cycle:** 14-day mooring limit (Canal & River Trust byelaw) + transit.
  - Inter-town canal gap ≈ `[~30 mi]`; at the brief's **4 mph** cruising = ~7.5 h pure travel, but locks/turnaround ⇒ plan **`[~2 travel days]`** per move.
  - Cycle = 14 + 2 = **`[16 days/stop]`**
- **Stops per year:** 240 / 16 ≈ **`[~15 stops/yr]`** (bracket `[12–20]`)
- **People per stop:** `[18 sessions]` × `[~20 capacity]` = 360 session-slots; de-duplicated cumulative **unique visitors ≈ `[120–200]`**, with **regulars (≥3 visits) ≈ `[30–60]`**
- **Annual unique reach:** `[15]` × `[150]` ≈ **`[~2,250 people/yr]`** across ~15 towns
- **Miles travelled/yr:** `[15]` × `[~30 mi]` ≈ **`[~450 mi/yr]`**

**Reach multiplier vs fixed venue**
- People-touched: `[2,250]` / fixed `[60 steady members]` ≈ **`[~37×]`**
- Geographic sites: `[15 towns]` / fixed `[1 postcode]` = **`[15×]`**

> Caveat: a fixed "member" is a deep, repeated relationship; a mobile "visitor" is shallow. The 37× is *reach*, not *equivalence* — depth is the trade-off (see §3).

---

## 3. SROI proxy shift

| Metric | Fixed 4th Space | Mobile 5th Space (proxy) |
|---|---|---|
| `sroi_proxy` | **x3.2** | **`[x2.6 – x3.4]`, central `[x3.0]`** |
| Basis | £4,320 cohort cost | ~`[£70,000/yr]` operating cost |
| Est. social value | £13,824 | ~`[£210,000/yr]` (£70k × 3.0) |
| Value shape | Depth at one site | Breadth + **averted-escalation** in pre-crisis towns |

**Why the proxy shifts (not just the denominator):**
1. **Lower per-person intensity** — a 14-day stop cannot build the embedded community a permanent sauna does, so `loneliness_reduction` proxy drops from `0.80` → **`[0.55]`**.
2. **Higher per-£ breadth** — the same pound now reaches ~37× more people and 15× more places, and is *targeted* at towns the prediction layer flags as tipping into crisis.
3. **New value stream:** *prevention in pre-crisis towns* — averted escalation that the fixed venue (stuck in one postcode) could never capture. This is harder to monetise, so it is tracked as a **separate proxy**, not folded into the headline x3.0.

**Net read:** comparable per-£ social return, but **distributed thinner per person and wider per place** — and with a prevention-timing dividend the fixed model omits.

---

## 4. New mobile-only metrics (the fixed model cannot compute these)

| Metric | Meaning | Illustrative proxy |
|---|---|---|
| `towns_visited_annual` | Distinct towns served/yr | `[15]` |
| `miles_travelled_annual` | Canal miles sailed/yr | `[450]` |
| `unique_people_reached_annual` | Cumulative unduplicated visitors | `[2,250]` |
| `reach_multiplier_vs_fixed` | People-touched ÷ 60 | `[~37×]` |
| `geo_reach_multiplier` | Towns ÷ 1 | `[15×]` |
| `regulars_per_stop` | Recurring connections per stop | `[30–60]` |
| `connection_depth_index` | Avg visits/regular (depth proxy) | `[~3]` |
| `crisis_priority_hit_rate` | % stops in AI-flagged Critical/Priority towns | `[target ≥80%]` |
| `return_visit_rate` | Re-engagement at later stop or local service | `[measure]` |
| `cost_per_town_reached` | opex ÷ towns | `[~£4,700]` |
| `cost_per_person_reached` | opex ÷ unique people | `[~£31]` |
| `transient_connection_decay` | Loneliness-reduction retention at 30/60 days post-departure | `[new longitudinal metric]` |

---

## 5. Intervention name / record for the data model

**Recommended primary key:** **`5th_space_barge`** (preserves the "Space" lineage: 4th Space sauna → 5th Space barge; the "5th space" is the *mobile* community space).

**Display aliases:** `mobile_warm_space`, `canal_community`

**Causal-graph update** (in `CAUSAL["isolation"]`):
- Remove: `("4th_space_contrast","reduced_loneliness_connection")`
- Add: `("5th_space_barge","reduced_loneliness_connection")` and `("5th_space_barge","mobile_reach_connection")`

**Allocation update** (`allocate()`): the barge is a *single mobile asset*, not "≤3 per place". Add a mobile branch that ring-fences the annual operating cost and tags each stop with its prediction-flagged town, rather than the fixed per-place loop.

---

## 6. Drop-in record (paste-ready)

See `fifth_space_dropin.py` for the exact dict + `fifth_space_model()` function the data team can import. Summary record below.

```json
{
  "id": "5th_space_barge",
  "aliases": ["mobile_warm_space", "canal_community"],
  "name": "5th Space — mobile canal-barge community hub",
  "mode": "mobile",
  "rationale": "Travelling community space that combats loneliness by sailing to towns the prediction layer flags as tipping into crisis. Replaces fixed 4th Space sauna; trades per-site depth for geographic reach + prevention timing.",
  "loneliness_reduction": 0.55,
  "sessions_per_stop": 18,
  "capacity_per_session": 20,
  "stops_per_year": 15,
  "people_reached_per_stop": 150,
  "regulars_per_stop": 45,
  "sroi_proxy": 3.0,
  "annual_operating_cost": 70000,
  "reach_multiplier_vs_fixed_people": 37,
  "geo_reach_multiplier": 15,
  "miles_travelled_annual": 450,
  "illustrative": true
}
```

---

## 7. Economist's recommendation

Adopt `5th_space_barge` as the pillar-2 intervention key. Keep the fixed venue's `reduced_loneliness_connection` outcome but **add `mobile_reach_connection`** and the §4 metrics so the model can express what mobility uniquely delivers. Set the SROI proxy at **`[x3.0]`** (central) with a separate *averted-escalation* proxy for crisis-targeted stops. Flag the lowered per-person depth (`0.55` vs `0.80`) honestly — mobility's dividend is reach and timing, not intensity. **All numbers here are planning proxies; commission a 12-month pilot evaluation before any SIB/grant case.**
