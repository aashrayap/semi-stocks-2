---
status: completed
feature: semi-stocks-v2-layout
---

# Feature Spec: semi-stocks-v2-layout

## Goal
Define a clean high-level folder map for semi-stocks v2 in `semi-stocks-2` and a minimal documentation contract for repo root versus `docs/`, without yet planning detailed content migration for most folders.

## Users and Workflows
- Primary operator: the repo owner working with Codex and Claude on research, synthesis, and automation tasks.
- Agent workflow: an agent should be able to start at repo root, understand the lane boundaries quickly, and know which docs are authoritative.
- Human workflow: the owner should be able to find canonical research, application code, sidecar agent work, and generated outputs without inferring intent from historical clutter.
- Planning workflow: this pass should produce a structure that is stable enough to scaffold now and populate later.

## Acceptance Criteria
- A proposed top-level folder map exists for `semi-stocks-2` with clear ownership per folder.
- The proposal distinguishes canonical research artifacts, application/runtime code, agent-side experimentation, generated outputs, and local scratch space.
- A root markdown contract exists that specifies which files belong at repo root and why.
- A `docs/` contract exists that specifies which doc types belong under `docs/` and which do not.
- The proposal is intentionally high level and does not require deciding detailed migration sequencing for research and code folders.
- The proposal does cover docs migration at a high level, since the root/doc boundary is part of the feature.

## Boundaries
- In scope: top-level folder structure, lane boundaries, root markdown policy, `docs/` policy, and the minimal set of initial docs to create.
- In scope: reading only high-leverage files from the current `semi-stocks` repo that inform structure and authority boundaries.
- Out of scope: migrating most existing files, renaming every legacy path, or implementing the full import of research/code/agents content.
- Out of scope: redesigning the thesis, changing report behavior, or reworking the research pipeline semantics beyond clarifying where each concern belongs.
- Out of scope: low-level file trees under every future folder beyond what is needed to make the top-level contract legible.

## Risks and Dependencies
- The current repo may encode useful conventions implicitly in a small number of core files; missing one could produce a folder model that looks clean but breaks operator flow.
- If root docs are too thin, agents will lose routing context; if they are too thick, the root becomes cluttered again.
- The current repo appears to use two lanes, canonical and sidecar, but they are documented across multiple files and may not align perfectly in practice.
- This planning work depends on correctly extracting structure from a small set of high-leverage files in `semi-stocks`: root docs, thesis/control-plane files, and report/synthesis code.
