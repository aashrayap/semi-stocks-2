---
status: completed
feature: semi-stocks-v2-layout
---

# Tasks: semi-stocks-v2-layout

## Task 1: Scaffold top-level folders

**Files to create or modify**
- `research/.gitkeep`
- `research/wiki/.gitkeep`
- `research/data/.gitkeep`
- `app/.gitkeep`
- `agents/.gitkeep`
- `outputs/.gitkeep`
- `tmp/.gitkeep`

**Dependency order**
First

**Acceptance criteria**
- The top-level lane structure exists in `semi-stocks-2`.
- The structure is intentionally high level and does not imply detailed migration yet.

**Verify commands**
- `find . -maxdepth 2 -type d | sort`

**Boundaries / out of scope**
- Do not migrate legacy files into these folders in this task.

## Task 2: Create minimal root docs

**Files to create or modify**
- `README.md`
- `AGENTS.md`
- `CLAUDE.md`

**Dependency order**
After Task 1

**Acceptance criteria**
- Root `README.md` is short and routes readers to the architecture and doc contract.
- Root `AGENTS.md` and `CLAUDE.md` are thin routing docs aligned to the new folder map.
- No long-form thesis or process docs remain at root in the new repo.

**Verify commands**
- `sed -n '1,220p' README.md`
- `sed -n '1,220p' AGENTS.md`
- `sed -n '1,220p' CLAUDE.md`

**Boundaries / out of scope**
- Do not port detailed workflow rules from the old repo verbatim in this pass.

## Task 3: Create durable docs contract

**Files to create or modify**
- `docs/architecture.md`
- `docs/doc-contract.md`

**Dependency order**
After Task 2

**Acceptance criteria**
- `docs/architecture.md` defines the v2 lane model and top-level ownership.
- `docs/doc-contract.md` defines root-doc versus `docs/` responsibilities and identifies which global docs are allowed at root.

**Verify commands**
- `sed -n '1,260p' docs/architecture.md`
- `sed -n '1,260p' docs/doc-contract.md`

**Boundaries / out of scope**
- Do not document detailed migration steps except where docs themselves need a destination.

## Task 4: Validate repo shape

**Files to create or modify**
- None, unless small fixes are needed

**Dependency order**
After Tasks 1-3

**Acceptance criteria**
- The repo root is understandable from a shallow tree plus the root docs.
- The docs clearly separate global architecture docs from subsystem-local docs.

**Verify commands**
- `find . -maxdepth 2 -type d | sort`
- `rg --files -g 'README.md' -g 'AGENTS.md' -g 'CLAUDE.md' -g 'docs/*.md' . | sort`

**Boundaries / out of scope**
- No content migration beyond these newly created docs.
