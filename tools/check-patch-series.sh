#!/bin/bash
# Applies every patch in tools/projectm-patches, in order, to a clean export of the pinned projectM
# (and its projectm-eval submodule), as preset-lab and a fresh clone do. Exit 1 names the first failure.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
git -C "$ROOT/third_party/projectm" archive HEAD | tar -x -C "$WORK"
git -C "$ROOT/third_party/projectm/vendor/projectm-eval" archive --prefix=vendor/projectm-eval/ HEAD | tar -x -C "$WORK"
for patch in "$ROOT"/tools/projectm-patches/*.patch; do
    (cd "$WORK" && GIT_CEILING_DIRECTORIES="$WORK/.." git apply "$patch") || { echo "FAIL $(basename "$patch")"; exit 1; }
done
echo "all $(ls "$ROOT"/tools/projectm-patches/*.patch | wc -l | tr -d ' ') patches apply"
