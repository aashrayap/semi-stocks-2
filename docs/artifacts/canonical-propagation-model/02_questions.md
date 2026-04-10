---
status: completed
feature: canonical-propagation-model
---

# Research Questions: canonical-propagation-model

## Codebase

- In the legacy `semi-stocks` repo, which files currently define the narrowest canonical state and the downstream path from that state to rendered reports?
- Which legacy code or scripts assume specific top-level paths for wiki content, structured data, synthesis logic, or report outputs?
- Where do existing automation paths write intermediate artifacts today, and which of those artifacts behave as canonical state versus generated output versus sidecar scratch?
- What evidence exists in current code or data that company-level models are distinct from wider source/evidence state rather than just another output format?
- What evidence exists that thesis state is operationally distinct from broader structured research state, rather than just one file inside a generic data layer?

## Docs

- Which current docs in `semi-stocks` describe durable authority boundaries, and which are mostly historical naming that should not drive the new layout?
- What do the current wiki docs say about the distinctions among raw evidence, source pages, concept pages, and query outputs?
- What does the current agent documentation say about agent-side authority, and does it already imply a read-all, write-local workflow?
- Which docs are truly cross-cutting, and which should live next to `canonical/wiki/`, `canonical/data/`, or other subsystems instead of under `docs/`?
- Do current docs use `wiki` and `data` as true concerns, or mostly as implementation buckets that hide multiple propagation stages?

## Patterns

- Does the legacy repo already behave as a wide-to-narrow propagation system even though its top-level folders do not say so explicitly?
- Where do overlap problems currently appear between prose knowledge, structured data, code outputs, and agent artifacts?
- What stable pattern exists, if any, for narrowing from broad evidence into a final thesis or bet-sizing input?
- What recurring workflow exists or is implied for scheduled research updates, and how separate is that workflow from the canonical decision path?
- Is the cleaner canonical split best modeled by representation/tooling (`wiki`, `data`) or by propagation stage (`evidence`, `knowledge`, `models`, `thesis`)?

## External

- Do the installed wiki workflow or local scheduling tools impose any file-layout or naming constraints that materially affect the proposed `canonical/wiki/*` or `agents/*` boundaries?

## Cross-Ref

- Given the legacy thesis state, wiki schema, synthesis/report paths, and agent-side docs, what is the actual propagation path today independent of folder names?
- Which top-level names preserve the real semantics of the system without copying obsolete wrapper names like `research/`, `app/`, or `outputs/`?
- Where should the review gate sit between sidecar automation and canonical state so that scheduled processes can accelerate research without becoming a second control plane?
- What is the minimum canonical path from external evidence to a published report, and which stages should remain human-readable versus strictly structured?
- Should thesis state live under a broader canonical state lane or become its own canonical stage, and what downstream behavior would that choice simplify or complicate?
