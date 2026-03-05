"""Generate short-form video scripts for bookmarks using Claude API."""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from pattssun.config import Settings
from pattssun.models import Script

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "scriptwriter.md"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text()


def load_bookmarks(path: Path) -> dict[str, dict]:
    raw = json.loads(path.read_text())
    if isinstance(raw, list):
        return {entry["id"]: {k: v for k, v in entry.items() if k != "id"} for entry in raw}
    return raw


def save_bookmarks(path: Path, data: dict[str, dict]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def load_pending(pending_path: Path) -> list[str]:
    if not pending_path.exists():
        return []
    ids = [line.strip() for line in pending_path.read_text().splitlines() if line.strip()]
    return ids


def remove_from_pending(pending_path: Path, done_ids: set[str]) -> None:
    if not pending_path.exists():
        return
    remaining = [tid for tid in load_pending(pending_path) if tid not in done_ids]
    if remaining:
        pending_path.write_text("\n".join(remaining) + "\n")
    else:
        pending_path.unlink()


def generate_script(client: httpx.Client, api_key: str, system_prompt: str, tweet_text: str) -> dict | None:
    resp = client.post(
        CLAUDE_API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": tweet_text}],
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    content = resp.json()["content"][0]["text"].strip()
    if content == "null":
        return None
    return json.loads(content)


def run(settings: Settings | None = None, dry_run: bool = False) -> None:
    if settings is None:
        settings = Settings()

    bookmarks_path = settings.bookmarks_path
    if not bookmarks_path.is_absolute():
        bookmarks_path = Path.cwd() / bookmarks_path

    if not bookmarks_path.exists() or bookmarks_path.stat().st_size == 0:
        print(f"No bookmarks file at {bookmarks_path}")
        return

    pending_path = bookmarks_path.parent / ".pending"
    pending_ids = load_pending(pending_path)

    if not pending_ids:
        print("No pending bookmarks to script.")
        return

    data = load_bookmarks(bookmarks_path)
    system_prompt = load_system_prompt()

    # Filter to IDs that exist, have text, and don't already have a script
    to_process = {
        tid: data[tid]
        for tid in pending_ids
        if tid in data and data[tid].get("text", "").strip() and data[tid].get("script") is None
    }

    if not to_process:
        print("All pending bookmarks already scripted or have no text.")
        remove_from_pending(pending_path, set(pending_ids))
        return

    print(f"Scripting {len(to_process)} new bookmarks.")

    if dry_run:
        for tid, entry in to_process.items():
            preview = entry["text"][:80].replace("\n", " ")
            print(f"  [DRY RUN] {tid}: @{entry.get('author_username', '?')} — {preview}")
        return

    done_ids: set[str] = set()
    generated = 0
    with httpx.Client() as client:
        for tid, entry in to_process.items():
            tweet_text = entry["text"]
            username = entry.get("author_username", "?")
            preview = tweet_text[:60].replace("\n", " ")
            print(f"  Generating script for {tid} (@{username}): {preview}...")

            try:
                script_data = generate_script(client, settings.anthropic_api_key, system_prompt, tweet_text)
                if script_data is not None:
                    Script(**script_data)
                    data[tid]["script"] = script_data
                    generated += 1
                    print(f"    -> {script_data['clip_count']} clips, {script_data['total_duration_seconds']}s")
                else:
                    print(f"    -> Skipped (empty/unsuitable content)")
                done_ids.add(tid)
            except Exception as e:
                print(f"    -> Error: {e}")

            time.sleep(1)

    save_bookmarks(bookmarks_path, data)
    remove_from_pending(pending_path, done_ids)
    print(f"\nDone. Generated {generated} scripts, saved to {bookmarks_path}")


if __name__ == "__main__":
    run()
