# pattssun — Creative Pipeline Toolkit

## Project Structure
```
src/pattssun/
  cli.py              — Typer CLI: `pattssun bookmarks`, `pattssun generate`
  config.py            — Settings (pydantic-settings, reads .env)
  models.py            — Pydantic models: Tweet, Clip, Script, ScrapedBookmark
  prompts/
    scriptwriter.md    — System prompt for video script generation
  steps/
    fetch_bookmarks.py — Fetch bookmarks from X API
    generate_scripts.py — Generate video scripts via Claude API
    migrate_bookmarks.py — One-time array→object migration
extension/             — Chrome extension for scraping X bookmarks
bookmarks/
  bookmarks.json       — Master bookmarks file (object keyed by tweet ID)
move-bookmarks.sh      — LaunchAgent-triggered merge + script generation
```

## Key Commands
```bash
source .venv/bin/activate
pattssun bookmarks --save       # Fetch & save bookmarks from X API
pattssun generate               # Generate scripts for all unscripted bookmarks
pattssun generate --dry-run     # Preview which bookmarks need scripts
python -m pattssun.steps.migrate_bookmarks  # One-time: array → object format
python -m pattssun.steps.generate_scripts   # Direct script generation
```

## Data Format
`bookmarks.json` is an object keyed by tweet ID:
```json
{
  "2022010411340771420": {
    "author_username": "signulll",
    "text": "...",
    "tweet_url": "...",
    "scraped_at": "...",
    "script": { "total_duration_seconds": 45, "clip_count": 9, "clips": [...] }
  }
}
```

## Conventions
- Python 3.12+, Pydantic v2, httpx for HTTP
- Settings via pydantic-settings + `.env`
- Scripts live in `src/pattssun/steps/`
- Each step module has a `run()` function and is also runnable via `__main__`
