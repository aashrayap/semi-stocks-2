# Deep-Dive Rollout Checklist

Date frozen: 2026-04-08
Source rollout: `docs/process/deep-dive-rollout-spec.md`

## Checklist

1. Lock the latest reported quarter for the ticker and confirm the exact earnings date.
2. Capture primary-source artifacts in `canonical/10-wiki/raw/`:
   - earnings release
   - prepared remarks / transcript / SEC filing
   - one or more AI-relevant product or partnership artifacts if thesis relevance depends on them
3. Build `canonical/10-wiki/sources/<ticker>-<quarter>.md` with:
   - key metrics table
   - management guidance
   - bottleneck mapping
   - fund positioning context
   - cross-links to the structured YAML and concept pages
4. Build `canonical/20-data/companies/<TICKER>/<quarter>.yaml` with:
   - `financials`
   - `forward_claims`
   - `thesis_signals`
   - `positioning`
   - trade-relevant `business` and `thesis_relevance` context
   - `source_artifacts` so claims can be traced back to raw evidence
5. Rebuild the report with `uv run python canonical/40-engine/report.py`.
6. Verify the ticker appears in `canonical/50-reports/latest.html` under the earnings dashboard.
7. Only after the report delta is visible, mark the tracked backlog or migration item complete.
