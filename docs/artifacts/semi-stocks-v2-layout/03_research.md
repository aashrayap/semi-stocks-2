---
status: completed
feature: semi-stocks-v2-layout
---

# Research: semi-stocks-v2-layout

## Flagged Items

- The current repo uses `wiki/` and `data/` as separate but tightly linked canonical layers. Confidence is high that both are authoritative, but the best v2 top-level naming is still a design choice rather than a discovered fact.
- `README.md` currently carries both onboarding/routing material and long-form thesis content. Confidence is high that this is too much for root, but the exact destination for the thesis prose is a design decision.

## Findings

### Codebase

#### Q: Which files currently act as the control plane and runtime entry points for the canonical lane, and what top-level folders do they assume?

**Answer**
`data/thesis.yaml` is the control plane for cascade status, ticker mapping, and earnings dates. `src/synthesis.py` and `src/report.py` are the canonical runtime path, and they assume sibling top-level folders `data/`, `wiki/`, and `reports/`.

**Evidence**
- `AGENTS.md` says to treat `data/thesis.yaml` as the control plane and preserve the funnel through `src/synthesis.py` and `src/report.py`.
- `data/thesis.yaml` contains the cascade, ticker map, and update date.
- `src/synthesis.py` loads `DATA_DIR / "thesis.yaml"` and defines `WIKI_DIR` relative to repo root.
- `src/report.py` writes canonical output to `reports/`.

**Confidence**
High

#### Q: Which files currently define or imply the separation between canonical research and agent-side work?

**Answer**
The strongest statement of lane separation is in `README.md` and `AGENTS.md`: canonical truth flows through `wiki/`, `data/`, and `src/`, while `agents/` is explicitly non-authoritative and writes only under its own subtree.

**Evidence**
- `README.md` has explicit “Canonical Truth Lane,” “Agent Sidecar Lane,” and “Human Promotion Gate” sections.
- `AGENTS.md` says to treat `wiki/` and `data/` as canonical research and use `agents/` for experiments, backtests, draft analyses, and sidecar automation output.

**Confidence**
High

#### Q: What top-level outputs are produced by the canonical reporting path versus the sidecar reporting path?

**Answer**
Canonical reporting writes to `reports/`; sidecar reporting writes under `agents/reports/`; the wiki also contains analysis outputs under `wiki/outputs/`.

**Evidence**
- `src/report.py` defines `REPORTS_DIR` as repo-root `reports/`.
- `AGENTS.md` calls out `agents/reports/` as non-canonical output.
- `README.md` includes `wiki/outputs/` in the report lens.

**Confidence**
High

### Docs

#### Q: Which existing root markdown files in `semi-stocks` carry durable routing value versus content that should move under `docs/`?

**Answer**
`AGENTS.md` and `CLAUDE.md` carry durable routing value. `README.md` has durable onboarding value but currently contains too much long-form thesis and architecture prose for root. `TODO.md` is operational state, not durable architecture, and should not be a root contract doc in v2.

**Evidence**
- `AGENTS.md` and `CLAUDE.md` primarily route users to authority files and workflows.
- `README.md` includes thesis exposition, source summaries, divergence tables, the research pipeline, and architecture lanes.
- `TODO.md` is backlog and session state.

**Confidence**
High

#### Q: What responsibilities are currently split across `README.md`, `AGENTS.md`, `CLAUDE.md`, and `TODO.md`, and where do they overlap?

**Answer**
Root docs currently overlap on thesis summary, key file map, and workflow routing. `README.md` also carries architecture and research explanations; `AGENTS.md` and `CLAUDE.md` both act as agent routers; `TODO.md` adds session-state noise at root.

**Evidence**
- `README.md`, `AGENTS.md`, and `CLAUDE.md` all point to `data/thesis.yaml`, `src/report.py`, and the canonical funnel.
- `README.md` and `AGENTS.md` both describe architecture lanes.
- `CLAUDE.md` and `AGENTS.md` both act as progressive-disclosure routers.

**Confidence**
High

#### Q: Which architecture or process docs are currently the highest-leverage references for preserving repo intent during a v2 cleanup?

**Answer**
The highest-leverage documents are `README.md` for the explicit two-lane model, `wiki/schema.md` for wiki ownership and generated-state conventions, and `data/research/earnings-pipeline.md` for the source-to-thesis process.

**Evidence**
- `README.md` contains the clearest overall lane model.
- `wiki/schema.md` defines the internal wiki structure, ownership, and generated files.
- `data/research/earnings-pipeline.md` defines the wide-to-narrow ingest path into thesis and report.

**Confidence**
High

### Patterns

#### Q: What repository pattern is already emerging in `semi-stocks` for authority boundaries between source-of-truth artifacts, generated artifacts, and experiments?

**Answer**
A four-way pattern is already present: canonical source material and research (`wiki/`, `data/`), application logic (`src/`), generated outputs (`reports/`, `wiki/outputs/`), and non-canonical experimentation/automation (`agents/`).

**Evidence**
- `README.md` describes raw, research, thesis, and report lenses.
- `AGENTS.md` distinguishes canonical versus sidecar work.
- `wiki/schema.md` distinguishes raw, wiki-owned, schema, and generated state.

**Confidence**
High

#### Q: Which documented conventions appear stable enough to keep in v2, even if paths change?

**Answer**
These conventions look stable: `data/thesis.yaml` as control plane, a wide-to-narrow ingest funnel, explicit separation of canonical and sidecar lanes, generated outputs living outside canonical source folders, and thin agent-router docs that point to deeper process docs.

**Evidence**
- Repeated consistently across `README.md`, `AGENTS.md`, `CLAUDE.md`, `data/thesis.yaml`, and `data/research/earnings-pipeline.md`.

**Confidence**
High

### External

#### Q: None expected unless local evidence is insufficient.

**Answer**
No external research was needed.

**Evidence**
- Local repo files answered the structural questions.

**Confidence**
High

### Cross-Ref

#### Q: Given the current control-plane files, report paths, and root docs, what top-level folder map would preserve the operating model while making lane boundaries more obvious?

**Answer**
The current operating model supports a top-level structure with separate homes for canonical knowledge, application/runtime code, sidecar automation, generated outputs, docs, and local scratch. The current names could be preserved or normalized, but the key is to make each lane visually distinct at root.

**Evidence**
- Control plane and pipeline span `data/`, `wiki/`, `src/`, and `reports/`.
- Sidecar automation is already isolated under `agents/`.
- Process docs live under `data/research/` and schema docs under `wiki/`, which indicates a missing shared docs home.

**Confidence**
Medium

#### Q: Given the current root markdown overlap, what is the minimum viable root-doc set for v2, and which docs should move under `docs/`?

**Answer**
The minimum viable root-doc set is `README.md`, `AGENTS.md`, and `CLAUDE.md`. Long-form thesis, architecture rationale, process docs, and migration notes should live under `docs/`.

**Evidence**
- `AGENTS.md` and `CLAUDE.md` already behave like routers.
- `README.md` currently contains both root-friendly overview content and deep material better suited to `docs/`.
- `TODO.md` is ephemeral state and not part of a durable root-doc contract.

**Confidence**
High

#### Q: Which docs should be created first in `semi-stocks-2` so the repo can be scaffolded cleanly before broader migration begins?

**Answer**
Create a short root `README.md`, root `AGENTS.md`, root `CLAUDE.md`, plus `docs/architecture.md` and `docs/doc-contract.md`. A stub `docs/migration.md` is also useful as a parking lot for later file moves, but it is not required for the initial structure.

**Evidence**
- The root needs fast routing.
- The folder map and doc contract need a durable home outside root.
- Migration details are explicitly out of scope for this pass but still need a future home.

**Confidence**
Medium

## Patterns Found

- Canonical lane: `wiki/raw/` -> `wiki/sources/` -> `data/companies|sources/` -> `data/thesis.yaml` -> `src/synthesis.py` -> `src/report.py` -> `reports/`
- Sidecar lane: read canonical artifacts, write only under `agents/`
- Generated-state pattern: wiki keeps machine-generated indexes separate from authored pages
- Router-doc pattern: root agent files point to deeper process docs rather than duplicating them completely

## Core Docs Summary

- `README.md`: strongest statement of the current operating model, but overloaded at root
- `AGENTS.md`: best expression of repo rules and authority boundaries
- `CLAUDE.md`: thinner router version of the same system
- `data/thesis.yaml`: actual control plane
- `src/synthesis.py` and `src/report.py`: canonical runtime path
- `wiki/schema.md`: internal sub-system contract for the wiki
- `data/research/earnings-pipeline.md`: clearest process doc for the wide-to-narrow research funnel

## Open Questions

- Whether v2 should keep `wiki/` and `data/` as peer top-level canonical folders or wrap them under a broader parent such as `research/`
- Whether `reports/` should remain a named top-level output folder or move to a more general `output/` folder in v2
