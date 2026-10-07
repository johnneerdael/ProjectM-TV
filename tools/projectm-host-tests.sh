#!/bin/bash
# Builds projectM from third_party/projectm as it is (patches applied) for the host, with its GTest
# suite, and runs the suite. Extra arguments go to the test binary (e.g. --gtest_filter=LineBatch.*).
# Requirements: CMake, Ninja, a C++ compiler, GTest (Homebrew's: brew install googletest).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build/projectm-host"
GTEST_DIR="${GTEST_DIR:-$(brew --prefix 2>/dev/null || echo /usr)/lib/cmake/GTest}"
cmake -S "$ROOT/third_party/projectm" -B "$BUILD" -G Ninja -DCMAKE_BUILD_TYPE=Debug \
    -DBUILD_TESTING=ON -DENABLE_SYSTEM_PROJECTM_EVAL=OFF -DENABLE_PLAYLIST=OFF \
    -DGTest_DIR="$GTEST_DIR" "-DCMAKE_CXX_FLAGS=-I$ROOT/third_party/projectm/vendor/glad/include -include $ROOT/tools/projectm-host-gl-shim.h" > /dev/null
cmake --build "$BUILD" --target projectM-unittest
"$BUILD/tests/libprojectM/projectM-unittest" "$@"
