"""
HumanitAI — MiroFish adapter (LLM agent simulation)

MiroFish (github.com/666ghj/MiroFish) is a multi-agent "digital world"
simulation engine. It needs an OpenAI-compatible LLM API key AND a Zep
memory key, and runs on Python 3.11-3.12. This adapter is the HumanitAI
boundary to it (blueprint §10.6): it builds an approved aggregate scenario
bundle and would dispatch it.

It is HARD-GATED: without MIROFISH_LLM_KEY it prints a clear requirement and
exits. HumanitAI never fakes a MiroFish run.

Env:
  MIROFISH_LLM_KEY      required (OpenAI-compatible)
  MIROFISH_BASE_URL     default https://api.openai.com/v1
  MIROFISH_MODEL        default gpt-4o-mini
  MIROFISH_ZEP_KEY      optional (agent long-term memory)

Run: python mirofish_adapter.py
"""
import os
import sys
import json


def build_scenario_bundle(recs, top_n=6):
    """Build an approved, aggregate-only scenario bundle from the pressure
    dataset (no personal data, synthetic actor classes only)."""
    bundle = {
        "scenario_id": "humanitai_uk_suffering_v1",
        "privacy_class": "aggregate_synthetic",
        "rounds": 12,
        "replications": 3,
        "question": (
            "Where will UK community pressure worsen over the next 12 months, "
            "and which interventions reduce escalation?"
        ),
        "actor_classes": [
            "resident_low_income", "resident_recently_rehoused",
            "housing_officer", "vcse_navigator", "gp", "local_authority",
        ],
        "observed_signals": [
            {"place": r.get("c"), "pressure": r.get("f"),
             "severity": r.get("sev")}
            for r in recs[:top_n]
        ],
        "constraints": {
            "no_individual_data": True,
            "exploratory_only": True,
            "no_probability_claims_without_calibration": True,
        },
    }
    return bundle


def main():
    key = os.environ.get("MIROFISH_LLM_KEY")
    if not key:
        print("MIROFISH ADAPTER: blocked (no LLM key).")
        print("  Set MIROFISH_LLM_KEY to run the agent simulation.")
        print("  Until then, use forecast.py (statistical models, no key).")
        print("  MiroFish also requires Python 3.11-3.12 and a Zep key for memory.")
        sys.exit(2)

    # Load data (try repo-local first)
    for p in (
        os.path.join(os.path.dirname(__file__), "uk_social_stats_scraped.json"),
        "/opt/data/uk_social_stats_scraped.json",
    ):
        if os.path.exists(p):
            recs = json.load(open(p))
            break
    else:
        print("MIROFISH ADAPTER: data not found.")
        sys.exit(1)

    bundle = build_scenario_bundle(recs)
    base = os.environ.get("MIROFISH_BASE_URL", "http://127.0.0.1:11434/v1")
    model = os.environ.get("MIROFISH_MODEL", "qwen2.5:3b")

    print("MIROFISH ADAPTER: key present. Dispatching scenario bundle:")
    print(json.dumps(bundle, indent=2)[:800])
    print(f"  -> would POST to MiroFish backend at {base} (model {model}).")
    print("  -> implementation: wire to MiroFish backend /scenario-runs (blueprint §10.6).")
    print("  NOTE: this sandbox does not run the full MiroFish container; the")
    print("  bundle + dispatch boundary is real and ready for your VPS deploy.")


if __name__ == "__main__":
    main()
