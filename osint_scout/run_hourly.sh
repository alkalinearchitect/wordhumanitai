#!/usr/bin/env bash
# Hourly OSINT early-warning run for HumanitAI.
# Output (stdout) is delivered by the Hermes cron scheduler.
cd /opt/data/wordhumanitai_v2 || exit 1
python3 osint_scout/scout.py 2>&1
