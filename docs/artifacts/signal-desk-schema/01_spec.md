---
status: draft
feature: signal-desk-schema
---

# Feature Spec: signal-desk-schema

## Goal

Define the minimum app schema for the Signal Desk surface so the UI can stay simple while still complementing the repo's wide-to-narrow canonical pipeline.

The schema discussion should clarify what "reviews" and "predictions" mean, how they relate to source evidence and signals, and which fields belong in the app surface versus canonical wiki/data/thesis layers.

## Users and Workflows

- Ash uses the Signal Desk to scan semiconductor themes from wide category context down to specific companies, signals, positions, and forward-looking calls.
- The UI should support quick filtering by category, company, signal, and direction without forcing every canonical artifact into the first screen.
- The schema should let future richer views expand from the same entities instead of creating parallel concepts for the UI.
- The planning workflow is schema-only for now: read repo reality, current surface work, and Justin's Wikiwise repo, then decide the smallest durable app contract.

## Acceptance Criteria

- Defines minimum entity set and relationships needed for the current UI surface.
- Separates canonical source-of-truth entities from app/integration view models.
- Explains whether "review" and "prediction" are first-class entities, derived counts, or labels over evidence.
- Maps the wide-to-narrow pipeline into app schema terms without adding unnecessary stages.
- Identifies fields needed for simple UI behavior: counts, filters, selected company/category panels, status, direction, and source traceability.
- Produces schema recommendations only; no implementation or UI expansion unless explicitly requested later.

## Boundaries

- In scope: schema names, entity boundaries, relationship shape, minimal required fields, and current-pipeline alignment.
- In scope: distinguishing canonical data from generated `canonical/wiki-site/` or app-facing `site-data` output.
- In scope: comparing this repo's current surface work against Justin's Wikiwise repo contracts.
- Out of scope: visual redesign, new dashboard features, ingestion changes, scoring algorithm changes, or report generation changes.
- Out of scope: code edits beyond planning artifacts unless Ash later approves design and execution.

## Risks and Dependencies

- Current generated surface data may already encode accidental schema choices; research must distinguish durable contracts from temporary implementation shape.
- "Review" and "prediction" may currently be overloaded across human review, earnings review, signal validation, and forecast claim.
- Justin's repo may impose integration constraints that should shape the app-facing schema but should not become canonical authority for semiconductor data.
- Dirty local changes exist in this repo; research must avoid treating unrelated in-progress files as intentional final design without evidence.
