"""
HumanitAI x MiroFish engine — UK community-pressure simulation (FREE, LOCAL)

Uses MiroFish's own simulation engine (OASIS / camel-ai) running entirely
locally:
  - LLM backend: Ollama + qwen2.5:3b (local, no API key, no cost)
  - No Zep Cloud, no external services

Scenario: a welfare-policy shock hits Middlesbrough (highest UK child-poverty
at ~47%). We simulate a small multi-agent "digital world" of community
stakeholders and let them react, surfacing where pressure will concentrate and
which interventions agents themselves propose.

Run (Ollama must be serving on :11434):
  . .venv-oasis/bin/activate
  python mirofish_uk_sim.py
"""
import os
import json
import textwrap

from camel.models import OllamaModel, ModelFactory
from camel.types import RoleType, ModelType
from camel.agents import ChatAgent
from camel.messages import BaseMessage

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")

# MiroFish-style persona set for a UK community-pressure "digital world"
PERSONAS = [
    {
        "name": "Priya",
        "role": "Lone parent, Middlesbrough, in work but below poverty line",
        "stance": "Struggling with childcare costs and the upcoming benefit cap.",
    },
    {
        "name": "Dave",
        "role": "Community navigator / VCSE outreach worker",
        "stance": "Sees rising referrals; worried about capacity to respond.",
    },
    {
        "name": "Councillor Rao",
        "role": "Local authority housing & welfare lead",
        "stance": "Under budget pressure; must prioritise prevention spend.",
    },
    {
        "name": "Sam",
        "role": "GP in a deprived practice",
        "stance": "Rising mental-health presentations linked to financial strain.",
    },
]

SHOCK = textwrap.dedent("""
A new national policy tightens the local-housing-allowance and reduces the
working-age benefit uprating below inflation, effective in 3 months.
Middlesbrough already has the worst child poverty in England (~47% of children).
""")

PROMPT_TEMPLATE = """You are {name}, {role}.
Your perspective: {stance}

CONTEXT — policy shock:
{shock}

As the simulation unfolds, respond in 2-3 sentences from your lived or
professional viewpoint: how does this shock hit the people you see, where will
pressure concentrate first, and what should be done in the next 90 days?
Stay concrete and place-specific (Middlesbrough / Tees Valley)."""


def build_model():
    return OllamaModel(
        model_type=MODEL,
        model_config_dict={"temperature": 0.7, "max_tokens": 400},
        url=OLLAMA_URL,
    )


def run_simulation(rounds=2):
    model = build_model()
    agents = []
    for p in PERSONAS:
        agent = ChatAgent(
            system_message=BaseMessage(
                role_name=p["name"],
                role_type=RoleType.USER,
                meta_dict={},
                content=PROMPT_TEMPLATE.format(
                    name=p["name"], role=p["role"], stance=p["stance"], shock=SHOCK
                ),
            ),
            model=model,
            message_window_size=6,
        )
        agents.append((p["name"], agent))

    transcript = []
    for r in range(rounds):
        for name, agent in agents:
            msg = BaseMessage(
                role_name=name,
                role_type=RoleType.USER,
                meta_dict={},
                content=f"[Round {r+1}] Share your update.",
            )
            resp = agent.step(msg)
            text = resp.msgs[0].content if resp.msgs else "(no response)"
            transcript.append({"round": r + 1, "agent": name, "text": text})
            print(f"\n--- {name} (round {r+1}) ---\n{text}")
    return transcript


def summarise(transcript):
    """A lightweight synthesis of where pressure concentrates + proposed fixes,
    derived purely from the agent transcript (no external claims)."""
    model = build_model()
    joined = "\n".join(f"[{t['agent']}] {t['text']}" for t in transcript)
    synth_agent = ChatAgent(
        system_message=BaseMessage(
            role_name="HumanitAI Analyst",
            role_type=RoleType.ASSISTANT,
            meta_dict={},
            content=(
                "You are a HumanitAI analyst. From the simulated stakeholder "
                "transcript below, extract: (1) where community pressure will "
                "concentrate first, (2) three concrete interventions the group "
                "implied. Be concise. Aggregate-level only — no individuals."
            ),
        ),
        model=model,
    )
    out = synth_agent.step(
        BaseMessage(role_name="Analyst", role_type=RoleType.USER,
                    meta_dict={}, content=joined)
    )
    return out.msgs[0].content if out.msgs else "(no synthesis)"


if __name__ == "__main__":
    print("=" * 72)
    print("HUMANITAI // MIROFISH-ENGINE UK SIMULATION (local, free)")
    print(f"LLM: {MODEL} @ {OLLAMA_URL}")
    print("=" * 72)
    transcript = run_simulation(rounds=2)
    print("\n" + "=" * 72)
    print("SYNTHESIS (where pressure concentrates + interventions)")
    print("=" * 72)
    synth = summarise(transcript)
    print(synth)
    with open(os.path.join(os.path.dirname(__file__),
                           "mirofish_uk_sim_out.json"), "w") as f:
        json.dump({"transcript": transcript, "synthesis": synth,
                   "model": MODEL, "llm_backend": OLLAMA_URL}, f, indent=2)
    print("\n[written] prediction/mirofish_uk_sim_out.json")
