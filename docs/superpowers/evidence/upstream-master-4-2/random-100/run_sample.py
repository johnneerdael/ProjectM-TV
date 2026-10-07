#!/usr/bin/env python3
"""Freeze/run/verify the random sample. init and summary never contact a device."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import time

from common import (CANDIDATE_ENGINE, HERE, PACKAGES, PROFILES,
                    ROOT, SCHEMA, SEED, SUPPLEMENTAL_PACKAGES, canonical, file_sha, first_difference, frame_hashes,
                    immutable_json, selection, frozen_selection, release_manifest, sha, verify_published, write, zip_hashes, catalog, named_profile_extensions)


def helpers():
    paths = [HERE / name for name in ("common.py", "run_sample.py", "prepare_worker.py", "harness/EveryFrameHashes.java", "q2160-profile-evidence.json")]
    paths.extend(ROOT / name for name in ("tools/native-trails/run_validation.py", "tools/core-corpus/run_corpus.py",
                                         "tools/preset-lab/src/preset_lab/identity.py"))
    return {str(path.relative_to(ROOT)): file_sha(path) for path in paths}


def low_level():
    spec = importlib.util.spec_from_file_location("random100_trails", ROOT / "tools/native-trails/run_validation.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def worker(path, role, release, supplemental=False):
    path = Path(path).resolve()
    identity = json.loads(path.read_text())
    shipping = role == "released"
    if (identity.get("schema") != SCHEMA or identity.get("role") != role
            or identity.get("package") != (SUPPLEMENTAL_PACKAGES if supplemental else PACKAGES)[role] or identity.get("abi") not in ("armeabi-v7a", "arm64-v8a")
            or identity.get("final_eligible") is not True
            or identity.get("shipping_byte_identity") is not (shipping and not supplemental)
            or identity.get("core_aar_shipping_byte_identity") is not shipping
            or identity.get("artifact_scope") != ("supplemental" if supplemental else "bundled")
            or identity.get("seed_reset_after_environment") is not (not shipping)
            or identity.get("release_manifest", {}).get("manifest_sha256") != release["manifest_sha256"]):
        raise ValueError("Unexpected post-release worker identity: " + role)
    if role in ("baseline", "released"):
        if (identity["source_commit"] != release["source_commit"] or identity["engine_commit"] != release["engine_commit"]
                or identity["ordered_patches"] != release["ordered_patches"]):
            raise ValueError("Worker does not use the verified released source")
    elif identity["engine_commit"] != CANDIDATE_ENGINE:
        raise ValueError("Unexpected candidate engine pin")
    if shipping and identity["aar_sha256"] != release["aar_sha256"]:
        raise ValueError("Runtime worker does not embed the unchanged released AAR")
    if file_sha(identity["source_identity_path"]) != identity["source_identity_sha256"]:
        raise ValueError("Producer identity changed")
    check_artifacts(identity)
    return dict(identity, worker_identity_path=str(path), worker_identity_sha256=file_sha(path))


def check_artifacts(identity):
    if file_sha(identity["aar"]) != identity["aar_sha256"] or file_sha(identity["apk"]) != identity["apk_sha256"]:
        raise ValueError("Frozen APK/AAR bytes changed")
    assets = zip_hashes(identity["aar"], "assets/")
    overlay = identity.get("supplemental_fixture_overlay")
    if identity.get("artifact_scope") == "supplemental":
        if not overlay or overlay.get("original_index_sha256") != assets["assets/presets.idx"]:
            raise ValueError("Supplemental index is not derived from this AAR")
        assets["assets/presets.idx"] = overlay["derived_index_sha256"]
        assets[overlay["fixture_asset_path"]] = overlay["fixture_sha256"]
    elif overlay:
        raise ValueError("Primary bundle has an unexpected fixture overlay")
    if assets != zip_hashes(identity["apk"], "assets/"):
        raise ValueError("APK asset payload differs from its exact declared scope")
    native = zip_hashes(identity["aar"], "jni/" + identity["abi"] + "/")
    if {name.replace("jni/", "lib/", 1): value for name, value in native.items()} != zip_hashes(identity["apk"], "lib/"):
        raise ValueError("APK native bytes differ from the unchanged supplied AAR")


def identity_for(protocol, job):
    group = "supplemental_workers" if job.get("artifact_scope") == "supplemental" else "workers"
    return protocol[group][job["role"]]


def proof_contract(selected):
    names = [row["filename"] for row in selected["random_presets"][:3]]
    midgit = "midgitstraights of majillaen - featy sweet.milk"
    if midgit not in names:
        names.append(midgit)
    owner = next((name for name, item in named_profile_extensions(selected).items()
                  if "native4k-medium" in item["profiles"]), None)
    if owner and owner not in names:
        names.append(owner)
    names.extend(row["filename"] for row in selected.get("required_external_presets", []))
    return {"positive_proof_presets": names, "positive_proof_frames": [120, 479], "positive_proof_repeats": [0, 1]}


def initialize(args):
    release = release_manifest(args.release_manifest)
    selected = frozen_selection(release, args.regression_inventory)
    records = catalog()
    verify_published(release, records)
    if args.mode == "final" and (args.frames != 480 or args.profiles != ["1080p"] or args.preset_limit):
        raise ValueError("Final sample gate is the complete frozen sample at 1080p, frames 0–479")
    if args.preset_limit < 0 or (args.user is not None and not 0 <= args.user <= 2147483647):
        raise ValueError("Preset limit or Android user is out of bounds")
    if not 1 <= args.frames <= 480:
        raise ValueError("Exploratory frame limit must be between 1 and 480")
    workers = {role: worker(path, role, release) for role, path in (("baseline", args.baseline), ("candidate", args.candidate), ("released", args.released))}
    supplemental = {}
    if selected["required_external_presets"]:
        paths = {"baseline": args.supplemental_baseline, "candidate": args.supplemental_candidate, "released": args.supplemental_released}
        if any(path is None for path in paths.values()):
            raise ValueError("Required external fixture needs separate supplemental workers for all three roles")
        supplemental = {role: worker(path, role, release, supplemental=True) for role, path in paths.items()}
        for item in supplemental.values():
            fixture = item["supplemental_fixture_overlay"]["fixture"]
            if not any(fixture["filename"] == row["filename"] and fixture["asset_sha256"] == row["asset_sha256"]
                       for row in selected["required_external_presets"]):
                raise ValueError("Supplemental worker uses another external fixture")
    if len({item["abi"] for item in list(workers.values()) + list(supplemental.values())}) != 1:
        raise ValueError("All source/runtime workers must use the same ABI")
    published_assets = zip_hashes(release["aar_path"], "assets/")
    if any(zip_hashes(item["aar"], "assets/") != published_assets for item in workers.values()):
        raise ValueError("Source-control assets differ from the unchanged released AAR")
    trials = selected["random_presets"] + selected["additional_regressions"]
    if args.preset_limit:
        trials = trials[:args.preset_limit]
    extensions = named_profile_extensions(selected) if args.mode == "final" else {}
    profile_names = list(dict.fromkeys(args.profiles + [profile for record in extensions.values() for profile in record["profiles"]]))
    proofs = proof_contract(selected)
    module = low_level()
    _, complete_pcm = module.corpus.signal()
    pcm = complete_pcm[:args.frames * 1470]
    protocol = {"schema": SCHEMA, "mode": args.mode, "can_satisfy_random_completion_gate": args.mode == "final",
                "device": args.device, "expected_user_id": args.user, "backend": args.backend, "workers": workers, "supplemental_workers": supplemental, "released_baseline": release, "seed": SEED, "clock": "frame/30.0",
                "frames": args.frames, "frame_indices": [0, args.frames - 1], "fps": 30,
                "profiles": {name: PROFILES[name] for name in profile_names}, "base_profiles": args.profiles,
                "named_profile_extensions": extensions, **proofs, "repeats": [0, 1],
                "presets": trials, "external_presets": selected["required_external_presets"], "random_sample_count": selected["random_count"],
                "selection_sha256": sha((canonical(selected) + "\n").encode()), "selection_catalog_sha256": selected["catalog_sha256"],
                "named_regression_count": len(selected["named_regressions"]), "additional_regression_count": len(selected["additional_regressions"]),
                "unresolved_regression_witnesses": selected["missing_external_witnesses"] + [row for row in selected["unresolved_name_aliases"] if not row.get("all_plausible_bundled_matches_required")],
                "ambiguous_references": selected["unresolved_name_aliases"],
                "synthetic_or_unbundled_controls": selected["synthetic_or_unbundled_controls"],
                "regression_inventory_path": str(args.regression_inventory.resolve()), "regression_inventory_sha256": file_sha(args.regression_inventory),
                "published_aar_path": release["aar_path"], "published_aar_sha256": release["aar_sha256"],
                "pcm_sha256": sha(pcm), "pcm_bytes": len(pcm), "complete_audio_sha256": sha(complete_pcm),
                "audio": "existing bass-.30 signal: seed 12345, 44100 Hz, four-second carrier warmup plus twelve-second bass envelope",
                "hash_scope": "every full-resolution top-down RGB8 frame; alpha excluded; zero tolerance",
                "settings": {"autoChange": False, "beatCuts": False, "blankDetection": False, "musicCategory": "all",
                             "mesh": [48, 32], "presetDurationSeconds": 3600, "softCutDurationSeconds": 0,
                             "transitionMode": "CLASSIC", "lowEndDevice": False, "nativeTrails": "per declared profile"},
                "normal_png_captures": [], "helper_sha256": helpers(),
                "separate_checks": "Native-active 4K four-witness regression controls and unchanged released-AAR real-clock checks remain separate evidence."}
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    immutable_json(work / "selection.json", selected)
    immutable_json(work / "protocol.json", protocol)
    audio = work / "audio.u8"
    if audio.exists() and file_sha(audio) != sha(pcm):
        raise ValueError("Frozen PCM changed")
    if not audio.exists():
        audio.write_bytes(pcm)
    print(canonical({"protocol_sha256": sha(canonical(protocol).encode()), "bundled_presets": len(trials),
                     "source_jobs": len(list(jobs(protocol))), "runtime_jobs": len(list(jobs(protocol, shipping=True))), "mode": args.mode}))


def jobs(protocol, shipping=False):
    digest = sha(canonical(protocol).encode())
    for preset in protocol["presets"] + protocol.get("external_presets", []):
        scope = "supplemental" if preset in protocol.get("external_presets", []) else "bundled"
        profiles = protocol.get("base_profiles", list(protocol["profiles"])) + protocol.get("named_profile_extensions", {}).get(preset["filename"], {}).get("profiles", [])
        for profile in list(dict.fromkeys(profiles)):
            for role in (("released",) if shipping else ("baseline", "candidate")):
                for repeat in ((0,) if shipping else (0, 1)):
                    job = {"preset": preset["filename"], "preset_sha256": preset["asset_sha256"],
                           "profile": profile, "role": role, "repeat": repeat, "artifact_scope": scope}
                    yield dict(job, key=sha(canonical(dict(job, protocol_sha256=digest)).encode()))


def request(protocol, job, captures=None):
    config = protocol["profiles"][job["profile"]]
    if captures is None:
        captures = [frame for frame in protocol.get("positive_proof_frames", []) if frame < protocol["frames"]]
        if job["role"] != "released" or job["preset"] not in protocol.get("positive_proof_presets", []):
            captures = []
    return {"preset": job["preset"], "width": config["width"], "height": config["height"],
            "referenceWidth": config["referenceWidth"], "referenceHeight": config["referenceHeight"],
            "nativeTrails": config["nativeTrails"], "seed": SEED, "instrumented": job["role"] != "released",
            "expectedPresetCount": 9607 if job.get("artifact_scope") == "supplemental" else 9606,
            "frameLimit": protocol["frames"], "captureFrames": captures}


def verify(directory, requested, preset_hash):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    frames = requested["frameLimit"]
    expected = {"protocol": SCHEMA, "status": "ok", "framesRendered": frames, "frameCountExpected": frames,
                "glErrorChecks": frames, "presetNameChecks": frames, "presetAssetSha256": preset_hash,
                "verifiedPresetName": requested["preset"], "eligiblePresetCountBeforeFrame0": 1,
                "eligiblePresetCountAfterFinalFrame": 1, "presetChangeCounter": 1,
                "coreReleased": True, "eglDestroyed": True,
                "determinism": "instrumented-fixed-clock-seed" if requested["instrumented"] else "nondeterministic-real-clock-smoke",
                "frameHashSemantics": "top-down full-resolution RGB8; RGBA readback with alpha excluded"}
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError("Failed/incomplete exact-frame manifest: " + str(manifest.get("error", manifest)))
    if manifest.get("job") != requested or manifest.get("requestSha256") != sha((canonical(requested) + "\n").encode()):
        raise ValueError("Manifest request identity changed")
    if manifest.get("bundledPresetCount") != requested["expectedPresetCount"] or manifest.get("fps") != 30:
        raise ValueError("Asset inventory or audio schedule changed")
    hashes = frame_hashes(directory, manifest, requested)
    if [row["frame"] for row in manifest.get("captures", [])] != requested["captureFrames"]:
        raise ValueError("Diagnostic capture indices differ")
    if requested["captureFrames"]:
        import cv2
        for capture in manifest["captures"]:
            path = directory / ("frame-%03d.png" % capture["frame"])
            if file_sha(path) != capture["pngSha256"]:
                raise ValueError("Diagnostic PNG changed")
            image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if image is None or image.shape[:2] != (requested["height"], requested["width"]):
                raise ValueError("Diagnostic capture dimensions differ")
            decoded = sha(cv2.cvtColor(image, cv2.COLOR_BGR2RGB).tobytes())
            if decoded != hashes[capture["frame"]] or decoded != capture["rgbSha256"]:
                raise ValueError("PNG bytes disagree with the every-frame RGB hash")
    return manifest


def require_session(module, protocol, state):
    if helpers() != protocol["helper_sha256"]:
        raise ValueError("Frozen helper code changed")
    if module.current_user(protocol["device"]) != state["user_id"]:
        raise ValueError("Foreground Android user changed")
    power = module.shell(protocol["device"], "dumpsys", "power")
    if not re.search(r"\bmWakefulness=Awake\b", power) or "mInteractive=false" in power:
        raise ValueError("Android device is not awake; preserve evidence without waking it")
    if (module.shell(protocol["device"], "getprop", "ro.build.fingerprint").strip() != state["fingerprint"]
            or int(module.shell(protocol["device"], "getprop", "ro.build.version.sdk").strip()) != state["sdk"]):
        raise ValueError("Device fingerprint changed")


def run(args):
    work = args.work.resolve()
    protocol = json.loads((work / "protocol.json").read_text())
    if args.limit_jobs < 0:
        raise ValueError("Job limit must be nonnegative")
    if helpers() != protocol["helper_sha256"] or file_sha(work / "audio.u8") != protocol["pcm_sha256"]:
        raise ValueError("Frozen runner/PCM changed")
    frozen_inputs(work, protocol)
    module = low_level()
    module.verify = verify  # Override only this process-local helper instance, never historical files.
    for group in ("workers", "supplemental_workers"):
        for role, identity in protocol[group].items():
            current = worker(identity["worker_identity_path"], role, protocol["released_baseline"], supplemental=group == "supplemental_workers")
            if current != identity:
                raise ValueError("Frozen worker identity changed")
    with module.corpus.session_lock(protocol["device"], 5037):
        state = {"user_id": module.current_user(protocol["device"]),
                 "fingerprint": module.shell(protocol["device"], "getprop", "ro.build.fingerprint").strip(),
                 "sdk": int(module.shell(protocol["device"], "getprop", "ro.build.version.sdk").strip())}
        if protocol.get("expected_user_id") is not None and state["user_id"] != protocol["expected_user_id"]:
            raise ValueError("Current Android user differs from the explicitly requested user")
        immutable_json(work / "device-state.json", state)
        installed, completed = set(), 0
        for job in jobs(protocol, shipping=args.shipping):
            identity = identity_for(protocol, job)
            directory = work / "jobs" / job["key"]
            if (directory / "row.json").exists():
                verified_row(work, protocol, job)
                continue
            require_session(module, protocol, state)
            if identity["package"] not in installed:
                module.install_worker(protocol["device"], identity, state["user_id"])
                installed.add(identity["package"])
            started = time.monotonic()
            try:
                manifest = module.render(protocol["device"], identity, request(protocol, job), directory,
                                         work / "audio.u8", job["preset_sha256"], state["user_id"])
                manifest = verify_render_contract(directory, work, protocol, job, bind_gl=True)
                write(directory / "row.json", dict(job, status="verified", elapsed_seconds=time.monotonic() - started,
                                                    frame_hashes_sha256=manifest["frameHashesSha256"]))
            except Exception as failure:
                directory.mkdir(parents=True, exist_ok=True)
                write(directory / "row.json", dict(job, status="failed", error=str(failure)))
                raise
            print(job["preset"], job["profile"], job["role"], job["repeat"], "verified", flush=True)
            completed += 1
            if args.limit_jobs and completed >= args.limit_jobs:
                break
    summarize(work)


def validate_protocol(protocol, selected):
    if (protocol.get("schema") != SCHEMA or protocol.get("seed") != SEED or protocol.get("fps") != 30
            or protocol.get("clock") != "frame/30.0" or protocol.get("repeats") != [0, 1]
            or protocol.get("backend") not in ("physical-tv", "android-gpu-emulator")
            or type(protocol.get("frames")) is not int or not 1 <= protocol["frames"] <= 480):
        raise ValueError("Frozen frame/seed/backend protocol is invalid")
    if not protocol.get("profiles") or any(PROFILES.get(name) != config for name, config in protocol["profiles"].items()):
        raise ValueError("Frozen profiles differ from their declared definitions")
    proofs = proof_contract(selected)
    if any(protocol.get(key) != value for key, value in proofs.items()):
        raise ValueError("Frozen positive image proof policy changed")
    union = selected["random_presets"] + selected["additional_regressions"]
    if protocol.get("external_presets", []) != selected.get("required_external_presets", []):
        raise ValueError("Required external fixture list changed")
    if protocol.get("mode") == "final":
        if (protocol["frames"] != 480 or protocol.get("base_profiles", list(protocol["profiles"])) != ["1080p"]
                or protocol.get("can_satisfy_random_completion_gate") is not True or protocol["presets"] != union
                or protocol.get("named_profile_extensions", {}) != named_profile_extensions(selected)):
            raise ValueError("Final protocol must include every frozen random and required named preset for all 480 frames")
    elif protocol.get("mode") == "explore":
        if protocol.get("can_satisfy_random_completion_gate") is not False or protocol["presets"] != union[:len(protocol["presets"])]:
            raise ValueError("Exploration cannot certify or cherry-pick the frozen sample")
    else:
        raise ValueError("Unknown protocol mode")


def frozen_inputs(work, protocol):
    release = release_manifest(protocol["released_baseline"]["manifest_path"])
    if release != protocol["released_baseline"] or helpers() != protocol["helper_sha256"]:
        raise ValueError("Frozen release or helper code changed")
    if file_sha(Path(work) / "audio.u8") != protocol["pcm_sha256"]:
        raise ValueError("Frozen audio changed")
    selected = selection(Path(work) / "selection.json", release, protocol["regression_inventory_path"])
    validate_protocol(protocol, selected)
    if file_sha(Path(work) / "selection.json") != protocol["selection_sha256"]:
        raise ValueError("Frozen selection bytes changed")
    for group in ("workers", "supplemental_workers"):
        for role, identity in protocol[group].items():
            if worker(identity["worker_identity_path"], role, release, supplemental=group == "supplemental_workers") != identity:
                raise ValueError("Frozen worker changed")
    return selected


def verified_row(work, protocol, job):
    directory = Path(work) / "jobs" / job["key"]
    row = json.loads((directory / "row.json").read_text())
    if row.get("status") != "verified":
        raise ValueError("Job is not verified: " + str(row.get("error", row)))
    if any(row.get(key) != value for key, value in job.items()):
        raise ValueError("Verified row belongs to another job")
    manifest = verify_render_contract(directory, work, protocol, job)
    if row.get("frame_hashes_sha256") != manifest["frameHashesSha256"]:
        raise ValueError("Verified row references another stream")
    return frame_hashes(directory, manifest, manifest["job"]), manifest


def verify_render_contract(directory, work, protocol, job, captures=None, bind_gl=False):
    requested = json.loads((Path(directory) / "request.json").read_text())
    logical = request(protocol, job, captures)
    if {key: value for key, value in requested.items() if key not in ("pcmPath", "outputDir")} != logical:
        raise ValueError("Render request differs from the frozen contract")
    manifest = verify(directory, requested, job["preset_sha256"])
    validate_manifest_context(manifest, work, protocol, job, bind_gl=bind_gl)
    return manifest


def validate_manifest_context(manifest, work, protocol, job, bind_gl=False):
    if manifest.get("pcmSha256") != protocol["pcm_sha256"]:
        raise ValueError("Consumed PCM differs from the frozen audio")
    identity = identity_for(protocol, job)
    if manifest.get("applicationId") != identity["package"]:
        raise ValueError("Manifest belongs to another worker")
    config = protocol["profiles"][job["profile"]]
    status = str(manifest.get("nativeTrailsStatus", "")).lower()
    if config["expected_level"] not in status or config["expected_trails"].lower() not in status or "fallback" in status:
        raise ValueError("Native trails profile differs")
    state = json.loads((Path(work) / "device-state.json").read_text())
    info = manifest.get("device", {})
    if info.get("fingerprint") != state["fingerprint"] or info.get("sdk") != state["sdk"]:
        raise ValueError("Observed device API/fingerprint differs from the frozen session")
    if identity["abi"] not in info.get("abis", []):
        raise ValueError("Worker ABI is not supported by the observed device")
    keys = ("glVendor", "glRenderer", "glVersion", "glShadingLanguageVersion")
    observed = {key: manifest.get(key) for key in keys}
    if any(not isinstance(value, str) or not value for value in observed.values()):
        raise ValueError("Incomplete observed GL driver tuple")
    if protocol["backend"] == "android-gpu-emulator" and any(word in observed["glRenderer"].lower()
            for word in ("swiftshader", "llvmpipe", "software")):
        raise ValueError("Software renderer is outside the frozen GPU-emulator scope")
    path = Path(work) / "gl-state.json"
    if not path.exists() and not bind_gl:
        raise ValueError("GL driver tuple has not been frozen by a verified original run")
    if bind_gl:
        immutable_json(path, observed)
    elif json.loads(path.read_text()) != observed:
        raise ValueError("Observed GL driver tuple changed")



def summarize(work):
    work = Path(work)
    protocol = json.loads((work / "protocol.json").read_text())
    frozen_inputs(work, protocol)
    complete, runtime = {}, {}
    missing, failed, invalid = [], [], []
    observed_backends = set()
    for shipping in (False, True):
        for job in jobs(protocol, shipping=shipping):
            row_path = work / "jobs" / job["key"] / "row.json"
            if not row_path.exists():
                missing.append(job)
                continue
            row = json.loads(row_path.read_text())
            if row.get("status") != "verified":
                failed.append(row)
                continue
            try:
                hashes, manifest = verified_row(work, protocol, job)
                observed_backends.add((manifest.get("glVendor"), manifest.get("glRenderer"), manifest.get("glVersion"),
                                       manifest.get("glShadingLanguageVersion")))
                target = runtime if shipping else complete
                target[(job["preset"], job["profile"], job["role"], job["repeat"])] = hashes
            except (OSError, ValueError, KeyError) as failure:
                invalid.append(dict(job, error=str(failure)))
    if len(observed_backends) > 1:
        invalid.append({"error": "Observed GL backend changed between comparison/runtime jobs"})
    differences = []
    for preset in protocol["presets"] + protocol.get("external_presets", []):
        active_profiles = protocol.get("base_profiles", list(protocol["profiles"])) + protocol.get("named_profile_extensions", {}).get(preset["filename"], {}).get("profiles", [])
        for profile in list(dict.fromkeys(active_profiles)):
            sequences = {key: complete.get((preset["filename"], profile, *key))
                         for key in (("baseline", 0), ("baseline", 1), ("candidate", 0), ("candidate", 1))}
            for label, first, second in (("baseline_repeat", ("baseline", 0), ("baseline", 1)),
                                         ("candidate_repeat", ("candidate", 0), ("candidate", 1)),
                                         ("baseline_candidate", ("baseline", 0), ("candidate", 0))):
                if sequences[first] is not None and sequences[second] is not None:
                    frame = first_difference(sequences[first], sequences[second])
                    if frame is not None:
                        differences.append({"preset": preset["filename"], "profile": profile, "comparison": label,
                                            "first_frame": frame, "first": list(first), "second": list(second),
                                            "first_rgb_sha256": sequences[first][frame], "second_rgb_sha256": sequences[second][frame]})
    planned, planned_runtime = len(list(jobs(protocol))), len(list(jobs(protocol, shipping=True)))
    source_bad = any(item.get("role") != "released" for item in failed + invalid)
    runtime_bad = any(item.get("role") == "released" for item in failed + invalid)
    source_pass = (protocol["can_satisfy_random_completion_gate"] and len(complete) == planned
                   and not source_bad and not differences and len(observed_backends) <= 1)
    runtime_pass = (len(runtime) == planned_runtime and not runtime_bad and len(observed_backends) <= 1)
    unresolved = protocol.get("unresolved_regression_witnesses", [])
    images = image_proof_complete(work, protocol)
    passed = source_pass and runtime_pass and images["complete"] and not invalid and not failed and not unresolved
    result = {"schema": SCHEMA, "protocol_sha256": sha(canonical(protocol).encode()), "mode": protocol["mode"],
              "status": "pass" if passed else "failed" if (failed or invalid or differences) else "incomplete",
              "sample_readiness_gate_satisfied": passed, "zero_pixel_changes_certified": source_pass,
              "unchanged_release_runtime_verified": runtime_pass, "positive_image_proof": images,
              "planned_source_jobs": planned, "verified_source_jobs": len(complete),
              "planned_runtime_jobs": planned_runtime, "verified_runtime_jobs": len(runtime),
              "missing": missing, "failed": failed, "invalid": invalid, "differences": differences,
              "unresolved_regression_witnesses": unresolved,
              "scope": {"random_presets": protocol["random_sample_count"],
                        "named_regressions": protocol["named_regression_count"],
                        "additional_regressions": protocol["additional_regression_count"],
                        "bundled_presets_in_union": len(protocol["presets"]), "required_external_presets": len(protocol.get("external_presets", [])),
                        "profiles": list(protocol["profiles"]),
                        "frames": protocol["frames"], "seed": SEED, "rgba_readback_rgb_comparison": True,
                        "alpha_compared": False, "backend": protocol["backend"]},
              "limits": "Exact equality applies only to fixed-seed source controls. Unchanged AAR runtime uses its real clock/RNG and is verified separately, without a deterministic pixel-equality claim. No full-inventory or other-device certificate."}
    write(work / "summary.json", result)
    print(canonical({key: result[key] for key in ("status", "zero_pixel_changes_certified", "unchanged_release_runtime_verified",
                                                "planned_source_jobs", "verified_source_jobs", "scope")}))
    return result


def proof_jobs(protocol):
    return [job for job in jobs(protocol) if job["preset"] in protocol.get("positive_proof_presets", [])
            and job["repeat"] in protocol.get("positive_proof_repeats", [])]


def verify_proof_row(work, protocol, job):
    original_directory = Path(work) / "jobs" / job["key"]
    original_hashes, _ = verified_row(work, protocol, job)
    directory = Path(work) / "positive-proof" / job["key"]
    manifest = verify_render_contract(directory, work, protocol, job, protocol["positive_proof_frames"])
    if frame_hashes(directory, manifest, manifest["job"]) != original_hashes:
        raise ValueError("Positive proof replay changed any original frame")
    return manifest


def image_proof_complete(work, protocol):
    expected = proof_jobs(protocol)
    missing, invalid = [], []
    for job in expected:
        directory = Path(work) / "positive-proof" / job["key"]
        if not (directory / "manifest.json").exists():
            missing.append(job)
            continue
        try:
            verify_proof_row(work, protocol, job)
        except (OSError, ValueError, KeyError) as failure:
            invalid.append(dict(job, error=str(failure)))
    return {"complete": bool(expected) and not missing and not invalid,
            "expected_replays": len(expected), "missing": missing, "invalid": invalid,
            "frames": protocol.get("positive_proof_frames", [])}


def proof(args):
    work = args.work.resolve()
    protocol = json.loads((work / "protocol.json").read_text())
    frozen_inputs(work, protocol)
    state = json.loads((work / "device-state.json").read_text())
    module = low_level()
    module.verify = verify
    completed = 0
    with module.corpus.session_lock(protocol["device"], 5037):
        for job in proof_jobs(protocol):
            directory = work / "positive-proof" / job["key"]
            if (directory / "manifest.json").exists():
                verify_proof_row(work, protocol, job)
                continue
            verified_row(work, protocol, job)
            require_session(module, protocol, state)
            identity = identity_for(protocol, job)
            module.install_worker(protocol["device"], identity, state["user_id"])
            module.render(protocol["device"], identity, request(protocol, job, protocol["positive_proof_frames"]),
                          directory, work / "audio.u8", job["preset_sha256"], state["user_id"])
            verify_proof_row(work, protocol, job)
            completed += 1
            if args.limit_jobs and completed >= args.limit_jobs:
                break
    write(work / "positive-proof.json", image_proof_complete(work, protocol))
    summarize(work)


def witness(args):
    work = args.work.resolve()
    result = summarize(work)
    if not result["differences"]:
        raise ValueError("No frozen first divergence to capture")
    difference = result["differences"][0]
    protocol = json.loads((work / "protocol.json").read_text())
    state = json.loads((work / "device-state.json").read_text())
    module = low_level()
    module.verify = verify
    witnesses = []
    with module.corpus.session_lock(protocol["device"], 5037):
        for role, repeat in (difference["first"], difference["second"]):
            job = next(job for job in jobs(protocol) if job["preset"] == difference["preset"]
                       and job["profile"] == difference["profile"] and job["role"] == role and job["repeat"] == repeat)
            require_session(module, protocol, state)
            identity = identity_for(protocol, job)
            module.install_worker(protocol["device"], identity, state["user_id"])
            directory = work / "witnesses" / (job["key"] + "-frame-" + str(difference["first_frame"]))
            manifest = module.render(protocol["device"], identity, request(protocol, job, [difference["first_frame"]]),
                                     directory, work / "audio.u8", job["preset_sha256"], state["user_id"])
            manifest = verify_render_contract(directory, work, protocol, job, [difference["first_frame"]])
            previous_directory = work / "jobs" / job["key"]
            previous = json.loads((previous_directory / "manifest.json").read_text())
            if frame_hashes(directory, manifest, manifest["job"]) != frame_hashes(previous_directory, previous, previous["job"]):
                raise ValueError("Diagnostic replay changed the original sequence; preserve hashes and report nondeterminism")
            witnesses.append({"role": role, "repeat": repeat, "directory": str(directory), "captures": manifest["captures"]})
    write(work / "first-divergence-witness.json", dict(difference, witnesses=witnesses))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize_parser = commands.add_parser("init")
    initialize_parser.add_argument("--baseline", type=Path, required=True)
    initialize_parser.add_argument("--candidate", type=Path, required=True)
    initialize_parser.add_argument("--release-manifest", type=Path, required=True)
    initialize_parser.add_argument("--regression-inventory", type=Path, required=True)
    initialize_parser.add_argument("--released", type=Path, required=True)
    for role in ("baseline", "candidate", "released"):
        initialize_parser.add_argument("--supplemental-" + role, type=Path)
    initialize_parser.add_argument("--backend", choices=("physical-tv", "android-gpu-emulator"), required=True)
    initialize_parser.add_argument("--device", required=True)
    initialize_parser.add_argument("--user", type=int, default=None, help="Optional explicit Android user; otherwise capture the foreground user")
    initialize_parser.add_argument("--work", type=Path, required=True)
    initialize_parser.add_argument("--mode", choices=("final", "explore"), default="final")
    initialize_parser.add_argument("--frames", type=int, default=480)
    initialize_parser.add_argument("--profiles", nargs="+", choices=tuple(PROFILES), default=["1080p"])
    initialize_parser.add_argument("--preset-limit", type=int, default=0)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--work", type=Path, required=True)
    run_parser.add_argument("--limit-jobs", type=int, default=0)
    run_parser.add_argument("--shipping", action="store_true", help="Run unchanged released-AAR real-clock rows separately")
    proof_parser = commands.add_parser("proof")
    proof_parser.add_argument("--work", type=Path, required=True)
    proof_parser.add_argument("--limit-jobs", type=int, default=0)
    for name in ("summary", "witness"):
        command = commands.add_parser(name)
        command.add_argument("--work", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.command == "init":
        initialize(arguments)
    elif arguments.command == "run":
        run(arguments)
    elif arguments.command == "proof":
        proof(arguments)
    elif arguments.command == "witness":
        witness(arguments)
    else:
        summarize(arguments.work)
