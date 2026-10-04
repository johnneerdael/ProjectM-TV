#!/bin/bash
# Dumps translator inputs (every attempt) for all presets: final = all patches, base = series 0001-0029.
set -euo pipefail
WT=/Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-translator-issues
SP=/private/tmp/claude-501/-Users-jneerdael-Scripts-Projectm-TV/ac120ff4-c9a0-4fff-97ed-eceb645ad6fa/scratchpad
SUB=$WT/third_party/projectm
run() {
    rm -rf "$SP/$1"; mkdir -p "$SP/$1"
    cmake --build "$WT/build/projectm-host" --target projectM-unittest > "$SP/$1.build.log" 2>&1
    PM_CORPUS_DIR=$WT/core/src/main/assets/presets PM_DUMP_HLSL_DIR=$SP/$1 \
        "$WT/build/projectm-host/tests/libprojectM/projectM-unittest" --gtest_filter='Scratch*' > "$SP/$1.log" 2>&1
    echo "$1: $(find "$SP/$1" -name '*_0.hlsl' | wc -l) authored, $(find "$SP/$1" -name '*_1.hlsl' | wc -l) fallbacks"
}
run dump-final
git -C "$SUB" switch -q -c local/baseline-dump ebada8f6555889bab553446a84c8324dcaa9fdcc
git -C "$SUB" checkout 31c5ca3ba -- src/libprojectM/MilkdropPreset/MilkdropShader.cpp tests/libprojectM/ScratchCorpusDump.cpp
# Keep only the instrumentation, not 0032, in MilkdropShader.cpp: rebuild it from the base version.
git -C "$SUB" show ebada8f6555889bab553446a84c8324dcaa9fdcc:src/libprojectM/MilkdropPreset/MilkdropShader.cpp > "$SUB/src/libprojectM/MilkdropPreset/MilkdropShader.cpp"
git -C "$SUB" diff 6a13128fe 31c5ca3ba -- src/libprojectM/MilkdropPreset/MilkdropShader.cpp | git -C "$SUB" apply
sed -i '' 's/        HLSLModuloTest.cpp/        HLSLModuloTest.cpp\n        ScratchCorpusDump.cpp/' "$SUB/tests/libprojectM/CMakeLists.txt"
run dump-base
git -C "$SUB" checkout -q -- . && git -C "$SUB" clean -fdq -- tests
git -C "$SUB" switch -q local/translator-fixes
git -C "$SUB" branch -q -D local/baseline-dump
echo done
