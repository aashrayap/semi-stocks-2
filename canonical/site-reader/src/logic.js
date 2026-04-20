export const emptyFilters = {
  search: '',
  source_channel_ids: [],
  company_role_ids: [],
  thesis_theme_ids: [],
  timeline: { from: null, to: null },
  include_undated: true,
}

export function createLookups(data) {
  return {
    companies: new Map(data.companies.map(company => [company.id, company])),
    rows: new Map(data.rows.map(row => [row.id, row])),
    sourceDocuments: new Map(data.source_documents.map(doc => [doc.id, doc])),
    sourceChannels: new Map(data.facets.source_channels.map(channel => [channel.id, channel])),
    companyRoles: new Map(data.facets.company_roles.map(role => [role.id, role])),
    thesisThemes: new Map(data.facets.thesis_themes.map(theme => [theme.id, theme])),
  }
}

export function applyFilters(data, filters = emptyFilters) {
  const lookups = createLookups(data)
  const selectedChannels = new Set(filters.source_channel_ids || [])
  const selectedRoles = new Set(filters.company_role_ids || [])
  const selectedThemes = new Set(filters.thesis_theme_ids || [])
  const q = (filters.search || '').trim().toLowerCase()
  const timelineActive = Boolean(filters.timeline?.from || filters.timeline?.to)

  const companyRolePass = company => {
    if (selectedRoles.size === 0) return true
    if (selectedRoles.has(company.primary_role_id)) return true
    return (company.secondary_role_ids || []).some(role => selectedRoles.has(role))
  }

  const timelinePass = item => {
    if (!timelineActive) return true
    const sortDate = item.timeline?.sort_date
    if (!sortDate) return Boolean(filters.include_undated)
    if (filters.timeline.from && sortDate < filters.timeline.from) return false
    if (filters.timeline.to && sortDate > filters.timeline.to) return false
    return true
  }

  const textPass = item => !q || (item.search_text || '').toLowerCase().includes(q)

  const docPassBase = doc => {
    if (selectedChannels.size && !selectedChannels.has(doc.source_channel_id)) return false
    if (!timelinePass(doc)) return false
    if (q && !textPass(doc)) return false
    return true
  }

  const visibleSourceDocuments = data.source_documents.filter(docPassBase)
  const visibleDocIds = new Set(visibleSourceDocuments.map(doc => doc.id))

  const rowPass = row => {
    if (selectedChannels.size && !selectedChannels.has(row.source_channel_id)) return false
    if (selectedThemes.size && !(row.thesis_theme_ids || []).some(id => selectedThemes.has(id))) return false
    if (!timelinePass(row)) return false
    const linkedCompanies = (row.company_ids || []).map(id => lookups.companies.get(id)).filter(Boolean)
    if (selectedRoles.size && !linkedCompanies.some(companyRolePass)) return false
    if (q) {
      const rowMatches = textPass(row)
      const companyMatches = linkedCompanies.some(textPass)
      const docMatches = (row.source_document_ids || [])
        .map(id => lookups.sourceDocuments.get(id))
        .filter(Boolean)
        .some(textPass)
      if (!rowMatches && !companyMatches && !docMatches) return false
    }
    return true
  }

  const visibleRows = data.rows.filter(rowPass)
  const visibleRowIds = new Set(visibleRows.map(row => row.id))

  const rowCompanyIds = new Set()
  for (const row of visibleRows) for (const companyId of row.company_ids || []) rowCompanyIds.add(companyId)
  const docCompanyIds = new Set()
  for (const doc of visibleSourceDocuments) for (const companyId of doc.company_ids || []) docCompanyIds.add(companyId)

  const companyPass = company => {
    if (!companyRolePass(company)) return false
    if (selectedThemes.size && !(company.thesis_theme_ids || []).some(id => selectedThemes.has(id)) && !rowCompanyIds.has(company.id)) return false
    if (q) {
      const ownMatch = textPass(company)
      const rowMatch = rowCompanyIds.has(company.id)
      const docMatch = docCompanyIds.has(company.id)
      if (!ownMatch && !rowMatch && !docMatch) return false
    }
    return rowCompanyIds.has(company.id) || docCompanyIds.has(company.id)
  }

  const visibleCompanies = data.companies.filter(companyPass)
  const visibleCompanyIds = new Set(visibleCompanies.map(company => company.id))

  const visibleEdges = data.graph.edges
    .map(edge => {
      if (!edge.company_ids.every(id => visibleCompanyIds.has(id))) return null
      const support = edge.support
        .map(item => {
          if (selectedChannels.size && !selectedChannels.has(item.source_channel_id)) return null
          const rowIds = item.row_ids.filter(id => visibleRowIds.has(id))
          if (rowIds.length === 0) return null
          return { ...item, row_ids: rowIds }
        })
        .filter(Boolean)
      if (support.length === 0) return null
      return {
        ...edge,
        support,
        visual_weight: round(support.reduce((sum, item) => sum + item.score, 0)),
      }
    })
    .filter(Boolean)
    .sort((a, b) => b.visual_weight - a.visual_weight || a.id.localeCompare(b.id))

  const edgeCompanyIds = new Set()
  for (const edge of visibleEdges) for (const companyId of edge.company_ids) edgeCompanyIds.add(companyId)
  const graphCompanies = visibleCompanies
    .filter(company => edgeCompanyIds.has(company.id) || rowCompanyIds.has(company.id))
    .sort((a, b) => a.name.localeCompare(b.name))

  return {
    lookups,
    rows: visibleRows,
    rowIds: visibleRowIds,
    sourceDocuments: visibleSourceDocuments,
    sourceDocumentIds: visibleDocIds,
    companies: visibleCompanies,
    companyIds: visibleCompanyIds,
    graphCompanies,
    graphEdges: visibleEdges,
  }
}

export function rowLabel(row) {
  return row.title || row.summary || row.id
}

export function formatDateLabel(item) {
  return item?.timeline?.label || 'Undated'
}

export function formatMoney(value) {
  if (value == null) return ''
  const n = Number(value)
  if (!Number.isFinite(n)) return ''
  if (Math.abs(n) >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(2)}B`
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(0)}M`
  return `$${n.toLocaleString()}`
}

export function formatPercent(value) {
  if (value == null) return ''
  const n = Number(value)
  if (!Number.isFinite(n)) return ''
  return `${(n * 100).toFixed(1)}%`
}

function round(value) {
  return Math.round(value * 1_000_000) / 1_000_000
}
