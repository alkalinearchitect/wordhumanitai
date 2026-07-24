"""Delivery handoff for the HumanitAI OSINT Scout.

In production this is where the rendered brief is sent to email, Slack,
or a ticketing system. The repo stub returns a no-op success so the
scheduler can run end-to-end in dry-run/demo mode. Wire a real sender
(e.g. SMTP, Slack incoming webhook, or WhatsApp Business API) here.
"""

from __future__ import annotations

from typing import Any


def send_brief(brief: dict[str, Any]) -> dict[str, Any]:
    """Hand the brief to a delivery channel. Stub: logs and reports.

    Replace the body with a real sender. Expected return shape:
        {"attempted": True, "sent": bool, "status": str, "detail": str}
    """
    # Example real wiring (left commented so the stub stays key-free):
    #
    #   import os, smtplib
    #   to = os.environ["HUMANITAI_ALERT_EMAIL"]
    #   ...send brief["text"] / brief["html"]...
    #
    print(f"[delivery] would send '{brief.get('subject')}' "
          f"with {len(brief.get('signals', []))} signals")
    return {
        "attempted": True,
        "sent": False,
        "status": "stub_noop",
        "detail": "Delivery stub: configure a real sender in delivery.py to go live.",
    }
