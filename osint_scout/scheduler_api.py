"""Scheduler-facing API for the HumanitAI OSINT Scout.

Run locally with:
    uvicorn scheduler_api:app --host 0.0.0.0 --port 8000

Mirrors the proven pattern from awesome-llm-apps/always_on_agents
(always_on_hn_briefing_agent/scheduler_api.py): a small FastAPI surface
with health, dry-run preview, scheduler trigger, and Pub/Sub push hooks.
The dry_run flag keeps delivery off so the monitor can be exercised
safely in cron before it ever sends.
"""

from __future__ import annotations

import base64
import json
from json import JSONDecodeError
from typing import Any, Optional

from fastapi import FastAPI, Request

try:
    from .scout import run_scout
    from .delivery import send_brief
except ImportError:
    from scout import run_scout
    from delivery import send_brief

app = FastAPI(
    title="HumanitAI OSINT Scout — Scheduler API",
    description="HTTP and Pub/Sub hooks for scheduled UK social-pressure scouting runs.",
)


def _as_bool(value: Any, *, default: bool | None = None) -> bool | None:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.lower()
        if low in {"1", "true", "yes"}:
            return True
        if low in {"0", "false", "no"}:
            return False
    return default


def _as_top_n(value: Any) -> int:
    try:
        top_n = int(value)
    except (TypeError, ValueError):
        return 12
    return max(1, min(top_n, 20))


def run_scheduled_scout(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    dry_run = _as_bool(payload.get("dry_run"), default=True)
    live = _as_bool(payload.get("live"), default=None)
    top_n = _as_top_n(payload.get("top_n"))

    brief = run_scout(live=live, top_n=top_n)
    delivery = {
        "attempted": False,
        "sent": False,
        "status": "dry_run",
        "detail": "Set dry_run=false to use configured email/Slack/webhook delivery.",
    }
    if dry_run is False:
        delivery = {"attempted": True, **send_brief(brief)}

    return {"dry_run": dry_run, "top_n": top_n, "delivery": delivery, "brief": brief}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/osint/dry-run")
def dry_run_preview(top_n: int = 12, live: Optional[bool] = None) -> dict[str, Any]:
    return run_scheduled_scout({"dry_run": True, "top_n": top_n, "live": live})


@app.post("/osint/trigger")
async def scheduler_trigger(request: Request) -> dict[str, Any]:
    try:
        payload = await request.json() if request.headers.get("content-length") else {}
    except JSONDecodeError:
        payload = {}
    return run_scheduled_scout(payload)


@app.post("/osint/pubsub")
async def pubsub_trigger(request: Request) -> dict[str, Any]:
    """Cloud Scheduler -> Pub/Sub push compatible endpoint."""
    envelope = await request.json()
    message = envelope.get("message", {}) if isinstance(envelope, dict) else {}
    payload: dict[str, Any] = {}
    encoded = message.get("data")
    if encoded:
        try:
            payload = json.loads(base64.b64decode(encoded).decode("utf-8"))
        except (ValueError, JSONDecodeError):
            payload = {}
    return run_scheduled_scout(payload)
