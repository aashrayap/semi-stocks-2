# semi-stocks

Second-iteration workspace for semi-stocks with clearer boundaries between canonical research, runtime code, sidecar agents, outputs, and docs.

Start here:
- Read [docs/architecture.md](docs/architecture.md) for the lane model and folder ownership.
- Read [docs/doc-contract.md](docs/doc-contract.md) for what belongs at repo root versus under `docs/`.
- Use [AGENTS.md](AGENTS.md) or [CLAUDE.md](CLAUDE.md) for agent routing.

## Top-Level Map

- `research/` — canonical knowledge lane
- `app/` — runtime and synthesis code
- `agents/` — sidecar automation and experiments
- `outputs/` — generated artifacts
- `docs/` — durable human docs
- `tmp/` — local scratch

This repo is intentionally scaffolded at a high level first. Detailed migration of legacy content is a separate step.

