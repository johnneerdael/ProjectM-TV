#!/bin/bash
set -euo pipefail
CORPUS_ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
CORPUS_PYTHON="$CORPUS_ROOT/build/preset-lab-venv/bin/python"
if [ ! -x "$CORPUS_PYTHON" ]; then
  echo "Prepared predictor Python environment missing: $CORPUS_PYTHON" >&2
  echo "See tools/milk-analyzer/CORPUS_EXPORT.md and the analyzer README prerequisites." >&2
  exit 1
fi
cd "$CORPUS_ROOT"
exec "$CORPUS_PYTHON" "$CORPUS_ROOT/tools/milk-analyzer/preset_corpus.py" "$@"
