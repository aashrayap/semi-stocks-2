---
status: accepted-finalization
feature: signal-desk-schema
updated: 2026-04-19
---

# Research Pro Final Decisions

## Verdict

Research Pro finalized the MVP as a web-only, data-contract-first evidence reader.

The accepted final direction:

- one generated artifact: `canonical/site-data/signal_desk.json`
- one web reader consuming only that artifact
- graph is contextual evidence only
- mobile is out of MVP scope
- Trace is absent from MVP toolbar
- graph support families are only `co_position` and `shared_signal`

## Final Changes From v0.2

### Remove Mobile From MVP

Accepted.

MVP success target is a large-screen browser viewport at roughly 1280px+.

Out of scope:

- mobile bottom sheets
- mobile toolbar/chip rows
- mobile-first layout behavior
- `MobileFilterSheet.jsx` adaptation

The web implementation can be reasonably responsive to avoid breakage, but mobile-specific behavior is not an MVP gate.

### Narrow Graph Families

Accepted.

Do not emit these graph support families in MVP:

- `shared_thesis`
- `explicit_relationship`

Reserved future support families:

- `shared_thesis`
- `explicit_relationship`

Only emitted MVP graph support families:

- `co_position`
- `shared_signal`

Reason: thesis themes are filters/context, not edge-generation sources. `explicit_relationship` requires typed relationship data that does not exist yet.

### Source Documents Are Canonical Inputs Only

Accepted.

In MVP, emit one `source_document` per authoritative canonical input file.

Do not emit companion wiki source pages as independent `source_documents`.

Companion wiki pages become metadata on source documents:

- `related_paths`
- `wiki_page_slug`

Reason: separate wiki source document records would double-count provenance and make the Sources table noisy.

### Add Explicit Role Mapping File

Accepted.

Add:

```text
canonical/20-data/company_roles.yaml
```

Rules:

- every visible company must have an explicit `primary_role_id`
- optional `secondary_role_ids`
- optional `display_tags`
- no fallback from bottleneck slugs to company roles
- no fallback from thesis themes to company roles
- unknown roles are not allowed in MVP
- missing role mapping fails validation

Implementation discovery:

- `company-role:software-services` and `company-role:market-basket` are included to preserve raw 13F position fidelity for non-core source-filing exposures such as INFY and QQQ.
- These are source-fidelity roles, not thesis/value-chain roles.

### Final Web Layout

Accepted.

Layout:

```text
header
toolbar
main:
  left:
    graph
    table
  right:
    profile panel
```

Controls:

```text
Search | Source Channel | Company Role | Filters
```

Filters contains:

- Thesis Theme
- Timeline from/to
- Include undated

Trace is not a toolbar control.

## Implementation Target

The final implementation target is now:

```text
docs/artifacts/signal-desk-schema/17_final_mvp_spec.md
```

Older specs remain historical context:

- `09_final_spec.md` is pre-Research-Pro history
- `14_final_spec_v0_2.md` is superseded by the final web MVP spec
