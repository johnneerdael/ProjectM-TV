#!/bin/bash
# Rewrites tools/projectm-patches/<name> from the unstaged changes in third_party/projectm, keeping the
# patch's header (its lines up to the first "---"). The patches before it must be applied and staged
# (git -C third_party/projectm add -A); new files are added with intent-to-add so the diff shows them.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PATCH="$ROOT/tools/projectm-patches/$1"
SUB="$ROOT/third_party/projectm"
git -C "$SUB" add -N -- src tests
HEADER=""
if [ -f "$PATCH" ]; then HEADER="$(sed -n '1,/^---$/p' "$PATCH")"; fi
DIFF="$(git -C "$SUB" diff)"
if [ -z "$DIFF" ]; then echo "no changes in $SUB" >&2; exit 1; fi
{ if [ -n "$HEADER" ]; then printf '%s\n' "$HEADER"; fi; printf '%s\n' "$DIFF"; } > "$PATCH.tmp"
mv "$PATCH.tmp" "$PATCH"
echo "wrote $PATCH ($(grep -c '^diff --git' "$PATCH") files)"
