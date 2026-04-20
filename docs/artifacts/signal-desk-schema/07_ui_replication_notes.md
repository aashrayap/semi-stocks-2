---
status: draft
feature: signal-desk-schema
---

# UI Replication Notes: Justin Compute Site

## Decision

Use Justin's visual system and interaction model as the baseline for the Signal Desk reader, with semi-stocks data behind it.

The source site repo reports MIT license metadata in `package.json`, so direct reuse should preserve license attribution if substantial CSS/components are copied.

Pinned inspected commit:

`jstwng/compute-site@1f90a873c44ceea03240ccb5658e115dbc40e6c6`

## Theme To Copy

Use the same theme variables and dark-mode behavior:

```css
:root {
  color-scheme: light dark;
  --bg: #FFFFFF;
  --text: #2A2A2A;
  --text-strong: #000000;
  --text-muted: #8A8A8A;
  --text-faint: #999999;
  --border: rgb(213, 208, 200);
  --border-strong: #000000;
  --border-soft: #E8E8E8;
  --node-fill: #FFFFFF;
  --node-stroke: #2A2A2A;
  --edge: #2A2A2A;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0E0E0E;
    --text: #F2F2F2;
    --text-strong: #FFFFFF;
    --text-muted: #888888;
    --text-faint: #666666;
    --border: #333333;
    --border-strong: #B0B0B0;
    --border-soft: #1F1F1F;
    --node-fill: #161616;
    --node-stroke: #B0B0B0;
    --edge: #B0B0B0;
  }
}
```

Use Inter, 12px base density, square corners, thin borders, no color-coded rainbow graph by default.

## Layout To Copy

### Header

- Small title.
- Short text description.
- Source link.
- No large hero.

### Toolbar

Justin desktop order:

`Trace` `Timeline` `Cluster` then search field.

Signal Desk desktop order:

`Trace` `Timeline` `Thesis Cluster` `Company Category` `Signal Cluster` then search field.

Mobile should use compact chips and bottom sheets, following Justin's `MobileFilterSheet` pattern.

### Graph

Copy the feel:

- Full-width graph block under toolbar.
- Company nodes as thin rectangular boxes with name + ticker.
- Edges as thin muted lines.
- Hover dims unrelated nodes/edges.
- Click company opens profile panel.
- Click edge opens edge/evidence panel.
- Click empty graph expands or resets.

Graph should not render every available edge. It should use a graph-specific projection that preserves legibility.

### Detail below graph

Justin has a transaction table. Signal Desk should use the same dense table style but switch the row kind:

- Signals
- Claims / proof gates
- Positions
- Sources

## Traversal Model To Copy

Justin's Trace is clean because it is not generic graph search. It imposes a value-chain rank:

`equipment -> foundry/memory/packaging -> chip_designer -> server/power/networking -> operator -> ai_lab`

Signal Desk should do the same before enabling Trace. Proposed rank:

```yaml
0: equipment
1: foundry | memory | packaging
2: chip_designer
3: server_oem | networking | optics | power
4: gpu_cloud | data_center | hyperscaler
5: ai_lab | application
```

Rules to copy:

- Downstream-only traversal.
- Cap max depth.
- Cap max path count.
- Group trace paths by category shape.
- Add hop-count chips.
- If no path, allow swap.
- Highlight selected path in graph and filter table to path evidence.

## Graph Implementation Qualities To Preserve

- Deterministic layout cache.
- First paint waits for real dimensions.
- ResizeObserver with debounce.
- Force layout + overlap removal.
- Dynamic node width based on measured label text.
- Focus mode shows selected company plus neighborhood.
- Dimmed nodes disable pointer events.
- Edge clipping stops lines at node borders.

## Semi-Stocks Data Binding

| UI object | Data source |
|---|---|
| node | company |
| node label | company name + ticker |
| node category | company category cluster |
| graph edge | evidence relationship projection |
| edge type | signal kind / claim / position / source relationship |
| trace path | downstream value-chain projection |
| table row | signal, claim, position, or source |
| profile panel | selected company or evidence edge |

## Open Design Question

Top toolbar now has five controls plus search. This matches the desired dimensions but may be dense. If it feels too crowded, fold `Thesis Cluster`, `Company Category`, and `Signal Cluster` into one `Cluster` dropdown with tabs. Start explicit, collapse only if needed.
