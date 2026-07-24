# HumanitAI Pressure Taxonomy (controlled vocabulary)

Used by the `community-signal-classifier` skill to map incoming reports to a
common ontology (blueprint §7.4, §6.2). Place-level only. Each issue_code maps
to the five pressures tracked on the public dashboard.

issue_code        pressure          label                 source_basis
---------------------------------------------------------------------------
poverty           poverty           Poverty / low income  JRF, ONS, Trussell
child_poverty     poverty           Child poverty         End Child Poverty
homelessness      homelessness      Homelessness          MHCLG statutory
rough_sleeping    homelessness      Rough sleeping        MHCLG / Police.uk
nhs_wait          nhs               NHS waiting lists     NHS England RTT
mental_health     mental            Mental health         Fingertips / survey
isolation         isolation         Isolation / loneliness  Survey / VCSE feed
housing_arrears   homelessness      Housing arrears       LA housing feeds
debt              poverty           Problem debt          VCSE / advice feeds
unemployment      poverty           Unemployment / claimant  Nomis
service_gap       (cross)           Service capacity gap  Partner feeds
wellbeing         mental            Wellbeing decline     WHO-5 / survey

# Privacy classes (blueprint §5.1 / C1)
public_aggregate     - official open data, no personal data
partner_aggregate     - consented partner operational aggregates
personal_consented    - individual consented participant data (exceptional, separate governance)

# Confidence levels
low | medium | high

# Review statuses
automated_pass | human_review | quarantined
