"""Plot actual RED/GREEN test outcomes; this is not an app screenshot."""
import json
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CASES = [
    ("JoinsIdentifierSplitAcrossRecords", "Split identifier"),
    ("RemovesLineCommentsBeforeJoiningRecords", "Split identifier + // comment"),
    ("SupportsLegacyBackslashComments", "Split identifier + backslash comment"),
    ("KeepsAcceptedBlockCommentsOnOriginalPath", "Accepted block comment preserved"),
    ("InvalidExpressionStillReportsFailure", "Invalid expression still rejected"),
]

def outcomes(name):
    text = (HERE / name).read_text()
    found = {}
    for state, case in re.findall(r"\[\s*(FAILED|OK)\s*\]\s+PerFrameRecordCompatibility\.(\w+)", text):
        found[case] = state == "OK"
    return [found[case] for case, _ in CASES]

before, after = outcomes("red.log"), outcomes("green.log")
assert before == [False, False, False, True, True] and all(after)
canvas = Image.new("RGB", (1380, 540), "white")
draw = ImageDraw.Draw(canvas)
font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
font = ImageFont.truetype(font_path, 26)
small = ImageFont.truetype(font_path, 20)
title = ImageFont.truetype(font_path, 34)
draw.text((30, 24), "Per-frame record fallback: actual test outcomes", fill="#172030", font=title)
for left, text in [(30, "Real per-frame compiler regression"), (1060, "Before"), (1210, "After")]:
    draw.text((left, 86), text, fill="#172030", font=font)
for i, ((_, label), b, a) in enumerate(zip(CASES, before, after)):
    top = 128 + i * 60
    draw.rectangle((30, top, 1340, top + 54), outline="#ccd2db")
    draw.text((45, top + 12), label, fill="#172030", font=font)
    for left, passed in [(1040, b), (1190, a)]:
        draw.rectangle((left, top, left + 149, top + 54), fill="#e2f2e3" if passed else "#f9dfdf", outline="#ccd2db")
        draw.text((left + 20, top + 12), "PASS" if passed else "FAIL", fill="#172030", font=font)
draw.text((30, 450), "PASS verifies the expected behavior, including correct rejection of invalid code.", fill="#172030", font=small)
draw.text((30, 480), "5/5 focused tests after; full host suite 179/179. Component evidence; no TV screenshot or corpus verdict.", fill="#172030", font=small)
canvas.save(HERE / "10-per-frame-record-fallback.png")
(HERE / "figure-data.json").write_text(json.dumps({"cases": [{"case": case, "before_pass": b, "after_pass": a}
    for (case, _), b, a in zip(CASES, before, after)], "kind": "measured-test-outcomes"}, indent=2) + "\n")
