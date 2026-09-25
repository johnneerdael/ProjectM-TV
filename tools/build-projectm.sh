#!/usr/bin/env bash
# Builds libprojectM for Android from an upstream release tag, applies tools/projectm-patches/*.patch
# and installs the shared libraries and headers into app/src/main/jniLibs (the app links against
# these prebuilt files).
#
#   tools/build-projectm.sh
#
# Needs git, cmake, ninja and the Android NDK named in app/build.gradle (ndkVersion), found under
# $ANDROID_NDK_HOME, $ANDROID_HOME/ndk/<version> or ~/Library/Android/sdk/ndk/<version>.
# Builds armeabi-v7a (e.g. NVIDIA SHIELD runs the app 32-bit) and arm64-v8a, API level = the app's
# minSdk. projectM-eval is built in (vendored submodule); the playlist library is not needed.
# jniLibs is only touched once both ABIs have built. Update TAG/COMMIT and docs/THIRD_PARTY.md
# together.

set -euo pipefail

TAG="v4.1.7"
COMMIT="e0b0a967f0ffd7d332106c366668ed271718472b"  # what TAG pointed to when this was pinned

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JNI="$ROOT/app/src/main/jniLibs"
PATCHES="$ROOT/tools/projectm-patches"
NDK_VERSION="$(sed -n 's/.*ndkVersion "\(.*\)".*/\1/p' "$ROOT/app/build.gradle")"
MIN_SDK="$(sed -n 's/.*minSdkVersion \([0-9]*\).*/\1/p' "$ROOT/app/build.gradle")"
[ -n "$NDK_VERSION" ] && [ -n "$MIN_SDK" ] || { echo "ndkVersion/minSdkVersion not found in app/build.gradle" >&2; exit 1; }

NDK=""
for candidate in "${ANDROID_NDK_HOME:-}" "${ANDROID_HOME:-}/ndk/$NDK_VERSION" "${ANDROID_SDK_ROOT:-}/ndk/$NDK_VERSION" \
                 "$HOME/Library/Android/sdk/ndk/$NDK_VERSION" "$HOME/Android/Sdk/ndk/$NDK_VERSION"; do
    [ -n "$candidate" ] && [ -z "$NDK" ] && [ -f "$candidate/build/cmake/android.toolchain.cmake" ] || continue
    if grep -q "Pkg.Revision = $NDK_VERSION" "$candidate/source.properties" 2>/dev/null; then NDK="$candidate"; fi
done
[ -n "$NDK" ] || { echo "Android NDK $NDK_VERSION not found (install it or set ANDROID_NDK_HOME)" >&2; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
fail() {  # show the end of the failing step's log before the work folder is removed
    echo "FAILED: $1" >&2
    tail -40 "$2" >&2
    exit 1
}

echo "Building projectM $TAG with NDK $NDK_VERSION (API $MIN_SDK)"
git -c advice.detachedHead=false clone -q --depth 1 --branch "$TAG" --recurse-submodules --shallow-submodules \
    https://github.com/projectM-visualizer/projectm.git "$WORK/src"
cd "$WORK/src"  # projectM's CMake records the git commit of the current directory
[ "$(git rev-parse HEAD)" = "$COMMIT" ] || { echo "$TAG is $(git rev-parse HEAD), expected $COMMIT" >&2; exit 1; }
for patch in "$PATCHES"/*.patch; do
    [ -e "$patch" ] || continue
    git apply "$patch" || { echo "patch does not apply: $patch" >&2; exit 1; }
    echo "  applied $(basename "$patch")"
done

for abi in armeabi-v7a arm64-v8a; do
    log="$WORK/$abi.log"
    cmake -S "$WORK/src" -B "$WORK/build-$abi" -G Ninja \
        -DCMAKE_TOOLCHAIN_FILE="$NDK/build/cmake/android.toolchain.cmake" \
        -DANDROID_ABI="$abi" -DANDROID_PLATFORM="android-$MIN_SDK" \
        -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON \
        -DENABLE_SYSTEM_PROJECTM_EVAL=OFF -DENABLE_PLAYLIST=OFF -DENABLE_DEBUG_POSTFIX=OFF \
        -DCMAKE_INSTALL_PREFIX="$WORK/install-$abi" > "$log" 2>&1 || fail "configure $abi" "$log"
    cmake --build "$WORK/build-$abi" -j 8 >> "$log" 2>&1 || fail "build $abi" "$log"
    cmake --install "$WORK/build-$abi" >> "$log" 2>&1 || fail "install $abi" "$log"
done

# Both ABIs built: now replace the libraries and the (ABI-independent) headers.
for abi in armeabi-v7a arm64-v8a; do
    cp "$WORK/install-$abi/lib/libprojectM-4.so" "$JNI/$abi/libprojectM-4.so"
    echo "  $abi: $(du -h "$JNI/$abi/libprojectM-4.so" | cut -f1)"
done
rm -rf "$JNI/include/projectM-4"
cp -R "$WORK/install-arm64-v8a/include/projectM-4" "$JNI/include/"
echo "Installed projectM $(sed -n 's/.*PROJECTM_VERSION_STRING "\(.*\)".*/\1/p' "$JNI/include/projectM-4/version.h") into $JNI"
