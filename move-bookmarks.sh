#!/bin/bash
# Merges bookmarks.json from Downloads into pattssun/bookmarks/bookmarks.json
# Format: object keyed by tweet ID (preserves existing scripts on merge)
SRC="$HOME/Downloads"
MASTER="$HOME/GitHub/pattssun/bookmarks/bookmarks.json"
PENDING="$HOME/GitHub/pattssun/bookmarks/.pending"
VENV="$HOME/GitHub/pattssun/.venv/bin/python"

if [ -f "$SRC/bookmarks.json" ]; then
  # Extract incoming IDs and append to .pending queue
  jq -r 'if type == "array" then .[].id else keys[] end' "$SRC/bookmarks.json" >> "$PENDING"

  if [ -f "$MASTER" ] && [ -s "$MASTER" ]; then
    # Merge: convert incoming array to object, then overlay onto master
    # Master wins via `*` so existing scripts are preserved
    jq --slurpfile incoming "$SRC/bookmarks.json" '
      . as $master |
      ($incoming[0] |
        if type == "array" then
          reduce .[] as $item ({}; . + {($item.id): ($item | del(.id))})
        else
          .
        end
      ) as $new |
      $new * $master
    ' "$MASTER" > "$MASTER.tmp"

    # Safety: only replace if output is non-empty
    if [ -s "$MASTER.tmp" ]; then
      mv -f "$MASTER.tmp" "$MASTER"
    else
      echo "ERROR: merge produced empty file, keeping original"
      rm -f "$MASTER.tmp"
      exit 1
    fi
  else
    mkdir -p "$(dirname "$MASTER")"
    # Convert array to object if needed
    jq 'if type == "array" then
      reduce .[] as $item ({}; . + {($item.id): ($item | del(.id))})
    else . end' "$SRC/bookmarks.json" > "$MASTER"
  fi
  rm "$SRC/bookmarks.json"
  echo "Merged bookmarks.json and deleted from Downloads"

  # Auto-generate scripts for new bookmarks
  cd "$HOME/GitHub/pattssun" && "$VENV" -m pattssun.steps.generate_scripts
fi
