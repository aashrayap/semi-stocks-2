---
status: foundation-complete-next-polish
feature: signal-desk-schema
updated: 2026-04-20
---

# Tasks: Signal Desk MVP

MVP foundation is implemented in PR #3. This task list now tracks what remains
after Research Pro's explanation output in
[19_research_pro_explanation_output.md](19_research_pro_explanation_output.md).

## Completed Foundation

- `canonical/20-data/company_roles.yaml`
- `canonical/site-data/signal_desk.json`
- source channels
- source documents
- unified evidence rows
- contextual evidence graph data
- validation and contract tests
- web reader scaffold
- search/source-channel/company-role/filter logic
- graph/table/profile first pass

## Next Implementation Batch

### SD-POLISH-1 - Graph Semantics And Readability

Status: implemented first pass.

- Add always-visible graph legend:
  - graph means shared evidence
  - graph does not mean relationship flow
  - Trace is parked
- Add one clutter-control mechanism:
  - support-family toggle, threshold, top-N, or equivalent
- Keep graph support families limited to:
  - `co_position`
  - `shared_signal`
- Acceptance:
  - graph area clearly says "shared evidence"
  - user can reduce edge clutter
  - edge click still shows support rows
  - Trace remains absent from toolbar

### SD-POLISH-2 - Company And Edge Profile Depth

Status: implemented first pass.

- Group company profile evidence by source channel and row type.
- Edge profile must show:
  - why edge exists
  - support family
  - source channel
  - supporting row IDs/titles
  - linked source documents
- Acceptance:
  - selected company explains why it is visible
  - selected edge cannot be mistaken for supplier/customer relationship
  - proposal/claim lifecycle badges are visible

### SD-POLISH-3 - Table And Timeline Honesty

Status: implemented first pass.

- Improve per-tab columns for:
  - Signals
  - Claims
  - Positions
  - Proposals
  - Sources
- Render label-only timelines honestly.
- Sort null dates last by default.
- Acceptance:
  - table tabs read cleanly
  - undated/label-only rows do not masquerade as dated rows
  - positions show value and portfolio percent clearly

### SD-POLISH-4 - Filter State And Empty States

Status: implemented first pass.

- Show active filters clearly.
- Explain Include undated.
- Add empty-state copy for:
  - graph
  - table
  - profile
- Acceptance:
  - user can tell which filters are active
  - zero-result state explains whether data is absent or filtered out

### SD-POLISH-5 - Large-Screen Browser QA

Status: implemented first pass.

- Review large-screen web layout at target viewport.
- Capture/check states:
  - default
  - filtered
  - company selected
  - edge selected
  - empty result
- Acceptance:
  - graph/table/profile remain usable together
  - no critical text/control overlap
  - no semantic affordance disappears

### SD-PARKED-1 - Keep Trace Parked

- Do not implement Trace.
- Do not infer supplier/customer edges.
- Future unpark requires typed `relationship_edges`.

## Historical Foundation Tasks

## SD-MVP-1 - Add Explicit Company Role Mapping

- Create: `canonical/20-data/company_roles.yaml`.
- Include every company visible in Signal Desk.
- Fields per company should include:
  - `company_id` or ticker key
  - `primary_role_id`
  - optional `secondary_role_ids`
  - optional `display_tags`
- Acceptance:
  - every visible company has one valid primary role
  - no unknown role mappings
  - no fallback from bottleneck or thesis theme
  - `neocloud` / `data_center` appear only as display tags unless later promoted
- Verify:
  - role validator fails if any visible company lacks mapping
- Estimate: 1-2h.

## SD-MVP-2 - Build Source Channels And Source Documents

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add `facets.source_channels`.
- Add top-level `source_documents`.
- Emit one source document per authoritative canonical input file.
- Do not emit wiki source pages as standalone source documents.
- Link companion wiki pages via:
  - `related_paths`
  - `wiki_page_slug`
- Acceptance:
  - every future row can reference at least one `source_document_id`
  - source documents preserve canonical path, source channel, period, timeline, company IDs, thesis theme IDs
- Estimate: 3-5h.

## SD-MVP-3 - Generate Unified Rows

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add top-level `rows`.
- Emit row variants:
  - `position`
  - `signal`
  - `claim`
  - `proposal`
- Add required base fields:
  - `id`
  - `row_type`
  - `title`
  - `summary`
  - `company_ids`
  - `primary_company_id`
  - `source_channel_id`
  - `source_document_ids`
  - `source_paths`
  - `thesis_theme_ids`
  - `search_text`
  - `period`
  - `timeline`
  - `graph_eligibility`
  - `lifecycle_state`
  - `ui_badges`
- Acceptance:
  - Baker emits exactly 20 raw position rows
  - Leopold emits exactly 25 raw position rows
  - claims gain `source_document_ids` and `source_paths`
  - proposals are rows, not signals
  - every row has a timeline object
- Estimate: 5-8h.

## SD-MVP-4 - Add Period, Timeline, And Search Helpers

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add helpers:
  - `_period_for_*`
  - `_timeline_for_*`
  - `_search_text(*values)`
- Acceptance:
  - every row and source document has `period`
  - every row and source document has `timeline`
  - null sort dates are counted in `quality`
  - all search text is normalized and stable
- Estimate: 2-4h.

## SD-MVP-5 - Build Derived Companies, Facets, Indexes, And Table Views

- Modify: `canonical/40-engine/engine/site_data.py`.
- Build:
  - `companies`
  - `facets.company_roles`
  - `facets.thesis_themes`
  - `facets.row_types`
  - `facets.graph_support_families`
  - `indexes.*`
  - `tables`
- Acceptance:
  - company counts derive from rows/source documents
  - table views contain IDs and column configs only
  - `tables.default_view_id == signals`
  - indexes resolve correctly
- Estimate: 3-5h.

## SD-MVP-6 - Build Contextual Evidence Graph

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add graph mode: `contextual_evidence`.
- Nodes:
  - companies only
  - node `id` equals company ID
- Edges:
  - undirected
  - use sorted `company_ids`
  - `trace_eligible: false`
  - `semantic_label: shared_evidence`
  - support arrays only
- Emitted support families:
  - `co_position`
  - `shared_signal`
- Do not emit:
  - `shared_thesis`
  - `explicit_relationship`
- Acceptance:
  - no graph nodes from pages/thesis/sources/reports
  - no proposal or claim graph support
  - graph support row IDs resolve and touch both companies
  - visual weights are deterministic
- Estimate: 3-5h.

## SD-MVP-7 - Add Quality Diagnostics

- Modify: `canonical/40-engine/engine/site_data.py`.
- Add top-level `quality`.
- Include:
  - `ui_ready`
  - `trace_ready`
  - `rows_without_source_document`
  - `rows_without_sort_date`
  - `rows_with_label_only_timeline`
  - `graph_edges_contextual_only`
  - `position_leg_counts`
  - `trace_blockers`
- Acceptance:
  - `trace_ready == false`
  - `graph_edges_contextual_only == true`
  - Baker/Leopold emitted counts match source counts
- Estimate: 1-2h.

## SD-MVP-8 - Extend Schema And Semantic Validation

- Modify: `canonical/40-engine/engine/site_data.py`.
- Modify generated: `canonical/site-data/schema.json`.
- Add dedicated `signal_desk` schema entry.
- Add hard-fail semantic validation:
  - top-level keys complete
  - no duplicate IDs
  - every company role resolves
  - role mapping file complete
  - every row has required base fields
  - row/source/company references resolve
  - graph nodes/edges resolve
  - graph support families only `co_position` and `shared_signal`
  - proposals/claims are not graph eligible
  - machine dates pass real date validation
  - Baker/Leopold raw position counts match emitted rows
  - `graph.mode == contextual_evidence`
  - `quality.trace_ready == false`
  - `features.trace.visible == false`
- Acceptance:
  - validator fails hard on semantic contract breakage
  - quality counters remain non-fatal diagnostics
- Estimate: 3-5h.

## SD-MVP-9 - Add Fixture And Golden Tests

- Create/update tests near the generator unless repo test conventions indicate a better location.
- Add deterministic fixture with:
  - 4-6 companies
  - Baker filing with at least one multi-leg name
  - Leopold filing
  - two multi-company signal rows
  - one company packet yielding a claim
  - one thesis proposal
  - one theme covering only part of data
  - one label-only timeline row
- Snapshot deterministic subtrees:
  - `facets`
  - `companies`
  - `rows`
  - `graph`
  - `indexes`
  - `tables`
  - `quality`
- Acceptance:
  - fixture tests pass
  - snapshots stable after deterministic sorting
- Estimate: 3-6h.

## SD-MVP-10 - Emit `signal_desk.json`

- Modify: `canonical/40-engine/engine/site_data.py`.
- Modify if output text changes: `canonical/40-engine/site_data.py`.
- Write: `canonical/site-data/signal_desk.json`.
- Include artifact in build manifest/schema/validation.
- Verify:
  - `uv run python canonical/40-engine/site_data.py --validate`
  - `python3 -m json.tool canonical/site-data/signal_desk.json >/dev/null`
- Acceptance:
  - artifact generated
  - schema validation passes
  - semantic validation passes
  - quality diagnostics present
- Estimate: 1-2h after prior tasks.

## SD-MVP-11 - Scaffold Web Reader After Data Gate

- Create after SD-MVP-1 through SD-MVP-10 pass:
  - `canonical/site-reader/package.json`
  - `canonical/site-reader/index.html`
  - `canonical/site-reader/src/**`
  - `canonical/site-reader/THIRD_PARTY_NOTICES.md`
- Load only `../site-data/signal_desk.json`.
- Implement web layout:
  - header
  - toolbar
  - graph above table in left column
  - fixed-width right profile panel
- Toolbar controls:
  - Search
  - Source Channel
  - Company Role
  - Filters
- Filters:
  - Thesis Theme
  - Timeline from/to
  - Include undated
- Omit:
  - mobile-specific behavior
  - Trace toolbar control
- Verify:
  - `cd canonical/site-reader && npm install`
  - `npm run build`
  - `npm run test`
- Acceptance:
  - graph, table, profile visible together in the large-screen web layout
  - filters intersect correctly
  - no direct reader dependency on canonical markdown/YAML
  - Trace absent from toolbar
- Estimate: 8-12h after data gate.

## SD-MVP-12 - Keep Trace Parked

- Do not implement enabled Trace.
- Do not add relationship pathfinding.
- Do not infer supplier/customer edges from prose.
- Future unpark requires separate `relationship_edges` dataset.
- Acceptance:
  - `features.trace.visible == false`
  - no user-facing control implies Trace is available
- Estimate if later approved: separate feature.
