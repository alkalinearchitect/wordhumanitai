# HumanitAI: Open-Source Intelligence Architecture for UK Social Impact

## Technical Whitepaper v1.0

**Author:** HumanitAI CIC  
**Date:** July 2026  
**License:** AGPL-3.0  

---

## Abstract

Britain spends £1.2 trillion per year through Whitehall. 14.3 million people remain in poverty. The gap between spending and outcome is not a funding problem — it is an intelligence problem. This whitepaper presents the HumanitAI architecture: a multi-layer system combining Open-Source Intelligence (OSINT), multi-agent swarm prediction (Human Architect Technology), Community Health Worker (CHW) ground truth, Social Impact Bond (SIB) financing, and Social Return on Investment (SROI) measurement. Deployed across 18 UK regions with verified ONS, JRF, and Trussell Trust data.

---

## 1. Problem Statement

### 1.1 The Intelligence Gap

The UK government collects vast amounts of social data — ONS poverty statistics, NHS waiting lists, Trussell Trust food bank figures, MHCLG homelessness counts. This data is:
- **Siloed** across departments with no cross-referencing
- **Lagging** — published quarterly or annually, never real-time
- **Uncorrelated** — no system connects rising child poverty with NHS waiting lists with food bank demand

The result: £1.2T spent, but interventions arrive after crisis, not before.

### 1.2 The Prediction Gap

Traditional social forecasting relies on:
- Linear regression on historical data
- Single-factor analysis
- Expert opinion panels

None of these capture the **emergent behavior** of complex social systems — where rising rents + NHS delays + benefit cuts interact non-linearly to create homelessness spikes that no single indicator predicted.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    HUMANITAI ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐    ┌──────────────────────────────┐     │
│  │   LAYER 1:       │    │   LAYER 2:                    │     │
│  │   OSINT DATA      │───▶│   HUMAN ARCHITECT            │     │
│  │   GATHERING       │    │   TECHNOLOGY                 │     │
│  │                   │    │   (Multi-Agent Swarm)        │     │
│  │ • ONS API         │    │                              │     │
│  │ • NHS England RTT │    │ • Knowledge Graph (Neo4j)    │     │
│  │ • Trussell Trust  │    │ • Agent Persona Generation   │     │
│  │ • JRF Publications│    │ • Social Simulation (OASIS)  │     │
│  │ • gov.uk MHCLG    │    │ • Sentiment Tracking         │     │
│  │ • End Child Poverty│   │ • Cross-Dimensional Analysis │     │
│  │ • Web Search/Browser│  │ • Confidence Scoring         │     │
│  └─────────────────┘    └──────────┬───────────────────┘     │
│                                    │                           │
│                                    ▼                           │
│  ┌────────────────────────────────────────────────────────┐   │
│  │   LAYER 3: PREDICTION + VERIFICATION PIPELINE           │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌───────────┐  ┌──────────────────┐ │   │
│  │  │ CHW Ground   │  │ SIB       │  │ SROI             │ │   │
│  │  │ Truth Teams  │  │ Financing │  │ Measurement      │ │   │
│  │  │ (Model 1)    │  │ (Model 3) │  │ (Model 4)        │ │   │
│  │  └──────────────┘  └───────────┘  └──────────────────┘ │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │   OUTPUTS                                              │   │
│  │  • Crisis Prediction Maps (18 UK regions)               │   │
│  │  • SROI-Verified Outcome Reports                        │   │
│  │  • Deployment Recommendations                           │   │
│  │  • Real-time OSINT Dashboard                            │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1: OSINT Data Gathering

### 3.1 Data Sources

| Source | Data Type | Access Method | Update Frequency |
|--------|-----------|---------------|------------------|
| ONS API | Poverty, employment, life expectancy | REST API | Quarterly |
| NHS England RTT | Waiting lists by trust | Public CSV download | Monthly |
| Trussell Trust | Food parcel distribution | Open data portal | Quarterly |
| JRF Publications | UK Poverty reports | PDF/HTML scrape | Annually |
| gov.uk MHCLG | Statutory homelessness | API + CSV | Quarterly |
| End Child Poverty Coalition | Child poverty by ward | Published datasets | Annually |
| NOMIS | Labour market, claimant counts | API | Monthly |
| UK Parliament | Constituency data | OpenAPI | Continuous |

### 3.2 Browser-Based Data Gathering

For data sources without APIs, we employ browser automation techniques:
- Headless browser scraping of public dashboards
- HTML parsing of published HTML tables
- PDF-to-text extraction for published reports
- RSS/Atom feed monitoring for new publications

### 3.3 Data Schema

Every data point is normalized to a common schema:

```json
{
  "region": "Bradford West",
  "category": "poverty",
  "indicator": "child_poverty_rate",
  "value": 40.5,
  "unit": "percent",
  "source": "End Child Poverty Coalition",
  "year": 2024,
  "confidence": 0.95,
  "geo": { "lat": 53.796, "lng": -1.7594 }
}
```

---

## 4. Layer 2: Human Architect Technology

### 4.1 Core Architecture (MiroFish-Based)

Human Architect Technology is a multi-agent swarm intelligence engine built on the open-source [MiroFish](https://github.com/666ghj/MiroFish) framework (69K+ ⭐, AGPL-3.0).

#### 4.1.1 Graph Building

Seed data from OSINT Layer 1 feeds a knowledge graph (Neo4j):
- **Entities**: UK regions, demographics, social indicators, institutions
- **Relationships**: Correlation weights, temporal sequences, causal links
- **Memory**: Individual (per-region historical trends) and collective (national patterns)

#### 4.1.2 Agent Persona Generation

Each of 5+ agent clusters represents a distinct analytical perspective:

| Cluster | Perspective | Input Data |
|---------|-------------|------------|
| Economic | Cost-of-living, employment, inflation | ONS, NOMIS, HMRC |
| Health | NHS capacity, mental health, life expectancy | NHS England, ONS Health |
| Housing | Homelessness, rent, temporary accommodation | MHCLG, Shelter |
| Education/Youth | NEET rates, child poverty, digital exclusion | DfE, End Child Poverty |
| Community | Loneliness, food security, social cohesion | Trussell Trust, ONS Loneliness |

Each agent has:
- **Personality**: Analytical bias (conservative/aggressive in predictions)
- **Memory**: Historical awareness of their domain
- **Influence Weight**: How much their predictions affect the ensemble
- **Reaction Function**: How they respond to new data injection

#### 4.1.3 Simulation Engine (OASIS-Based)

The simulation runs on [OASIS](https://github.com/camel-ai/oasis) (Open Agent Social Interaction Simulations):
- Agents post predictions to a shared "social platform"
- Agents read and react to each other's predictions
- Consensus emerges through iterative debate
- Sentiment tracked per dimension over simulated time

#### 4.1.4 Cross-Dimensional Analysis

Seven dimensions analysed simultaneously:
1. Health
2. Housing
3. Food security
4. Employment
5. Digital exclusion
6. Education
7. Social isolation

Each dimension is scored (0-100 severity) and cross-correlated.

### 4.2 Prediction Output

```json
{
  "prediction_id": "2026-Q3-Bradford",
  "target_region": "Bradford West",
  "primary_crisis": "child_poverty_escalation",
  "confidence": 0.85,
  "timeframe": "6 months",
  "contributing_factors": [
    { "factor": "rising_rent_costs", "weight": 0.7, "source": "ONS" },
    { "factor": "benefit_cap_impact", "weight": 0.6, "source": "JRF" },
    { "factor": "food_bank_demand", "weight": 0.5, "source": "Trussell Trust" }
  ],
  "recommended_intervention": "CHW early-years nutrition programme",
  "estimated_sroi": 4.2
}
```

---

## 5. Layer 3: Verification Pipeline

### 5.1 Model 1: CHW Ground Truth (Field Verification)

Community Health Workers are deployed to neighbourhoods identified by Layer 2 as high-risk. They collect:
- Needs assessments (standardised intake forms)
- Photo evidence of housing conditions
- Location-stamped reports
- Face-to-face interviews

### 5.2 Model 3: SIB Financing

Social Impact Bonds funded by:
- Impact investors (upfront capital)
- Government outcome payments (upon verified results)
- HumanitAI as the measurement and verification layer

Global SIB context: 276 SIBs operating in 23 countries, $745M capital deployed (Social Finance, 2022). UK pioneered the model at Peterborough Prison (2010).

### 5.3 Model 4: SROI Measurement

UK-government-recognised framework (Social Value UK, 8 principles):
- Every £1 tracked from investor → intervention → outcome
- Outcomes monetised using HACT social value bank
- Verified by independent evaluator
- Published in auditable reports

---

## 6. Deployment: 18 UK Regions

| Region | Primary Risk | Severity | OSINT Sources | CHW Status |
|--------|-------------|----------|---------------|------------|
| Birmingham | Child poverty | 92 | ONS, End Child Poverty | Planned |
| Manchester | Homelessness | 88 | MHCLG, Shelter | Planned |
| Liverpool | Mental health | 81 | NHS England | Planned |
| Glasgow | Life expectancy | 90 | ONS Health | Planned |
| London (Newham) | Digital exclusion | 87 | ONS, Ofcom | Planned |
| Bradford | Child poverty | 86 | End Child Poverty | Planned |
| Middlesbrough | Child poverty | 90 | End Child Poverty | Planned |
| Blackpool | Life expectancy | 88 | ONS Health | Planned |
| Hull | Child poverty | 84 | End Child Poverty | Planned |
| Stoke-on-Trent | Deprivation | 80 | ONS IMD | Planned |
| ... | ... | ... | ... | ... |

---

## 7. Weakness Analysis (Self-Audit)

### 7.1 Identified Weaknesses

| # | Weakness | Severity | Impact | Mitigation |
|---|----------|----------|--------|------------|
| W1 | OSINT data is lagging (quarterly/annual) | HIGH | Predictions based on past data | Real-time browser scraping + CHW ground truth for current signal |
| W2 | Agent bias amplification | MEDIUM | Agents may reinforce each others' biases | Differential personality weighting + human-in-the-loop review |
| W3 | SIB funding requires track record | HIGH | No outcomes yet = hard to raise capital | Phased deployment: start with grant-funded pilot in 3 regions |
| W4 | CHW team recruitment and training | MEDIUM | Quality varies by region | Standardised training programme + gamified quality assurance |
| W5 | Neo4j knowledge graph maintenance | LOW | Graph grows unbounded | Regular archival + pruning of low-importance nodes |
| W6 | Browser automation reliability | MEDIUM | Sites change structure | Multi-strategy fallback (API → browser → manual) |
| W7 | Public trust in AI-driven social intervention | HIGH | Communities may resist "predicted" interventions | Transparency: publish all predictions, CHW as trusted intermediaries |
| W8 | SROI monetisation can be subjective | MEDIUM | Different valuations of social outcomes | Use HACT standard values + independent auditor |

### 7.2 Critical Weakness: W1 (Data Lag)

**Problem:** ONS publishes poverty data with a 12-18 month lag. By the time we know where crisis happened, it's too late to prevent it.

**Solution:** Three-layer verification:
1. **OSINT leading indicators**: Browser-scraped job postings, housing listings, food bank appointment availability
2. **Human Architect nowcasting**: Agent simulation using available real-time proxies to estimate current conditions
3. **CHW spot checks**: Monthly micro-surveys in high-risk wards for real-time validation

### 7.3 Critical Weakness: W7 (Public Trust)

**Problem:** Communities may distrust AI-predicted interventions, especially in already-marginalised areas.

**Solution:**
- All predictions published openly on the HumanitAI map
- CHWs are local residents, not external consultants
- Interventions are opt-in, not mandated
- SROI outcomes are independently verified and published

---

## 8. Improvement Roadmap

### Phase 1 (Current): Foundation
- [x] OSINT data pipeline for 18 regions
- [x] Multi-agent simulation (Human Architect Technology)
- [x] Public deployment map
- [x] SROI framework documentation

### Phase 2 (Q3 2026): Pilot
- [ ] 3-region pilot with grant funding
- [ ] CHW recruitment and training
- [ ] First SIB structure
- [ ] Real-time OSINT dashboard

### Phase 3 (Q4 2026): Scale
- [ ] 18-region deployment
- [ ] Multiple SIBs
- [ ] Independent SROI audit
- [ ] Academic publication of methodology

### Phase 4 (2027): Autonomous
- [ ] Fully automated OSINT → prediction → recommendation pipeline
- [ ] Community-owned data cooperatives
- [ ] Open-source release of Human Architect Technology stack
- [ ] Replication toolkit for other UK CICs

---

## 9. Open Source Stack

| Component | Technology | License |
|-----------|-----------|---------|
| Swarm Engine | [MiroFish](https://github.com/666ghj/MiroFish) | AGPL-3.0 |
| Simulation Backend | [OASIS](https://github.com/camel-ai/oasis) | Apache 2.0 |
| Knowledge Graph | Neo4j Community | GPL-3.0 |
| LLM Integration | Ollama + OpenAI API | Various |
| Frontend Map | Leaflet + CartoDB | BSD-2-Clause |
| Public Data | ONS, NHS, gov.uk APIs | Open Government |

---

## Appendix: OSINT Use Cases in Detail

### A.1 NHS Waiting List OSINT

**Data sources:**
- NHS England RTT monthly data (CSV via public URL)
- Trust-level performance reports (HTML scrape)
- Local demographics (ONS API)

**Method:**
1. Download NHS RTT CSV
2. Parse trust-level waiting times (52+ week breaches)
3. Cross-reference with ONS population density and age profile
4. Human Architect Technology scores trusts by breach rate ÷ population need
5. Output: Ranked list of trusts requiring CHW triage intervention

### A.2 Food Bank Demand OSINT

**Data sources:**
- Trussell Trust open data portal
- Universal Credit claimant count (NOMIS)
- local housing allowance rates (gov.uk)

**Method:**
1. Download Trussell Trust regional parcel data
2. Correlate with Universal Credit claimant trends
3. Cross-reference with local housing costs
4. Predict demand spikes 2-3 months in advance

---

## References

1. MiroFish — Universal Swarm Intelligence Engine. https://github.com/666ghj/MiroFish
2. OASIS — Open Agent Social Interaction Simulations. https://github.com/camel-ai/oasis
3. Social Finance UK — Social Impact Bond Database. https://socialfinance.org.uk/sib-database
4. Social Value UK — SROI Framework. https://socialvalueuk.org/
5. HM Treasury PESA 2024 — Public Expenditure Statistical Analysis
6. JRF UK Poverty 2024 — https://www.jrf.org.uk/uk-poverty-2024
7. End Child Poverty Coalition — Child poverty maps. https://endchildpoverty.org.uk/
8. Office for National Statistics API — https://api.beta.ons.gov.uk/
