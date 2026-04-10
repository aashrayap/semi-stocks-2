---
status: completed
feature: canonical-propagation-model
---

# Feature Spec: canonical-propagation-model

## Goal

Define a clean repo authority model for `semi-stocks-2` that treats the system as a wide-to-narrow propagation pipeline instead of a generic project tree or a direct copy of `semi-stocks`.

## Users and Workflows

- Primary operator: Ash, using the repo to build and refine semiconductor research over time.
- Human research workflow: collect external evidence, synthesize it into readable knowledge, narrow it into structured company and thesis state, and review downstream reports.
- Wiki workflow: use a wiki-oriented workspace for raw evidence, source pages, concepts, and query outputs without letting the wiki become disconnected from structured thesis state.
- Scheduled automation workflow: let recurring processes add or update sidecar research artifacts safely, with clear review and promotion boundaries before canonical state changes.
- Agent workflow: allow agents to read canonical context broadly, write local sidecar outputs, and avoid introducing a second unofficial control plane.

## Acceptance Criteria

- A proposed root layout exists that centers `docs/`, `canonical/`, `agents/`, and `tmp/`.
- The canonical wide-to-narrow path is explicit from external evidence through knowledge capture, structured state, thesis state, engine code, and published reports.
- The plan explicitly decides whether thesis state belongs inside a broader canonical state lane or deserves its own canonical lane.
- Each canonical directory in the proposed model maps to one propagation concern rather than a vague storage bucket or tool wrapper.
- The design states where subsystem-local docs belong versus cross-cutting docs under `docs/`.
- A sidecar lane is defined where `agents/*` can read canonical material, write sidecar artifacts, and optionally promote reviewed changes back into canonical lanes.
- The plan supports both wiki-skill workflows and automated scheduled processes without creating duplicate sources of truth.
- The planning output is strong enough to guide scaffold work without requiring full legacy migration in the same pass.

## Boundaries

- In scope: top-level authority boundaries, lane names, propagation stages, and the minimal docs and planning artifacts needed to lock the model.
- In scope: defining how human-readable knowledge, structured research state, synthesis code, and reports relate to one another.
- In scope: clarifying canonical-versus-sidecar responsibilities and the review/promotion boundary between them.
- Out of scope: migrating all legacy files from `semi-stocks`, implementing every scheduled process, or redesigning report content in this planning pass.
- Out of scope: changing the substance of the semiconductor thesis itself.
- Out of scope: full low-level file trees for every subsystem beyond what is needed to make authority and flow clear.

## Risks and Dependencies

- The old repo may encode real operating semantics in legacy filenames; copying those names forward mechanically would preserve clutter instead of intent.
- Human-readable wiki material and structured data can easily overlap unless the authority boundary between them is explicit.
- Names like `wiki/` and `data/` may describe tools or storage types rather than true propagation concerns, which could reintroduce overlap even in a cleaner tree.
- Thesis state may be too narrow and decision-critical to leave buried inside a generic state folder, but pulling it out too early could also fragment the canonical lane.
- Scheduled automation can create competing state unless sidecar outputs and promotion rules are defined before implementation work begins.
- The current repo docs still describe the earlier `research/` + `app/` + `outputs/` shape, so follow-on scaffold work depends on correcting those docs first.
- Research will need to inspect a small number of high-leverage legacy files to separate stable semantics from obsolete layout choices.
