---
status: draft
feature: proposal-gated-data-pipeline
---

# Research Questions: proposal-gated-data-pipeline

## Human Direction

1. Resolved: accepted proposals stay internal and only authorize the admitted
   companies and evidence. They should not appear in the main Signal Desk feed
   as explicit reader rows/documents.
2. Resolved: `canonical/20-data/companies/` should be generated/mirrored from
   accepted proposals in v1. Accepted proposals remain the authored admission
   authority; generated company dossiers are derived members of the admitted
   universe.
3. Resolved: the decision state model for this phase is `proposed | accepted |
   rejected`. `accepted` is the reader gate. No distinct `applied` state now.
4. Resolved: generated company dossiers persist under
   `canonical/20-data/companies/_generated/` instead of existing only inside
   `canonical/site-data/`.
5. Resolved: row and source-document emission must be strict to accepted
   proposal `evidence_refs[].source_document_id`.
6. Resolved: the hard gate applies to reader-consumed site-data artifacts, not
   only `signal_desk.json`.

## Codebase

1. Which current engine paths admit companies from ungated inputs before any
   proposal gate is applied?
2. Which Signal Desk payload sections currently emit pending proposal data into
   the main reader contract?
3. Do current contract tests encode source-rooted emission assumptions that must
   be inverted?

## Docs

1. What do current repo docs already say about `canonical/20-data/thesis-proposals/`
   and the human approval loop?
2. Does the repo-local `ingest-semi` skill already route thesis-affecting
   source changes into proposal files instead of direct thesis edits?

## Patterns

1. Is the safer first move a hard admission root with two physical layers, or a
   single physical lane with status plus parity validation?

## External

1. None required for the current checkpoint.

## Cross-Ref

1. How do the Research Pro review findings compare with current local engine and
   contract reality?
