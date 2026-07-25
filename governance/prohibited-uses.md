# HumanitAI — Prohibited Uses

These uses are **never** permitted, in any module, by any agent or human operator.
They are encoded as hard constraints in the Hermes AGENTS.md and the tool
security pattern, and are checked by red-team tests.

## Surveillance and profiling
- Covert monitoring of distressed or politically inconvenient individuals.
- Citizen-level risk scores shared across agencies without meaningful consent
  or appeal.
- Using vulnerability as a proxy for threat, fraud or disorder.
- Profiling vulnerable groups or predicting access/service demand at the
  individual level.
- Systematic monitoring of public online spaces to infer mental-health status.
- Collecting personal data "because it may become useful later."

## Automated decisions with significant effects
- Automated eligibility, benefits, housing-entitlement or care decisions.
- Automated resource withdrawal, debt enforcement or policing actions.
- Clinical diagnosis or predictive policing.
- Safeguarding closure by an automated system.
- Allocation of emergency help to a named person without human judgement.

## Misuse of intelligence
- Optimising case-closure statistics while leaving root causes unchanged.
- Presenting MiroFish simulation output as numerical probability or community
  consensus.
- Replacing real resident deliberation, trials or service-user research with
  synthetic agent consensus.
- Bypassing authentication, rate limits or technical access controls to collect
  data.
- Editing one's own evaluation results without audit.

## Data minimisation
- Ingesting more data than the stated, approved purpose requires.
- Linking datasets in a way that creates new individual-level inferences without
  a DPIA and a lawful basis.

## Governance overrides
Any of the above may only be permitted if explicitly re-approved by the
HumanitAI Board, DPO and community panel through a recorded, contested decision
— which, by design, this list is intended to prevent.

> Control-heavy pattern: *State sees the citizen.*
> HumanitAI replacement: *Citizen and community can see the system response.*
