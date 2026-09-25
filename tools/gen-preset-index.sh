#!/bin/bash
# Generates app/src/main/assets/presets.idx: the sorted list of bundled presets.
# The app reads this one small file at startup instead of listing ~10k assets, which is slow and
# holds Android's asset-manager lock (blocking UI inflation) while it runs.
#   tools/gen-preset-index.sh          regenerate
#   tools/gen-preset-index.sh --check  fail if the committed index is out of date (used by CI)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIR="$ROOT/app/src/main/assets/presets"
OUT="$ROOT/app/src/main/assets/presets.idx"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
(cd "$DIR" && ls -1) | grep -i '\.milk$' | LC_ALL=C sort > "$TMP"
if [ "${1:-}" = "--check" ]; then
    if ! cmp -s "$TMP" "$OUT"; then
        echo "presets.idx is out of date: run tools/gen-preset-index.sh and commit the result" >&2
        diff "$OUT" "$TMP" | head -20 >&2 || true
        exit 1
    fi
    echo "presets.idx is up to date ($(wc -l < "$OUT" | tr -d ' ') presets)"
else
    mv "$TMP" "$OUT"
    trap - EXIT
    echo "Wrote $OUT ($(wc -l < "$OUT" | tr -d ' ') presets)"
fi
