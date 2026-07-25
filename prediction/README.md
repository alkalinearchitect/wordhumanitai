# HumanitAI — UK Prediction Stack (free, local, no API keys)

Two complementary prediction layers, both running on open-source GitHub repos
and a free local model — **no paid API, no external accounts**.

## Layer 1 — Statistical models (`forecast.py`)
Reproducible, no-LLM prediction on the 29-record UK pressure dataset:
- composite suffering index per place
- spatial hotspots (PySAL Getis-Ord Gi\*)
- systemic-stress by pressure
- data-derived interventions per place

Run: `.venv-pred/bin/python prediction/forecast.py`

## Layer 2 — MiroFish engine simulation (`mirofish_uk_sim.py`)
Runs MiroFish's own multi-agent engine (OASIS / camel-ai) as a "digital world"
of UK community stakeholders reacting to a policy shock. Free because the LLM
backend is **Ollama + qwen2.5:3b** running locally (OpenAI-compatible, no key).

Setup (one shot): `bash prediction/setup_local.sh`
Run:   `.venv-oasis/bin/python prediction/mirofish_uk_sim.py`
Output: `prediction/mirofish_uk_sim_out.json`

## Why not the full MiroFish app?
MiroFish's web app hard-requires **Zep Cloud** (hosted agent-memory service,
needs an account/key). The simulation *engine* (OASIS) does not. This stack
uses the engine directly — same prediction, fully free and local. To run the
full MiroFish app instead, add a free Zep key and point `LLM_BASE_URL` in
`MiroFish/.env` at `http://127.0.0.1:11434/v1` with `LLM_MODEL_NAME=qwen2.5:3b`.

## Ethics guardrails (per Community Intelligence Blueprint)
- aggregate / synthetic actors only; no individual-level inference
- outputs are exploratory hypotheses, not calibrated probabilities
- MiroFish runs internally; never presented as community consensus
