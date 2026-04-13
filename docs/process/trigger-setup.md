# Trigger Setup: hourly-market-intel

Date: 2026-04-13

## Create the Trigger

Via Claude Code CLI:
```
/schedule
```
Or via the Claude Code web UI at claude.ai/code → Scheduled Tasks.

## Configuration

| Setting | Value |
|---|---|
| Name | `hourly-market-intel` |
| Cron | `0 13-21 * * 1-5` |
| Cron (human) | Hourly, 8 AM - 4 PM ET, weekdays |
| Model | opus |
| Repository | `aashrayap/semi-stocks-2` |
| Branch permissions | Allow pushes to `claude/daily-signals` |
| Setup script | `pip install pyyaml beautifulsoup4 pdfplumber` |
| Tools | Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch |
| Prompt | Contents of `agents/trigger-prompt.md` |

## Environment Variables

None required — all monitored sources are public. If Twitter/X API access is added later, add:
- `TWITTER_BEARER_TOKEN` — Twitter API v2 bearer token

## After Setup

1. Verify the trigger runs successfully by using `/schedule run` or the web UI "Run now" button
2. Check the PR at `github.com/aashrayap/semi-stocks-2/pulls` for the first `[signals]` PR
3. Check `agents/state/signals/` for the first signal file
4. Check `agents/logs/hourly-intel-YYYY-MM.log` for the trigger's activity log

## Retiring Old Triggers

After verifying `hourly-market-intel` works for 2-3 days:

1. Disable `daily-briefing` trigger (its work is now covered by the earnings pipeline in Part A)
2. Disable `earnings-calendar` trigger (covered by Part A)
3. Disable `predictor-and-transcript-fetcher` trigger (covered by Part A)
4. Optionally enable `13F Filing Monitor` — or leave it disabled since 13F checks are now in Part B (weekly on Mondays)

## Troubleshooting

- **Trigger doesn't run:** Check cron expression — `0 13-21 * * 1-5` is UTC. Adjust if your timezone offset changes (DST).
- **Python import errors:** Setup script may have failed. Check if `pip install` ran in the setup phase.
- **PR creation fails:** Ensure the repo has branch permissions for `claude/daily-signals`. Check `gh auth status` in the trigger.
- **No signals found:** Normal on quiet days. The trigger only creates a PR if there are new findings.
- **Earnings pipeline runs every hour:** Check that `agents/logs/daily-runner-YYYY-MM.log` is being committed. The daily check reads from the committed log file.
