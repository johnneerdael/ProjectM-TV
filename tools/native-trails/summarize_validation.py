#!/usr/bin/env python3
"""Verify the frozen 17×8 Native trails matrix and export diagnostic evidence."""
import argparse
import csv
import hashlib
import html
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import zipfile

import cv2
import numpy as np

spec = importlib.util.spec_from_file_location("native_trails_runner", Path(__file__).with_name("run_validation.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
from preset_lab.identity import canonical_json, digest, file_digest

METRIC_SIZE = (1182, 665)
LUMA = np.array([.2126, .7152, .0722], dtype=np.float32)
DARK_FLOOR = .001
WORKER_JAVA = "tools/core-corpus/android-worker/app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java"
CONTROLS = (("authored", "authored_repeat"), ("native_before", "native_off"),
            ("standard", "standard_default"))
DISPLAY = ("authored", "native_before", "standard", "medium", "high")
TIMING_SCOPE = "onDrawFrame plus glFinish; 360 frames; excludes capture/PNG I/O; emulator engine, not TV app fps"
# The completed focused-v1 run predates explicit Android-user scoping. Verify
# its immutable source explicitly; never silently waive a changed runner hash.
LEGACY_RUNNER_SHA256 = "a3cc20476cfa8e0cab65669b91e321e8963ed8bacbf9bd7bbd73791b405dd1be"
LEGACY_SOURCE_COMMIT = "a8a75f4435c80c46aaa99274f6007ac285170eeb"
# Historical plan identifies these witnesses as chaotic. This is a review cue,
# not a classifier or an excuse to waive identity checks.
CHAOTIC = {"TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk",
           "Flexi + orb + geiss - the computer is your friend trust the computer.milk"}


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def user_scope(protocol, legacy_runner=None):
    require(type(protocol.get("schema")) is int and protocol["schema"] in (1, 2), "Unsupported frozen protocol schema")
    if protocol["schema"] == 2:
        require(legacy_runner is None, "Use legacy source only with historical schema1")
        user_id = runner.validate_user_id(protocol.get("user_id"))
        require(protocol["runner_sha256"] == file_digest(Path(runner.__file__)), "Frozen runner changed")
        return {"mode": "explicit-user", "user_id": user_id, "runner_sha256": protocol["runner_sha256"]}
    require(legacy_runner is not None, "Historical schema1 requires explicit --legacy-runner source; it did not freeze the Android user")
    require("user_id" not in protocol and protocol["runner_sha256"] == LEGACY_RUNNER_SHA256,
            "Unknown legacy user scope/source")
    legacy_runner = Path(legacy_runner).resolve()
    require(file_digest(legacy_runner) == LEGACY_RUNNER_SHA256, "Frozen legacy runner checksum differs")
    return {"mode": "historical-user-zero", "user_id": 0, "runner_sha256": LEGACY_RUNNER_SHA256,
            "original_validator_source": str(legacy_runner), "source_commit": LEGACY_SOURCE_COMMIT,
            "limitation": "Static verification of previously verified user0 captures; original runtime commands were unscoped and schema1 did not capture the active user"}


def verify_worker(identity, presets):
    """Check the retained instrumented export, not the mutable task checkout."""
    runner.check_artifacts(identity)
    directory = Path(identity["aar"]).parent
    source = directory / "source"
    require(read(directory / "identity.json") == identity, "Frozen worker identity differs")
    require(identity["builder_sha256"] == file_digest(runner.ROOT / "tools/native-trails/build_validation.py"),
            "Frozen builder changed")
    require(identity["instrumentation_diff_sha256"] == file_digest(directory / "instrumentation.diff"),
            "Frozen instrumentation changed")
    require(identity["worker_java_sha256"] == file_digest(source / WORKER_JAVA), "Frozen worker Java changed")
    require(identity["source_files_sha256"], "Missing frozen source identities")
    for name, sha in identity["source_files_sha256"].items():
        require(file_digest(source / name) == sha, "Frozen source changed: " + name)
    for name, sha in identity["bridge_sha256"].items():
        require(file_digest(source / "core/src/main/cpp" / name) == sha, "Frozen bridge changed: " + name)
    patches = [{"name": path.name, "sha256": file_digest(path)}
               for path in sorted((source / "tools/projectm-patches").glob("*.patch"))]
    require(patches == identity["ordered_patches"], "Frozen patch series changed")
    require(identity["policy"] == "native" and identity["shipping_byte_identity"] is False,
            "Expected instrumented Native actual-core worker")
    with zipfile.ZipFile(identity["aar"]) as archive:
        natives = {name: hashlib.sha256(archive.read(name)).hexdigest()
                   for name in archive.namelist() if name.startswith("jni/") and name.endswith(".so")}
        assets = {name: hashlib.sha256(archive.read(name)).hexdigest()
                  for name in archive.namelist() if name.startswith("assets/")}
        require(natives == identity["native_sha256"], "Frozen native library identities differ")
        require(digest(assets) == identity["assets_sha256"], "Frozen packaged assets differ")
        for name, sha in presets.items():
            require(assets.get("assets/presets/" + name) == sha, "Packaged preset differs: " + name)


def verify_protocol(work, preset_root, names, legacy_runner=None):
    protocol = read(work / "protocol.json")
    user_scope(protocol, legacy_runner)
    require(len(names) == 17 and len(set(names)) == 17, "Expected the 17 selected presets")
    require(set(protocol["presets"]) == set(names), "Frozen selected presets differ")
    require(protocol["profiles"] == json.loads(canonical_json(runner.PROFILES)), "Frozen profiles differ")
    require(protocol["captures"] == runner.CAPTURES
            and protocol["frames"] == 480 and protocol["seed"] == 12345
            and protocol["clock"] == "frame/30.0", "Frozen capture/clock/seed protocol differs")
    require(protocol["pcm_sha256"] == file_digest(work / "audio.u8"), "Frozen PCM changed")
    for name, sha in protocol["presets"].items():
        require(file_digest(preset_root / name) == sha, "Frozen preset changed: " + name)
    require(set(protocol["workers"]) == {"baseline-native", "candidate-native"}, "Unexpected worker roles")
    for role, identity in protocol["workers"].items():
        require(identity["role"] == role, "Frozen worker role differs")
        verify_worker(identity, protocol["presets"])
    baseline = protocol["workers"]["baseline-native"]
    candidate = protocol["workers"]["candidate-native"]
    require(candidate["ordered_patches"][:-1] == baseline["ordered_patches"],
            "Candidate must retain baseline patches and add one production patch")
    require(candidate["assets_sha256"] == baseline["assets_sha256"], "Baseline/candidate assets differ")
    return protocol


def collect_matrix(work, preset_root, names, partial=False, legacy_runner=None):
    """Missing work is diagnostic only with partial; corrupted work always fails."""
    protocol = verify_protocol(work, preset_root, names, legacy_runner)
    scope = user_scope(protocol, legacy_runner)
    protocol_sha = digest(protocol)
    expected = {}
    for preset, sha in protocol["presets"].items():
        for profile in runner.PROFILES:
            key = digest({"protocol": protocol_sha, "preset": sha, "profile": profile[0]})
            require(key not in expected, "Duplicate job key")
            expected[key] = (preset, sha, profile)
    jobs_root = work / "jobs"
    actual = {path.name for path in jobs_root.iterdir()} if jobs_root.exists() else set()
    require(not actual - expected.keys(), "Unexpected job directories: " + str(sorted(actual - expected.keys())))
    missing = [{"preset": preset, "profile": profile[0]} for key, (preset, sha, profile) in expected.items()
               if not (jobs_root / key / "manifest.json").is_file() or not (jobs_root / key / "row.json").is_file()]
    # Fail before expensive decoding when a live run is not yet complete.
    require(partial or not missing, "Incomplete matrix: %d/136 jobs present" % (136 - len(missing)))
    jobs = {}
    environment = None
    for key, (preset, sha, profile) in expected.items():
        directory = jobs_root / key
        if not (directory / "manifest.json").is_file() or not (directory / "row.json").is_file():
            # A failed manifest must not disappear into partial-progress counts.
            if (directory / "manifest.json").is_file():
                require(read(directory / "manifest.json").get("status") == "ok", "Failed rendering in incomplete job")
            if (directory / "row.json").is_file():
                require(read(directory / "row.json").get("status") == "ok", "Failed rendering in incomplete row")
            continue
        label, role, width, height, rw, rh, level = profile
        identity = protocol["workers"][role]
        private = runner.private_directory(identity["package"], key, scope["user_id"])
        request = dict(runner.request(preset, width, height, rw, rh, level),
                       pcmPath=private + "/audio.u8", outputDir=private + "/output")
        require(read(directory / "request.json") == request, "Frozen request differs: " + key)
        manifest = runner.verify(directory, request, sha)
        for capture in manifest["captures"]:
            require((capture["width"], capture["height"]) == (width, height), "Capture metadata dimensions differ")
            # IMREAD_COLOR alone normalizes 16-bit inputs to RGB8. Retain the
            # corpus verifier's original-format gate for every control too.
            runner.corpus.decode_capture(directory / ("frame-%03d.png" % capture["frame"]), capture)
        require(manifest["applicationId"] == identity["package"]
                and manifest["device"]["fingerprint"] == protocol["fingerprint"]
                and manifest["pcmSha256"] == protocol["pcm_sha256"]
                and manifest["determinism"] == "instrumented-fixed-clock-seed"
                and manifest["fps"] == 30 and manifest["bundledPresetCount"] == 9606,
                "Manifest driver/PCM/worker/protocol identity differs: " + key)
        current = {field: manifest[field] for field in ("settings", "glRenderer", "glVendor", "glVersion")}
        require(environment is None or current == environment, "Mixed rendering environment/settings")
        environment = current
        require(manifest["timingScope"] == TIMING_SCOPE, "Unexpected serialized timing scope")
        for field in ("serializedFrameMeanMs", "serializedFrameP90Ms", "renderWallDurationMs",
                      "pssBeforeFramesKB", "pssAfterFramesKB"):
            value = manifest[field]
            require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
                    "Invalid timing/PSS measurement: " + field)
        require(manifest["serializedFrameMeanMs"] > 0 and manifest["serializedFrameP90Ms"] > 0,
                "Missing measured frame timings")
        if label in ("standard", "standard_default", "medium", "high"):
            wanted = "standard" if label == "standard_default" else label
            status = manifest["nativeTrailsStatus"].lower()
            require(wanted in status and "1280×720" in status and "canvas" in status and "fallback" not in status,
                    "Production path did not activate: " + manifest["nativeTrailsStatus"])
        row = read(directory / "row.json")
        expected_row = {"preset": preset, "profile": label, "key": key, "status": manifest["status"],
                        "frame_hashes": [c["rgbSha256"] for c in manifest["captures"]],
                        "trail_status": manifest.get("nativeTrailsStatus"), "duration_ms": manifest["renderWallDurationMs"],
                        "frame_mean_ms": manifest["serializedFrameMeanMs"], "frame_p90_ms": manifest["serializedFrameP90Ms"],
                        "pss_kb": manifest["pssAfterFramesKB"]}
        require(row == expected_row, "Row differs from verified manifest: " + key)
        jobs[preset, label] = {"directory": directory, "manifest": manifest, "row": row}
    checks = []
    for preset in names:
        for first, second in CONTROLS:
            if (preset, first) not in jobs or (preset, second) not in jobs:
                continue
            hashes = jobs[preset, first]["row"]["frame_hashes"]
            require(hashes == jobs[preset, second]["row"]["frame_hashes"],
                    "Identity mismatch: %s / %s / %s" % (preset, first, second))
            checks.append({"preset": preset, "profiles": [first, second], "matched_frames": runner.CAPTURES})
    require(digest(read(work / "protocol.json")) == protocol_sha, "Protocol changed during summary")
    return {"protocol": protocol, "protocol_sha256": protocol_sha, "jobs": jobs,
            "expected_jobs": 136, "verified_jobs": len(jobs), "missing_jobs": missing,
            "complete": not missing and len(jobs) == 136, "identity_checks": checks, "environment": environment,
            "user_scope": scope}


def decode(job, frame):
    capture = next(c for c in job["manifest"]["captures"] if c["frame"] == frame)
    return runner.corpus.decode_capture(job["directory"] / ("frame-%03d.png" % frame), capture)


def frame_metrics(rgb, authored):
    small = cv2.resize(rgb, METRIC_SIZE, interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    reference = cv2.resize(authored, METRIC_SIZE, interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    gray, authored_gray = small @ LUMA, reference @ LUMA
    luma, authored_luma = float(gray.mean()), float(authored_gray.mean())
    contrast, authored_contrast = float(gray.std()), float(authored_gray.std())
    return {"luma": luma, "authored_luma": authored_luma, "contrast": contrast,
            "authored_contrast": authored_contrast, "mae_authored": float(np.abs(small - reference).mean()),
            "luma_absolute_error": abs(luma - authored_luma), "contrast_absolute_error": abs(contrast - authored_contrast),
            "luma_ratio": luma / authored_luma if authored_luma >= DARK_FLOOR else None,
            "regularized_luma_ratio": (luma + DARK_FLOOR) / (authored_luma + DARK_FLOOR),
            "contrast_ratio": contrast / authored_contrast if authored_contrast >= DARK_FLOOR else None,
            "near_black_authored": authored_luma < DARK_FLOOR,
            "lap_native": float(cv2.Laplacian(rgb.astype(np.float32) @ LUMA / 255, cv2.CV_32F).var()),
            "lap_1182": float(cv2.Laplacian(gray, cv2.CV_32F).var())}


def visual_flags(preset, profiles):
    flags = []
    if preset in CHAOTIC:
        flags.append("known_chaotic_preset: compare structure by eye; MAE may reflect divergence")
    if profiles.get("authored", {}).get("mean", {}).get("near_black_authored"):
        flags.append("near_black_authored: raw luma ratio omitted; regularized ratio is diagnostic")
    return flags


def measurements(matrix, names):
    results = []
    for preset in names:
        if (preset, "authored") not in matrix["jobs"]:
            continue
        profiles = {}
        for label in DISPLAY:
            job = matrix["jobs"].get((preset, label))
            if job is None:
                continue
            frames = {str(frame): frame_metrics(decode(job, frame), decode(matrix["jobs"][preset, "authored"], frame))
                      for frame in runner.CAPTURES}
            fields = next(iter(frames.values())).keys()
            # Ratio-of-means is reported alongside per-frame ratios. Omit raw
            # ratios near black instead of averaging a subset of brighter frames.
            means = {field: float(np.mean([f[field] for f in frames.values()]))
                     for field in fields if field not in ("luma_ratio", "contrast_ratio", "near_black_authored")}
            means["luma_ratio"] = means["luma"] / means["authored_luma"] if means["authored_luma"] >= DARK_FLOOR else None
            means["contrast_ratio"] = means["contrast"] / means["authored_contrast"] if means["authored_contrast"] >= DARK_FLOOR else None
            means["regularized_luma_ratio"] = (means["luma"] + DARK_FLOOR) / (means["authored_luma"] + DARK_FLOOR)
            means["near_black_authored"] = means["authored_luma"] < DARK_FLOOR
            profiles[label] = {"mean": means, "frames": frames,
                               "timing": {key: job["manifest"][key] for key in
                                          ("serializedFrameMeanMs", "serializedFrameP90Ms", "renderWallDurationMs",
                                           "pssBeforeFramesKB", "pssAfterFramesKB")},
                               "key": job["row"]["key"], "frame_hashes": job["row"]["frame_hashes"],
                               "manifest_sha256": file_digest(job["directory"] / "manifest.json")}
        wins = {}
        if "native_before" in profiles:
            before = profiles["native_before"]["mean"]
            for label in ("standard", "medium", "high"):
                if label in profiles:
                    current = profiles[label]["mean"]
                    wins[label] = {metric: current[metric] < before[metric] for metric in
                                   ("mae_authored", "luma_absolute_error", "contrast_absolute_error")}
        costs = {}
        if "medium" in profiles and "high" in profiles:
            for field in ("serializedFrameMeanMs", "serializedFrameP90Ms"):
                medium, high = profiles["medium"]["timing"][field], profiles["high"]["timing"][field]
                costs[field] = {"medium": medium, "high": high, "high_minus_medium": high - medium,
                                "high_over_medium": high / medium}
        results.append({"preset": preset, "profiles": profiles, "wins_vs_native_before": wins,
                        "medium_high_cost_comparison": costs, "visual_review_required": True,
                        "visual_review_flags": visual_flags(preset, profiles)})
    return results


def diagnostics(results):
    over = {label: [] for label in ("standard", "medium", "high")}
    without_standard = {label: [] for label in ("medium", "high")}
    structure = []
    for row in results:
        profiles = row["profiles"]
        for label in over:
            if label not in profiles:
                continue
            ratio = profiles[label]["mean"]["luma_ratio"]
            if ratio is not None and ratio > 1.10:
                over[label].append(row["preset"])
                standard = profiles.get("standard", {}).get("mean", {}).get("luma_ratio")
                if label != "standard" and standard is not None and standard <= 1.10:
                    without_standard[label].append(row["preset"])
        if "native_before" in profiles:
            for label in ("standard", "medium", "high"):
                if label in profiles:
                    before, now = profiles["native_before"]["mean"], profiles[label]["mean"]
                    if now["mae_authored"] > before["mae_authored"] or now["contrast_absolute_error"] > before["contrast_absolute_error"]:
                        structure.append({"preset": row["preset"], "profile": label,
                                          "reason": "MAE or contrast error exceeds old Native; inspect structure/chaotic divergence"})
    return {"diagnostic_only": True, "luma_ratio_over_1_10": over,
            "luma_ratio_over_1_10_when_standard_is_not": without_standard,
            "structure_review_flags": structure,
            "mae_outlier_order": {label: sorted(
                [{"preset": r["preset"], "mae_authored": r["profiles"][label]["mean"]["mae_authored"]}
                 for r in results if label in r["profiles"]], key=lambda r: r["mae_authored"], reverse=True)
                for label in ("standard", "medium", "high")}}


def export_images(matrix, names, output):
    """Copy frame300 exactly; retain selected temporal previews and native crops."""
    sections = []
    for index, preset in enumerate(names):
        cells = []
        for frame in (120, 300, 479):
            for label in DISPLAY:
                job = matrix["jobs"].get((preset, label))
                if job is None:
                    continue
                rgb = decode(job, frame)
                stem = "%02d-%s-%03d" % (index, label, frame)
                preview = Path("images") / (stem + "-preview.png")
                crop = Path("images") / (stem + "-crop.png")
                height, width = rgb.shape[:2]
                region = rgb[height * 3 // 8:max(height * 5 // 8, height * 3 // 8 + 1),
                             width * 3 // 8:max(width * 5 // 8, width * 3 // 8 + 1)]
                for relative, pixels in ((preview, cv2.resize(rgb, (480, 270), interpolation=cv2.INTER_AREA)), (crop, region)):
                    require(cv2.imwrite(str(output / relative), cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR)), "Image export failed")
                if frame == 300:
                    full = Path("images") / (stem + "-full.png")
                    shutil.copyfile(job["directory"] / "frame-300.png", output / full)
                    require(file_digest(output / full) == job["manifest"]["captures"][5]["pngSha256"], "Copied full frame differs")
                    full_url = full.as_posix()
                else:
                    full_url = os.path.relpath(job["directory"] / ("frame-%03d.png" % frame), output)
                cells.append('<figure><a href="%s"><img src="%s" alt="%s"></a><figcaption>%s frame%s · <a href="%s">center crop</a> · <a href="%s">full PNG</a></figcaption></figure>' %
                             tuple(html.escape(str(x), quote=True) for x in (full_url, preview.as_posix(), label, label, frame, crop.as_posix(), full_url)))
        sections.append("<h2>%s</h2><div class=grid>%s</div>" % (html.escape(preset), "".join(cells)))
    return "".join(sections)


def summarize(work, output, partial=False, preset_root=None, names=None, legacy_runner=None):
    work, output = Path(work).resolve(), Path(output).resolve()
    preset_root = preset_root or runner.ROOT / "core/src/main/assets/presets"
    names = names or [name for name in Path(__file__).with_name("presets.txt").read_text().splitlines() if name]
    require(not output.exists(), "Output already exists; choose a fresh evidence directory")
    require(output != work and not output.is_relative_to(work / "jobs"), "Output must not replace raw jobs")
    matrix = collect_matrix(work, preset_root, names, partial=partial, legacy_runner=legacy_runner)
    rows = measurements(matrix, names)
    status = "partial_progress" if partial else "complete_verified_matrix"
    data = {key: value for key, value in matrix.items() if key not in ("jobs", "protocol")}
    protocol = matrix["protocol"]
    data.update(schema=1, status=status, final_evidence=not partial and matrix["complete"],
                scope="17 known presets × 8 profiles; not whole-corpus coverage", presets=rows,
                verified_rows=[dict(job["row"], manifest_sha256=file_digest(job["directory"] / "manifest.json"),
                                    request_sha256=job["manifest"]["requestSha256"],
                                    png_hashes=[c["pngSha256"] for c in job["manifest"]["captures"]])
                               for job in matrix["jobs"].values()],
                diagnostics=diagnostics(rows),
                identities={role: {key: identity[key] for key in
                                    ("source_commit", "apk_sha256", "aar_sha256", "assets_sha256", "ordered_patches",
                                     "builder_sha256", "instrumentation_diff_sha256", "worker_java_sha256")}
                            for role, identity in protocol["workers"].items()},
                capture_frames=runner.CAPTURES,
                metric_definition={"resolution": list(METRIC_SIZE), "resize": "OpenCV INTER_AREA RGB8 then float32 /255",
                                   "luma": "Rec709 .2126R+.7152G+.0722B (encoded RGB, no linear-light conversion)",
                                   "contrast": "population standard deviation of per-frame luma at common resolution",
                                   "aggregation": "equal mean across eight selected frames; luma/contrast ratios use means",
                                   "mae": "mean absolute RGB error against same-frame authored reference at common resolution",
                                   "sharpness": "OpenCV default 3x3 Laplacian variance on native-size normalized luma; resolution-dependent",
                                   "near_black_floor": DARK_FLOOR, "regularized_ratio": "(luma+.001)/(authored_luma+.001)",
                                   "acceptance": "No fixed numeric acceptance threshold; all images require visual review"},
                limitations=[protocol["limitations"], TIMING_SCOPE,
                             "Guest process PSS excludes some host GPU allocations; correlated observations, not all GPU memory",
                             "Only eight selected RGB hashes, not all 480 frames; chaotic divergence can inflate MAE",
                             "Authored profile renders at1280x720; metrics downsample all profiles to1182x665; historical numbers may use different authored sizes",
                             "Frame300 full PNGs and center-quarter crops are exported; other full-frame links require retained raw build captures"])
    output.mkdir(parents=True)
    (output / "images").mkdir()
    gallery = export_images(matrix, names, output)
    runner.write(output / "summary.json", data)
    fields = ["preset", "profile", "luma", "authored_luma", "luma_ratio", "regularized_luma_ratio", "near_black_authored",
              "contrast", "contrast_ratio", "mae_authored", "luma_absolute_error", "contrast_absolute_error", "lap_native", "lap_1182",
              "serializedFrameMeanMs", "serializedFrameP90Ms", "pssBeforeFramesKB", "pssAfterFramesKB"]
    with (output / "per-preset.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            for label, profile in row["profiles"].items():
                values = dict(preset=row["preset"], profile=label, **profile["mean"], **profile["timing"])
                writer.writerow({field: values.get(field) for field in fields})
    title = "PARTIAL PROGRESS — not final evidence" if partial else "Verified complete Native trails matrix"
    (output / "index.html").write_text('<!doctype html><meta charset="utf-8"><title>%s</title>'
        '<style>body{font-family:system-ui;background:#171717;color:#eee;margin:24px}a{color:#9cf}'
        '.grid{display:grid;grid-template-columns:repeat(5,minmax(160px,1fr));gap:12px}'
        'figure{margin:0}img{width:100%%;display:block}figcaption{font-size:12px}h2{margin-top:32px}'
        '@media(max-width:900px){.grid{grid-template-columns:repeat(2,1fr)}}</style>'
        '<h1>%s</h1><p>%d/136 verified jobs. Preview rows: frame120,300,479; columns: Authored, old Native, Standard, Medium, High. '
        'Same normalized center-quarter crop in every profile. Frame300 full PNGs are self-contained; other full links use retained raw captures.</p>'
        '<p>Metrics are diagnostics, not acceptance. Near-black and chaotic presets need visual review. Timings are serialized emulator engine work; '
        'guest PSS excludes some host GPU allocations.</p><p><a href="summary.json">JSON evidence</a> · <a href="per-preset.csv">Per-preset CSV</a></p>%s' %
        (html.escape(title), html.escape(title), matrix["verified_jobs"], gallery))
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path, help="fresh explicit evidence directory")
    parser.add_argument("--partial", action="store_true", help="progress diagnostics only; never final evidence")
    parser.add_argument("--legacy-runner", type=Path,
                        help="explicit immutable schema1 user0 runner source from a8a75f44; checksum required")
    args = parser.parse_args()
    try:
        result = summarize(args.work, args.out, args.partial, legacy_runner=args.legacy_runner)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, "Evidence rejected: %s\n" % error)
    print(canonical_json({key: result[key] for key in ("status", "final_evidence", "verified_jobs", "expected_jobs", "protocol_sha256")}))


if __name__ == "__main__":
    main()
