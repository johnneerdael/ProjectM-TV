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
            "$BASE/raw-point-experiment/worker-candidate.json" \
            "$ROOT/build/follow-ups/pristine-source/projectm" \
            "$PY"; do
    [ -e "$need" ] || { echo "missing prerequisite: $need" >&2; missing=1; }
done
[ "$missing" = 0 ] || exit 1
# Everything else run.py reads, by recorded size/SHA256: the PCM signals (hashes run.py asserts), the six
# preset files (as rendered by the comparator rows), and the comparator rows and their native captures.
python3 - "$HERE/run.py" "$ROOT" "$BASE" <<'PYCHECK' || missing=1
import ast, hashlib, json, sys
from pathlib import Path
run, root, base = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()
problems = []
names = next(ast.literal_eval(node.value) for node in ast.parse(run.read_text()).body
             if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'NAMES')
def same_bytes(path, size, digest):
    return path.is_file() and path.stat().st_size == size and sha(path) == digest
pcm = {240: '38a09d906e93452d4af5ebea36fcdc684a8383eacbd162d2d61b4ed3fbd2674c',
       480: '14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc'}
for frames, digest in pcm.items():
    path = base / f'targeted-matrix/signals/pcm-{frames}.u8'
    if not path.is_file():
        problems.append(f'missing signal: {path}')
    elif sha(path) != digest:
        problems.append(f'signal hash differs: {path}')
analysis = json.loads((base / 'raw-point-controls/analysis.json').read_text())
if analysis.get('state') != 'complete':
    problems.append('raw-point-controls/analysis.json is not complete')
rows = []
recorded_presets = {}
for case in analysis.get('cases', []):
    recorded_presets[case['preset']['path']] = case['preset']
    for role in ['p1', 'raw-point']:
        info = case['roles'][role]
        if info.get('status') != 'success':
            problems.append(f"comparator {role} {case['profile']} {case['preset']['path']} not successful")
        rows += zip(info['row_paths'], info['row_sha256'])
    rows += zip(case['reference']['row_paths'], case['reference']['row_sha256'])
# The new run must render the same preset bytes as the comparator rows it is compared with.
for name in names:
    record = recorded_presets.get(name)
    path = root / 'core/src/main/assets/presets' / name
    if record is None:
        problems.append(f'preset not in comparator analysis: {name}')
    elif not same_bytes(path, record['bytes'], record['sha256']):
        problems.append(f'preset missing or changed: {path}')
for path, digest in rows:
    path = Path(path)
    if not path.is_file() or sha(path) != digest:
        problems.append(f'comparator row missing or changed: {path}')
        continue
    for sample in json.loads(path.read_text())['result']['selected_files']:
        capture = path.parent / 'output' / sample['path']
        if not same_bytes(capture, sample['bytes'], sample['sha256']):
            problems.append(f'comparator capture missing or changed: {capture}')
for problem in problems[:20]:
    print(problem, file=sys.stderr)
if problems:
    print(f'{len(problems)} input problem(s)', file=sys.stderr)
    sys.exit(1)
print(f'inputs ok: {len(names)} presets, 2 signals, {len(rows)} comparator rows; preset and capture sizes/SHA256s match')
PYCHECK
"$PY" -c 'import numpy, cv2' 2> /dev/null || { echo "missing numpy/OpenCV in $PY" >&2; missing=1; }
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
