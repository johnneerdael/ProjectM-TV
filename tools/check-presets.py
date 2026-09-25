#!/usr/bin/env python3
"""Static checks of the bundled MilkDrop presets (app/src/main/assets/presets).

A preset fails when it:
  * cannot react to music: no audio variable (bass, mid, treb, vol, *_att) in any equation or
    shader, the main waveform hidden, and no custom waveform enabled;
  * uses a texture that is excluded (text, logos or photos of people), see EXCLUDED_TEXTURES;
  * uses an image texture that is not bundled in app/src/main/assets/textures.

Usage:
  tools/check-presets.py            report failing presets, exit 1 if any (used by CI)
  tools/check-presets.py --remove   delete failing presets (then run tools/gen-preset-index.py)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = os.path.join(ROOT, "app/src/main/assets/presets")
TEXTURES = os.path.join(ROOT, "app/src/main/assets/textures")

# Textures that show text, logos or people; presets using them are not bundled.
EXCLUDED_TEXTURES = {"suff5", "prayerwheel", "winamp_woofer", "vitriol", "kaite", "portal1", "portal2"}

AUDIO = re.compile(r"(?<![a-z0-9_])(bass|mid|treb|vol)(_att)?(?![a-z0-9_])")
CODE_LINE = re.compile(r"^(per_frame|per_pixel|per_frame_init|wave_\d+_per|shape_\d+_per|warp_|comp_)\w*=")
SAMPLER = re.compile(r"sampler_(?:(?:fw|fc|pw|pc|wf|cf|wp|cp)_)?([a-z0-9_]+)")
PREFIX = r"(?:(?:fw|fc|pw|pc|wf|cf|wp|cp)_)?"
ALIAS = re.compile(r"#define\s+sampler_" + PREFIX + r"(\w+)\s+sampler_" + PREFIX + r"(\w+)")
# Built-in samplers, random textures (rand00..15) and HLSL's "sampler_state" keyword.
BUILTIN = re.compile(r"^(main|blur[123]|noise_(lq|mq|hq)(_lite)?|noisevol_(lq|hq)|pw_\w+|fc_main|fw_main|pc_main|"
                     r"rand\d\d(_\w+)?|state)$")
WAVE_HIDDEN_IN_CODE = re.compile(r"(?<![a-z_])wave_a\s*=\s*0(\.0*)?\s*;")


def number(text, key, default):
    match = re.search(r"^" + key + r"=([-0-9.eE]+)", text, re.M)
    return float(match.group(1)) if match else default


def problems(text, bundled):
    text = text.lower()
    code = "\n".join(line.split("=", 1)[1] for line in text.splitlines() if CODE_LINE.match(line))
    found = []

    wave_hidden = number(text, "fwavealpha", 1.0) <= 0.01 or WAVE_HIDDEN_IN_CODE.search(code) is not None
    custom_waves = any(number(text, "wavecode_%d_enabled" % i, 0) > 0 for i in range(4))
    if not AUDIO.search(code) and wave_hidden and not custom_waves:
        found.append("cannot react to music")

    # A texture counts when its sampler is declared and used (a declaration alone draws nothing),
    # directly or through "#define sampler_pic sampler_cells" (then the alias must be used).
    def mentions(name):
        return len(re.findall(r"sampler_(?:(?:fw|fc|pw|pc|wf|cf|wp|cp)_)?" + name + r"(?![a-z0-9_])", text))

    aliases = dict(ALIAS.findall(text))
    names = {n for n in SAMPLER.findall(text) if not BUILTIN.match(n) and n not in aliases}
    names = {n for n in names if mentions(n) >= 2}
    names |= {target for alias, target in aliases.items() if not BUILTIN.match(target) and mentions(alias) >= 2}
    excluded = sorted(names & EXCLUDED_TEXTURES)
    if excluded:
        found.append("uses excluded texture " + ", ".join(excluded))
    missing = sorted(names - bundled - EXCLUDED_TEXTURES)
    if missing:
        found.append("uses missing texture " + ", ".join(missing))
    return found


def main():
    remove = "--remove" in sys.argv[1:]
    bundled = {os.path.splitext(f)[0].lower() for f in os.listdir(TEXTURES)}
    leftover = sorted(bundled & EXCLUDED_TEXTURES)
    failing = []
    for name in sorted(os.listdir(PRESETS)):
        if not name.lower().endswith(".milk"):
            continue
        path = os.path.join(PRESETS, name)
        with open(path, encoding="utf-8", errors="replace") as f:
            found = problems(f.read(), bundled)
        if found:
            failing.append((name, found))
            if remove:
                os.remove(path)
    for name, found in failing:
        print("%s: %s" % (name, "; ".join(found)))
    if leftover:
        print("excluded textures still bundled: " + ", ".join(leftover))
    if remove:
        print("Removed %d presets. Now run tools/gen-preset-index.py" % len(failing))
        return 0
    print("%d presets fail the checks" % len(failing) if failing else "All presets pass the checks")
    return 1 if failing or leftover else 0


if __name__ == "__main__":
    sys.exit(main())
