#!/bin/bash
# Host-side tests for the native engine (app/src/main/cpp/native-lib.cpp).
# Compiles the engine against fakes of projectM, AAssetManager and GLES, then exercises preset
# indexing, commands, skip-list persistence, black-frame detection and context loss.
# Requirements: g++ (C++17) and a JDK (for jni.h). Usage: app/src/test/native/run_native_tests.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
JAVA_HOME="${JAVA_HOME:-$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")}"
JNI_OS=$([ "$(uname)" = "Darwin" ] && echo darwin || echo linux)
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Fixture: 9 good presets, one upper-case extension, 2 broken, 1 pre-skipped, plus junk files.
mkdir -p "$WORK/assets/presets"
for i in $(seq 1 9); do echo "preset $i" > "$WORK/assets/presets/good $i.milk"; done
echo "preset upper" > "$WORK/assets/presets/Upper.MILK"
echo "BROKEN" > "$WORK/assets/presets/broken1.milk"
echo "BROKEN" > "$WORK/assets/presets/broken2.milk"
echo "x" > "$WORK/assets/presets/preskipped.milk"
echo junk > "$WORK/assets/presets/.DS_Store"
echo junk > "$WORK/assets/presets/readme.txt"
echo "preskipped.milk" > "$WORK/assets/skip.txt"

SAN="-fsanitize=address,undefined"
[ "${NO_SANITIZERS:-0}" = "1" ] && SAN=""
g++ -std=c++17 -O1 -g $SAN -pthread \
    -I"$HERE/stubs" -I"$JAVA_HOME/include" -I"$JAVA_HOME/include/$JNI_OS" \
    -I"$ROOT/app/src/main/jniLibs/include" -I"$ROOT/app/src/main/cpp" \
    "$HERE/engine_test.cpp" -o "$WORK/engine_test"
ASAN_OPTIONS=detect_leaks=0 "$WORK/engine_test" "$WORK/assets" 2>"$WORK/engine.log"
