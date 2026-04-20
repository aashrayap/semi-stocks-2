import { describe, expect, it } from 'vitest'
import { applyFilters, emptyFilters } from './logic.js'

const fixture = {
  facets: {
    source_channels: [
      { id: 'source-channel:baker', label: 'Baker' },
      { id: 'source-channel:semianalysis', label: 'SemiAnalysis' },
    ],
    company_roles: [
      { id: 'company-role:chip-designer', label: 'Chip designers', rank: 2 },
      { id: 'company-role:foundry', label: 'Foundry', rank: 1 },
    ],
    thesis_themes: [{ id: 'thesis-theme:n3', label: 'N3' }],
  },
  companies: [
    { id: 'company:NVDA', ticker: 'NVDA', name: 'NVIDIA', primary_role_id: 'company-role:chip-designer', secondary_role_ids: [], thesis_theme_ids: ['thesis-theme:n3'], source_document_ids: ['doc:baker'], source_channel_ids: ['source-channel:baker'], search_text: 'nvda nvidia' },
    { id: 'company:TSM', ticker: 'TSM', name: 'TSMC', primary_role_id: 'company-role:foundry', secondary_role_ids: [], thesis_theme_ids: ['thesis-theme:n3'], source_document_ids: ['doc:semi'], source_channel_ids: ['source-channel:semianalysis'], search_text: 'tsm tsmc foundry' },
  ],
  source_documents: [
    { id: 'doc:baker', source_channel_id: 'source-channel:baker', company_ids: ['company:NVDA'], timeline: { sort_date: '2026-02-17' }, search_text: 'baker nvda' },
    { id: 'doc:semi', source_channel_id: 'source-channel:semianalysis', company_ids: ['company:NVDA', 'company:TSM'], timeline: { sort_date: '2026-04-02' }, search_text: 'semianalysis gpu shortage' },
  ],
  rows: [
    { id: 'row:position:baker:nvda', row_type: 'position', title: 'Baker NVDA', company_ids: ['company:NVDA'], source_channel_id: 'source-channel:baker', source_document_ids: ['doc:baker'], thesis_theme_ids: ['thesis-theme:n3'], timeline: { sort_date: '2026-02-17' }, search_text: 'baker nvda position' },
    { id: 'row:signal:semi:nvda-tsm', row_type: 'signal', title: 'N3 shortage', company_ids: ['company:NVDA', 'company:TSM'], source_channel_id: 'source-channel:semianalysis', source_document_ids: ['doc:semi'], thesis_theme_ids: ['thesis-theme:n3'], timeline: { sort_date: null }, search_text: 'semianalysis n3 shortage tsm nvda' },
  ],
  graph: {
    edges: [
      { id: 'edge:company:NVDA__company:TSM', company_ids: ['company:NVDA', 'company:TSM'], visual_weight: 1, support: [{ family: 'shared_signal', source_channel_id: 'source-channel:semianalysis', score: 1, row_ids: ['row:signal:semi:nvda-tsm'] }] },
    ],
  },
  tables: { view_order: ['signals'], views: { signals: { row_type: 'signal' } } },
}

describe('applyFilters', () => {
  it('uses OR within a filter and AND across filters', () => {
    const result = applyFilters(fixture, {
      ...emptyFilters,
      source_channel_ids: ['source-channel:baker', 'source-channel:semianalysis'],
      company_role_ids: ['company-role:foundry'],
    })
    expect(result.rows.map(row => row.id)).toEqual(['row:signal:semi:nvda-tsm'])
    expect(result.companies.map(company => company.id)).toEqual(['company:TSM'])
  })

  it('keeps undated rows only when include_undated is true under timeline filtering', () => {
    const keep = applyFilters(fixture, {
      ...emptyFilters,
      timeline: { from: '2026-01-01', to: '2026-12-31' },
      include_undated: true,
    })
    const drop = applyFilters(fixture, {
      ...emptyFilters,
      timeline: { from: '2026-01-01', to: '2026-12-31' },
      include_undated: false,
    })
    expect(keep.rows.map(row => row.id)).toContain('row:signal:semi:nvda-tsm')
    expect(drop.rows.map(row => row.id)).not.toContain('row:signal:semi:nvda-tsm')
  })

  it('search intersects with source channel filters', () => {
    const result = applyFilters(fixture, {
      ...emptyFilters,
      search: 'foundry',
      source_channel_ids: ['source-channel:baker'],
    })
    expect(result.rows).toEqual([])
  })
})
