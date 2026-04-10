---
status: completed
feature: canonical-propagation-model
---

# Research: canonical-propagation-model

## Flagged Items

- **Wiki path compatibility is real, not cosmetic.**
  - Answer: The installed wiki skill auto-discovers a wiki only at top-level `./wiki/`, `../wiki/`, or global document locations, and its scaffold assumes `raw/`, `concepts/`, `sources/`, and `outputs/`.
  - Evidence: `~/.codex/skills/wiki/SKILL.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: Decide whether to preserve a visible top-level `wiki/` path or intentionally update the wiki skill and its discovery contract.

- **`data/` is the current overlap bucket.**
  - Answer: In the legacy repo, `data/` holds structured source state, company models, process documentation, update logs, and the thesis control plane. Those are not one concern.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`, `/Users/ash/Documents/2026/semi-stocks/CLAUDE.md`, `/Users/ash/Documents/2026/semi-stocks/data/research/earnings-pipeline.md`, directory listing under `/Users/ash/Documents/2026/semi-stocks/data/`
  - Confidence: high
  - Conflicts: none found
  - Open items: Decide whether to keep `data/` but narrow it, or rename it to a more stage-accurate term.

- **`thesis.yaml` already behaves like a distinct control plane.**
  - Answer: The thesis file is the narrowest canonical state and is read directly by both canonical synthesis/report code and sidecar agent code.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`, `/Users/ash/Documents/2026/semi-stocks/src/synthesis.py`, `/Users/ash/Documents/2026/semi-stocks/agents/README.md`, `/Users/ash/Documents/2026/semi-stocks/agents/src/pre_earnings_predictor.py`
  - Confidence: high
  - Conflicts: none found
  - Open items: Decide whether thesis remains a file under a broader structured-state lane or becomes its own canonical stage.

## Findings

### Docs

- **Q: Which current docs describe durable authority boundaries versus historical naming?**
  - Answer: The durable semantics are the funnel `raw -> synthesized -> structured -> thesis -> report`, the sidecar `agents/` write boundary, and `thesis.yaml` as control plane. The weaker, more historical names are the broad wrappers `wiki/` and especially `data/` as top-level buckets.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`, `/Users/ash/Documents/2026/semi-stocks/CLAUDE.md`
  - Confidence: high
  - Conflicts: `wiki/` is both a durable workflow term and a broad wrapper; see next finding.
  - Open items: Keep `wiki` visible while deciding whether it stays a top-level lane or a compatibility surface.

- **Q: What does current wiki documentation say about raw evidence, source pages, concept pages, and outputs?**
  - Answer: The wiki is explicitly modeled as an LLM knowledge base with three layers: immutable `raw/`, LLM-owned `sources/` + `concepts/` + `outputs/`, and co-evolved `schema.md`. Queries are expected to stay in wiki first and only traverse into structured state when needed.
  - Evidence: `~/.codex/skills/wiki/SKILL.md`, `/Users/ash/Documents/2026/semi-stocks/wiki/schema.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: None on internal wiki semantics; the open issue is only where the wiki lives in the new repo.

- **Q: What does current agent documentation say about authority?**
  - Answer: The legacy repo already uses a strong read-all, write-local sidecar model. Agents can read canonical state broadly but should write only under `agents/`, with human promotion as the only bridge back.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`, `/Users/ash/Documents/2026/semi-stocks/agents/README.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: None at the lane level.

### Codebase

- **Q: What currently defines the narrowest canonical state and downstream report path?**
  - Answer: `data/thesis.yaml` is the narrowest canonical state. `src/synthesis.py` loads it directly and derives agreement, divergence, cycle, and earnings views from it; `src/report.py` renders the canonical report from synthesis outputs.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/src/synthesis.py`, `/Users/ash/Documents/2026/semi-stocks/src/report.py`
  - Confidence: high
  - Conflicts: none found
  - Open items: None on current behavior.

- **Q: Which path names are deeply assumed by code?**
  - Answer: Code assumes `data/thesis.yaml`, `data/companies/`, `data/sources/`, `wiki/concepts/`, `wiki/sources/`, and `reports/`. Sidecar code also assumes direct repo-root access to those paths.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/src/synthesis.py`, `/Users/ash/Documents/2026/semi-stocks/agents/src/earnings_calendar.py`, `/Users/ash/Documents/2026/semi-stocks/agents/src/pre_earnings_predictor.py`, repo-wide path references in `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: Any rename of `wiki/`, `data/`, or `reports/` will require either code changes or compatibility shims.

- **Q: What evidence shows company models are distinct from wider evidence state?**
  - Answer: Company YAMLs are the first deep structured narrowing step after wiki synthesis. They store financials, forward claims, thesis signals, and positioning cross-references for a small deep-dive set, not the full evidence corpus.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/data/research/earnings-pipeline.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: Decide whether company models should remain under a broader structured lane with source YAMLs or become their own stage.

- **Q: What evidence shows thesis state is operationally distinct?**
  - Answer: The repo repeatedly treats `data/thesis.yaml` as the control plane. It is narrower than company or source YAMLs and drives both canonical synthesis and agent scheduling/prediction logic.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`, `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/src/synthesis.py`, `/Users/ash/Documents/2026/semi-stocks/agents/README.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: Root placement remains open.

### Patterns

- **Q: Does the legacy repo already behave as a wide-to-narrow propagation system?**
  - Answer: Yes. The docs and process files explicitly describe the system as a layered funnel: `wiki/raw/ -> wiki/sources/ -> data/companies/ or data/sources/ -> data/thesis.yaml -> src/synthesis.py -> report`.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/data/research/earnings-pipeline.md`, `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: The new layout should make this explicit in folder names instead of requiring docs to explain it.

- **Q: Where do overlap problems currently appear?**
  - Answer: Overlap sits mostly inside `data/`, which mixes structured source snapshots, company models, process docs, update logs, and thesis control-plane state. A second overlap is between `reports/` and `wiki/outputs/`, which are both outputs but serve different workflows.
  - Evidence: directory listing of `/Users/ash/Documents/2026/semi-stocks/`, `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/wiki/schema.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: Preserve the distinction between knowledge-query outputs and canonical published reports.

- **Q: Is the cleaner split better modeled by tooling (`wiki`, `data`) or stage (`raw`, `sources`, `companies`, `thesis`)?**
  - Answer: The evidence favors a hybrid. `wiki` should likely stay visible because it is a real tool/workflow contract, while `data` should probably be decomposed because it bundles several propagation stages. Stable stage terms already present in the repo are `raw`, `sources`, `concepts`, `companies`, `thesis`, and `reports`.
  - Evidence: `~/.codex/skills/wiki/SKILL.md`, `/Users/ash/Documents/2026/semi-stocks/wiki/schema.md`, `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`
  - Confidence: medium-high
  - Conflicts: none found
  - Open items: Decide whether the new root is a flat set of stage lanes or a wrapped `canonical/` lane plus compatibility entrypoints.

### Cross-Ref

- **Q: What is the actual propagation path today independent of wrapper names?**
  - Answer: External evidence is ingested into immutable raw wiki material, synthesized into wiki source and concept pages, narrowed into structured company/source state, promoted into thesis state only when evidence shifts cascade status, then rendered by synthesis/report code. Agents run in parallel from canonical state and can propose promotions after human review.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/wiki/schema.md`, `/Users/ash/Documents/2026/semi-stocks/data/research/earnings-pipeline.md`, `/Users/ash/Documents/2026/semi-stocks/agents/README.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: None on semantic flow.

- **Q: Which names preserve semantics without copying obsolete wrappers?**
  - Answer: Preserve `wiki`, `thesis`, `agents`, `reports`, `sources`, `concepts`, and `companies`. Reconsider `data` as the main umbrella because it is the most overloaded term in the current repo.
  - Evidence: same as above
  - Confidence: medium-high
  - Conflicts: code currently assumes `data/` paths, so renaming has migration cost.
  - Open items: Choose between keeping `data/` with a tighter scope or renaming the structured lane entirely.

- **Q: Where should the review gate sit between sidecar automation and canonical state?**
  - Answer: The existing model is already clear and should be preserved: agents read canonical lanes, write only under `agents/`, and human review is the only path for promotion back into canonical artifacts.
  - Evidence: `/Users/ash/Documents/2026/semi-stocks/README.md`, `/Users/ash/Documents/2026/semi-stocks/agents/README.md`, `/Users/ash/Documents/2026/semi-stocks/AGENTS.md`
  - Confidence: high
  - Conflicts: none found
  - Open items: None.

## Patterns Found

- The current repo already encodes a propagation model; the problem is that top-level names do not expose it cleanly.
- `wiki` is a real operating concept with tool support, schema rules, and query behavior. It is not just a prose bucket.
- `data` is the least stable umbrella because it mixes structured evidence, process docs, updates, and thesis state.
- `thesis.yaml` is already the narrowest canonical decision layer and behaves like a control plane.
- `reports/` and `wiki/outputs/` are both outputs, but one is canonical publication and the other is knowledge-base query filing.
- `agents/` already has the right sidecar contract: read everything canonical, write locally, promote only through human review.

## Core Docs Summary

- `README.md` has the clearest high-level statement of the actual funnel and the two-lane canonical/sidecar model.
- `wiki/schema.md` defines the wiki’s internal contract and its link to thesis/data.
- `data/research/earnings-pipeline.md` is the clearest expression of the wide-to-narrow process.
- `AGENTS.md` is the clearest statement that `data/thesis.yaml` is the control plane and that `agents/` is sidecar-only.
- `CLAUDE.md` reinforces that `wiki/` is an operational lane with required conventions, while `data/` currently acts as a broad source/thesis bucket.

## Open Questions

- Should the new repo keep a visible top-level `wiki/` path for skill compatibility, or should the wiki skill be updated to discover a deeper canonical path?
- Should thesis become its own root-level canonical stage, or remain a distinguished file or subtree within a broader structured-state lane?
- Should the root expose canonical stages directly, or keep a `canonical/` wrapper and rely on adapters or aliases for workflow tools like the wiki skill?
- If `data/` survives, what exact scope is allowed inside it so it stops becoming a catch-all?
- How should canonical published reports be distinguished from wiki query artifacts so `reports/` and `wiki/outputs/` remain complementary rather than overlapping?
