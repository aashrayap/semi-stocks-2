---
status: approved
feature: daily
---

# Research Questions: daily

## Codebase

### Agent Scripts & Config
1. What CLI arguments does each script in `agents/src/` accept? Document every `argparse` flag, its type, default value, and what it controls.
2. How does `agents/src/daily_runner.py` discover and invoke the individual agent scripts? What is the exact sequence, error handling, and exit behavior?
3. What does `agents/config.yaml` contain? Document the full structure: keys, nesting, what each section controls, and which scripts read which sections.
4. How does `agents/src/report.py` build its HTML output? What data sources does it read, what sections does it render, and where does it write?
5. What is the schema of prediction YAML files in `agents/state/predictions/`? Show a real example with all fields.
6. What is the schema of `agents/state/transcripts.yaml`? Does it exist? If so, show its structure.

### Canonical Lanes
7. What is the exact structure of `canonical/30-thesis/thesis.yaml`? Document all top-level keys, per-ticker fields, and how earnings dates, forward claims, and bottleneck assignments are represented.
8. How do scripts in `agents/src/` resolve paths to canonical lanes? What does `runtime_paths.py` export and how do callers use it?
9. What files exist under `canonical/20-data/sources/` and `canonical/20-data/companies/`? What is the YAML schema for each?

### Trigger Infrastructure
10. How are the 4 existing Claude Code Remote Triggers configured? What are their exact prompts, cron expressions, environment variables, setup scripts, and tool permissions?
11. What branch do existing triggers push to? Do they push directly to main or to a feature branch?
12. What is the commit/push pattern used by existing triggers? Do they stage specific files or `git add -A`?

## Docs

13. What does `docs/process/earnings-pipeline.md` describe as the intended agent flow? How does it differ from what's actually implemented?
14. What does `docs/process/agent-scheduler.md` document about runtime conditions and the launchd setup?
15. What does `docs/process/13f-pipeline-design.md` specify for the 13F monitoring approach? What libraries, APIs, and data flows are described?

## Patterns

16. What logging pattern do agent scripts use? Format, log file naming, rotation, and how the report reads them.
17. What is the signal/finding output format used by `agents/reports/daily-2026-04-07.md`? What fields does each finding have?
18. How do agent scripts handle network failures? What retry/fallback patterns exist in `transcript_fetcher.py`?
19. What deduplication or state-tracking patterns exist across agent scripts? How does the system know what has already been processed?

## External

20. What is the Claude Code Remote Trigger API? How are triggers created, updated, listed, and run? What are the configuration options (cron, env vars, setup script, tools, model, branch permissions)?
21. What does `newsletter.semianalysis.com` expose publicly? Is there an RSS feed, public article listing, or API?
22. What does SEC EDGAR's EFTS full-text search API (`efts.sec.gov/LATEST/search-index`) support? What query parameters, rate limits, and response formats?
23. What do the 13F aggregator sites (WhaleWisdom, InsideArbitrage, HedgeFollow, StockZoa, 13F.info) expose that can be programmatically accessed? RSS, API, or structured pages?
24. What does Finviz expose publicly for screening data? Free tier endpoints, screener URL patterns, export formats?
25. What does Google web search return when queried via Claude Code's `WebSearch` tool? Format, result count, snippet structure?

## Cross-Ref

26. Do any existing agent scripts already produce signal/finding output that matches what the new source monitors would produce? Is there an existing format to standardize on?
27. How do the existing remote triggers interact with each other? Do later triggers depend on artifacts committed by earlier ones?
28. What is the overlap between `agents/reports/daily-2026-04-07.md` source citations and the sources listed in `canonical/20-data/sources/`? Which sources appear in daily reports but not in canonical data?
29. What Python dependencies does the repo currently declare in `pyproject.toml`? What additional libraries would be needed for web scraping, RSS parsing, or API calls?
30. How does the existing `canonical/40-engine/` synthesis code reference Baker, Leopold, and SemiAnalysis data? Does it pull from `canonical/20-data/sources/` or directly from agent artifacts?
