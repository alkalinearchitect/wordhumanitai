# HumanitAI OSINT Scout

An **always-on early-warning monitor** for UK social pressure — the real
engine behind the HumanitAI claim that *"the agent that helps you think is
the same swarm that tells our teams where to go."*

Built following the proven architecture from
[awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)
(`always_on_agents/always_on_hn_briefing_agent`): a self-contained
**scout → scheduler API → delivery** loop with `dry_run` safety and a
sample-data fallback so it runs with **zero API keys**.

## What it does

- Tracks five pressures HumanitAI forecasts: **poverty, homelessness, NHS
  strain, mental health, isolation**.
- Scores and ranks signals by severity (highest pressure first — same
  ordering as the public dashboard).
- Flags **SPIKE** language (record / rising / surge / worst) for prioritisation.
- Renders a plain-text + HTML brief ready to hand to email, Slack, or a
  ticketing system.

## Run it (no keys)

```bash
python3 osint_scout/scout.py            # prints the sample brief
python3 osint_scout/scout.py --live      # attempts live ONS pull, falls back to sample
```

## Run the API

```bash
pip install -r osint_scout/requirements.txt
uvicorn osint_scout.scheduler_api:app --host 0.0.0.0 --port 8000
```

Endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | liveness |
| GET | `/osint/dry-run?top_n=12` | preview the brief, no delivery |
| POST | `/osint/trigger` | scheduled run; `{"dry_run":false}` to deliver |
| POST | `/osint/pubsub` | Cloud Scheduler → Pub/Sub push hook |

## Wire it to a schedule

- **cron / systemd**: `curl -X POST localhost:8000/osint/trigger -d '{"dry_run":false}'`
- **GitHub Actions** (hourly): a workflow that hits `/osint/trigger`.
- **Cloud Scheduler + Pub/Sub**: POST to `/osint/pubsub`.

## Going live (real OSINT)

Set `HUMANITAI_LIVE_OSINT=1` to attempt unauthenticated UK open-data
endpoints (ONS download CSVs, NOMIS bulk CSV, Trussell Trust open
releases). The repo's `uk-data-scraping-research.md` documents the
verified, live-tested sources. On any failure it silently falls back to
the bundled, source-cited sample set so the monitor never returns empty.

## Files

- `scout.py` — fetch + score + render the brief (stdlib core)
- `scheduler_api.py` — FastAPI hooks (health / dry-run / trigger / pubsub)
- `delivery.py` — handoff stub (wire email / Slack / WhatsApp here)
