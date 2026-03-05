"""One-time migration: convert bookmarks.json from array format to object format keyed by tweet ID."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from pattssun.config import Settings


def migrate(bookmarks_path: Path | None = None) -> None:
    if bookmarks_path is None:
        settings = Settings()
        bookmarks_path = settings.bookmarks_path
        if not bookmarks_path.is_absolute():
            bookmarks_path = Path.cwd() / bookmarks_path

    if not bookmarks_path.exists():
        print(f"No bookmarks file at {bookmarks_path}")
        return

    raw = json.loads(bookmarks_path.read_text())

    if isinstance(raw, dict):
        print("Already in object format. Nothing to do.")
        return

    if not isinstance(raw, list):
        print(f"Unexpected format: {type(raw)}")
        return

    # Back up original
    backup = bookmarks_path.with_suffix(".json.bak")
    shutil.copy2(bookmarks_path, backup)
    print(f"Backed up to {backup}")

    # Convert: array -> object keyed by id
    obj = {}
    for entry in raw:
        tid = entry.pop("id")
        obj[tid] = entry

    bookmarks_path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
    print(f"Migrated {len(obj)} bookmarks to object format.")


if __name__ == "__main__":
    migrate()
