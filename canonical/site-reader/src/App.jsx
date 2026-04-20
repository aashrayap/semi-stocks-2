import { useEffect, useMemo, useState } from 'react'
import {
  applyFilters,
  companiesForGraph,
  createLookups,
  defaultGraphOptions,
  emptyFilters,
  filterGraphEdges,
  formatDateLabel,
  formatMoney,
  formatPercent,
  formatRowType,
  rowLabel,
  sortRowsForView,
} from './logic.js'

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState(emptyFilters)
  const [openFilter, setOpenFilter] = useState(null)
  const [tableView, setTableView] = useState('signals')
  const [selection, setSelection] = useState(null)
  const [graphOptions, setGraphOptions] = useState(defaultGraphOptions)

  useEffect(() => {
    fetch('/site-data/signal_desk.json')
      .then(response => {
        if (!response.ok) throw new Error(`Failed to load signal_desk.json: ${response.status}`)
        return response.json()
      })
      .then(setData)
      .catch(err => setError(err.message))
  }, [])

  const filtered = useMemo(() => data ? applyFilters(data, filters) : null, [data, filters])
  const lookups = useMemo(() => data ? createLookups(data) : null, [data])

  useEffect(() => {
    if (!selection || !filtered) return
    if (selection.type === 'company' && !filtered.companyIds.has(selection.id)) setSelection(null)
    if (selection.type === 'edge' && !filterGraphEdges(filtered.graphEdges, graphOptions).some(edge => edge.id === selection.id)) setSelection(null)
  }, [filters, graphOptions, filtered, selection])

  if (error) return <div className="page"><div className="error">{error}</div></div>
  if (!data || !filtered || !lookups) return <div className="page"><div className="loading">Loading Signal Desk</div></div>

  const tableRows = rowsForView(tableView, data, filtered)
  const visibleEdges = filterGraphEdges(filtered.graphEdges, graphOptions)
  const graphCompanies = companiesForGraph(filtered.companies, filtered.rows, visibleEdges)
  const selectedCompany = selection?.type === 'company' ? lookups.companies.get(selection.id) : null
  const selectedEdge = selection?.type === 'edge' ? visibleEdges.find(edge => edge.id === selection.id) : null

  const setArrayFilter = (key, value) => {
    setFilters(prev => {
      const set = new Set(prev[key])
      if (set.has(value)) set.delete(value)
      else set.add(value)
      return { ...prev, [key]: [...set].sort() }
    })
  }

  return (
    <div className="page">
      <header className="header">
        <div>
          <h1>Signal Desk</h1>
          <p>Source-channel evidence map for semi-stocks canonical data.</p>
        </div>
        <div className="build">
          <span>{data.version}</span>
          <span>{data.build.generated_at}</span>
        </div>
      </header>

      <section className="toolbar">
        <label className="searchBox">
          <span>Search</span>
          <input
            value={filters.search}
            onChange={event => setFilters(prev => ({ ...prev, search: event.target.value }))}
            placeholder="companies, sources, signals, claims"
          />
        </label>
        <FilterMenu
          id="source"
          label="Source Channel"
          openFilter={openFilter}
          setOpenFilter={setOpenFilter}
          count={filters.source_channel_ids.length}
        >
          <CheckboxList
            items={data.facets.source_channels}
            selected={filters.source_channel_ids}
            onToggle={id => setArrayFilter('source_channel_ids', id)}
          />
        </FilterMenu>
        <FilterMenu
          id="role"
          label="Company Role"
          openFilter={openFilter}
          setOpenFilter={setOpenFilter}
          count={filters.company_role_ids.length}
        >
          <CheckboxList
            items={data.facets.company_roles}
            selected={filters.company_role_ids}
            onToggle={id => setArrayFilter('company_role_ids', id)}
          />
        </FilterMenu>
        <FilterMenu id="more" label="Filters" openFilter={openFilter} setOpenFilter={setOpenFilter} count={filters.thesis_theme_ids.length + (filters.timeline.from || filters.timeline.to ? 1 : 0)}>
          <div className="filterGroupTitle">Thesis Theme</div>
          <CheckboxList
            items={data.facets.thesis_themes}
            selected={filters.thesis_theme_ids}
            onToggle={id => setArrayFilter('thesis_theme_ids', id)}
          />
          <div className="filterGroupTitle">Timeline</div>
          <div className="dateGrid">
            <label>From<input type="date" value={filters.timeline.from || ''} onChange={event => setFilters(prev => ({ ...prev, timeline: { ...prev.timeline, from: event.target.value || null } }))} /></label>
            <label>To<input type="date" value={filters.timeline.to || ''} onChange={event => setFilters(prev => ({ ...prev, timeline: { ...prev.timeline, to: event.target.value || null } }))} /></label>
          </div>
          <label className="checkRow">
            <input type="checkbox" checked={filters.include_undated} onChange={event => setFilters(prev => ({ ...prev, include_undated: event.target.checked }))} />
            Include undated
          </label>
          <p className="helperText">Rows without exact dates stay visible by default. Turn this off only for strict date-window review.</p>
        </FilterMenu>
        <button className="ghostButton" onClick={() => { setFilters(emptyFilters); setSelection(null) }}>Clear</button>
      </section>

      <ActiveFilters
        filters={filters}
        lookups={lookups}
        setFilters={setFilters}
      />

      <section className="stats">
        <Stat label="Companies" value={filtered.companies.length} />
        <Stat label="Rows" value={filtered.rows.length} />
        <Stat label="Edges" value={filtered.graphEdges.length} />
        <Stat label="Source docs" value={filtered.sourceDocuments.length} />
        <Stat label="Trace" value="Parked" muted />
      </section>

      <main className="workspace">
        <div className="mainColumn">
          <Graph
            companies={graphCompanies}
            edges={visibleEdges}
            lookups={lookups}
            roles={data.facets.company_roles}
            selection={selection}
            onSelect={setSelection}
            graphOptions={graphOptions}
            setGraphOptions={setGraphOptions}
            totalEdges={filtered.graphEdges.length}
          />
          <EvidenceTable
            data={data}
            filtered={filtered}
            lookups={lookups}
            tableView={tableView}
            setTableView={setTableView}
            rows={tableRows}
            onSelect={setSelection}
          />
        </div>
        <ProfilePanel
          selection={selection}
          company={selectedCompany}
          edge={selectedEdge}
          data={data}
          filtered={filtered}
          lookups={lookups}
        />
      </main>
    </div>
  )
}

function FilterMenu({ id, label, count, openFilter, setOpenFilter, children }) {
  const open = openFilter === id
  return (
    <div className="filterMenu">
      <button className={open ? 'filterButton active' : 'filterButton'} onClick={() => setOpenFilter(open ? null : id)}>
        {label}: <span>{count ? `${count} selected` : 'All'}</span>
      </button>
      {open && <div className="filterPanel">{children}</div>}
    </div>
  )
}

function ActiveFilters({ filters, lookups, setFilters }) {
  const chips = []
  if (filters.search) chips.push({ key: 'search', label: `Search: ${filters.search}`, remove: () => setFilters(prev => ({ ...prev, search: '' })) })
  for (const id of filters.source_channel_ids) chips.push({ key: `source:${id}`, label: `Source: ${lookups.sourceChannels.get(id)?.label || id}`, remove: () => removeArray(setFilters, 'source_channel_ids', id) })
  for (const id of filters.company_role_ids) chips.push({ key: `role:${id}`, label: `Role: ${lookups.companyRoles.get(id)?.label || id}`, remove: () => removeArray(setFilters, 'company_role_ids', id) })
  for (const id of filters.thesis_theme_ids) chips.push({ key: `theme:${id}`, label: `Theme: ${lookups.thesisThemes.get(id)?.label || id}`, remove: () => removeArray(setFilters, 'thesis_theme_ids', id) })
  if (filters.timeline.from || filters.timeline.to) chips.push({ key: 'timeline', label: `Timeline: ${filters.timeline.from || 'start'} to ${filters.timeline.to || 'end'}`, remove: () => setFilters(prev => ({ ...prev, timeline: { from: null, to: null } })) })
  if (!filters.include_undated) chips.push({ key: 'dated', label: 'Undated excluded', remove: () => setFilters(prev => ({ ...prev, include_undated: true })) })
  if (!chips.length) return null
  return (
    <section className="activeFilters">
      {chips.map(chip => (
        <button key={chip.key} className="filterChip" onClick={chip.remove}>
          {chip.label}<span> x</span>
        </button>
      ))}
    </section>
  )
}

function removeArray(setFilters, key, value) {
  setFilters(prev => ({ ...prev, [key]: prev[key].filter(item => item !== value) }))
}

function CheckboxList({ items, selected, onToggle }) {
  const set = new Set(selected)
  return (
    <div className="checkList">
      {items.map(item => (
        <label className="checkRow" key={item.id}>
          <input type="checkbox" checked={set.has(item.id)} onChange={() => onToggle(item.id)} />
          <span>{item.label}</span>
          {item.counts && <em>{item.counts.companies ?? item.counts.rows ?? 0}</em>}
        </label>
      ))}
    </div>
  )
}

function Stat({ label, value, muted }) {
  return <div className={muted ? 'stat muted' : 'stat'}><span>{label}</span><strong>{value}</strong></div>
}

function Graph({ companies, edges, lookups, roles, selection, onSelect, graphOptions, setGraphOptions, totalEdges }) {
  const layout = useMemo(() => layoutCompanies(companies, roles), [companies, roles])
  const selectedCompanyId = selection?.type === 'company' ? selection.id : null
  const selectedEdgeId = selection?.type === 'edge' ? selection.id : null
  const selectedEdge = selectedEdgeId ? edges.find(edge => edge.id === selectedEdgeId) : null
  const neighborhood = new Set(selectedCompanyId ? [selectedCompanyId] : selectedEdge?.company_ids || [])
  if (selectedCompanyId) {
    for (const edge of edges) if (edge.company_ids.includes(selectedCompanyId)) edge.company_ids.forEach(id => neighborhood.add(id))
  }
  const hasFocus = Boolean(selection)

  return (
    <section className="graphCard">
      <div className="sectionHead">
        <h2>Contextual Evidence Graph</h2>
        <span>{companies.length} nodes / {edges.length} shown of {totalEdges} edges</span>
      </div>
      <GraphLegend graphOptions={graphOptions} setGraphOptions={setGraphOptions} />
      {companies.length === 0 || edges.length === 0 ? (
        <div className="emptyState">
          <strong>No graph edges under current settings.</strong>
          <span>Loosen filters, lower the edge threshold, or include both support families.</span>
        </div>
      ) : null}
      <svg className="graph" viewBox="0 0 1120 520" role="img" onClick={() => onSelect(null)}>
        {edges.map(edge => {
          const a = layout.get(edge.company_ids[0])
          const b = layout.get(edge.company_ids[1])
          if (!a || !b) return null
          const dim = hasFocus && !edge.company_ids.some(id => neighborhood.has(id))
          return (
            <line
              key={edge.id}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              className={edge.id === selectedEdgeId ? 'edge selected' : dim ? 'edge dim' : 'edge'}
              strokeWidth={Math.max(1, Math.min(5, 1 + edge.visual_weight))}
              onClick={event => { event.stopPropagation(); onSelect({ type: 'edge', id: edge.id }) }}
            />
          )
        })}
        {companies.map(company => {
          const point = layout.get(company.id)
          if (!point) return null
          const role = lookups.companyRoles.get(company.primary_role_id)
          const dim = hasFocus && !neighborhood.has(company.id)
          return (
            <g key={company.id} transform={`translate(${point.x - 64}, ${point.y - 18})`} onClick={event => { event.stopPropagation(); onSelect({ type: 'company', id: company.id }) }}>
              <rect className={company.id === selectedCompanyId ? 'node selected' : dim ? 'node dim' : 'node'} width="128" height="36" />
              <text x="10" y="15" className="nodeTicker">{company.ticker || company.name}</text>
              <text x="10" y="28" className="nodeRole">{role?.label || company.primary_role_id}</text>
            </g>
          )
        })}
      </svg>
    </section>
  )
}

function GraphLegend({ graphOptions, setGraphOptions }) {
  const toggleFamily = family => {
    setGraphOptions(prev => {
      const set = new Set(prev.support_families)
      if (set.has(family)) set.delete(family)
      else set.add(family)
      return { ...prev, support_families: [...set].sort() }
    })
  }
  return (
    <div className="graphLegend">
      <div>
        <strong>Graph = shared evidence, not relationship flow.</strong>
        <span>Edges do not imply supplier/customer, money flow, ownership, causality, or Trace path.</span>
      </div>
      <div className="graphControls">
        <label><input type="checkbox" checked={graphOptions.support_families.includes('co_position')} onChange={() => toggleFamily('co_position')} /> co-position</label>
        <label><input type="checkbox" checked={graphOptions.support_families.includes('shared_signal')} onChange={() => toggleFamily('shared_signal')} /> shared signal</label>
        <label>Min weight <input type="range" min="0" max="1" step="0.05" value={graphOptions.min_weight} onChange={event => setGraphOptions(prev => ({ ...prev, min_weight: Number(event.target.value) }))} /> <span>{graphOptions.min_weight.toFixed(2)}</span></label>
        <label>Top edges <select value={graphOptions.edge_limit} onChange={event => setGraphOptions(prev => ({ ...prev, edge_limit: Number(event.target.value) }))}><option value="40">40</option><option value="80">80</option><option value="140">140</option><option value="240">240</option></select></label>
      </div>
    </div>
  )
}

function EvidenceTable({ data, filtered, lookups, tableView, setTableView, rows, onSelect }) {
  const order = data.tables.view_order
  return (
    <section className="tableCard">
      <div className="tabs">
        {order.map(viewId => (
          <button key={viewId} className={tableView === viewId ? 'tab active' : 'tab'} onClick={() => setTableView(viewId)}>
            {data.tables.views[viewId].label}
          </button>
        ))}
      </div>
      <div className="tableWrap">
        {rows.length === 0 && <div className="emptyState"><strong>No rows in this view.</strong><span>Change filters or switch table tabs.</span></div>}
        {tableView === 'sources' ? (
          <SourceTable docs={rows} lookups={lookups} />
        ) : (
          <RowTable rows={rows} lookups={lookups} onSelect={onSelect} />
        )}
      </div>
    </section>
  )
}

function RowTable({ rows, lookups, onSelect }) {
  return (
    <table>
      <thead><tr><th>Date</th><th>Evidence</th><th>Companies</th><th>Source</th><th>Details</th><th>State</th></tr></thead>
      <tbody>
        {rows.map(row => (
          <tr key={row.id} onClick={() => row.primary_company_id && onSelect({ type: 'company', id: row.primary_company_id })}>
            <td>{formatDateLabel(row)}</td>
            <td><strong>{rowLabel(row)}</strong><small>{row.summary}</small></td>
            <td>{row.company_ids.map(id => lookups.companies.get(id)?.ticker || id).join(', ')}</td>
            <td>{lookups.sourceChannels.get(row.source_channel_id)?.label || row.source_channel_id}</td>
            <td>{rowDetail(row)}</td>
            <td>{row.lifecycle_state}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function SourceTable({ docs, lookups }) {
  return (
    <table>
      <thead><tr><th>Date</th><th>Source</th><th>Channel</th><th>Kind</th><th>Path</th></tr></thead>
      <tbody>
        {docs.map(doc => (
          <tr key={doc.id}>
            <td>{formatDateLabel(doc)}</td>
            <td><strong>{doc.title}</strong></td>
            <td>{lookups.sourceChannels.get(doc.source_channel_id)?.label || doc.source_channel_id}</td>
            <td>{doc.document_kind}</td>
            <td><code>{doc.canonical_path}</code></td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function ProfilePanel({ selection, company, edge, filtered, lookups }) {
  if (!selection) {
    return <aside className="profile empty"><h2>Select a company or shared-evidence edge</h2><p>Profile context will show source channels, rows, and provenance under current filters.</p></aside>
  }
  if (company) {
    const rows = filtered.rows.filter(row => row.company_ids.includes(company.id))
    const role = lookups.companyRoles.get(company.primary_role_id)
    const grouped = groupRowsByChannelAndType(rows)
    return (
      <aside className="profile">
        <p className="eyebrow">Company</p>
        <h2>{company.name}</h2>
        <div className="ticker">{company.ticker}</div>
        <dl>
          <dt>Role</dt><dd>{role?.label || company.primary_role_id}</dd>
          <dt>Rows</dt><dd>{rows.length}</dd>
          <dt>Sources</dt><dd>{company.source_document_ids.length}</dd>
        </dl>
        <TagList items={company.display_tags} />
        <h3>Why visible</h3>
        <p className="helperText">This company appears because current rows or source documents touch it under active filters.</p>
        {grouped.map(group => (
          <div className="profileGroup" key={group.key}>
            <strong>{lookups.sourceChannels.get(group.channel)?.label || group.channel} / {formatRowType(group.type)}</strong>
            <EvidenceList rows={group.rows.slice(0, 5)} lookups={lookups} />
          </div>
        ))}
      </aside>
    )
  }
  if (edge) {
    const [a, b] = edge.company_ids.map(id => lookups.companies.get(id))
    const supportRows = edge.support.flatMap(item => item.row_ids.map(id => ({ support: item, row: lookups.rows.get(id) }))).filter(item => item.row)
    return (
      <aside className="profile">
        <p className="eyebrow">Shared evidence</p>
        <h2>{a?.ticker || edge.company_ids[0]} &lt;-&gt; {b?.ticker || edge.company_ids[1]}</h2>
        <p className="warning">This edge reflects shared evidence under the current filters. It does not imply a directional supplier/customer relationship.</p>
        {edge.support.map((item, index) => (
          <div className="support" key={`${item.family}-${item.source_channel_id}-${index}`}>
            <strong>{formatRowType(item.family)}</strong>
            <span>{lookups.sourceChannels.get(item.source_channel_id)?.label || item.source_channel_id}</span>
            <em>{item.row_ids.length} rows / score {item.score}</em>
          </div>
        ))}
        <h3>Rows</h3>
        <EvidenceList rows={supportRows.map(item => item.row)} lookups={lookups} />
      </aside>
    )
  }
  return null
}

function EvidenceList({ rows, lookups }) {
  return (
    <div className="evidenceList">
      {rows.map(row => (
        <div className="evidenceItem" key={row.id}>
          <span>{formatDateLabel(row)}</span>
          <strong>{rowLabel(row)}</strong>
          <small>{lookups.sourceChannels.get(row.source_channel_id)?.label || row.source_channel_id}</small>
          <small>{row.source_document_ids.map(id => lookups.sourceDocuments.get(id)?.title || id).join(' | ')}</small>
        </div>
      ))}
    </div>
  )
}

function TagList({ items }) {
  if (!items || items.length === 0) return null
  return <div className="tags">{items.map(item => <span key={item}>{item}</span>)}</div>
}

function rowsForView(viewId, data, filtered) {
  if (viewId === 'sources') return filtered.sourceDocuments
  const view = data.tables.views[viewId]
  return sortRowsForView(filtered.rows
    .filter(row => row.row_type === view.row_type)
  )
}

function rowDetail(row) {
  if (row.row_type === 'position') return `${row.position_type} ${formatMoney(row.value)} ${formatPercent(row.pct_portfolio)}`
  if (row.row_type === 'signal') return row.impact_direction
  if (row.row_type === 'claim') return row.verification_window_label || row.verification_target || ''
  if (row.row_type === 'proposal') return row.proposal_type
  return ''
}

function groupRowsByChannelAndType(rows) {
  const groups = new Map()
  for (const row of rows) {
    const key = `${row.source_channel_id}:${row.row_type}`
    if (!groups.has(key)) groups.set(key, { key, channel: row.source_channel_id, type: row.row_type, rows: [] })
    groups.get(key).rows.push(row)
  }
  return [...groups.values()].sort((a, b) => a.key.localeCompare(b.key))
}

function layoutCompanies(companies, roles) {
  const roleById = new Map(roles.map(role => [role.id, role]))
  const byRank = new Map()
  for (const company of companies) {
    const rank = roleById.get(company.primary_role_id)?.rank ?? 8
    if (!byRank.has(rank)) byRank.set(rank, [])
    byRank.get(rank).push(company)
  }
  const ranks = [...byRank.keys()].sort((a, b) => a - b)
  const xForRank = new Map(ranks.map((rank, index) => [rank, 90 + index * (940 / Math.max(1, ranks.length - 1))]))
  const points = new Map()
  for (const [rank, list] of byRank) {
    list.sort((a, b) => a.ticker.localeCompare(b.ticker))
    const x = xForRank.get(rank)
    const step = 430 / Math.max(1, list.length)
    list.forEach((company, index) => {
      points.set(company.id, { x, y: 54 + step * index })
    })
  }
  return points
}
