# HumanitAI — Hermes operating files

This directory holds the Hermes Agent operating system for HumanitAI, per the
**Community Intelligence Blueprint v1.0** (July 2026), §7 and §13.4.

## Files
- `SOUL.md` — civic-intelligence operator identity and doctrine.
- `AGENTS.md` — 10 binding operating rules for every session, subagent and cron.
- `skills/humanitai-weekly-brief/` — the weekly Community Pressure Brief skill
  (Appendix B1). Copy to `~/.hermes/skills/` to activate.
- `cron/weekly_brief.sh` — self-contained Monday 07:00 brief generator
  (Appendix B3). Run by the Hermes cron scheduler.

## Active schedules (Hermes cron)
- **Hourly** — `osint_scout` early-warning run → Telegram ping.
- **Monday 07:00** — weekly Community Pressure Brief → Telegram.

## Boundary (never violated)
Hermes orchestrates but cannot bypass access control, publish externally, or
alter production data without a signed approval token. Aggregate place-level
intelligence is the default; individual case data is exceptional, consented and
separately governed. See `governance/prohibited-uses.md`.
