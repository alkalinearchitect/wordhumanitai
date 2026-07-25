# The 5th Space — Canal Barge (HumanitAI pillar-2 venue)

**Status:** Active concept — replaces the retired fixed "4th Space" sauna venue.
**Last updated:** 2026-07-25

## What it is
The **5th Space** is a large, off-grid **canal barge** that travels the UK inland-waterway
network (CRT canals + connected rivers) and moors at the towns the HumanitAI forecast flags
as tipping into crisis. It is the mobile, physical arm of the CIC's loneliness intervention.

## Why a barge (not a fixed building)
- A fixed venue waits for people to come to it. The barge **goes to the people**.
- The forecast decides the next mooring; the mooring decides the company.
- Loneliness is a *where-are-you-right-now* problem, so the venue has to move.
- 2,000+ miles of navigable UK canal/river = reach into towns a fixed site could never serve.

## The narrative (website voice)
- "The 4th Space was a room people had to travel to. The 5th Space travels to the people."
- "When the data says a town is about to tip, we don't send a leaflet. We send a hull, a
  fridge, and a face that's expecting you."
- "We arrive before the crisis, before the waiting list, before the headline."

## On-board spaces (target spec)
- Warm room / community saloon (the heart — warm, lit, free)
- Contrast / wellbeing circle (sauna + cold plunge + breathwork, subsidised)
- CHW consultation pod (private, no referral, no waiting list)
- Community galley / kettle (dignity, not a waiting room)
- Small stage / circle for intergenerational sessions

## Operations
- **Vessel:** wide-beam canal barge, ~60–100 ft, ~12–14 ft beam, step-free access where possible.
- **Power:** solar + lithium off-grid (no shore power needed); backup diesel/wood for heat.
- **Water:** tank + pump-out; CRT 14-day mooring limit shapes the stop schedule.
- **Speed:** canals are 4 mph; dispatch is planned weeks ahead from the forecast window.
- **Dispatch:** AI flags a town → route via canal to nearest reachable mooring → moor 14 days →
  rotate. Approx **~12 towns/year** (illustrative planning proxy, not a measured figure).

## Data-model record
- Intervention key: `5th_space_barge`
- Domain: `isolation`
- Outcome: `reduced_loneliness_connection` (kept from the old 4th Space) + `mobile_reach_connection`
- Causal edge: `("5th_space_barge","reduced_loneliness_connection")`
- SROI proxy: `x3.2` (illustrative — replace with evaluation data before any spend)
- Members/mooring: `60` · expected loneliness reduced: `~48` · reach multiplier vs fixed: `x12` (proxies)

## Honest framing (per HumanitAI brand rules)
- Mobility's dividend is **reach and prevention timing**, not per-person intensity.
- All numbers are **illustrative planning proxies**. No fake statistics. No external blame.
- The enemy is the weakness inside — isolation is met with presence, not a leaflet.

## Source files
- `index.html` — section `#fifth-space` (hero copy, SVG barge illustration, pull-quotes, dispatch rows)
- `prediction/prevention_system_v3.py` — `FIFTH_SPACE` dict + `fifth_space_model()` + allocation
- `prediction/prevention_out_v3.json` — generated model output (`fifth_space` key)
- `prediction/prevention_report_v3.html` — generated report (Pillar 2)
- `prediction/5th_space_barge_remodel.md` — impact re-modelling notes (swarm output)
- `prediction/fifth_space_dropin.py` — paste-ready data-model record
