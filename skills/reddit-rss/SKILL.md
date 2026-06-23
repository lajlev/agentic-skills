# Reddit RSS Skill

Use this skill when the user wants recurring or on-demand updates from `https://www.reddit.com/r/boardgames.rss`.

## Trigger
- User asks for daily/recurring `/r/boardgames` updates.
- User asks for recent posts from Reddit via RSS.
- User wants a lightweight summary without API tokens.

## Requirements
- Python (`python3` preferred; `.venv/bin/python` optional)
- No API token required.

## Workflow
1. Run `python3 skills/reddit-rss/scripts/reddit_rss_summary.py`.
2. Set `--limit` based on requested summary size.
3. If needed, filter to recent items with `--hours`.
4. Use `--format markdown --timezone Europe/Copenhagen` for cleaner scheduled output.
5. Return concise bullets with short title, local publish time, and link.

## Commands
- Latest 10 posts:
  - `python3 skills/reddit-rss/scripts/reddit_rss_summary.py --limit 10 --format markdown --timezone Europe/Copenhagen`
- Last 24 hours:
  - `python3 skills/reddit-rss/scripts/reddit_rss_summary.py --hours 24 --limit 12 --format markdown --timezone Europe/Copenhagen`
- Raw-style JSON output:
  - `python3 skills/reddit-rss/scripts/reddit_rss_summary.py --limit 10 --json`

## Recommended Schedule Prompt
Use this for `reddit-boardgames-weekday-0800`:

`Run python3 skills/reddit-rss/scripts/reddit_rss_summary.py --hours 24 --limit 8 --format markdown --timezone Europe/Copenhagen --title-max 80. Then send only the final summary in Danish with this structure: short one-line intro, top 5 hottest posts section, 3 more interesting posts section, and one "Hvad vil du dykke ned i i aften?" question. No technical logs or setup details.`

## Safety
- Use low-frequency polling for scheduled jobs.
- Respect RSS source availability; fail gracefully on network errors.
