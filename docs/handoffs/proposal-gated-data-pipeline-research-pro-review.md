# Proposal-Gated Data Pipeline And Reader Surface: Research Pro Review Brief

## Copy-Paste Prompt

Review this single self-contained architecture packet. Assume you have no
repository access and no local runtime. Do not ask for files. Every repo fact,
chat-derived decision, current state detail, and proposed design constraint
needed for review is included below.

Lead with findings. Challenge the thesis, architecture, gate placement, data
model shape, and reader feed contract. The goal is to prevent semi-stock reader
pollution from ungated company data while keeping the pipeline easy to populate
from a clean reset state.

Do not focus on long-term staleness or archive policy except where today's gate
design would make next month's staleness work impossible. Staleness is a parked
follow-up, not the main review.

## Reviewer Context

You are reviewing the current and proposed architecture for a personal
semi-stocks research application called Signal Desk.

The system is a canonical research pipeline plus a generated reader:

```text
raw source material
  -> canonical wiki / source synthesis
  -> structured data
  -> thesis / proposal gate
  -> engine build
  -> generated app feed
  -> web reader
```

The human user, Ash, is rebuilding from a clean state and wants very selective
data entry. The core concern: as data gets repopulated, companies must not enter
the app merely because they appeared in a source, 13F filing, signal, or scratch
research note. The reader should consume only after a formal gate.

## Review Target And Mode

- Mode: architecture/design critique plus format critique
- Remote target: packet only
- Base/comparison: current documented pipeline and generated reader behavior,
  summarized in this packet
- Requested scrutiny: whether the proposed gate prevents app pollution without
  creating too much process drag

## Access Protocol

1. Use this packet as the only source of truth.
2. Treat repo-relative paths named here as labels only; the relevant evidence is
   directly included in the packet.
3. Do not request repository files, screenshots, runtime output, or web access.
4. If a finding depends on missing information, label it as an assumption or
   blind spot and explain what evidence would settle it.

## Source And Access Policy

- Primary evidence: this packet only
- Web/external sources: not needed
- Non-repo context: chat-derived user intent is included below
- Sensitive context check: no secrets, API keys, or private credentials included

## Goal

1. Define a data pipeline gate that keeps the reader/app clean.
2. Preserve the existing canonical pipeline shape and generated reader contract.
3. Decide whether the system needs two physical data layers or one physical
   layer with explicit gate status.
4. Define the minimum proposal/data format that lets data live past proposal
   without immediately solving staleness.

## Compressed Thesis

The app should have two logical data layers and one reader feed.

```text
Candidate evidence layer
  Broad, messy, useful for research, not app-visible.

Human proposal gate
  Converts selected evidence into a formal proposal or approved thesis/data
  object.

Approved proposal/data layer
  Durable, structured, lineaged, reader-eligible.

Generated app feed
  Built only from approved proposal/data records.
```

The key invariant:

```text
Company existence in source data is not enough for app inclusion.
Reader inclusion requires a proposal/data gate decision.
```

The practical implementation can be either:

1. Two physical layers: separate candidate and approved directories/files.
2. One physical data lane: records carry explicit status and reader eligibility.

The architecture must behave like two layers even if stored as one. Tests and
the engine must prove the reader feed cannot emit pre-gate companies.

## Chat-Derived User Intent

Recent user decisions and corrections:

```text
Data needs to live past proposal.
Unclear whether there should be two data layers or one.
Need a data layer with companies after the gate.
Without a gate, app will be polluted by companies not wanted until formalized.
Only proposals / gated proposal-derived data should make it into the app.
Reader should consume only after a certain gate.
Do not add freshness fields now.
Staleness / obsolete data is next month's problem.
Right now focus is data pipeline quality.
```

Prior conceptual alignment:

```text
The pipeline is mainly a DAG.
Data lineage is core and needed.
Provenance is core and claim-focused.
Knowledge graph ideas are useful for companies/concepts/themes/sources, but
the system does not need a graph database yet.
```

## Current Architecture Summary

Current documented canonical flow:

```text
canonical/10-wiki/raw
  -> canonical/10-wiki/sources|concepts|outputs
  -> canonical/20-data/sources|companies
  -> canonical/30-thesis/thesis.yaml
  -> canonical/40-engine
  -> canonical/50-reports
```

Generated reader flow:

```text
canonical truth
  -> canonical/40-engine
  -> canonical/site-data
  -> canonical/site-reader
```

Current lane ownership:

```text
canonical/10-wiki:
  Owns authored wiki knowledge and generated wiki metadata.

canonical/20-data:
  Owns structured evidence only.
  Current documented subareas:
    sources
    companies
    thesis-proposals

canonical/30-thesis/thesis.yaml:
  Owns the narrow thesis control plane.

canonical/40-engine:
  Owns synthesis and render code.

canonical/50-reports:
  Owns canonical published reports.

canonical/site-data:
  Generated app data for repo-owned web readers.
  Not a canonical stage.

canonical/site-reader:
  Repo-owned web reader source.
  Consumes generated site data.
  Not a canonical stage.

agents:
  Sidecar-only unless explicitly promoted.
```

Current documented human loop:

```text
raw source
  -> wiki ingest/query
  -> human approval
  -> canonical data/thesis
  -> signal_desk.json
  -> web reader
  -> next research question
```

Current reader principle:

```text
Signal Desk supports decisions.
It does not make decisions.
```

## Current Clean Reset State

The repo is on a data reset branch. There is no tracked code diff at the moment
this packet was created.

Branch:

```text
codex/data-reset-six-company-spine
```

Latest local commit:

```text
49e2db3260836467f77a025556b736d4b1a28fa4
```

Untracked, out-of-scope local files:

```text
agents/logs/daily-runner-2026-04.log
agents/logs/earnings-calendar-2026-04.log
agents/logs/launchd-daily.stderr.log
agents/logs/launchd-daily.stdout.log
agents/logs/pre-earnings-predictor-2026-04.log
agents/logs/transcript-fetcher-2026-04.log
agents/reports/latest.html
canonical/.obsidian/
```

Current structured data reset:

```yaml
# company role scaffold
roles:
  unknown:
    id: company-role:unknown
    label: Unknown
    rank: null
    aliases: []
    description: Placeholder role for zero-data baseline.
    search_text: unknown

companies:
  RESET:
    primary_role_id: company-role:unknown
    secondary_role_ids: []
    display_tags: []
```

Current thesis reset:

```yaml
updated: "2026-04-21"
baker_hedge_ratio: {}
cascade: []
ticker_map: {}
```

Current Baker source reset:

```yaml
source: baker
entity: "Atreides Management LP"
quarter: "Q4 1900"
period: "1900-12-31"
filed: "1901-01-01"
positions: []
exits: []
```

Current Leopold source reset:

```yaml
source: leopold
entity: "Situational Awareness LP"
quarter: "Q4 1900"
period: "1900-12-31"
filed: "1901-01-01"
positions: []
exits: []
```

Current SemiAnalysis source reset:

```yaml
source: semianalysis
entity: "SemiAnalysis (Dylan Patel)"
updated: "2026-04-21"
signals: []
media: []
```

There is currently no physical `thesis-proposals` directory present, though the
architecture document describes it as a structured evidence staging area for
pending thesis patches before promotion.

Current generated app data summary:

```json
{
  "version": "signal-desk-v0.2",
  "companies": 0,
  "rows": 0,
  "source_documents": 4,
  "graph_nodes": 0,
  "graph_edges": 0,
  "row_types": ["position", "signal", "claim", "proposal"]
}
```

Current source channel counts:

```json
[
  {"id": "source-channel:baker", "label": "Baker", "counts": {"companies": 0, "rows": 0, "source_documents": 1}},
  {"id": "source-channel:company-earnings", "label": "Company earnings", "counts": {"companies": 0, "rows": 0, "source_documents": 0}},
  {"id": "source-channel:leopold", "label": "Leopold", "counts": {"companies": 0, "rows": 0, "source_documents": 1}},
  {"id": "source-channel:pending-proposals", "label": "Pending proposals", "counts": {"companies": 0, "rows": 0, "source_documents": 0}},
  {"id": "source-channel:semianalysis", "label": "SemiAnalysis", "counts": {"companies": 0, "rows": 0, "source_documents": 1}},
  {"id": "source-channel:thesis-stage", "label": "Thesis stage", "counts": {"companies": 0, "rows": 0, "source_documents": 1}}
]
```

Generated build counts:

```json
{
  "artifact_counts": {
    "claims": 0,
    "companies": 0,
    "edges": 1,
    "entities": 5,
    "pages": 3,
    "reports": 1,
    "signals": 0,
    "thesis_stages": 0
  },
  "source_counts": {
    "data_yaml": 4,
    "reports": 1,
    "wiki_markdown": 3
  }
}
```

Note: `artifact_counts.edges=1` belongs to the broader site-data artifact set,
while Signal Desk graph edges are `0`.

## Current Engine Behavior Summary

The site-data generator:

```text
Builds generated JSON artifacts under canonical/site-data.
Can validate generated artifacts.
Collects thesis, wiki pages, company packets, and thesis proposals.
Builds companies, claims, signals, reports, entities, edges, thesis payload,
search, graph, and signal_desk payload.
Deletes and rewrites canonical/site-data during build.
```

Current generated artifact names:

```text
build.json
schema.json
pages.json
companies.json
signals.json
entities.json
edges.json
claims.json
thesis.json
reports.json
search.json
graph.json
signal_desk.json
```

Current validation enforces:

```text
Required artifact keys exist.
Edges reference known IDs.
Companies have ticker and name.
Signals have kind and evidence.
Graph link endpoints exist.
Signal Desk contract is valid.
Trace feature is hidden.
Graph mode is contextual_evidence.
Graph support families are only co_position and shared_signal.
Claim and proposal rows cannot create graph edges in MVP.
Rows need source documents, source paths, company IDs, period, and timeline.
```

Current company construction:

```text
Companies are built from:
  thesis ticker_map
  company earnings packets
  Leopold source tickers
  Baker source tickers
  SemiAnalysis source tickers

This means source data can currently create company candidates before any
explicit proposal approval, unless some later filter blocks them.
```

Current reader company payload construction:

```text
Signal Desk companies are emitted only if:
  the company has role mapping
  and the company has rows or source documents

This role map acts as a weak accidental gate, but it is not the desired human
proposal gate. Role assignment answers "what role is this company?" It does not
answer "has this company been approved for reader visibility?"
```

Current proposal behavior:

```text
The engine can load proposal YAML files from a thesis-proposals area if it
exists.

Proposal rows:
  row_type = proposal
  source_channel_id = pending-proposals
  graph_eligibility = false
  lifecycle_state = proposal status or pending
  affected company and thesis theme IDs are included

Claims and proposals are table/profile context only, not graph edge support.
```

Current source channels include:

```text
Baker
Leopold
SemiAnalysis
Company earnings
Thesis stage
Pending proposals
```

## Current Reader Behavior Summary

The web reader fetches one generated payload:

```text
/site-data/signal_desk.json
```

The reader builds lookups for:

```text
companies
rows
source_documents
source_channels
company_roles
thesis_themes
```

The reader filters by:

```text
search
source_channel_ids
company_role_ids
thesis_theme_ids
timeline
include_undated
```

The reader shows:

```text
header/build info
filters
active filter chips
stats
contextual evidence graph
evidence table
profile panel
```

Current graph semantics:

```text
Graph edges mean shared evidence under current filters.
Graph edges do not mean supplier/customer, money flow, chip flow, ownership,
causality, or trace path.

Current support families:
  co_position
  shared_signal

Trace is parked until a separate typed relationship_edges dataset exists.
```

## Problem Statement

As the clean state gets repopulated, any of these could currently become
reader-visible if the generator sees them and they pass the existing structural
rules:

```text
13F source tickers
SemiAnalysis tickers
company earnings packet tickers
thesis ticker_map companies
claim companies
signal companies
proposal companies
```

That is too permissive for the desired workflow.

The desired workflow is selective:

```text
Evidence can be broad.
Candidate data can be broad.
Reader-visible companies must be narrow.
Reader-visible companies require a formal gate.
```

The reader should not become a dumping ground for "companies mentioned
somewhere." It should represent the current gated proposal/thesis universe.

## Proposed Architecture

Minimum logical architecture:

```text
1. Candidate Evidence
   Broad, source-backed, pre-gate.
   Can include many companies.
   Not reader-visible.

2. Proposal Gate
   Human-selected proposal object.
   Pulls in only selected companies and evidence.
   Can be pending, accepted, rejected, or applied.

3. Approved Proposal/Data
   Durable post-gate data.
   Carries company scope, evidence lineage, thesis relevance, and app
   eligibility.

4. Generated App Feed
   Built only from approved proposal/data.
   No free-floating source companies.
```

Pipeline shape:

```text
raw source
  -> wiki/source synthesis
  -> candidate structured evidence
  -> human proposal gate
  -> approved proposal/data
  -> engine
  -> signal_desk.json
  -> reader
```

Reader feed invariant:

```text
Every company in signal_desk.companies must be reachable from an approved
proposal/data object.
```

Row feed invariant:

```text
Every reader row must either be:
  a gated proposal/data row
  or evidence attached to a gated proposal/data object.

No standalone candidate source row should appear merely because it exists in
structured source data.
```

Source document invariant:

```text
Source documents can exist as lineage/provenance.
The reader should expose only source documents that support an approved
proposal/data object, unless there is an intentionally separate internal review
surface.
```

Graph invariant:

```text
Graph nodes and edges can only use reader-visible companies and gated evidence.
The graph remains contextual evidence, not causal or supply-chain Trace.
```

## One Physical Layer Vs Two Physical Layers

The open design question:

```text
Should candidate data and approved proposal/data live in separate physical
locations, or in one data lane with explicit status fields?
```

Option A: two physical layers.

```text
candidate layer:
  candidate evidence, broad source extraction, scratch structured facts

approved layer:
  proposal-approved company/data records that feed the reader
```

Pros:

```text
Harder to accidentally emit candidate companies.
Cleaner mental model.
Easier audit of app-eligible universe.
File location itself communicates gate state.
```

Cons:

```text
More directories and migration rules.
Data may move or be duplicated after approval.
Need clear lineage links from approved record back to candidate evidence.
```

Option B: one physical layer, explicit status.

```text
records:
  status: candidate | proposed | accepted | rejected | applied
  reader_eligible: true | false
```

Pros:

```text
Less file churn.
Single structured evidence area.
Lineage can stay in one record.
Easier to populate quickly from clean state.
```

Cons:

```text
Pollution risk if generator forgets to filter.
Harder for humans to see app-eligible universe by path alone.
Status semantics must be extremely strict.
Requires strong tests.
```

Recommended middle ground for review:

```text
Use two logical layers no matter what.
Start with one physical lane only if:
  status names are explicit
  reader_eligible defaults false
  generator filters centrally
  tests assert no pre-gate company reaches signal_desk.json
  app-visible company count can be explained from approved proposal IDs
```

## Proposed Minimal Format

This is a candidate shape for review. It is intentionally minimal and avoids
staleness fields for now.

```yaml
id: proposal:nvidia-memory-pressure-2026-q2
status: proposed
reader_eligible: false
proposal:
  title: "NVIDIA memory pressure should enter the gated thesis universe"
  decision_question: "Should NVDA be included in the current Signal Desk universe?"
  thesis_relevance: "Connects AI accelerator demand to HBM and advanced packaging constraints."
companies:
  - ticker: NVDA
    name: NVIDIA
    role: chip_designer
    inclusion_reason: "Primary company under review for this proposal."
evidence:
  - id: evidence:semianalysis:2026-04-21:01
    source_channel: semianalysis
    source_title: "Example source title"
    claim: "Example extracted claim."
    supports: "proposal:nvidia-memory-pressure-2026-q2"
    confidence: medium
lineage:
  raw_source_ids:
    - raw:example-source-id
  wiki_pages:
    - wiki:example-source-page
  candidate_records:
    - candidate:example-extraction-id
decision:
  decided_by: human
  decided_at: null
  notes: ""
```

After acceptance, either the same record changes:

```yaml
status: accepted
reader_eligible: true
```

Or a promoted approved record is created:

```yaml
id: approved-company:NVDA
from_proposal: proposal:nvidia-memory-pressure-2026-q2
reader_eligible: true
companies:
  - ticker: NVDA
evidence_ids:
  - evidence:semianalysis:2026-04-21:01
```

Review question: which format is better for this app's current stage?

## Required Engine Contract

The engine should enforce:

```text
1. Candidate records never emit directly to signal_desk.json.
2. Every emitted company has an approved proposal/data ancestor.
3. Every emitted row has an approved proposal/data ancestor or supports one.
4. Every emitted source document is attached to at least one emitted row or
   approved proposal/data object.
5. Graph nodes are exactly reader-visible companies.
6. Graph edges are built only from gated rows.
7. Role mapping is not a substitute for human approval.
8. Empty clean state remains valid.
```

Suggested validation failures:

```text
Company emitted with no approved proposal ancestor.
Row emitted from candidate source only.
Source document emitted with no gated row/proposal relationship.
Graph edge uses a pre-gate company.
reader_eligible true on a record with no human decision.
Accepted proposal has no source lineage.
```

## Required Reader Contract

The reader should assume:

```text
signal_desk.json is already gated.
Reader code should not decide approval.
Reader filters should not be responsible for hiding candidates.
Reader UI may show proposal status, but only for records allowed into the feed.
```

The reader should not:

```text
Fetch candidate data directly.
Show all source-mentioned companies.
Infer inclusion from role mapping.
Treat graph edges as causal relationships.
```

## Data Lineage Requirement

Lineage is not optional. The reviewer should treat this as a core design
requirement.

Minimum lineage chain:

```text
raw/source material
  -> extracted candidate evidence
  -> proposal evidence item
  -> accepted proposal/data object
  -> generated reader row/company
```

Every app-visible assertion should be answerable:

```text
Why is this company in the reader?
Which proposal admitted it?
Which evidence supported that proposal?
Which source produced that evidence?
```

The app does not need a graph database. It needs lineage IDs, strict references,
and validation.

## Data Quality Focus For This Review

Challenge whether the proposed architecture gives enough quality controls:

```text
Clear gate before reader visibility.
Explicit company inclusion reason.
Proposal status lifecycle.
Lineage from app row back to source.
Default-hidden candidate records.
Validation that blocks accidental app emission.
Tests that cover clean reset and populated gated data.
No staleness complexity yet.
```

Do not spend primary effort on:

```text
TTL policy.
Archive UX.
Freshness fields.
Superseded proposal chain.
Monthly review workflow.
```

Those are acknowledged future work.

## Assumptions To Falsify

1. Two logical data layers are necessary.
   Current evidence: user explicitly fears app pollution from ungated companies.
   Falsifier: a single-layer status model can be made simpler and equally safe
   with strong central filtering and tests.

2. Role mapping is not a sufficient gate.
   Current evidence: role mapping describes company role, not human approval.
   Falsifier: the project intentionally redefines role mapping as the approval
   manifest, with naming and tests changed accordingly.

3. Reader should receive only gated data.
   Current evidence: user says reader should consume only after a certain gate.
   Falsifier: there is a separate internal review mode where pending proposals
   are intentionally visible, clearly separated from the main reader feed.

4. Proposal/data objects need to survive beyond proposal decision.
   Current evidence: user says data needs to live past proposal.
   Falsifier: accepted proposals can be fully compiled into another durable
   approved data object without preserving the original proposal as an app data
   ancestor.

5. Staleness can be deferred.
   Current evidence: user says staleness is next month and not current focus.
   Falsifier: today's gate schema would be impossible to extend with stale,
   superseded, or archived states later.

## Blind Spots

The reviewer cannot independently inspect:

```text
Full repository.
Full generated JSON files.
Current screenshots.
Runtime behavior.
Untracked local logs and reports.
Previous branch history.
```

The included summaries are enough for architecture review but not enough for
line-by-line implementation review.

## Known Out Of Scope

Out of scope for this review:

```text
Long-term staleness handling.
External market/source research.
UI redesign.
Graph Trace implementation.
Full schema migration.
Running tests.
PR merge readiness.
Untracked local logs/reports.
```

## Review Tasks

Please review for:

1. Gate placement: Is the human gate at the right point between candidate
   evidence and reader feed?
2. Layer shape: Should this be two physical data layers, or one physical layer
   with explicit status and `reader_eligible`?
3. Format: Is the proposed minimal proposal/data format enough to support
   app-visible companies, evidence, lineage, and future staleness?
4. Engine contract: Are the required validation rules sufficient to prevent
   pre-gate companies from entering `signal_desk.json`?
5. Reader contract: Should pending proposals appear in the main reader at all,
   or should the main reader only show accepted/applied proposal data?
6. Current architecture fit: Does this proposal preserve the canonical
   pipeline, or does it accidentally create a second source of truth?
7. Data quality: What minimal tests should exist before repopulating the clean
   state with real companies?

## Desired Reviewer Output

Lead with findings. For each finding include:

```text
severity: blocker | high | medium | low
area: gate | data model | engine | reader | validation | docs | future risk
issue:
why it matters:
suggested fix:
```

Then provide:

```text
Recommended architecture: two physical layers or one physical statused layer.
Recommended minimum schema.
Recommended reader inclusion rule.
Recommended validation/test list.
Any parked staleness concern that must be accounted for now.
```

If there are no blocker/high concerns, say that explicitly and focus on
medium/low improvements.

## Findings Intake Plan

Returned findings should be triaged as:

```text
fix now:
  Gate semantics, schema shape, engine validation, app feed inclusion tests.

backlog:
  Staleness, archive, superseded proposal UI, richer provenance browser.

local verification:
  Any finding requiring repo commands, generated JSON inspection, or browser
  behavior.

reject with reason:
  Findings that require graph database adoption, full Trace semantics, or
  staleness work before the current gate is established.
```
