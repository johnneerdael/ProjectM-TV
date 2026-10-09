#!/usr/bin/env python3
"""Seal exact private APK, original instrumented AAR, fixtures, PCM and worker source."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from verify_lifecycle import PROTOCOL, require, sha

PACKAGE = "nl.neerdael.projectmtv.corpuslifecycle"
HERE = Path(__file__).resolve().parent

def bind(args):
    identity = json.loads(args.core_identity.read_text())
    require(identity["source_commit"] == "cd3f0e44aa09afa72b7b729a0d75574154973b0d", "Wrong sealed 33-patch source")
    require(len(identity["ordered_patches"]) == 33 and identity["policy"] == "native" and identity["native_frame_time_api"] is True, "Wrong source policy/instrumentation")
    require(sha(args.aar) == identity["aar_sha256"], "Actual AAR changed")
    fixture_paths = sorted(args.fixtures.glob("*.milk"))
    require(fixture_paths, "No exact fixture files")
    fixtures = {path.name:sha(path) for path in fixture_paths}
    require(len(args.pcm.read_bytes()) == 705600, "PCM must have exactly 480 complete blocks")
    with zipfile.ZipFile(args.aar) as aar, zipfile.ZipFile(args.apk) as apk:
        native = "lib/arm64-v8a/libprojectmtv.so"
        native_sha256 = hashlib.sha256(apk.read(native)).hexdigest()
        require(apk.read(native) == aar.read("jni/arm64-v8a/libprojectmtv.so"), "APK actual JNI bytes differ from sealed AAR")
        for name in aar.namelist():
            if name.startswith("assets/") and not name.endswith("/") and name != "assets/presets.idx":
                require(apk.read(name) == aar.read(name), "Original AAR asset changed: " + name)
        original_assets = {name for name in aar.namelist() if name.startswith("assets/") and not name.endswith("/")}
        additional_assets = {name for name in apk.namelist() if name.startswith("assets/") and not name.endswith("/")} - original_assets
        require(additional_assets == {"assets/presets/"+name for name in fixtures}, "Unexpected APK-only assets")
        for name,value in fixtures.items():
            require(hashlib.sha256(apk.read("assets/presets/"+name)).hexdigest() == value, "APK fixture changed: " + name)
        original_index = aar.read("assets/presets.idx").decode("utf-8").splitlines()
        index = apk.read("assets/presets.idx")
        lines = index.decode("utf-8").splitlines()
        names = [line.split("\t",1)[0] for line in lines if line.split("\t",1)[0].lower().endswith(".milk")]
        require(len(names) == len(set(names)), "Duplicate APK preset index names")
        require(all(line in lines for line in original_index), "Original preset index rows changed")
        require(set(names)-{line.split("\t",1)[0] for line in original_index} == set(fixtures), "Fixture index delta differs")
    driver = json.loads(args.driver_identity.read_text())
    for key in ("fingerprint","glVendor","glRenderer","glVersion","glShadingLanguageVersion"):
        require(isinstance(driver[key],str) and driver[key], "Missing observed driver identity: " + key)
    require(driver["sdk"] == 34 and driver["ownedSerial"] == "emulator-5640" and driver["androidUser"] == 0, "Wrong device qualification identity")
    driver = {key:driver[key] for key in ("fingerprint","glVendor","glRenderer","glVersion","glShadingLanguageVersion","sdk","ownedSerial","androidUser")}
    sources = {str(path.relative_to(HERE)):sha(path) for path in sorted((HERE/"android-worker").rglob("*")) if path.is_file() and (path.suffix in (".java",".gradle",".xml",".properties")) and "build" not in path.relative_to(HERE/"android-worker").parts}
    binding = dict(protocol=PROTOCOL,package=PACKAGE,source_commit=identity["source_commit"],
        ordered_patches=identity["ordered_patches"],core_identity_sha256=sha(args.core_identity),
        aar=str(args.aar.resolve()),aar_sha256=sha(args.aar),apk=str(args.apk.resolve()),apk_sha256=sha(args.apk),
        apk_native_sha256=native_sha256,fixtures_sha256=fixtures,
        apk_index_sha256=hashlib.sha256(index).hexdigest(),apk_preset_count=len(names),
        pcm=str(args.pcm.resolve()),pcm_sha256=sha(args.pcm),worker_source_sha256=sources,
        verifier_sha256=sha(HERE/"verify_lifecycle.py"),controller_sha256=sha(HERE/"run_lifecycle.py"),
        binder_sha256=sha(Path(__file__)),driver_identity_sha256=sha(args.driver_identity),**driver)
    require(not args.output.exists(), "Refuse changing a frozen lifecycle binding")
    args.output.write_text(json.dumps(binding,sort_keys=True,indent=2)+"\n")
    return binding

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    for option in ("core-identity","aar","apk","fixtures","pcm","driver-identity","output"):
        parser.add_argument("--"+option,type=Path,required=True)
    bind(parser.parse_args())
