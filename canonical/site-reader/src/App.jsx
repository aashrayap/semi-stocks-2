import { useEffect, useMemo, useState } from 'react'
import {
  applyFilters,
  createLookups,
  emptyFilters,
  formatDateLabel,
  formatMoney,
  formatPercent,
  rowLabel,
} from './logic.js'

const EDGE_LIMIT = 180

export default function App() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState(emptyFilters)
  const [openFilter, setOpenFilter] = useState(null)
  const [tableView, setTableView] = useState('signals')
  const [selection, setSelection] = useState(null)

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
    if (selection.type === 'edge' && !filtered.graphEdges.some(edge => edge.id === selection.id)) setSelection(null)
  }, [filters, filtered, selection])

  if (error) return <div className="page"><div className="error">{error}</div></div>
  if (!data || !filtered || !lookups) return <div className="page"><div className="loading">Loading Signal Desk</div></div>

  const tableRows = rowsForView(tableView, data, filtered)
  const visibleEdges = filtered.graphEdges.slice(0, EDGE_LIMIT)
  const selectedCompany = selection?.type === 'company' ? lookups.companies.get(selection.id) : null
  const selectedEdge = selection?.type === 'edge' ? filtered.graphEdges.find(edge => edge.id === selection.id) : null

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
        </FilterMenu>
        <button className="ghostButton" onClick={() => { setFilters(emptyFilters); setSelection(null) }}>Clear</button>
      </section>

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
            companies={filtered.graphCompanies}
            edges={visibleEdges}
            lookups={lookups}
            roles={data.facets.company_roles}
            selection={selection}
            onSelect={setSelection}
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

function Graph({ companies, edges, lookups, roles, selection, onSelect }) {
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
        <span>{companies.length} nodes / {edges.length} visible edges</span>
      </div>
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
      <thead><tr><th>Date</th><th>Evidence</th><th>Companies</th><th>Source</th><th>State</th></tr></thead>
      <tbody>
        {rows.map(row => (
          <tr key={row.id} onClick={() => row.primary_company_id && onSelect({ type: 'company', id: row.primary_company_id })}>
            <td>{formatDateLabel(row)}</td>
            <td><strong>{rowLabel(row)}</strong><small>{row.summary}</small></td>
            <td>{row.company_ids.map(id => lookups.companies.get(id)?.ticker || id).join(', ')}</td>
            <td>{lookups.sourceChannels.get(row.source_channel_id)?.label || row.source_channel_id}</td>
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
    const rows = filtered.rows.filter(row => row.company_ids.includes(company.id)).slice(0, 14)
    const role = lookups.companyRoles.get(company.primary_role_id)
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
        <h3>Evidence</h3>
        <EvidenceList rows={rows} lookups={lookups} />
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
            <strong>{item.family}</strong>
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
  return filtered.rows
    .filter(row => row.row_type === view.row_type)
    .sort((a, b) => (b.timeline.sort_date || '').localeCompare(a.timeline.sort_date || ''))
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
