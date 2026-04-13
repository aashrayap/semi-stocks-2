# Agent Scheduler

Date: 2026-04-10

## Primary: Claude Code Remote Trigger

The primary execution path is the `hourly-market-intel` Claude Code Remote Trigger running on Anthropic's cloud infrastructure.

- **Schedule:** Hourly during US market hours — `0 13-21 * * 1-5` UTC (8 AM - 4 PM ET, weekdays)
- **Execution:** ~9 runs per trading day, fresh repo clone each run
- **What it does each run:**
  1. Earnings pipeline (first run of day only): calendar, predictions, transcripts, report
  2. Source monitoring (every run): per-ticker web search, SemiAnalysis RSS, analyst searches, SEC EDGAR 13F (weekly), financial news
  3. Signal output: writes to `agents/state/signals/YYYY-MM-DD.yaml`
  4. Commits to `claude/daily-signals` branch, creates/updates daily PR

- **No Mac dependency** — runs on Anthropic cloud regardless of laptop state
- **Setup:** See `docs/process/trigger-setup.md` for configuration instructions
- **Trigger prompt:** See `agents/trigger-prompt.md`

## Local Backup: launchd

The local launchd job serves as a backup for the earnings pipeline only.

`launchd -> uv run python agents/src/daily_runner.py`

The runner executes:

1. `agents/src/earnings_calendar.py`
2. `agents/src/pre_earnings_predictor.py --all-upcoming`
3. `agents/src/transcript_fetcher.py --all-due`
4. `agents/src/report.py`

`agents/src/post_earnings_scorer.py` is excluded because it is interactive and requires manual scoring input.

## Installed Local Schedule

The local installer writes `~/Library/LaunchAgents/com.ash.semi-stocks-agents.daily.plist`.

Default schedule:

- daily at `06:05` local time

Install or update it with:

```bash
uv run python agents/src/install_launchd.py --hour 6 --minute 5 --load
```

Kick off an immediate run after install:

```bash
uv run python agents/src/install_launchd.py --hour 6 --minute 5 --load --run-now
```

## Conditions For Auto Runs

- Your macOS user session must be logged in so the `LaunchAgent` is loaded.
- The Mac must be awake at the scheduled time. If the laptop is asleep, the job will not run while asleep.
- The computer does not need to be physically open if it stays awake and your session remains loaded.
- Network access must be available for transcript fetch attempts. The other sidecar steps can still run if transcript fetches find nothing due.
- The repo path and the `uv` binary path used at install time must still exist.

## Outputs

- consolidated runner log: `agents/logs/daily-runner-YYYY-MM.log`
- launchd stdout/stderr mirrors: `agents/logs/launchd-daily.stdout.log`, `agents/logs/launchd-daily.stderr.log`
- sidecar HTML report: `agents/reports/latest.html`
- sidecar drafts/state/logs remain under `agents/`
