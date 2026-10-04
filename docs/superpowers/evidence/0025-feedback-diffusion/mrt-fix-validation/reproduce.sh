#!/bin/bash
# Re-runs this experiment in a NEW epoch directory.
#
# build_mrt_fix.py and run.py are the exact adapters that produced results.json (their SHA256s are
# recorded there), so they are not edited to run in place. They resolve the repository root from
# their execution depth, build/native-4k-current-main/<epoch>/, and write their outputs beside
# themselves. This launcher checks their hashes and the prerequisites, copies them unchanged to a new
# epoch at that depth, and runs them there.
#
# Usage: reproduce.sh [--check] <new-epoch-name>
#   --check  verify hashes and prerequisites only; build nothing and touch no device.
# PROJECTM_ROOT selects the checkout whose build/native-4k-current-main tree holds the prerequisites
# (default: this checkout).
#
# The run installs and renders on emulator-5582 only, after its own launch-identity and lease guards.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${PROJECTM_ROOT:-$(git -C "$HERE" rev-parse --show-toplevel)}"
CHECK=0
if [ "${1:-}" = "--check" ]; then CHECK=1; shift; fi
EPOCH="${1:?usage: reproduce.sh [--check] <new-epoch-name>}"
BASE="$ROOT/build/native-4k-current-main"
DEST="$BASE/$EPOCH"
PY="$ROOT/build/preset-lab-venv/bin/python"

expect() { # file, recorded key in results.json
    local actual recorded
    actual="$(shasum -a 256 "$HERE/$1" | cut -d' ' -f1)"
    recorded="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['artifacts'][sys.argv[2]])" "$HERE/results.json" "$2")"
    [ "$actual" = "$recorded" ] || { echo "$1: SHA256 $actual differs from recorded $recorded" >&2; exit 1; }
}
expect build_mrt_fix.py build_adapter_sha256
expect run.py run_adapter_sha256

missing=0
for need in "$ROOT/docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/build.py" \
            "$ROOT/docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/run.py" \
            "$BASE/emulator/launch.json" \
            "$BASE/raw-point-controls/analysis.json" \
            "$BASE/classic-reference-control/worker-baseline.json" \
            "$ROOT/build/follow-ups/pristine-source/projectm" \
            "$PY"; do
    [ -e "$need" ] || { echo "missing prerequisite: $need" >&2; missing=1; }
done
git -C "$ROOT" rev-parse --verify --quiet '25e6aa83^{commit}' > /dev/null ||
    { echo "missing commit 25e6aa83 (git fetch origin bug/native-4k-feedback-fidelity)" >&2; missing=1; }
[ "$missing" = 0 ] || exit 1
[ -e "$DEST" ] && { echo "refusing to reuse existing epoch $DEST" >&2; exit 1; }

if [ "$CHECK" = 1 ]; then
    echo "ok: adapter hashes match results.json; prerequisites present; would create $DEST"
    exit 0
fi
mkdir -p "$DEST"
cp "$HERE/build_mrt_fix.py" "$HERE/run.py" "$DEST/"
"$PY" "$DEST/build_mrt_fix.py"
"$PY" "$DEST/run.py"
