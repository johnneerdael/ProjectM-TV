#!/usr/bin/env python3
"""Generates app/src/main/assets/presets.idx: the sorted list of bundled presets with a memory
weight per preset.

The app reads this one small file at startup instead of listing ~10k assets, which is slow and
holds Android's asset-manager lock. Each line is "<file name>\\t<weight MB>". The weight is the
estimated memory a preset needs on top of what every preset needs (its frame buffers), so the app
can lower the resolution for heavy presets only:
  * images the preset loads, counted the way projectM does (MilkdropShader::GetReferencedSamplers:
    every "sampler_<name>" and "texsize_<name>" in the warp/comp shaders, used or not), at their
    decoded size (width x height x 4 bytes, no mipmaps);
  * random-image slots (sampler_rand00..15), each counted as the largest bundled image;
  * complex shaders (top 1% by size, or two or more loops): a fixed allowance for the GPU driver's
    compile memory. This part is an estimate; LOAD log lines on devices calibrate it.

Usage:
  tools/gen-preset-index.py           regenerate
  tools/gen-preset-index.py --check   fail if the committed index is out of date (used by CI)
"""
import math
import os
import re
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS = os.path.join(ROOT, "app/src/main/assets/presets")
TEXTURES = os.path.join(ROOT, "app/src/main/assets/textures")
INDEX = os.path.join(ROOT, "app/src/main/assets/presets.idx")

COMPLEX_SHADER_BYTES = 4200   # top 1% of warp+comp shader code
COMPLEX_SHADER_LOOPS = 2
COMPLEX_SHADER_MB = 32        # allowance for driver compile memory (to be calibrated)

SHADER_LINE = re.compile(r"^(warp_|comp_)\d+=")
BUILTIN = re.compile(r"^(main|blur[123]|noise_(lq|mq|hq)(_lite)?|noisevol_(lq|hq))$")
RANDOM = re.compile(r"^rand\d\d")
PREFIXES = ("fw_", "fc_", "pw_", "pc_", "wf_", "cf_", "wp_", "cp_")  # filter/wrap sampler prefixes


def image_size(path):
    """(width, height) of a JPEG or PNG, read from its header."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                return width, height
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    raise ValueError("unsupported image: " + path)


def image_bytes():
    sizes = {}
    for name in os.listdir(TEXTURES):
        width, height = image_size(os.path.join(TEXTURES, name))
        sizes[os.path.splitext(name)[0].lower()] = width * height * 4
    return sizes


def shader_code(text):
    code = "\n".join(line.split("=", 1)[1].lstrip("`") for line in text.splitlines() if SHADER_LINE.match(line))
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    return re.sub(r"//[^\n]*", "", code)


def weight_mb(text, images):
    code = shader_code(text)
    names = set(re.findall(r"sampler_(\w+)", code)) | set(re.findall(r"texsize_(\w+)", code))
    names.discard("state")
    total = 0
    randoms = set()
    for name in names:
        name = name.lower()
        if len(name) > 3 and name[:3] in PREFIXES:
            name = name[3:]
        if BUILTIN.match(name):
            continue
        if RANDOM.match(name):
            randoms.add(name[:6])
            continue
        total += images.get(name, 0)
    total += len(randoms) * max(images.values(), default=0)
    loops = len(re.findall(r"\bfor\s*\(", code))
    if len(code) >= COMPLEX_SHADER_BYTES or loops >= COMPLEX_SHADER_LOOPS:
        total += COMPLEX_SHADER_MB << 20
    return math.ceil(total / 2**20)


def build():
    images = image_bytes()
    lines = []
    for name in sorted(os.listdir(PRESETS), key=lambda n: n.encode()):
        if not name.lower().endswith(".milk"):
            continue
        with open(os.path.join(PRESETS, name), encoding="utf-8", errors="replace") as f:
            lines.append("%s\t%d\n" % (name, weight_mb(f.read(), images)))
    return "".join(lines)


def main():
    content = build()
    count = content.count("\n")
    heavy = sum(1 for line in content.splitlines() if int(line.rsplit("\t", 1)[1]) >= 5)
    if "--check" in sys.argv[1:]:
        with open(INDEX, encoding="utf-8") as f:
            if f.read() != content:
                print("presets.idx is out of date: run tools/gen-preset-index.py and commit the result",
                      file=sys.stderr)
                return 1
        print("presets.idx is up to date (%d presets, %d with a weight of 5 MB or more)" % (count, heavy))
        return 0
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(content)
    print("Wrote %s (%d presets, %d with a weight of 5 MB or more)" % (INDEX, count, heavy))
    return 0


if __name__ == "__main__":
    sys.exit(main())
