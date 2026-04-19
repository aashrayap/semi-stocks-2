# agents/

Automated agents are sidecar workers for `semi-stocks-2`.

## Response Contract

Follow the root [CLAUDE.md](../CLAUDE.md) human response contract for
non-trivial work: `Result`, `Visual`, `Gate`, `Ledger`, concrete
`Next Actions`, and `Details` links.

## Boundary

- Read: `canonical/`, root `config.yaml`, and repo docs.
- Write: `agents/` only.
- Promotion: a human decides what moves from sidecar output into canonical lanes.

## Read First

- `canonical/30-thesis/thesis.yaml` for control-plane state.
- `config.yaml` for tracked tickers and sources.
- `canonical/10-wiki/schema.md` before wiki-aware analysis.
- `docs/process/agent-scheduler.md` for unattended runtime.
- `docs/process/trigger-setup.md` for Claude Code Remote Trigger setup.

## Runtime

- Use `uv run python agents/src/<script>.py ...`.
- Daily sidecar flow: `uv run python agents/src/daily_runner.py`.
- Local scheduler install: `uv run python agents/src/install_launchd.py --hour 6 --minute 5 --load`.
- Remote trigger prompt: `agents/trigger-prompt.md`.

## Outputs

- Reports: `agents/reports/`.
- Drafts: `agents/drafts/`.
- Logs: `agents/logs/`.
- State: `agents/state/`.

Agent reports and drafts are proposals. They do not replace `canonical/50-reports/` or `canonical/30-thesis/thesis.yaml`.
