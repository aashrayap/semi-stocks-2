---
status: completed
feature: semi-stocks-v2-layout
---

# Research Questions: semi-stocks-v2-layout

## Codebase
- Which files currently act as the control plane and runtime entry points for the canonical lane, and what top-level folders do they assume?
- Which files currently define or imply the separation between canonical research and agent-side work?
- What top-level outputs are produced by the canonical reporting path versus the sidecar reporting path?

## Docs
- Which existing root markdown files in `semi-stocks` carry durable routing value versus content that should move under `docs/`?
- What responsibilities are currently split across `README.md`, `AGENTS.md`, `CLAUDE.md`, and `TODO.md`, and where do they overlap?
- Which architecture or process docs are currently the highest-leverage references for preserving repo intent during a v2 cleanup?

## Patterns
- What repository pattern is already emerging in `semi-stocks` for authority boundaries between source-of-truth artifacts, generated artifacts, and experiments?
- Which documented conventions appear stable enough to keep in v2, even if paths change?

## External
- None expected unless local evidence is insufficient.

## Cross-Ref
- Given the current control-plane files, report paths, and root docs, what top-level folder map would preserve the operating model while making lane boundaries more obvious?
- Given the current root markdown overlap, what is the minimum viable root-doc set for v2, and which docs should move under `docs/`?
- Which docs should be created first in `semi-stocks-2` so the repo can be scaffolded cleanly before broader migration begins?
