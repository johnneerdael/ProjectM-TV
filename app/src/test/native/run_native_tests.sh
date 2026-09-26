#!/bin/bash
# Host-side tests for the native engine (app/src/main/cpp/native-lib.cpp).
# 1. engine_test: the engine against fakes of projectM, AAssetManager and GLES. Covers preset
#    indexing (presets.idx and folder fallback), commands, skip list, transitions (lightweight,
#    classic, auto), output measurement, black-preset skipping and context loss.
# 2. fade_gl_test: the lightweight-transition overlay on a real GLES3 driver (skipped without one).
# Requirements: g++ (C++17) and a JDK (for jni.h); for 2, EGL/GLES (Mesa) development files.
# Usage: app/src/test/native/run_native_tests.sh
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
# Prebuilt index as written by tools/gen-preset-index.py ("name<TAB>weight MB"), plus a line without
# a weight, a CRLF line, a blank line and junk. "good 3.milk" is heavy.
(cd "$WORK/assets/presets" && ls -1) | grep -i '\.milk$' | grep -v '^good [12]\.milk$' | LC_ALL=C sort \
    | awk '{ print $0 "\t" ($0 == "good 3.milk" ? 40 : 0) }' > "$WORK/assets/presets.idx"
printf 'good 1.milk\ngood 2.milk\t2\ncrlf.milk\t7\r\n\nreadme.txt\t9\n' >> "$WORK/assets/presets.idx"
echo "preset crlf" > "$WORK/assets/presets/crlf.milk"
# Second fixture without an index: the folder listing is used.
mkdir -p "$WORK/noindex/presets"
for n in a.milk b.milk C.MILK notes.txt; do echo "x" > "$WORK/noindex/presets/$n"; done
mkdir -p "$WORK/assets/textures"
printf 'JPEGworms' > "$WORK/assets/textures/worms.jpg"
printf 'JPEGclouds' > "$WORK/assets/textures/clouds.jpg"

# The engine uses projectM API additions from tools/projectm-patches; apply them like the app's
# CMake build does (a patch that already applies in reverse is in place).
for patch in "$ROOT"/tools/projectm-patches/*.patch; do
    if ! git -C "$ROOT/third_party/projectm" apply --reverse --check "$patch" 2>/dev/null; then
        git -C "$ROOT/third_party/projectm" apply "$patch"
    fi
done

SAN="-fsanitize=address,undefined"
[ "${NO_SANITIZERS:-0}" = "1" ] && SAN=""
g++ -std=c++17 -O1 -g $SAN -pthread \
    -I"$HERE/stubs" -I"$JAVA_HOME/include" -I"$JAVA_HOME/include/$JNI_OS" \
    -I"$ROOT/third_party/projectm/src/api/include" -I"$ROOT/app/src/main/cpp" \
    "$HERE/engine_test.cpp" -o "$WORK/engine_test"
if ! ASAN_OPTIONS=detect_leaks=0 "$WORK/engine_test" "$WORK/assets" "$WORK/noindex" 2>"$WORK/engine.log"; then
    echo "--- engine log (last 80 lines)"
    tail -80 "$WORK/engine.log"
    exit 1
fi

# Transition overlay against a real OpenGL ES 3 driver (Mesa llvmpipe, headless EGL). Needs the
# EGL/GLES development files (CI: libegl-dev libgles-dev libegl-mesa0). GL_CFLAGS/GL_LIBS override
# pkg-config, e.g. for a Mesa build outside the system paths.
GL_CFLAGS="${GL_CFLAGS:-$(pkg-config --cflags egl glesv2 2>/dev/null || true)}"
GL_LIBS="${GL_LIBS:-$(pkg-config --libs egl glesv2 2>/dev/null || true)}"
if [ -z "$GL_LIBS" ]; then
    echo "SKIPPED transition overlay GL test: no EGL/GLES development files (pkg-config egl glesv2)"
    exit 0
fi
# The Android stubs come last so the real GLES3 headers win.
# shellcheck disable=SC2086
g++ -std=c++17 -O1 -g $SAN $GL_CFLAGS -idirafter "$HERE/stubs" -I"$ROOT/app/src/main/cpp" \
    "$HERE/fade_gl_test.cpp" "$ROOT/app/src/main/cpp/snapshot_fade.cpp" $GL_LIBS -o "$WORK/fade_gl_test"
ASAN_OPTIONS=detect_leaks=0 "$WORK/fade_gl_test"
