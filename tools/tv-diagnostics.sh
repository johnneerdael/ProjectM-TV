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

case "$DURATION" in
    ''|*[!0-9]*) die "--duration must be a whole number of seconds (got '$DURATION')" ;;
esac
[ "$DURATION" -ge 30 ] || die "--duration must be at least 30 seconds"

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
        die "local build failed (see $OUT/build.log). Fix the build, or use --release to test the latest GitHub Release instead"
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
# Run adb itself in the background (not the shell function), so $! is the adb process.
"$ADB" -s "$TARGET" logcat -v threadtime > "$OUT/raw_logcat.txt" 2>&1 &
LOGCAT_PID=$!
SWEEP_ACTIVE=0
MENU_OPEN=0

open_resolution_row() {  # menu -> focus starts on shuffle -> 4x down = "Resolution"
    key KEYCODE_DPAD_CENTER
    MENU_OPEN=1
    sleep 1
    key KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN KEYCODE_DPAD_DOWN
}
close_menu() {
    key KEYCODE_BACK
    MENU_OPEN=0
}
restore_auto_resolution() {
    open_resolution_row
    key KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT KEYCODE_DPAD_LEFT
    close_menu
}
cleanup() {
    if [ "$SWEEP_ACTIVE" = 1 ]; then
        log "Interrupted during the sweep: restoring Auto resolution"
        SWEEP_ACTIVE=0
        # A half-navigated menu would turn the next CENTER into a click on some row.
        [ "$MENU_OPEN" = 1 ] && close_menu && sleep 1
        restore_auto_resolution
    fi
    kill $LOGCAT_PID 2>/dev/null
}
trap cleanup EXIT
trap 'exit 130' INT TERM

log "Cold start"
ash am force-stop "$PKG"
sleep 1
ash am start -W -n "$ACTIVITY" > "$OUT/am_start.txt"
START_MS="$(grep -E "TotalTime" "$OUT/am_start.txt" | sed 's/[^0-9]//g')"
sleep 2
APP_PIDS=" $(ash pidof "$PKG") "
if ! grep -q "Status: ok" "$OUT/am_start.txt" || [ -z "$(printf '%s' "$APP_PIDS" | tr -d ' ')" ]; then
    cat "$OUT/am_start.txt"
    die "the app did not start (is it installed? see am_start.txt)"
fi

# The app's process ids during the run (a crash + restart gives a new one).
track_pid() {
    for pid in $(ash pidof "$PKG"); do
        case "$APP_PIDS" in *" $pid "*) ;; *) APP_PIDS="$APP_PIDS$pid " ;; esac
    done
}

# The app's buffer layer. The first "surfaceview" match is "Background for -SurfaceView - ...", a
# colour layer without buffers, so match the line that starts with "SurfaceView - ".
surface_layer() {
    ash dumpsys SurfaceFlinger --list | grep -E '^[[:space:]]*SurfaceView - ' | grep -i "projectm" | head -1 \
        | sed -E 's/^[[:space:]]+//'
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
snapshot_done=0
log "Observing for ${DURATION}s"
while [ $elapsed -lt "$DURATION" ]; do
    sleep 10
    elapsed=$((elapsed + 10))
    LATENCY_SAMPLES="$LATENCY_SAMPLES $(latency_fps)"
    track_pid

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
    if [ $snapshot_done = 0 ] && { [ $elapsed -ge 60 ] || [ $elapsed -ge "$DURATION" ]; }; then
        snapshot_done=1
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
    # Fixed levels offered by the app (QualityController.manualHeights): 720/1080/1440/2160 up to
    # the panel height and the memory limit, plus that maximum itself if it is not one of those.
    PANEL_H="$(grep -o 'Panel [0-9]*x[0-9]*' "$OUT/raw_logcat.txt" | head -1 | sed 's/.*x//')"
    [ -n "$PANEL_H" ] || PANEL_H=1080
    MAX_H="$PANEL_H"
    LIMIT_H="$(grep -o 'Memory limit: .*' "$OUT/raw_logcat.txt" | tail -1 | sed -n 's/.*up to \([0-9]*\).*/\1/p')"
    if [ -n "$LIMIT_H" ] && [ "$LIMIT_H" -lt "$MAX_H" ]; then MAX_H="$LIMIT_H"; fi
    LEVELS=0
    for h in 720 1080 1440 2160; do [ "$h" -le "$MAX_H" ] && LEVELS=$((LEVELS + 1)); done
    case "$MAX_H" in 720|1080|1440|2160) ;; *) LEVELS=$((LEVELS + 1)) ;; esac
    log "Resolution sweep over $LEVELS fixed levels (panel height $PANEL_H, highest offered $MAX_H)"
    SWEEP_ACTIVE=1
    restore_auto_resolution
    step=1
    while [ $step -le $LEVELS ]; do
        open_resolution_row
        key KEYCODE_DPAD_RIGHT
        close_menu
        sleep 15
        mark "SWEEP start step=$step"
        s1="$(latency_fps)"; sleep 10; s2="$(latency_fps)"; sleep 10; s3="$(latency_fps)"
        mark "SWEEP end step=$step"
        SWEEP_ROWS="$SWEEP_ROWS
$step $s1 $s2 $s3"
        track_pid
        step=$((step + 1))
    done
    log "Restoring Auto resolution"
    restore_auto_resolution
    SWEEP_ACTIVE=0
fi

ash dumpsys meminfo "$PKG" | grep -E "TOTAL|Graphics|GL mtrack|EGL mtrack" > "$OUT/meminfo.txt"
ash dumpsys thermalservice 2>/dev/null | head -40 > "$OUT/thermal.txt"
track_pid
kill $LOGCAT_PID 2>/dev/null
trap - EXIT INT TERM
sleep 1

# ---------------------------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------------------------
L="$OUT/raw_logcat.txt"
# threadtime format: date time PID TID level tag: message. Keep lines from the app's processes,
# our sweep markers, and crash-dump lines that name the package (tombstones come from crash_dump).
awk -v pids="$APP_PIDS" -v pkg="$PKG" '
    BEGIN { n = split(pids, p, " "); for (i = 1; i <= n; i++) mine[p[i]] = 1 }
    ($3 in mine) || /TVDIAG/ || (index($0, pkg) && /(FATAL|Fatal signal|>>>|Process: )/)
' "$L" > "$OUT/app_log.txt"
A="$OUT/app_log.txt"

# min / avg / max (count) of a numeric key=value field in the given lines
field_summary() {
    grep -oE "(^|[ :])$1=[0-9.]+" | sed 's/.*=//' | awk '
        { s += $1; n++; if (min == "" || $1 < min) min = $1; if ($1 > max) max = $1 }
        END { if (n) printf "%.1f / %.1f / %.1f (%d)", min, s / n, max, n; else print "n/a" }'
}

stats_summary() {  # min / avg / max of the app's STATS fps lines
    grep -o "STATS fps=[0-9.]*" "$1" | sed 's/.*=//' | awk '
        { s += $1; n++; if (min == "" || $1 < min) min = $1; if ($1 > max) max = $1 }
        END { if (n) printf "%.1f / %.1f / %.1f (%d samples)", min, s / n, max, n; else print "no samples" }'
}

layer_excerpt() {
    [ -f "$OUT/raw_surfaceflinger.txt" ] || return
    grep -n -i "surfaceview.*projectm\|projectm.*surfaceview" "$OUT/raw_surfaceflinger.txt" | grep -v "Background for" | head -3
    grep -i -A 12 "[^-]SurfaceView - .*projectm" "$OUT/raw_surfaceflinger.txt" | grep -v "Background for" \
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
    echo "- $(grep -h -o 'STARTUP first preset rendered.*' "$A" | head -1)"
    echo "- $(grep -h -o 'Textures ready.*' "$A" | head -1)"
    echo
    echo "## Performance"
    echo "- App FPS (min / avg / max): $(stats_summary "$A")"
    echo "- Audio level (RMS 0-1, min / avg / max): $(grep -o 'audio=[0-9.]*' "$A" | sed 's/audio=//' | awk '
        { s += $1; n++; if (min == "" || $1 < min) min = $1; if ($1 > max) max = $1 }
        END { if (n) printf "%.3f / %.3f / %.3f", min, s / n, max; else print "n/a" }')  (≈0 means the TV delivers no audio: most presets then look dim)"
    echo "- Audio source: $(grep -h -o 'Audio source: .*' "$A" | tail -1 | sed 's/^Audio source: //' | grep . || echo 'standard (Visualizer)')"
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
    echo "## Preset switches (min / avg / max (count))"
    echo "- Load time, ms (parse + textures + shader compile, the stall at each switch): $(grep -h 'LOAD preset=' "$A" | field_summary ms)"
    for mode in lightweight classic; do
        T="$(grep -h "TRANSITION preset=.* mode=$mode" "$A" || true)"
        [ -n "$T" ] || continue
        echo "- $mode transitions: fps incl. load $(printf '%s\n' "$T" | field_summary fps), blend fps $(printf '%s\n' "$T" | field_summary blend_fps), fps before $(printf '%s\n' "$T" | field_summary before_fps), frames > 50 ms $(printf '%s\n' "$T" | field_summary slow_frames)"
    done
    grep -h -o "TRANSITION auto:.*" "$A" | sed 's/^/- /' | head -3
    echo "- Biggest memory drops during a load (avail_drop_mb, with weight_mb, shader_kb, loops):"
    grep -h -o "LOAD preset=.*" "$A" | awk -F"avail_drop_mb=" 'NF > 1 { split($2, a, " "); print a[1] "\t" $0 }' \
        | sort -rn | head -10 | cut -f2 | sed 's/^/  - /'
    echo "- Average memory drop per load by shader size and by image weight:"
    grep -h -o "LOAD preset=.*" "$A" | awk '
        function v(k,   i) { for (i = 1; i <= NF; i++) if (index($i, k "=") == 1) return substr($i, length(k) + 2) + 0; return -1 }
        v("avail_drop_mb") >= 0 {
            d = v("avail_drop_mb"); kb = v("shader_kb"); w = v("weight_mb")
            complex = kb >= 4.2 || v("loops") >= 2
            s = complex ? "complex shader" : kb >= 2 ? "shader 2-4 KB" : "shader < 2 KB"
            sum[s] += d; n[s]++
            if (!complex) { g = w >= 5 ? "simple shader, images >= 5 MB" : "simple shader, images < 5 MB"; sum[g] += d; n[g]++ }
        }
        END { for (k in n) printf "  - %s: %.0f MB over %d loads\n", k, sum[k] / n[k], n[k] }' | sort
    echo "- Slowest loads:"
    grep -h -o "LOAD preset=.*" "$A" | awk -F"ms=" '{ split($2, a, " "); print a[1] "\t" $0 }' | sort -rn | head -5 \
        | cut -f2 | sed 's/^/  - /'
    echo
    echo "## Output measurements (per preset; nothing is skipped for flat or still output)"
    O="$(grep -h -o "OUTPUT preset=.*" "$A" || true)"
    if [ -n "$O" ]; then
        echo "- Presets measured: $(printf '%s\n' "$O" | wc -l | tr -d ' ')"
        echo "- Flat in every sample: $(printf '%s\n' "$O" | awk '{ for (i = 1; i <= NF; i++) if ($i ~ /^flat=/) { split(substr($i, 6), f, "/"); if (f[2] > 0 && f[1] == f[2]) n++ } } END { print n + 0 }')"
        echo "- Still in every compared sample: $(printf '%s\n' "$O" | awk '{ for (i = 1; i <= NF; i++) if ($i ~ /^still=/) { split(substr($i, 7), f, "/"); if (f[2] > 0 && f[1] == f[2]) n++ } } END { print n + 0 }')"
        echo "- Candidates (flat or still in every sample):"
        printf '%s\n' "$O" | awk '{ c = 0; for (i = 1; i <= NF; i++) if ($i ~ /^(flat|still)=/) { split(substr($i, index($i, "=") + 1), f, "/"); if (f[2] > 0 && f[1] == f[2]) c = 1 } } c' \
            | head -20 | sed 's/^/  - /'
    else
        echo "- none (needs music playing and the 1.9 build)"
    fi
    echo
    echo "## Memory"
    grep -h -o -E "Memory limit: .*|Memory pressure.*" "$A" | sort -u | sed 's/^/- /' | head -10
    echo "- Other apps killed during the run (low memory; cached processes omitted):"
    grep -E "ActivityManager: Process .* has died: (prcp|prcl|fg|vis|svc|fore|percep)" "$L" | grep -v "$PKG" \
        | sed -E 's/.*Process ([^ ]+) \(pid [0-9]+\) has died: ([^ ]+).*/\1 (\2)/' | sort | uniq -c | sort -rn \
        | head -15 | sed 's/^ */  - /'
    grep -q -E "has died: (prcp|prcl|fg|vis|svc)" "$L" || echo "  - none"
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
    echo "App process ids during the run:$APP_PIDS"
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
