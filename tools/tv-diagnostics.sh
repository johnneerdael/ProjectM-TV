#!/usr/bin/env bash
# Collects performance / fidelity diagnostics for projectM TV from an Android TV over adb.
#
#   tools/tv-diagnostics.sh [host:port] [options]
#
# Options
#   --duration SEC     how long to observe the running app (default 180)
#   --apk PATH         install this APK instead of building one
#   --release          download the latest GitHub Release APK instead of building
#   --no-install       test the version that is already installed
#   --allow-uninstall  if the install fails because of a different signing key, uninstall the
#                      existing app first (this resets the app's settings)
#   --sweep            also measure each fixed resolution (drives the menu with key events)
#   --out DIR          output directory (default diagnostics/<model>-<timestamp>)
#
# Output: summary.md (human readable) plus logs, dumps and screenshots in the output directory.
# Works with the bash 3.2 that ships with macOS; needs adb, curl and awk.
#
# Tip: play music on the TV while this runs. Without audio the visuals barely react and
# blank-preset detection stays idle (performance numbers are still valid).

set -u

TARGET="192.168.50.105:5555"
DURATION=180
APK=""
APK_SOURCE="build"
ALLOW_UNINSTALL=0
SWEEP=0
OUT=""
PKG="com.example.projectm.visualizer"
ACTIVITY="$PKG/.MainActivity"
REPO="johnneerdael/projectm-android-tv"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

while [ $# -gt 0 ]; do
    case "$1" in
        --duration) DURATION="$2"; shift ;;
        --apk) APK="$2"; APK_SOURCE="file"; shift ;;
        --release) APK_SOURCE="release" ;;
        --no-install) APK_SOURCE="none" ;;
        --allow-uninstall) ALLOW_UNINSTALL=1 ;;
        --sweep) SWEEP=1 ;;
        --out) OUT="$2"; shift ;;
        -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
        -*) echo "Unknown option: $1" >&2; exit 2 ;;
        *) TARGET="$1" ;;
    esac
    shift
done

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
die() { log "ERROR: $*"; exit 1; }

# ---------------------------------------------------------------------------------------------
# adb
# ---------------------------------------------------------------------------------------------
ADB="$(command -v adb || true)"
for candidate in "${ANDROID_HOME:-}/platform-tools/adb" "${ANDROID_SDK_ROOT:-}/platform-tools/adb" \
                 "$HOME/Library/Android/sdk/platform-tools/adb" "$HOME/Android/Sdk/platform-tools/adb"; do
    [ -z "$ADB" ] && [ -x "$candidate" ] && ADB="$candidate"
done
[ -n "$ADB" ] || die "adb not found (install Android platform-tools or set ANDROID_HOME)"

a() { "$ADB" -s "$TARGET" "$@"; }
ash() { "$ADB" -s "$TARGET" shell "$@" 2>/dev/null | tr -d '\r'; }
key() {  # one key at a time so focus changes keep up on slow devices
    for k in "$@"; do ash input keyevent "$k" >/dev/null; sleep 0.4; done
}
mark() { ash log -t TVDIAG "$*" >/dev/null; }

connect() {
    log "Connecting to $TARGET"
    "$ADB" connect "$TARGET" >/dev/null 2>&1
    i=0
    while [ $i -lt 30 ]; do
        state="$("$ADB" -s "$TARGET" get-state 2>&1 | tr -d '\r')"
        case "$state" in
            device) log "Connected"; return 0 ;;
            *unauthorized*) log "Waiting: accept the 'Allow debugging?' prompt on the TV" ;;
            *) "$ADB" connect "$TARGET" >/dev/null 2>&1 ;;
        esac
        sleep 3
        i=$((i + 1))
    done
    die "could not connect to $TARGET (state: $state). Is wireless/network debugging enabled?"
}

connect

MODEL="$(ash getprop ro.product.model)"
SAFE_MODEL="$(printf '%s' "$MODEL" | tr -c 'A-Za-z0-9._-' '_' | sed 's/_*$//')"
[ -n "$OUT" ] || OUT="$ROOT/diagnostics/${SAFE_MODEL:-device}-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || die "cannot create $OUT"
log "Output: $OUT"

# ---------------------------------------------------------------------------------------------
# Device facts
# ---------------------------------------------------------------------------------------------
log "Collecting device information"
{
    for p in ro.product.manufacturer ro.product.model ro.product.device ro.hardware ro.board.platform \
             ro.soc.manufacturer ro.soc.model ro.product.cpu.abilist ro.build.version.release \
             ro.build.version.sdk ro.build.fingerprint ro.config.low_ram vendor.display-size \
             sys.display-size ro.hardware.egl ro.opengles.version; do
        v="$(ash getprop "$p")"
        [ -n "$v" ] && printf '%-28s %s\n' "$p" "$v"
    done
    echo
    echo "## wm"; ash wm size; ash wm density
    echo; echo "## memory"; ash cat /proc/meminfo | head -3
    echo; echo "## cpu"; ash cat /sys/devices/system/cpu/present
    ash cat /proc/cpuinfo | grep -iE "^(Hardware|processor|CPU part|model name)" | sort | uniq -c | head -12
    echo; echo "## display modes"
    ash dumpsys display | grep -E "mModeId|supportedModes|mDefaultModeId|DisplayDeviceInfo|renderFrameRate|mActiveModeId" | head -20
    echo; echo "## GPU (SurfaceFlinger)"
    ash dumpsys SurfaceFlinger | grep -iE "^GLES|EGL implementation|GL_RENDERER|gpu" | head -5
} > "$OUT/device.txt"

# ---------------------------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------------------------
download_release() {
    url="$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
        | grep -o '"browser_download_url": *"[^"]*\.apk"' | head -1 | sed 's/.*"\(http[^"]*\)"/\1/')"
    [ -n "$url" ] || return 1
    log "Downloading $url"
    curl -fsSL -o "$OUT/app.apk" "$url" || return 1
    APK="$OUT/app.apk"
    APK_SOURCE="release: $url"
}

if [ "$APK_SOURCE" = "build" ]; then
    log "Building release APK from $ROOT (./gradlew assembleRelease)"
    if (cd "$ROOT" && ./gradlew -q assembleRelease > "$OUT/build.log" 2>&1); then
        APK="$ROOT/app/build/outputs/apk/release/app-release.apk"
        APK_SOURCE="local build of $(cd "$ROOT" && git rev-parse --short HEAD 2>/dev/null || echo '?')"
    else
        log "Local build failed (see build.log); falling back to the latest GitHub Release"
        download_release || die "no APK available"
    fi
elif [ "$APK_SOURCE" = "release" ]; then
    download_release || die "could not download the latest release APK"
fi

[ "$APK_SOURCE" = "file" ] && APK_SOURCE="file: $APK"
if [ "$APK_SOURCE" != "none" ]; then
    [ -f "$APK" ] || die "APK not found: $APK"
    log "Installing $APK"
    result="$(a install -r "$APK" 2>&1 | tr -d '\r')"
    if printf '%s' "$result" | grep -q "INSTALL_FAILED_UPDATE_INCOMPATIBLE"; then
        if [ "$ALLOW_UNINSTALL" = 1 ]; then
            log "Installed app has a different signing key; uninstalling it (--allow-uninstall)"
            a uninstall "$PKG" >/dev/null 2>&1
            result="$(a install -r "$APK" 2>&1 | tr -d '\r')"
            APK_SOURCE="$APK_SOURCE (previous install removed: different signing key)"
        else
            die "installed app is signed with a different key. Re-run with --allow-uninstall (resets app settings) or use --no-install"
        fi
    fi
    printf '%s' "$result" | grep -q "Success" || die "install failed: $result"
fi
ash pm grant "$PKG" android.permission.RECORD_AUDIO >/dev/null
VERSION="$(ash dumpsys package "$PKG" | grep -m1 versionName | sed 's/.*versionName=//')"
log "App version: ${VERSION:-unknown}"

# ---------------------------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------------------------
a logcat -c
a logcat -v threadtime > "$OUT/raw_logcat.txt" 2>&1 &
LOGCAT_PID=$!
trap 'kill $LOGCAT_PID 2>/dev/null' EXIT

log "Cold start"
ash am force-stop "$PKG"
sleep 1
ash am start -W -n "$ACTIVITY" > "$OUT/am_start.txt"
START_MS="$(grep -E "TotalTime" "$OUT/am_start.txt" | sed 's/[^0-9]//g')"

surface_layer() {
    ash dumpsys SurfaceFlinger --list | grep -i "surfaceview" | grep -i "projectm" | head -1
}

# FPS from SurfaceFlinger's frame timestamps for our layer (independent of the app's own count).
latency_fps() {
    layer="$(surface_layer)"
    [ -n "$layer" ] || { echo "n/a"; return; }
    ash "dumpsys SurfaceFlinger --latency '$layer'" | awk '
        NR == 1 { next }
        NF == 3 && $2 > 0 && $2 < 9e18 { t[n++] = $2 }
        END { if (n > 2 && t[n-1] > t[0]) printf "%.1f", (n - 1) / ((t[n-1] - t[0]) / 1e9); else print "n/a" }'
}

LATENCY_SAMPLES=""
elapsed=0
shots_done=0
log "Observing for ${DURATION}s"
while [ $elapsed -lt "$DURATION" ]; do
    sleep 10
    elapsed=$((elapsed + 10))
    LATENCY_SAMPLES="$LATENCY_SAMPLES $(latency_fps)"

    if [ $elapsed -ge 20 ] && [ $shots_done = 0 ]; then
        shots_done=1
        log "Screenshots (visuals, main panel, advanced panel)"
        a exec-out screencap -p > "$OUT/screen_visuals.png"
        key KEYCODE_DPAD_CENTER; sleep 1
        a exec-out screencap -p > "$OUT/screen_menu.png"
        key KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN
        key KEYCODE_DPAD_CENTER; sleep 1
        a exec-out screencap -p > "$OUT/screen_advanced.png"
        key KEYCODE_BACK; key KEYCODE_BACK
    fi
    if [ $elapsed = 60 ]; then
        log "SurfaceFlinger and CPU snapshot"
        ash dumpsys SurfaceFlinger > "$OUT/raw_surfaceflinger.txt"
        ash top -b -n 1 > "$OUT/top.txt" 2>/dev/null || ash top -n 1 > "$OUT/top.txt"
    fi
done

# ---------------------------------------------------------------------------------------------
# Optional resolution sweep: menu -> 4x down to "Resolution" -> left to Auto -> right per level
# ---------------------------------------------------------------------------------------------
SWEEP_ROWS=""
if [ "$SWEEP" = 1 ]; then
    log "Resolution sweep"
    open_resolution_row() { key KEYCODE_DPAD_CENTER; sleep 1; key KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN; }
    open_resolution_row
    key KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT
    key KEYCODE_BACK
    step=1
    while [ $step -le 4 ]; do
        open_resolution_row
        key KEYCODE_DPAD_RIGHT
        key KEYCODE_BACK
        sleep 15
        mark "SWEEP start step=$step"
        s1="$(latency_fps)"; sleep 10; s2="$(latency_fps)"; sleep 10; s3="$(latency_fps)"
        mark "SWEEP end step=$step"
        SWEEP_ROWS="$SWEEP_ROWS
$step $s1 $s2 $s3"
        step=$((step + 1))
    done
    log "Restoring Auto resolution"
    open_resolution_row
    key KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT
    key KEYCODE_BACK
fi

ash dumpsys meminfo "$PKG" | grep -E "TOTAL|Graphics|GL mtrack|EGL mtrack" > "$OUT/meminfo.txt"
ash dumpsys thermalservice 2>/dev/null | head -40 > "$OUT/thermal.txt"
kill $LOGCAT_PID 2>/dev/null
trap - EXIT
sleep 1

# ---------------------------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------------------------
L="$OUT/raw_logcat.txt"
grep -E "projectM-Native|VisualizerRenderer|VisualizerView|DisplayInfo|DeviceProfile|QualityController|ProjectMTV|ProjectMApplication|TVDIAG|AndroidRuntime|FATAL|Fatal signal" "$L" > "$OUT/app_log.txt"
A="$OUT/app_log.txt"

stats_summary() {  # min / avg / max of the app's STATS fps lines
    grep -o "STATS fps=[0-9.]*" "$1" | sed 's/.*=//' | awk '
        { s += $1; n++; if (min == "" || $1 < min) min = $1; if ($1 > max) max = $1 }
        END { if (n) printf "%.1f / %.1f / %.1f (%d samples)", min, s / n, max, n; else print "no samples" }'
}

layer_excerpt() {
    [ -f "$OUT/raw_surfaceflinger.txt" ] || return
    grep -n -i "surfaceview.*projectm\|projectm.*surfaceview" "$OUT/raw_surfaceflinger.txt" | head -3
    grep -i -A 12 "surfaceview.*projectm" "$OUT/raw_surfaceflinger.txt" \
        | grep -iE "buffer|composition|crop|frame=|dataspace|size|HWC|DEVICE|CLIENT" | head -20
    echo "--- HWC / display"
    grep -iE "^Display .*(HWC|mode)|activeMode|refresh-rate|HWC2 display|Display [0-9]+ HWC layers" "$OUT/raw_surfaceflinger.txt" | head -8
}

{
    echo "# projectM TV diagnostics: $MODEL"
    echo
    echo "- Collected: $(date '+%Y-%m-%d %H:%M %Z'), ${DURATION}s run"
    echo "- Target: \`$TARGET\`"
    echo "- App: ${VERSION:-unknown} ($APK_SOURCE)"
    echo
    echo "## Device"
    echo '```'
    grep -E "^ro\.(product\.(manufacturer|model)|hardware |board\.platform|soc\.|build\.version\.(release|sdk)|config\.low_ram)|display-size|^Physical size|^Override size|^Physical density|MemTotal" "$OUT/device.txt"
    grep -h -E "GL: |Panel |Device .* tier" "$A" | sed 's/.*: //' | sort -u
    echo '```'
    echo
    echo "## Startup"
    echo "- Activity start (am start -W TotalTime): ${START_MS:-n/a} ms"
    echo "- $(grep -h -o 'Indexed [0-9]* presets.*' "$A" | head -1)"
    echo "- $(grep -h -o 'STARTUP first preset shown.*' "$A" | head -1)"
    echo
    echo "## Performance"
    echo "- App FPS (min / avg / max): $(stats_summary "$A")"
    echo "- Render sizes seen: $(grep -o 'surface=[0-9]*x[0-9]*' "$A" | sed 's/surface=//' | sort | uniq -c | awk '{printf "%s (%s samples)  ", $2, $1}')"
    echo "- SurfaceFlinger FPS samples (every 10 s):${LATENCY_SAMPLES}"
    echo "- Resolution decisions:"
    grep -h -E "QualityController" "$A" | sed 's/.*QualityController: /  - /' | head -30
    if [ "$SWEEP" = 1 ]; then
        echo
        echo "## Resolution sweep (fixed levels, SurfaceFlinger FPS x3)"
        echo
        echo "| Step | Render size | FPS samples |"
        echo "|---|---|---|"
        printf '%s\n' "$SWEEP_ROWS" | while read -r step s1 s2 s3; do
            [ -n "$step" ] || continue
            size="$(awk -v s="step=$step" '
                index($0, "SWEEP start " s) { on = 1; next }
                index($0, "SWEEP end " s) { on = 0 }
                on && match($0, /surface=[0-9]+x[0-9]+/) { v = substr($0, RSTART + 8, RLENGTH - 8) }
                END { print v }' "$A")"
            echo "| $step | ${size:-?} | $s1 / $s2 / $s3 |"
        done
    fi
    echo
    echo "## Surface composition (is the render surface shown at full panel resolution?)"
    echo '```'
    layer_excerpt
    echo '```'
    echo
    echo "## Skipped presets"
    grep -h -o "SKIP preset=.*" "$A" | sed 's/^/- /' | head -50
    grep -q 'SKIP preset=' "$A" || echo "- none"
    echo
    echo "## Errors and crashes"
    grep -h -E "FATAL|Fatal signal|AndroidRuntime| E [A-Za-z-]*(projectM|Visualizer|ProjectM)" "$A" | head -20
    grep -q -E 'FATAL|Fatal signal' "$A" || echo "- no crashes"
    echo
    echo "## Resources"
    echo '```'
    cat "$OUT/meminfo.txt"
    grep -i "projectm" "$OUT/top.txt" 2>/dev/null | head -3
    echo '```'
    echo
    echo "Files: device.txt, app_log.txt, am_start.txt, meminfo.txt, thermal.txt, top.txt, screen_*.png (raw_* files are large and not meant for git)."
} > "$OUT/summary.md"

log "Done. Summary: $OUT/summary.md"
