#!/usr/bin/env python3
"""Prepare/build a private every-frame Java harness around an unchanged instrumented AAR."""
from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

from common import (CANDIDATE_ENGINE, HERE, PACKAGES, SUPPLEMENTAL_PACKAGES, ROOT, SCHEMA, bridge_is_reset_after_seed,
                    canonical, file_sha, release_manifest, sha, write, zip_hashes)


def once(text, before, after):
    if text.count(before) != 1:
        raise ValueError("Private harness anchor changed: " + repr(before))
    return text.replace(before, after)


def extend_harness(text, fixed_seed=True):
    text = once(text, 'manifest.put("protocol", "projectmtv-core-corpus-v1");',
                'manifest.put("protocol", "' + SCHEMA + '");')
    text = once(text, 'boolean instrumented = job.getBoolean("instrumented");',
                '''boolean instrumented = job.getBoolean("instrumented");
        if (!instrumented) throw new IllegalArgumentException("Exact source controls require the fixed seed/clock bridge");
        int frameLimit = job.optInt("frameLimit", FRAMES);
        if (frameLimit < 1 || frameLimit > FRAMES) throw new IllegalArgumentException("Frame limit out of bounds");
        int[] captureFrames = EveryFrameHashes.captures(job, frameLimit);''')
    if not fixed_seed:
        text = text.replace('if (!instrumented) throw new IllegalArgumentException("Exact source controls require the fixed seed/clock bridge");',
                            'if (instrumented) throw new IllegalArgumentException("Unchanged release runtime must not invoke a private bridge");')
    text = text.replace('manifest.put("frameCountExpected", FRAMES);', 'manifest.put("frameCountExpected", frameLimit);')
    text = text.replace('"eight selected frames, top-down RGB8 SHA256; sampled metrics under common 16-second audio; no all-frame image hash"',
                        '"every declared full-resolution frame, top-down RGB8 SHA256; alpha discarded; optional first-divergence PNGs"')
    text = text.replace('"complete unsigned 8-bit mono blocks via ProjectMJNI.addWaveform; production FeedAudio retains latest 512 samples"',
                        '"complete unsigned 8-bit mono blocks via production ProjectMJNI.addWaveform; actual API buffer bound applies"')
    text = once(text, 'pcm.length != FRAMES * PCM_BLOCK', 'pcm.length != frameLimit * PCM_BLOCK')
    text = text.replace('"PCM must contain exactly 480 complete 1470-byte blocks, got " + pcm.length',
                        '"PCM must contain exactly " + frameLimit + " complete 1470-byte blocks, got " + pcm.length')
    text = once(text, 'ProjectMJNI.setAutoChange(false);', '''ProjectMJNI.class.getMethod("setNativeTrails", int.class).invoke(null, job.getInt("nativeTrails"));
        ProjectMJNI.setAutoChange(false);''')
    text = once(text, 'int nextCapture = 0;', '''File frameHashFile = new File(output, "frame-hashes.jsonl");
        int nextCapture = 0;
        try (EveryFrameHashes frameHashes = new EveryFrameHashes(frameHashFile, width, height)) {''')
    text = once(text, 'for (int frame = 0; frame < FRAMES; frame++)',
                'for (int frame = 0; frame < frameLimit; frame++)')
    text = once(text, 'manifest.put("framesRendered", frame + 1);',
                'frameHashes.writeFrame(frame, rgba);\n            manifest.put("framesRendered", frame + 1);')
    text = text.replace('CAPTURES.length', 'captureFrames.length').replace('frame == CAPTURES[nextCapture]',
                                                                         'frame == captureFrames[nextCapture]')
    text = once(text, 'checkGl("completed frame loop");', '''}
        manifest.put("frameHashCount", frameLimit);
        manifest.put("frameHashesSha256", hex(fileSha256(frameHashFile)));
        manifest.put("frameHashSemantics", "top-down full-resolution RGB8; RGBA readback with alpha excluded");
        checkGl("completed frame loop");''')
    text = once(text, 'manifest.put("verifiedPresetName", ProjectMJNI.getCurrentPresetName());',
                '''manifest.put("nativeTrailsStatus", ProjectMJNI.class.getMethod("getNativeTrailsStatus").invoke(null));
        manifest.put("verifiedPresetName", ProjectMJNI.getCurrentPresetName());''')
    text = text.replace('manifest.put("presetNameChecks", FRAMES);', 'manifest.put("presetNameChecks", frameLimit);')
    text = text.replace('manifest.put("glErrorChecks", FRAMES);', 'manifest.put("glErrorChecks", frameLimit);')
    text = text.replace('"eligiblePresetCountAfterFrame479"', '"eligiblePresetCountAfterFinalFrame"')
    return text


def producer(path):
    """Accept ordinary producers or the recorded one-line seed-reset intervention."""
    path = Path(path).resolve()
    recorded = json.loads(path.read_text())
    if "parent_identity" not in recorded:
        return recorded, path.parent / "source", {"kind": "ordinary producer"}
    parent = recorded["parent_identity"]
    before = parent["source_files_sha256"]
    source = Path(recorded["source"])
    # The intervention records a compact native subset. Recompute all parent sources.
    after = {name: file_sha(source / name) for name in before}
    if any(after.get(name) != value for name, value in recorded["source_files_sha256"].items()):
        raise ValueError("Diagnostic source subset changed")
    changed = {name for name in set(before) | set(after) if before.get(name) != after.get(name)}
    if changed != {"core/src/main/cpp/lab_bridge.cpp"} or recorded.get("unchanged_parent_source_files_verified") != len(before) - 1:
        raise ValueError("Diagnostic producer changed more than the common seed-reset bridge")
    combined = dict(parent)
    combined.update({key: recorded[key] for key in ("aar", "aar_sha256", "apk", "apk_sha256", "native_sha256", "source_files_sha256")})
    combined["bridge_sha256"] = dict(parent["bridge_sha256"], **{"lab_bridge.cpp": after["core/src/main/cpp/lab_bridge.cpp"]})
    return combined, Path(recorded["source"]), {"kind": "one-line common seed-reset intervention",
        "parent_aar_sha256": parent["aar_sha256"], "reset_diff_sha256": recorded["reset_diff_sha256"],
        "complete_intervention_diff_sha256": recorded["complete_intervention_diff_sha256"]}


def seed_reset_site(original, source, role):
    bridge = source / "core/src/main/cpp/lab_bridge.cpp"
    if file_sha(bridge) != original["bridge_sha256"]["lab_bridge.cpp"]:
        raise ValueError("Recorded bridge source changed")
    if bridge_is_reset_after_seed(bridge.read_text()):
        return "common JNI initializer after PRESET_LAB_SEED", file_sha(bridge)
    if role == "baseline":
        relative = "third_party/projectm/src/libprojectM/ProjectM.cpp"
        constructor = source / relative
        text = constructor.read_text()
        if (file_sha(constructor) == original["source_files_sha256"][relative]
                and "srand(lab::Seed(1));" in text and "lab::ResetShaderRandom();" in text):
            return "verified historical seeded ProjectM constructor", file_sha(constructor)
    raise ValueError("Source producer has no verified reset after the seed environment is configured")


def fixture_overlay(project, aar, inventory_path, destination):
    inventory_path = Path(inventory_path).resolve()
    inventory = json.loads(inventory_path.read_text())
    fixtures = inventory.get("required_external_presets", [])
    if len(fixtures) != 1:
        raise ValueError("Supplemental worker expects the one explicitly recovered external fixture")
    fixture = fixtures[0]
    asset = inventory_path.parent / fixture["asset_path"]
    if file_sha(asset) != fixture["asset_sha256"] or asset.stat().st_size != fixture["asset_bytes"]:
        raise ValueError("External fixture bytes changed")
    generator_path = ROOT / "tools/gen-preset-index.py"
    spec = importlib.util.spec_from_file_location("random100_index_generator", generator_path)
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    with tempfile.TemporaryDirectory(dir=destination) as temporary:
        base = Path(temporary)
        with zipfile.ZipFile(aar) as archive:
            original_index = archive.read("assets/presets.idx")
            for name in archive.namelist():
                if name.startswith(("assets/presets/", "assets/textures/")) and not name.endswith("/"):
                    path = base / name.removeprefix("assets/")
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(archive.read(name))
        generator.PRESETS = str(base / "presets")
        generator.TEXTURES = str(base / "textures")
        if generator.build().encode() != original_index:
            raise ValueError("Existing index generator does not reproduce the frozen released index")
        shutil.copyfile(asset, base / "presets" / fixture["filename"])
        derived = generator.build().encode()
        weight = generator.weight_mb(asset.read_text(encoding="utf-8", errors="replace"), generator.image_bytes())
        added_line = (fixture["filename"] + "\t" + str(weight) + "\n").encode()
        if derived.count(added_line) != 1 or derived.replace(added_line, b"", 1) != original_index:
            raise ValueError("Supplemental index changes an existing entry")
    assets = project / "app/src/main/assets"
    (assets / "presets").mkdir(parents=True)
    shutil.copyfile(asset, assets / "presets" / fixture["filename"])
    (assets / "presets.idx").write_bytes(derived)
    index_diff = destination / "supplemental-index.diff"
    index_diff.write_text("".join(difflib.unified_diff(original_index.decode().splitlines(keepends=True),
                                                    derived.decode().splitlines(keepends=True),
                                                    fromfile="released/presets.idx", tofile="supplemental/presets.idx")))
    return {"schema": "projectmtv-supplemental-preset-overlay-v1", "fixture": fixture,
            "fixture_asset_path": "assets/presets/" + fixture["filename"], "fixture_sha256": file_sha(asset),
            "original_index_sha256": sha(original_index), "derived_index_sha256": sha(derived),
            "index_diff_sha256": file_sha(index_diff), "index_generator_sha256": file_sha(generator_path),
            "fixture_inventory_sha256": file_sha(inventory_path), "expected_preset_count": 9607,
            "existing_presets_and_textures_modified": False, "aar_binary_modified": False,
            "scope": "One additional lab preset and minimally derived APK-only index; not unchanged primary assets"}


def prepare(args):
    identity_path = args.source_identity.resolve() if args.source_identity else None
    release = None if args.validation_only else release_manifest(args.release_manifest)
    shipping = args.role == "released"
    if shipping:
        if release is None:
            raise ValueError("Unchanged runtime preparation requires the verified post-#49 release manifest")
        identity_path = Path(release["manifest_path"])
        original = dict(release, aar=release["aar_path"], shipping_byte_identity=True, abi=args.abi)
        reset_site, reset_hash = "none: unchanged public AAR has no seed/clock control", None
        intervention = {"kind": "unchanged released AAR"}
    else:
        if identity_path is None:
            raise ValueError("Source-control preparation requires --source-identity")
        original, source, intervention = producer(identity_path)
        if (original.get("shipping_byte_identity") is not False
                or original.get("abi") not in ("armeabi-v7a", "arm64-v8a")
                or (args.role == "candidate" and original.get("engine_commit") != CANDIDATE_ENGINE)):
            raise ValueError("Expected a hash-identified actual instrumented source producer")
        if release and args.role == "baseline":
            if (original["source_commit"] != release["source_commit"] or original["engine_commit"] != release["engine_commit"]
                    or original["ordered_patches"] != release["ordered_patches"]):
                raise ValueError("Baseline source producer is not the verified post-#49 released source")
        if release and args.role == "candidate":
            ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", release["source_commit"], original["source_commit"]],
                                      cwd=ROOT, capture_output=True)
            if ancestry.returncode != 0:
                raise ValueError("Candidate must incorporate the released source history before final preparation")
        reset_site, reset_hash = seed_reset_site(original, source, args.role)
    aar = Path(original["aar"]).resolve()
    if file_sha(aar) != original["aar_sha256"]:
        raise ValueError("Producer AAR bytes changed")
    abi = original["abi"]
    packages = SUPPLEMENTAL_PACKAGES if args.overlay_inventory else PACKAGES
    destination = args.work.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    project = destination / "worker"
    template = ROOT / "tools/core-corpus/android-worker"
    shutil.copytree(template, project, ignore=shutil.ignore_patterns("build", ".gradle", "local.properties"))
    for relative in ("gradlew", "gradlew.bat", "gradle/wrapper/gradle-wrapper.jar", "gradle/wrapper/gradle-wrapper.properties"):
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    (project / "local.properties").write_text("sdk.dir=" + str(args.sdk.resolve()) + "\n")
    java = project / "app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java"
    before = java.read_text()
    java.write_text(extend_harness(before, fixed_seed=not shipping))
    shutil.copyfile(HERE / "harness/EveryFrameHashes.java", java.with_name("EveryFrameHashes.java"))
    gradle = project / "app/build.gradle"
    text = gradle.read_text()
    text = once(text, "['nl.neerdael.projectmtv.corpuspublished', 'nl.neerdael.projectmtv.corpusbaseline', 'nl.neerdael.projectmtv.corpuscandidate']",
                repr(list(packages.values())))
    text = once(text, "abiFilters 'arm64-v8a'", "abiFilters '" + abi + "'")
    text = once(text, '    compileOptions {', "    packaging { jniLibs { keepDebugSymbols += ['**/*.so'] } }\n    compileOptions {")
    gradle.write_text(text)
    overlay = fixture_overlay(project, aar, args.overlay_inventory, destination) if args.overlay_inventory else None
    diff = destination / "harness.diff"
    diff.write_text("".join(difflib.unified_diff(before.splitlines(keepends=True), java.read_text().splitlines(keepends=True),
                                            fromfile="template/CorpusInstrumentation.java", tofile="private/CorpusInstrumentation.java")))
    identity = {"schema": SCHEMA, "role": args.role, "package": packages[args.role], "abi": abi,
                "artifact_scope": "supplemental" if overlay else "bundled", "supplemental_fixture_overlay": overlay,
                "source_commit": original["source_commit"], "engine_commit": original["engine_commit"],
                "ordered_patches": original["ordered_patches"], "source_identity_path": str(identity_path),
                "source_identity_sha256": file_sha(identity_path), "seed_reset_source_sha256": reset_hash,
                "seed_reset_site": reset_site, "producer_intervention": intervention,
                "release_manifest": release, "final_eligible": not args.validation_only,
                "shipping_byte_identity": shipping and not overlay, "core_aar_shipping_byte_identity": shipping,
                "apk_primary_assets_unchanged": not overlay, "native_aar_modified_for_this_worker": False,
                "aar": str(aar), "aar_sha256": original["aar_sha256"], "seed_reset_after_environment": not shipping,
                "harness_diff_sha256": file_sha(diff), "preparer_sha256": file_sha(Path(__file__)),
                "worker_source_sha256": {str(path.relative_to(project)): file_sha(path) for path in sorted(project.rglob("*")) if path.is_file()}}
    write(destination / "prepared.json", identity)
    if not args.build:
        print(destination / "prepared.json")
        return
    command = [str(project / "gradlew"), ":app:assembleDebug", "--no-daemon", "--max-workers=2", "--console=plain",
               "-PcoreAar=" + str(aar), "-PcorpusApplicationId=" + identity["package"]]
    environment = dict(os.environ, JAVA_HOME=str(args.jdk.resolve()), ANDROID_HOME=str(args.sdk.resolve()))
    with (destination / "worker-build.log").open("w") as output:
        subprocess.run(command, cwd=project, env=environment, stdout=output, stderr=subprocess.STDOUT, check=True)
    apk = destination / (args.role + ".apk")
    shutil.copyfile(project / "app/build/outputs/apk/debug/app-debug.apk", apk)
    assets = zip_hashes(aar, "assets/")
    if overlay:
        assets["assets/presets.idx"] = overlay["derived_index_sha256"]
        assets[overlay["fixture_asset_path"]] = overlay["fixture_sha256"]
    if assets != zip_hashes(apk, "assets/"):
        raise ValueError("Worker assets differ from the supplied AAR")
    selected = zip_hashes(aar, "jni/" + abi + "/")
    if {name.replace("jni/", "lib/", 1): value for name, value in selected.items()} != zip_hashes(apk, "lib/"):
        raise ValueError("Worker native bytes differ from the supplied AAR")
    if file_sha(aar) != identity["aar_sha256"]:
        raise ValueError("Producer AAR changed during packaging")
    identity.update(apk=str(apk), apk_sha256=file_sha(apk), assets_sha256=sha(canonical(assets).encode()),
                    native_sha256=selected, worker_build_command=command, worker_build_log_sha256=file_sha(destination / "worker-build.log"))
    write(destination / "identity.json", identity)
    print(destination / "identity.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=tuple(PACKAGES), required=True)
    parser.add_argument("--source-identity", type=Path)
    parser.add_argument("--abi", choices=("armeabi-v7a", "arm64-v8a"), default="arm64-v8a")
    parser.add_argument("--overlay-inventory", type=Path, help="Separate supplemental APK only; never change the primary bundle")
    parser.add_argument("--work", type=Path, required=True)
    eligibility = parser.add_mutually_exclusive_group(required=True)
    eligibility.add_argument("--release-manifest", type=Path)
    eligibility.add_argument("--validation-only", action="store_true")
    parser.add_argument("--sdk", type=Path, default=Path(os.environ.get("ANDROID_HOME", str(Path.home() / "Library/Android/sdk"))))
    parser.add_argument("--jdk", type=Path, default=Path(os.environ.get("JAVA_HOME", "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")))
    parser.add_argument("--build", action="store_true")
    prepare(parser.parse_args())
