#!/usr/bin/env bash
# Weekly Community Pressure Brief (Blueprint Appendix B1/B3) — Monday 07:00
# Self-contained: generates the 8-part brief from the open-data scout.
cd /opt/data/wordhumanitai_v2 || exit 1
python3 - <<'PY'
import sys, datetime
sys.path.insert(0, "osint_scout")
import scout
brief = scout.run_scout(live=False)
signals = [scout.Signal(**s) for s in brief["signals"]]
now = datetime.datetime.now(datetime.timezone.utc)
print("HUMANITAI — WEEKLY COMMUNITY PRESSURE BRIEF")
print(f"Generated: {now:%Y-%m-%d %H:%M} UTC   |   Watch mode: {brief['watch_mode']}")
print("=" * 70)
print("1. MATERIAL VERIFIED CHANGES (by place / issue, ranked)")
for i, s in enumerate(signals, 1):
    tag = " [SPIKE]" if s.spike else ""
    print(f"  {i}. {s.place} — {s.pressure}{tag}: {s.headline} (sev {s.severity}/100, src {s.source})")
print("2. DATA-QUALITY WARNINGS")
print("  - Sample-mode active (HUMANITAI_LIVE_OSINT off): versioned snapshots, not live pulls.")
print("  - Action: set HUMANITAI_LIVE_OSINT=1 and verify ONS/Nomis refresh before operational use.")
print("3. FORECAST CHANGES")
print("  - Forecast pending: open-data phase. No model run yet (StatsForecast/PySAL phase 2).")
print("4. SERVICE-CAPACITY CONSTRAINTS")
print("  - Partner feeds not yet connected. Capacity gaps inferred from public stat signal only.")
print("5. POSSIBLE DRIVERS (HYPOTHESES, not facts)")
for s in signals[:3]:
    print(f"  - {s.place} ({s.pressure}): {s.detail}  [hypothesis: structural underinvestment + cost-of-living]")
print("6. EQUITY IMPLICATIONS")
print("  - Child-poverty concentration (Middlesbrough 47%) shows differential exposure by place;")
print("    protect small-count LSOA outputs from publication.")
print("7. THREE ACTION OPTIONS")
print("  A) Deploy CHW team to highest-severity ward — evidence: dashboard composite; cost: ~GBP 35-90k pilot; uncertainty: medium; stop: no improvement at 8 wks.")
print("  B) Fund debt/housing advice capacity — evidence: arrears signal; cost: GBP 830-1,330/avoided escalation; uncertainty: medium; stop: completion <35%.")
print("  C) Expand open-data monitoring to 18 places — evidence: current coverage; cost: low (compute); uncertainty: low; stop: no added signal.")
print("8. ITEMS REQUIRING REVIEW")
print("  - Data steward: approve live ONS pull + refresh cadence.")
print("  - Analyst: confirm SPIKE flags before external use.")
print("  - Safeguarding lead: none indicated (aggregate, no individual risk).")
PY
