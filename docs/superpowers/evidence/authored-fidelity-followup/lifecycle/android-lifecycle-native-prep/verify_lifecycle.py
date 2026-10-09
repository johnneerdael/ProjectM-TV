#!/usr/bin/env python3
"""Scoped verifier for lifecycle-v1. The normal corpus validator is untouched."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/core-corpus"))
import run_corpus as corpus

PROTOCOL = "projectmtv-core-lifecycle-v1"
CAPTURES = [119,120,121,150,179,180,181,209,210,211,239,240,241,269,299,300,301,329,330,331,359,360,361,389,390,391,419,420,421,479]
EVENTS = [(120,"memory-pressure-initialized"),(180,"resize-reduced"),(210,"resize-restored"),
          (240,"context-destroy-recreate-core-alive"),(300,"mesh-reduced"),(330,"mesh-restored"),
          (360,"trails-high"),(390,"trails-standard"),(420,"preserved-context-suspend-resume")]

def require(value, reason):
    if not value:
        raise ValueError(reason)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(directory, binding):
    directory = Path(directory)
    raw = (directory / "request.json").read_bytes()
    request = json.loads(raw)
    manifest = json.loads((directory / "manifest.json").read_text())
    require(manifest.get("protocol") == request.get("protocol") == PROTOCOL, "Wrong lifecycle protocol")
    require(request["androidUser"] == 0 and request["ownedSerial"] == "emulator-5640", "Wrong owned device/user")
    require(request["binding"] == binding == manifest["binding"], "Frozen identity binding differs")
    require(manifest.get("job") == request and manifest.get("requestSha256") == hashlib.sha256(raw).hexdigest(), "Wrong request identity")
    require(manifest.get("applicationId") == binding["package"], "Wrong worker package")
    require(manifest.get("status") == "ok", "Worker failure: " + str(manifest.get("error", manifest)))
    require(not any(key in manifest for key in ("error","releaseError","eglCleanupError")), "Cleanup or job error")
    require(manifest.get("framesRendered") == manifest.get("presetNameChecks") == manifest.get("glErrorChecks") == 480, "Incomplete frame checks")
    require(manifest.get("coreReleased") is True and manifest.get("eglDestroyed") is True, "Incomplete cleanup")
    require(manifest.get("coreInitCalls") == 1 and manifest.get("coreSurfaceCreatedCalls") == manifest.get("expectedPresetReloads") == 2, "Wrong lifecycle topology")
    require(manifest.get("presetChangeCounter") == 2, "Expected exactly two preset loads")
    require(manifest.get("eligiblePresetCountBeforeFrame0") == manifest.get("eligiblePresetCountAfterFrame479") == 1, "Preset eligibility changed")
    require(manifest.get("verifiedPresetName") == request["preset"], "Wrong preset")
    require(manifest.get("presetAssetSha256") == binding["fixtures_sha256"][request["preset"]], "Fixture changed")
    require(manifest.get("indexSha256") == binding["apk_index_sha256"] and manifest.get("bundledPresetCount") == binding["apk_preset_count"], "APK inventory changed")
    require(manifest.get("pcmSha256") == binding["pcm_sha256"], "PCM changed")
    require(manifest.get("determinism") == "instrumented-fixed-clock-seed" and request["seed"] == 12345, "Seed/clock mode changed")
    require((request["referenceWidth"], request["referenceHeight"]) == (1280,720), "Expected frozen Native4K reference canvas")
    require(manifest["device"]["fingerprint"] == binding["fingerprint"], "Device fingerprint changed")
    require(manifest["device"]["sdk"] == 34 and manifest["glVersion"].startswith("OpenGL ES 3"), "Wrong SDK or GL")
    for key in ("glVendor","glRenderer","glVersion","glShadingLanguageVersion"):
        require(manifest[key] == binding[key], "Frozen driver identity differs: " + key)
    require([call["beforeFrame"] for call in manifest["memoryPressureCalls"]] == [-1], "Unexpected wall-dependent pause events")
    states = manifest["frameStates"]
    require(len(states) == 480, "Missing per-frame lifecycle states")
    for frame,state in enumerate(states):
        generation = 1 if frame < 240 else 2
        expected_size = (request["reducedWidth"], request["reducedHeight"]) if 180 <= frame < 210 else (request["width"], request["height"])
        require(state["frame"] == frame and state["completedFrameSerial"] == frame+1, "Completed serial skipped/repeated")
        require(state["contextGeneration"] == state["presetChangeCounter"] == generation, "Wrong context/reload generation")
        require(state["generationFrameOrdinal"] == frame-(240 if generation == 2 else 0), "Wrong generation frame ordinal")
        require(state["globalClockSeconds"] == frame/30 and state["pcmBlock"] == frame, "Clock/PCM index was reset/relabelled")
        require((state["width"],state["height"]) == expected_size, "Wrong rendered size")
        require((state["meshWidth"],state["meshHeight"]) == ((24,16) if 300 <= frame < 330 else (48,32)), "Wrong mesh request")
        require(state["requestedTrails"] == (2 if 360 <= frame < 390 else 0), "Wrong trails request")
        require(state["nativeTrailsStatus"].startswith("High" if 360 <= frame < 390 else "Standard"), "Trails request was not applied")
        require("1280×720 canvas" in state["nativeTrailsStatus"], "Active canvas required; inactive/fallback does not qualify Native detail")
        require(state["drawFramebufferBinding"] == state["glError"] == 0, "Strict GL/draw target failure")
    events = manifest["lifecycleEvents"]
    require([(event["beforeFrame"],event["kind"]) for event in events] == EVENTS, "Lifecycle events differ")
    for event in events:
        frame = event["beforeFrame"]
        require(event["completedFrameSerialBefore"] == frame and event["globalClockSeconds"] == frame/30, "Event ran before initialized preceding frame")
        require(event["presetChangeCounterBefore"] == (1 if frame <= 240 else 2), "Reload occurred at wrong event")
        require(event["afterFrameState"] == states[frame], "Event completion missing")
        if frame in (180,210,420):
            require(event["contextPreserved"] is True, "Preserved context was replaced")
        if frame == 240:
            require(event["oldEglDestroyed"] is True and event["newEglCreated"] is True, "No actual EGL destroy/recreate")
            require(event["publishedPresetWhileNoContext"] == request["preset"] and event["presetChangeCounterWhileNoContext"] == 1, "Published core state vanished before recreation")
            require(event["coreReleasedBeforeRecreate"] is False and event["seedReset"] is False and event["engineStateResetExpected"] is True, "Core/seed lifecycle differs")
        if frame == 420:
            require(event["surfacePreserved"] is True and event["suspendWallMs"] >= 50, "Resume scope differs")
    captures = manifest["captures"]
    require([capture["frame"] for capture in captures] == CAPTURES, "Missing lifecycle boundary captures")
    for capture in captures:
        state = states[capture["frame"]]
        require(capture["captureReadFramebufferBinding"] == 0, "Capture did not bind final read framebuffer zero")
        require((capture["width"],capture["height"]) == (state["width"],state["height"]), "Capture size differs")
        require(capture["contextGeneration"] == state["contextGeneration"] and capture["generationFrameOrdinal"] == state["generationFrameOrdinal"], "Capture generation differs")
        corpus.decode_capture(directory / ("frame-%03d.png" % capture["frame"]), capture)
    return manifest

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("directory",type=Path)
    parser.add_argument("--binding",type=Path,required=True)
    args=parser.parse_args()
    verify(args.directory,json.loads(args.binding.read_text()))
    print("Lifecycle protocol identity/events/strict GL/capture checks pass; no cross-generation pixel or cost claim")
