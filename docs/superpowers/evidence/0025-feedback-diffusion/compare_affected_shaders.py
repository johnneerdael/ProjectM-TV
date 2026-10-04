"""Compare brightness outliers with the repeatable measured control population.

Lexical features describe source presence, not executed branches or causal gates.
Use first-occurrence preset keys, numbered shader assembly and comment stripping.
"""
import hashlib
import json
import re
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent
REPO = EVIDENCE.parents[3]


def sections(path):
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values.setdefault(key.strip().lower(), value.lstrip("`"))
    result = {}
    for section in ["warp", "comp"]:
        lines = [(int(key.rsplit("_", 1)[1]), value) for key, value in values.items()
                 if re.fullmatch(section + r"_\d+", key)]
        source = "\n".join(value for _, value in sorted(lines))
        result[section] = re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)
    return result


def features(shaders):
    warp, comp = shaders["warp"], shaders["comp"]
    main = r"\b(?:GetPixel|GetMain)\s*\(|\bsampler_(?:[fp][cw]_)?main\b"
    blur = r"\bGetBlur[123]\s*\(|\bsampler_blur[123]\b"
    return {
        "custom_warp": bool(warp.strip()),
        "warp_uses_blur": bool(re.search(blur, warp)),
        "warp_uses_point_main": bool(re.search(r"\bsampler_p[cw]_main\b", warp)),
        "warp_uses_max": bool(re.search(r"\bmax\s*\(", warp)),
        "warp_uses_linear_alias": bool(re.search(r"\bsampler_f[cw]_main\b", warp)),
        "composite_uses_main_and_blur": bool(re.search(main, comp) and re.search(blur, comp)),
        "composite_uses_pow": bool(re.search(r"\bpow\s*\(", comp)),
        "composite_uses_saturate": bool(re.search(r"\bsaturate\s*\(", comp)),
    }


def main():
    measured = {}
    for dataset in ["set24", "royal191", "gradient", "regressions"]:
        report = json.loads((EVIDENCE / f"{dataset}-corrected-12s-report.json").read_text())
        for name, row in report["presets"].items():
            runs = row["runs"]
            stable = row["authored_deterministic"] and all(
                runs[key]["sha256"] == runs[key + "-repeat"]["sha256"]
                for height in [1330, 2160]
                for key in [f"baseline-{height}", f"corrected-{height}"]
            )
            if stable:
                measured.setdefault(name, row)
    audit = json.loads((EVIDENCE / "brightness-audit-12s.json").read_text())
    affected = {row["preset"] for row in audit if row["size_band_max"] is not None
                and row["brightness_error_increase"] > row["size_band_max"]}
    unclassified = {row["preset"] for row in audit if row["size_band_max"] is None}
    assert affected <= measured.keys()
    records, groups = {}, {}
    for name in sorted(measured):
        shaders = sections(REPO / "core/src/main/assets/presets" / name)
        canonical = [re.sub(r"\s+", "", shaders[section]) for section in ["warp", "comp"]]
        digest = hashlib.sha256(json.dumps(canonical).encode()).hexdigest()
        group = "affected" if name in affected else "unclassified" if name in unclassified else "other_repeatable"
        records[name] = {"group": group, "features": features(shaders), "shader_pair_sha256": digest}
        groups.setdefault(digest, []).append(name)
    population = {group: [r for r in records.values() if r["group"] == group]
                  for group in ["affected", "other_repeatable", "unclassified"]}
    counts = {feature: {group: {"present": sum(r["features"][feature] for r in rows), "total": len(rows)}
                        for group, rows in population.items()}
              for feature in next(iter(records.values()))["features"]}
    output = {"protocol": "12s, unique filenames across overlapping sets, all authored/baseline/candidate repeat hashes stable; lexical features are not causal proof", "counts": counts, "presets": records,
              "identical_shader_pairs": [names for names in groups.values() if len(names) > 1 and affected.intersection(names)]}
    (EVIDENCE / "affected-shader-comparison.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"counts": counts, "identical_shader_pairs": output["identical_shader_pairs"]}, indent=2))


if __name__ == "__main__":
    main()
