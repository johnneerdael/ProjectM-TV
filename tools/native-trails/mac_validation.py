#!/usr/bin/env python3
"""Risk-selected direct macOS OpenGL validation; historical Android data selects only."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import select
import shutil
import subprocess
import sys
import threading
import time

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/preset-lab/src"))
from preset_lab.identity import canonical_json, digest, file_digest
from preset_lab.build_worker import NATIVE

worker_spec = importlib.util.spec_from_file_location("mac_worker_adapter", Path(__file__).with_name("mac_worker.py"))
worker_adapter = importlib.util.module_from_spec(worker_spec)
worker_spec.loader.exec_module(worker_adapter)

spec = importlib.util.spec_from_file_location("trails_metrics", Path(__file__).with_name("summarize_validation.py"))
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
CAPTURES = [120, 150, 180, 210, 239, 300, 390, 479]
PROFILES = [("authored", "baseline", 1280, 720, 0, 0, -1),
            ("native_before", "baseline", 3840, 2160, 1024, 768, -1),
            ("native_off", "candidate", 3840, 2160, 1024, 768, -1),
            ("standard", "candidate", 3840, 2160, 1280, 720, 0),
            ("medium", "candidate", 3840, 2160, 1280, 720, .5),
            ("high", "candidate", 3840, 2160, 1280, 720, 1)]
OLD_PROTOCOL = "369263c90d7089ebfebb6fcf3609b5f2554899e26bf7ef321cad1800f36b8180"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(canonical_json(value) + "\n")
    temporary.replace(path)


def features(text):
    """Selection cues only, not a MilkDrop parser or an execution diagnosis."""
    lower = text.lower()
    def value(name, default=0):
        match = re.search(r"(?mi)^\s*" + name + r"\s*=\s*([-+\d.eE]+)", text)
        try:
            result = float(match[1]) if match else default
            return result if math.isfinite(result) else default
        except ValueError:
            return default
    warp, comp = int(value("fWarpShaderVersion")), int(value("fCompShaderVersion"))
    blur = sum(lower.count(token) for token in ("getblur", "blur1", "blur2", "blur3"))
    motion = value("bMotionVectorsOn") > 0 or value("bMvOn") > 0 or value("mv_a") > 0
    feedback = sum(lower.count(token) for token in ("sampler_main", "tex2d", "ret", "decay", "warp_", "zoom", "rot"))
    return {"shader_stratum": "%d/%d/%d/%d" % (warp, comp, bool(blur), bool(motion)),
            "feedback_score": feedback + max(value("fDecay") - .9, 0) * 100,
            "motion_score": int(motion) * (1 + value("nMotionVectorsX") + value("nMotionVectorsY")),
            "blur_score": blur, "complexity": len(text), "warp_shader": warp, "comp_shader": comp}


def classify_failure(runs):
    diagnostics, transport, render, success = [], False, False, False
    for row in runs:
        result = row.get("result", {})
        error = str(row.get("error", result.get("error", "")))
        successful = row.get("status") == "success" and result.get("status") == "success"
        success |= successful
        if not successful:
            is_transport = bool(re.search(r"pull failed|transport|offline|device.*closed|adb|broken pipe|timeout", error, re.I)) and result.get("status") != "failed"
            transport |= is_transport
            render |= result.get("status") == "failed"
            diagnostics.append({"status": row.get("status"), "result_status": result.get("status"), "error": error,
                                "kind": "transport" if is_transport else "render_or_preset" if result.get("status") == "failed" else "unknown"})
    category = ("mixed_transport_and_render_failure" if transport and render else
                "transport_with_successful_repeat" if transport and success else
                "transport_failure" if transport else "render_or_preset_failure" if render else "unclassified_failure")
    return {"classification": category, "diagnostics": diagnostics, "successful_repeat": success}


def load_historical(corpus, assets, expected_count=9606):
    corpus, assets = Path(corpus).resolve(), Path(assets).resolve()
    index_path = corpus / "baseline-completion-index.json"
    index, protocol, inventory = read(index_path), read(corpus / "protocol.json"), read(corpus / "inventory.json")
    require(index["complete_coverage"] and len(index["rows"]) == expected_count, "Historical index is incomplete")
    require(digest({k: v for k, v in protocol.items() if k != "sha256"}) == protocol["sha256"] == index["protocol_sha256"],
            "Historical protocol identity changed")
    if expected_count == 9606:
        require(protocol["sha256"] == OLD_PROTOCOL and index["statuses"] == {"failed": 67, "success": 9539},
                "Unexpected historical baseline scope")
    require(file_digest(corpus / "inventory.json") == index["inventory_sha256"], "Historical inventory identity changed")
    require(protocol["config"]["width"] == 2364 and protocol["config"]["height"] == 1330, "Historical baseline is not the selection source")
    patches = protocol["roles"]["baseline"]["backend_identity"]["ordered_patches"]
    require([int(p["name"][:4]) for p in patches] == list(range(1, 25)), "Historical source is not patches1–24")
    inventory_map = {r["path"]: r for r in inventory["presets"]}
    require(len(inventory_map) == expected_count, "Historical inventory duplicates or incomplete")
    records = []
    # One bounded metadata pass: no old capture decoding, device access or replay.
    for row in index["rows"]:
        preset = row["preset"]
        name = preset["path"]
        require(row["protocol_sha256"] == protocol["sha256"] and inventory_map.get(name) == preset,
                "Historical preset join changed: " + name)
        path = assets / name
        require(path.is_relative_to(assets) and file_digest(path) == preset["sha256"], "Historical/current preset changed: " + name)
        runs, hashes = [], []
        # Read both repeats only for failure classification. One successful row
        # supplies retained native metrics for ranking, never current fidelity.
        for relative in row["runs"] if row["status"] != "success" else row["runs"][:1]:
            run_path = corpus / relative
            require(run_path.resolve().is_relative_to(corpus), "Historical path escaped corpus")
            run = read(run_path)
            require(run["preset"] == preset and run["protocol_sha256"] == protocol["sha256"], "Historical run join changed")
            runs.append(run)
            hashes.append({"path": relative, "sha256": file_digest(run_path)})
        successful = next((r for r in runs if r.get("status") == "success" and r.get("result", {}).get("status") == "success"), None)
        files = successful["result"].get("selected_files", []) if successful else []
        native = [f["metrics"] for f in files if "metrics" in f]
        ranking = {field: float(np.mean([r.get(field, 0) for r in native])) if native else None
                   for field in ("native_luma_mean", "native_clipped_fraction", "native_bright_fraction")}
        record = {"preset": name, "preset_sha256": preset["sha256"], "historical_status": row["status"],
                  "historical_runs": hashes, "historical_ranking_metrics": ranking,
                  "features": features(path.read_text(errors="replace"))}
        if row["status"] != "success":
            record["historical_failure"] = classify_failure(runs)
        records.append(record)
    require(len({r["preset"] for r in records}) == expected_count, "Duplicate historical preset")
    return {"records": records, "provenance": {"corpus": str(corpus), "index_sha256": file_digest(index_path),
            "protocol_sha256": protocol["sha256"], "inventory_sha256": index["inventory_sha256"],
            "render_size": [2364, 1330], "patches": "0001–0024", "statuses": index["statuses"],
            "use": "Risk selection only; old emulator/1330 data is not a fresh4K or host fidelity baseline"}}


def stratified(records, count, salt):
    strata = defaultdict(list)
    for record in records:
        strata[record["features"]["shader_stratum"]].append(record)
    for values in strata.values():
        values.sort(key=lambda r: digest({"salt": salt, "preset_sha256": r["preset_sha256"]}))
    selected = []
    while len(selected) < count and any(strata.values()):
        for key in sorted(strata):
            if strata[key] and len(selected) < count:
                selected.append(strata[key].pop(0))
    return selected


def select_presets(history, witnesses, count=160):
    require(128 <= count <= 192, "Select128–192 presets; no whole-corpus replay")
    records = history["records"]
    by_name = {r["preset"]: r for r in records}
    require(set(witnesses) <= by_name.keys(), "Known witness absent from historical/current join")
    chosen = {}
    def add(record, reason):
        name = record["preset"]
        if name not in chosen:
            chosen[name] = dict(record, reasons=[])
        if reason not in chosen[name]["reasons"]:
            chosen[name]["reasons"].append(reason)
    for record in records:
        if record["historical_status"] != "success": add(record, "all_historical_failed")
    for name in witnesses: add(by_name[name], "known_witness")
    require(len(chosen) <= count - 16, "Mandatory risks leave insufficient stratified sample")
    risk_budget = count - 24
    categories = [("historical_dark", "native_luma_mean", False), ("historical_bright", "native_luma_mean", True),
                  ("historical_clipped", "native_clipped_fraction", True), ("historical_bright_pixels", "native_bright_fraction", True),
                  ("complex_feedback", "feedback_score", True), ("motion_vectors", "motion_score", True),
                  ("blur", "blur_score", True), ("complex_source", "complexity", True)]
    tails = []
    for reason, field, reverse in categories:
        source = "historical_ranking_metrics" if reason.startswith("historical") else "features"
        eligible = [r for r in records if r[source].get(field) is not None]
        if reason in ("historical_clipped", "historical_bright_pixels", "motion_vectors", "blur"):
            eligible = [r for r in eligible if r[source][field] > 0]
        ordered = sorted(eligible, key=lambda r: ((-1 if reverse else 1) * r[source][field], r["preset_sha256"]))
        tails.append((reason, ordered[:8]))
    # Balanced rounds reserve fresh representatives for later categories even
    # when mandatory failures consume most of the bounded risk budget.
    for rank in range(8):
        for reason, ordered in tails:
            if rank >= len(ordered): continue
            record = ordered[rank]
            if record["preset"] in chosen or len(chosen) < risk_budget: add(record, reason)
    remaining = [r for r in records if r["preset"] not in chosen]
    for record in stratified(remaining, count - len(chosen), "native-trails-wide-v1"):
        add(record, "stratified_sample")
    require(len(chosen) == count, "Insufficient joined presets for requested selection")
    selected = [chosen[name] for name in sorted(chosen)]
    repeats = [r["preset"] for r in stratified(selected, math.ceil(count / 10), "authored-repeat-v1")]
    return {"schema": 1, "count": count, "historical": history["provenance"], "presets": selected,
            "authored_repeats": repeats, "selection_policy": "all failed+witnesses;balanced rounds up to8 each risk tail;at least24 deterministic shader/blur/motion stratified samples",
            "reason_counts": dict(Counter(reason for r in selected for reason in r["reasons"])),
            "repeat_policy": "ceil10% deterministic stratified authored repeats; pilot repeats every preset",
            "limitations": "Risk-enriched subset; no statistically representative or whole-corpus certification"}


def verify_job(directory, request, reduced_size=(1182, 665)):
    directory = Path(directory)
    require(read(directory / "request.json") == request, "Frozen job request changed")
    require((directory / "receipt.sha256").read_text().strip() == file_digest(directory / "receipt.json"), "Receipt checksum changed")
    manifest, receipt = read(directory / "manifest.json"), read(directory / "receipt.json")
    require(receipt["request_sha256"] == digest(request), "Receipt request identity differs")
    require(receipt["worker_manifest_sha256"] == digest(manifest), "Worker manifest identity differs")
    require(manifest["status"] == receipt["status"] == "success" and manifest["frames"] == 480
            and manifest["gl_checks"] == 480 and manifest["gl_error_frames"] == 0,
            "Failed or incomplete worker GL/rendering checks")
    cfg = request["config"]
    require(manifest["identity"] == request["identity"] and manifest["seed"] == cfg["seed"]
            and manifest["fps"] == cfg["fps"] == 30 and (manifest["width"], manifest["height"]) == (cfg["width"], cfg["height"]),
            "Worker request/source identity differs")
    require(manifest["captures"] == CAPTURES and [c["frame"] for c in receipt["captures"]] == CAPTURES,
            "Incomplete selected capture sequence")
    require(manifest["selected_bytes"] == len(CAPTURES) * cfg["width"] * cfg["height"] * 3, "Incomplete native RGB stream")
    require(bool(manifest["gl_renderer"]) and bool(manifest["gl_version"]), "Missing host GL driver identity")
    if cfg["feedback_detail"] >= 0:
        require(manifest["detail_statuses"] == [3], "Enabled profile inactive or shader/resource fallback")
    else:
        require(manifest["detail_statuses"] == [-1], "Off profile unexpectedly activated detail")
    for capture in receipt["captures"]:
        path = directory / capture["path"]
        require(path.resolve().is_relative_to(directory.resolve()), "Capture path escaped job")
        require(file_digest(path) == capture["png_sha256"], "Retained PNG checksum differs")
        decoded = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        require(decoded is not None and decoded.dtype == np.uint8 and decoded.shape == (reduced_size[1], reduced_size[0], 3),
                "Retained PNG dimensions/format differ")
        rgb = cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)
        require(hashlib.sha256(rgb.tobytes()).hexdigest() == capture["reduced_rgb_sha256"], "Reduced RGB hash differs")
        require(re.fullmatch("[0-9a-f]{64}", capture["native_rgb_sha256"]) is not None, "Invalid native RGB hash")
        if "native_png_sha256" in capture:
            full = directory / "frame-300-native.png"
            require(file_digest(full) == capture["native_png_sha256"], "Native PNG checksum changed")
            decoded = cv2.imread(str(full), cv2.IMREAD_UNCHANGED)
            require(decoded is not None and decoded.dtype == np.uint8 and decoded.shape == (cfg["height"], cfg["width"], 3), "Native PNG dimensions/format differ")
            require(hashlib.sha256(cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB).tobytes()).hexdigest() == capture["native_rgb_sha256"], "Retained native RGB hash differs")
    return receipt


def compare_identity(first, second, label):
    require(len(first["captures"]) == len(second["captures"]) == 8 and
            [c["native_rgb_sha256"] for c in first["captures"]] == [c["native_rgb_sha256"] for c in second["captures"]],
            "Native selected-frame identity mismatch: " + label)


def freeze(path, protocol):
    if Path(path).exists():
        require(read(path) == protocol, "Frozen protocol differs; use a fresh run name")
    else:
        write(path, protocol)
    return protocol


def audit_results(expected, results, partial=False):
    keys = {r["key"] for r in expected}
    require(len(keys) == len(expected) and not results.keys() - keys, "Unexpected/duplicate result jobs")
    missing = keys - results.keys()
    require(partial or not missing, "Incomplete matrix: %d/%d terminal jobs" % (len(results), len(keys)))
    failed = sum(r["status"] != "success" for r in results.values())
    return {"expected_jobs": len(keys), "terminal_jobs": len(results), "failed_jobs": failed,
            "terminal_complete": not missing, "fidelity_complete": not missing and failed == 0,
            "status": "partial_progress" if partial else "complete_terminal_matrix_with_failures" if failed else "complete_verified_matrix"}


def tree_hashes(root):
    return {p.relative_to(root).as_posix(): file_digest(p) for p in sorted(Path(root).rglob("*")) if p.is_file()}


def prepare_workers(work, exports, source_commit):
    """Reuse verified _instrument exports; never touch the live submodule or Git."""
    require(platform.system() == "Darwin" and platform.machine() == "arm64", "Use direct Apple Silicon macOS host")
    work, exports = Path(work).resolve(), Path(exports).resolve()
    output = work / "workers"
    output.mkdir(parents=True, exist_ok=False)
    identities = {}
    for role, export_role in (("baseline", "baseline-native"), ("candidate", "candidate-native")):
        frozen = read(exports / export_role / "identity.json")
        count = len(frozen["ordered_patches"])
        selected = {name: file_digest(ROOT / "core/src/main/assets/presets" / name)
                    for name in Path(__file__).with_name("presets.txt").read_text().splitlines() if name}
        metrics.verify_worker(frozen, selected)
        require(count >= 41 and
                [int(p["name"][:4]) for p in frozen["ordered_patches"]] == list(range(1, count + 1)), "Unexpected shipping patch series")
        if role == "candidate":
            require(frozen["source_commit"].startswith(source_commit), "Candidate source commit differs")
            require(frozen["ordered_patches"][:-1] == identities["baseline"]["ordered_patches"], "Candidate patch prefix differs")
        original = exports / export_role / "snapshots/engines" / digest(frozen["engine_identity"])
        require(read(original / "preset-lab-identity.json") == frozen["engine_identity"], "Frozen _instrument snapshot differs")
        # Android changes only the copied clock hook to atomic. Verify all other
        # recorded engine sources against this original prepare_engine snapshot.
        for name, sha in frozen["source_files_sha256"].items():
            prefix = "third_party/projectm/"
            if name.startswith(prefix) and name != prefix + "src/libprojectM/analysis_hooks.hpp":
                require(file_digest(original / name[len(prefix):]) == sha, "Frozen engine source differs: " + name)
        require(file_digest(original / "src/libprojectM/analysis_hooks.hpp") == file_digest(NATIVE / "analysis_hooks.hpp"),
                "Frozen host clock/seed instrumentation differs")
        destination = output / role
        engine, native = destination / "engine", destination / "native"
        shutil.copytree(original, engine)
        shutil.copytree(NATIVE, native)
        (native / "worker.cpp").write_text(worker_adapter.adapt_worker((native / "worker.cpp").read_text(), CAPTURES))
        cmake = native / "CMakeLists.txt"
        cmake.write_text(cmake.read_text() + "\ntarget_compile_definitions(preset-lab-worker PRIVATE NATIVE_TRAILS_DETAIL_AVAILABLE=%d)\n" % (role == "candidate"))
        build = destination / "build"
        with (destination / "build.log").open("w") as log:
            subprocess.run(["cmake", "-S", str(native), "-B", str(build), "-DPROJECTM_SOURCE=" + str(engine),
                            "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_OSX_ARCHITECTURES=arm64"], check=True, stdout=log, stderr=subprocess.STDOUT)
            subprocess.run(["cmake", "--build", str(build), "-j", "4"], check=True, stdout=log, stderr=subprocess.STDOUT)
        executable = build / "preset-lab-worker"
        identities[role] = {"path": str(executable), "sha256": file_digest(executable), "source_commit": frozen["source_commit"],
                            "ordered_patches": frozen["ordered_patches"], "engine_identity": frozen["engine_identity"],
                            "engine_root": str(engine), "engine_sources": tree_hashes(engine), "worker_root": str(native),
                            "worker_sources": tree_hashes(native), "backend": "direct macOS SDL/OpenGL;Apple M4 host GL implementation,not native Metal engine",
                            "source_export": str(original), "builder_sha256": file_digest(Path(__file__)),
                            "instrumentation": "preset_lab.build_worker._instrument retained verified snapshot;frame/30;float PCM latest512",
                            "adapter_sha256": file_digest(Path(__file__).with_name("mac_worker.py"))}
        write(destination / "identity.json", identities[role])
        print("Built direct host " + role, flush=True)
    write(work / "workers.json", identities)
    return identities


def select_to_file(corpus, assets, output, count):
    require(not Path(output).exists(), "Selection output already exists")
    history = load_historical(corpus, assets)
    names = [name for name in Path(__file__).with_name("presets.txt").read_text().splitlines() if name]
    selection = select_presets(history, names, count)
    selection["selector_sha256"] = file_digest(Path(__file__))
    write(output, selection)
    Path(output).with_suffix(".txt").write_text("\n".join(r["preset"] for r in selection["presets"]) + "\n")
    print(canonical_json({"count": selection["count"], "failure_classes": dict(Counter(
        r["historical_failure"]["classification"] for r in selection["presets"] if "historical_failure" in r)),
        "reasons": selection["reason_counts"], "selection_sha256": digest(selection)}), flush=True)
    return selection


def initialize_run(work, selection_path, run_name, pilot, parallel, retain_full):
    require(2 <= parallel <= 4, "Use2–4 separate process/context workers")
    require(re.fullmatch(r"[A-Za-z0-9_-]+", run_name) is not None, "Use a simple unique run name")
    work, selection_path = Path(work).resolve(), Path(selection_path).resolve()
    selection = read(selection_path)
    require(selection["count"] == len(selection["presets"]) and 128 <= selection["count"] <= 192, "Invalid frozen selection scope")
    workers = read(work / "workers.json")
    for role, identity in workers.items():
        require(identity == read(work / "workers" / role / "identity.json"), "Worker identity changed")
        require(file_digest(Path(identity["path"])) == identity["sha256"], "Compiled worker changed")
        require(tree_hashes(Path(identity["engine_root"])) == identity["engine_sources"], "Frozen engine source changed")
        require(tree_hashes(Path(identity["worker_root"])) == identity["worker_sources"], "Frozen worker source changed")
    names = [r["preset"] for r in selection["presets"]]
    if pilot:
        names = ["Waltra - Heaven Liquid.milk", "Hexcollie - Julian Shader Wars4 nz+ sports fart.milk",
                 "$$$ Royal - Mashup (191).milk", "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk", "Fed - quadratrail.milk"]
        require(set(names) <= {r["preset"] for r in selection["presets"]}, "Pilot witnesses absent")
    records = {r["preset"]: r for r in selection["presets"] if r["preset"] in names}
    for name, record in records.items():
        require(file_digest(ROOT / "core/src/main/assets/presets" / name) == record["preset_sha256"], "Selected preset changed")
    pcm, _ = metrics.runner.corpus.signal()
    pcm_path = work / "audio-float.f32"
    if not pcm_path.exists(): pcm_path.write_bytes(pcm)
    require(file_digest(pcm_path) == hashlib.sha256(pcm).hexdigest(), "Frozen float PCM changed")
    textures = ROOT / "core/src/main/assets/textures"
    repeats = names if pilot else selection["authored_repeats"]
    protocol = {"schema": 1, "backend": "direct-macOS-SDL-OpenGL", "host": platform.platform(),
                "machine": platform.machine(), "source_scope": ";".join("shipping patches1–%d %s" % (len(identity["ordered_patches"]), role) for role, identity in workers.items()),
                "workers": workers, "selection_file": str(selection_path), "selection_sha256": file_digest(selection_path),
                "records": records, "presets": names, "authored_repeats": repeats,
                "profiles": json.loads(canonical_json(PROFILES)), "parallel_contexts": parallel, "retain_full_frame300": pilot or retain_full,
                "pcm_path": str(pcm_path), "pcm_sha256": file_digest(pcm_path), "frames": 480, "fps": 30,
                "clock": "frame/30.0", "seed": 12345, "capture_frames": CAPTURES,
                "texture_root": str(textures), "textures_sha256": digest(tree_hashes(textures)),
                "runner_sha256": file_digest(Path(__file__)),
                "metrics_source_sha256": file_digest(Path(metrics.__file__)),
                "adapter_sha256": file_digest(Path(__file__).with_name("mac_worker.py")),
                "audio_scope": "Same bass.30 synthetic float32 bytes;host PCM().Add latest512;not Android uint8/JNI numerical parity",
                "capture_trust_boundary": "Native RGB hashes/metrics computed from eight streamed full-size RGB8 frames from checksum-verified executable/request. Resume verifies worker manifest and all retained reduced PNG bytes; unavailable native bytes cannot be independently rehashed from previews.",
                "coverage": "five-preset pilot" if pilot else "risk-enriched160subset" if len(names) == 160 else "risk-enriched subset",
                "limitations": "Historical patches1–24 emulator1330 data selects risks only;new host captures compare fresh before/off/authored/levels. No full9606 replay,Android AAR fidelity,TV FPS or native Metal engine claim."}
    directory = work / "runs" / run_name
    directory.mkdir(parents=True, exist_ok=True)
    freeze(directory / "protocol.json", protocol)
    return directory, protocol


def requests_for(directory, protocol):
    requests = []
    profiles = list(protocol["profiles"])
    for name in protocol["presets"]:
        selected_profiles = profiles[:1] + ([list(profiles[0])] if name in protocol["authored_repeats"] else []) + profiles[1:]
        if name in protocol["authored_repeats"]: selected_profiles[1][0] = "authored_repeat"
        for label, role, width, height, rw, rh, feedback in selected_profiles:
            worker = protocol["workers"][role]
            identity = {"protocol_sha256": digest(protocol), "worker_sha256": worker["sha256"],
                        "preset_sha256": protocol["records"][name]["preset_sha256"], "profile": label, "role": role}
            key = digest(identity)
            job_dir = directory / "jobs" / key
            request = {"schema_version": 1, "preset_path": str(ROOT / "core/src/main/assets/presets" / name),
                       "pcm_path": protocol["pcm_path"], "texture_root": protocol["texture_root"],
                       "bands_path": str(job_dir / "bands.jsonl"), "manifest_path": str(job_dir / "manifest.json"),
                       "identity": identity, "config": {"width": width, "height": height, "fps": 30,
                         "warmup_seconds": 4, "measurement_seconds": 12, "seed": 12345,
                         "line_reference_width": rw, "line_reference_height": rh, "line_antialiasing": False,
                         "feedback_detail": feedback}}
            requests.append({"key": key, "preset": name, "profile": label, "role": role, "request": request})
    return requests


def read_exact(stream, size, deadline):
    chunks, remaining = [], size
    while remaining:
        require(time.monotonic() < deadline, "Native worker capture timeout")
        ready, _, _ = select.select([stream], [], [], min(1, max(0, deadline - time.monotonic())))
        if not ready: continue
        chunk = os.read(stream.fileno(), min(remaining, 1024 * 1024))
        require(bool(chunk), "Incomplete native capture stream")
        chunks.append(chunk); remaining -= len(chunk)
    return b"".join(chunks)


def run_job(directory, record, protocol, authored):
    job_dir = directory / "jobs" / record["key"]
    request = record["request"]
    if (job_dir / "receipt.json").exists() and (job_dir / "receipt.sha256").exists():
        previous = read(job_dir / "receipt.json")
        if previous["status"] == "success": return verify_job(job_dir, request)
        require((job_dir / "receipt.sha256").read_text().strip() == file_digest(job_dir / "receipt.json"), "Failed receipt checksum changed")
        require(read(job_dir / "request.json") == request and previous["request_sha256"] == digest(request), "Failed job request changed")
        return previous
    if job_dir.exists():
        require(read(job_dir / "request.json") == request, "Unfinished request changed")
        attempts = directory / "unfinished-attempts"
        attempts.mkdir(exist_ok=True)
        job_dir.rename(attempts / (record["key"] + "-" + str(time.time_ns())))
    job_dir.mkdir(parents=True)
    write(job_dir / "request.json", request)
    worker = protocol["workers"][record["role"]]
    require(file_digest(Path(worker["path"])) == worker["sha256"], "Compiled worker drift")
    require(file_digest(Path(request["preset_path"])) == request["identity"]["preset_sha256"], "Preset drift")
    reference_available = record["profile"] in ("authored", "authored_repeat") or bool(authored)
    receipt = {"status": "failed", "request_sha256": digest(request), "captures": [], "authored_reference_available": reference_available}
    start = time.monotonic(); deadline = start + 300
    process = None
    try:
        with (job_dir / "stderr.log").open("wb") as error_stream:
            process = subprocess.Popen([worker["path"], "--job", str(job_dir / "request.json")],
                stdout=subprocess.PIPE, stderr=error_stream, stdin=subprocess.DEVNULL,
                env=dict(os.environ, PRESET_LAB_SEED="12345"))
            width, height = request["config"]["width"], request["config"]["height"]
            for frame in CAPTURES:
                raw = read_exact(process.stdout, width * height * 3, deadline)
                rgb = np.frombuffer(raw, np.uint8).reshape(height, width, 3)
                reduced = cv2.resize(rgb, (1182, 665), interpolation=cv2.INTER_AREA)
                reference = authored.get(frame, rgb)
                measure = metrics.frame_metrics(rgb, reference)
                if not reference_available:
                    for field in ("authored_luma", "authored_contrast", "mae_authored", "luma_absolute_error",
                                  "contrast_absolute_error", "luma_ratio", "regularized_luma_ratio", "contrast_ratio", "near_black_authored"):
                        measure[field] = None
                measure.update(native_luma=float(rgb.mean(axis=(0, 1)) @ metrics.LUMA / 255),
                               native_clipped_fraction=float(np.any(rgb == 255, axis=2).mean()),
                               native_black_fraction=float(np.all(rgb == 0, axis=2).mean()))
                path = job_dir / ("frame-%03d.png" % frame)
                require(cv2.imwrite(str(path), cv2.cvtColor(reduced, cv2.COLOR_RGB2BGR)), "PNG export failed")
                capture = {"frame": frame, "native_rgb_sha256": hashlib.sha256(raw).hexdigest(),
                           "reduced_rgb_sha256": hashlib.sha256(reduced.tobytes()).hexdigest(),
                           "png_sha256": file_digest(path), "path": path.name, "metrics": measure}
                if frame == 300 and protocol["retain_full_frame300"]:
                    full = job_dir / "frame-300-native.png"
                    require(cv2.imwrite(str(full), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)), "Full PNG export failed")
                    capture["native_png_sha256"] = file_digest(full)
                receipt["captures"].append(capture)
            process.wait(timeout=max(.1, deadline - time.monotonic()))
            require(process.stdout.read(1) == b"", "Unexpected extra bytes in selected capture stream")
            require(process.returncode == 0, "Native worker failed with code%d" % process.returncode)
        manifest = read(job_dir / "manifest.json")
        receipt.update(status="success", worker_manifest_sha256=digest(manifest),
                       wall_seconds=time.monotonic() - start, stderr_sha256=file_digest(job_dir / "stderr.log"))
        write(job_dir / "receipt.json", receipt)
        (job_dir / "receipt.sha256").write_text(file_digest(job_dir / "receipt.json") + "\n")
        return verify_job(job_dir, request)
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired) as error:
        if process is not None and process.poll() is None:
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
        receipt.update(status="failed", error=str(error), wall_seconds=time.monotonic() - start,
                       stderr_sha256=file_digest(job_dir / "stderr.log") if (job_dir / "stderr.log").exists() else None,
                       historical_failure=protocol["records"][record["preset"]].get("historical_failure"))
        if (job_dir / "manifest.json").exists(): receipt["worker_manifest_sha256"] = digest(read(job_dir / "manifest.json"))
        write(job_dir / "receipt.json", receipt)
        (job_dir / "receipt.sha256").write_text(file_digest(job_dir / "receipt.json") + "\n")
        return receipt
    finally:
        if process is not None and process.stdout is not None: process.stdout.close()


def aggregate_job(receipt):
    frames = receipt["captures"]
    fields = frames[0]["metrics"].keys()
    aggregate = {field: float(np.mean([c["metrics"][field] for c in frames])) if all(c["metrics"][field] is not None for c in frames) else None for field in fields
                 if field not in ("luma_ratio", "contrast_ratio", "near_black_authored")}
    if aggregate["authored_luma"] is None:
        aggregate.update(near_black_authored=None, luma_ratio=None, regularized_luma_ratio=None, contrast_ratio=None)
        return aggregate
    aggregate["near_black_authored"] = aggregate["authored_luma"] < .001
    aggregate["luma_ratio"] = aggregate["luma"] / aggregate["authored_luma"] if not aggregate["near_black_authored"] else None
    aggregate["regularized_luma_ratio"] = (aggregate["luma"] + .001) / (aggregate["authored_luma"] + .001)
    aggregate["contrast_ratio"] = aggregate["contrast"] / aggregate["authored_contrast"] if aggregate["authored_contrast"] >= .001 else None
    return aggregate


def run_matrix(work, selection_path, run_name, pilot=False, parallel=2, retain_full=False):
    cv2.setNumThreads(1)
    work = Path(work).resolve()
    run_dir = work / "runs" / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "run.lock").open("w") as exclusive:
        fcntl.flock(exclusive, fcntl.LOCK_EX | fcntl.LOCK_NB)
        directory, protocol = initialize_run(work, selection_path, run_name, pilot, parallel, retain_full)
        expected = requests_for(directory, protocol)
        results, mutex = {}, threading.Lock()
        by_preset = {name: [r for r in expected if r["preset"] == name] for name in protocol["presets"]}
        def one_preset(name):
            authored, local = {}, {}
            for record in by_preset[name]:
                receipt = run_job(directory, record, protocol, authored)
                local[record["profile"]] = receipt
                if record["profile"] == "authored" and receipt["status"] == "success":
                    job_dir = directory / "jobs" / record["key"]
                    authored = {c["frame"]: cv2.cvtColor(cv2.imread(str(job_dir / c["path"])), cv2.COLOR_BGR2RGB)
                                for c in receipt["captures"]}
                if record["profile"] in ("authored_repeat", "native_off"):
                    first = "authored" if record["profile"] == "authored_repeat" else "native_before"
                    if receipt["status"] == local[first]["status"] == "success":
                        compare_identity(local[first], receipt, name + "/" + first + "/" + record["profile"])
                with mutex:
                    results[record["key"]] = receipt
                    write(directory / "progress.json", dict(audit_results(expected, results, partial=True),
                                                             last_preset=name, last_profile=record["profile"], protocol_sha256=digest(protocol)))
                    print(name + " / " + record["profile"] + " " + receipt["status"], flush=True)
        with ThreadPoolExecutor(max_workers=parallel) as pool:
            futures = [pool.submit(one_preset, name) for name in protocol["presets"]]
            for future in as_completed(futures): future.result()
        _, final_protocol = initialize_run(work, selection_path, run_name, pilot, parallel, retain_full)
        require(final_protocol == protocol, "Frozen source/protocol drift")
        report = dict(audit_results(expected, results), protocol_sha256=digest(protocol),
                      coverage=protocol["coverage"], limitations=protocol["limitations"],
                      capture_trust_boundary=protocol["capture_trust_boundary"], presets=[])
        drivers = set()
        regressions = []
        for name in protocol["presets"]:
            profiles = {}
            for record in by_preset[name]:
                receipt = results[record["key"]]
                if receipt["status"] == "success":
                    receipt = verify_job(directory / "jobs" / record["key"], record["request"])
                    manifest = read(directory / "jobs" / record["key"] / "manifest.json")
                    drivers.add((manifest["gl_renderer"], manifest["gl_version"], manifest.get("gl_vendor")))
                    profiles[record["profile"]] = {"mean": aggregate_job(receipt), "captures": receipt["captures"],
                                                   "serialized_frame_mean_ms": manifest["serialized_frame_mean_ms"],
                                                   "serialized_frame_p90_ms": manifest["serialized_frame_p90_ms"], "key": record["key"]}
                else:
                    profiles[record["profile"]] = {"status": "failed", "error": receipt["error"], "key": record["key"]}
                    if protocol["records"][name]["historical_status"] == "success": regressions.append({"preset": name, "profile": record["profile"], "error": receipt["error"]})
            report["presets"].append({"preset": name, "profiles": profiles, "selection_reasons": protocol["records"][name]["reasons"],
                                      "historical_failure": protocol["records"][name].get("historical_failure"), "visual_review_required": True})
        require(len(drivers) <= 1, "Mixed host GL drivers")
        report.update(driver=list(drivers), previously_successful_failures=regressions,
                      numeric_acceptance="Diagnostic only;near-black and chaotic cases require matched image inspection")
        write(directory / "summary.json", report)
        require(not regressions, "Previously successful presets now failed: inspect saved summary/receipts")
        print(canonical_json({k: report[k] for k in ("status", "terminal_jobs", "expected_jobs", "failed_jobs", "fidelity_complete")}), flush=True)
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    selection = commands.add_parser("select")
    selection.add_argument("--corpus", type=Path, required=True)
    selection.add_argument("--out", type=Path, required=True)
    selection.add_argument("--count", type=int, default=160)
    selection.add_argument("--assets", type=Path, default=ROOT / "core/src/main/assets/presets")
    build = commands.add_parser("build")
    build.add_argument("--work", type=Path, required=True)
    build.add_argument("--exports", type=Path, required=True)
    build.add_argument("--source", required=True)
    run = commands.add_parser("run")
    run.add_argument("--work", type=Path, required=True)
    run.add_argument("--selection", type=Path, required=True)
    run.add_argument("--run-name", required=True)
    run.add_argument("--pilot", action="store_true")
    run.add_argument("--parallel", type=int, default=2)
    run.add_argument("--retain-full", action="store_true", help="also keep native frame300 outside pilot")
    args = parser.parse_args()
    try:
        if args.mode == "select": select_to_file(args.corpus, args.assets, args.out, args.count)
        elif args.mode == "build": prepare_workers(args.work, args.exports, args.source)
        else: run_matrix(args.work, args.selection, args.run_name, args.pilot, args.parallel, args.retain_full)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, "Mac validation rejected: %s\n" % error)


if __name__ == "__main__": main()
