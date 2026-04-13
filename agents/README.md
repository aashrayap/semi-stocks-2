# agents/ — Automated Agent Fleet

Automated agents monitor the canonical semi-stocks repo and produce parallel reports, alerts, and draft analyses for human review.

## Boundary Rules

| Access | Scope |
|---|---|
| **Read** | Canonical state under `canonical/`, root `config.yaml`, and repo docs |
| **Write** | `agents/` only |

## Relationship to Canonical State

- Agent reports in `agents/reports/` run parallel to human reports in `canonical/50-reports/`.
- Agent drafts in `agents/drafts/` are proposals. A human reviews before promoting content into canonical lanes.
- Agents read `canonical/30-thesis/thesis.yaml` and `config.yaml` as their main control inputs.

## Structure

```text
agents/
  CLAUDE.md
  README.md
  config.yaml
  src/
  autoagent/
  reports/
  drafts/
  logs/
  state/
```

## Runtime

- Use `uv run python agents/src/<script>.py ...`.
- Use `uv run python agents/src/daily_runner.py` for the unattended daily sidecar flow.
- Use `uv run python agents/src/install_launchd.py --hour 6 --minute 5 --load` to install the local macOS scheduler.
- Canonical read paths live under `canonical/10-wiki/`, `canonical/20-data/`, and `canonical/30-thesis/`.
- Agent writes remain under `agents/`.
- Runtime conditions for unattended runs are documented in `docs/process/agent-scheduler.md`.

## Remote Trigger (Primary)

The `hourly-market-intel` Claude Code Remote Trigger runs on Anthropic cloud during market hours.
It executes the earnings pipeline (once/day) and source monitoring (hourly), then commits signals
and opens a daily PR.

- Trigger prompt: `agents/trigger-prompt.md`
- Signal output: `agents/state/signals/YYYY-MM-DD.yaml`
- Signal schema: `agents/state/signals/schema.md`
- Setup instructions: `docs/process/trigger-setup.md`
- Trigger log: `agents/logs/hourly-intel-YYYY-MM.log`
