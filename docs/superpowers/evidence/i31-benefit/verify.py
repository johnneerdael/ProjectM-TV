"""Verify frozen I31 request/source/timing/statistics custody without rendering."""
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

from benchmark import analyze, canonical, config, digest, schedule_recipe
from source_observer import observe

SOURCE = "8a15996e8510533113a44e26feaddc3a7d6e85f5"
ENGINE = "6f64807467e312034883a4389e6aa80a675458bc"
EVALUATOR = "22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a"
VIDEO = "src/libprojectM/MilkdropPreset/VideoEcho.cpp"
PATCH = "0019-gamma-only-pass-epsilon.patch"
# Frozen identities observed at execution, independent of mutable receipt labels.
CATALOG_SOURCE_SHA256 = "5e48da2b8a47f160a1884a648cae19127d833e69f5b5f3c55ffb5c64eff66533"
ENGINE_VIDEO_SHA256 = "56d7ab07f064c3addd5d71a6e7dac07d1d51f51f8af50bc02bf42379c106403b"
# Established independently from all 80 preserved original result.json files,
# then cross-checked against the decoded compressed corpus. Never derive this
# expected value from the artifact under verification or its analysis output.
TIMED_CORPUS_SHA256 = "2f5263bb1a3e52d4b434050ebc225d528f3b88fab6e906119b5a3c20157446a1"
INPUTS_SHA256 = "d5afb472ed0801641c9f2c76919207918e417b0768b668f04537ed944e52f7d6"
TIMED_WORKERS = {"with-0019": "6ed77578216c4774c00bb6eafdbe19605b87801f5289afeac9ce3ee1031f9693",
                 "without-0019": "25c13aae8b2c2b03903b3c6a510da091e993bc077c225343ea850d4c8866e4eb"}
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(root, name):
    return json.loads((root / name).read_text())

def verify_sources(root, repo, workers, custody):
    catalog = repo / "docs/superpowers/evidence/patch-visual-catalog"
    base = load(catalog, "patched-source-tree.json")
    catalog_worker = load(catalog, "workers.json")["patched"]
    assert digest(base) == catalog_worker["source_tree_sha256"] == CATALOG_SOURCE_SHA256, "catalog source inventory"
    assert catalog_worker["source_commit"] == SOURCE
    assert catalog_worker["engine"]["commit"] == ENGINE
    assert catalog_worker["evaluator_commit"] == EVALUATOR
    source = root / "source-proof"
    assert {p.name for p in source.iterdir() if p.is_file()} == set(custody["source_files"])
    for name, expected in custody["source_files"].items():
        assert sha(source / name) == expected, f"source proof bytes: {name}"
    patch_bytes = subprocess.check_output(["git", "-C", str(repo), "show",
                                         f"{SOURCE}:tools/projectm-patches/{PATCH}"])
    assert (source / "0019.patch").read_bytes() == patch_bytes, "frozen patch bytes"
    assert (repo / "tools/projectm-patches" / PATCH).read_bytes() == patch_bytes, "shipping patch drift"
    assert sha(source / "frozen-patched.cpp") == base[VIDEO], "frozen patched VideoEcho"
    assert sha(source / "engine-base.cpp") == ENGINE_VIDEO_SHA256, "engine pin VideoEcho bytes"
    # Reconstruct this file from the engine pin and every patch at the frozen app
    # commit, independently of the catalog's post-application source inventory.
    with tempfile.TemporaryDirectory(prefix="i31-frozen-source-") as temporary:
        tree = Path(temporary)
        video = tree / VIDEO
        video.parent.mkdir(parents=True)
        video.write_bytes((source / "engine-base.cpp").read_bytes())
        for patch in catalog_worker["ordered_patches"]:
            content = subprocess.check_output(["git", "-C", str(repo), "show",
                f"{SOURCE}:tools/projectm-patches/{patch['filename']}"])
            assert hashlib.sha256(content).hexdigest() == patch["sha256"], "ordered frozen patch bytes"
            subprocess.run(["git", "apply", "--include=" + VIDEO, "-"], input=content,
                           cwd=tree, env=dict(os.environ, GIT_CEILING_DIRECTORIES=str(tree.parent)),
                           check=True, capture_output=True)
        assert video.read_bytes() == (source / "frozen-patched.cpp").read_bytes(), "frozen Git patch reconstruction"
    # Reverse the real committed patch, then apply the SAME observer recipe to both roles.
    with tempfile.TemporaryDirectory(prefix="i31-source-proof-") as temporary:
        tree = Path(temporary)
        video = tree / VIDEO
        video.parent.mkdir(parents=True)
        video.write_bytes((source / "frozen-patched.cpp").read_bytes())
        subprocess.run(["git", "apply", "--reverse", str((source / "0019.patch").resolve())],
                       cwd=tree, env=dict(os.environ, GIT_CEILING_DIRECTORIES=str(tree.parent)),
                       check=True, capture_output=True)
        before = observe(video.read_text()).encode()
    after = observe((source / "frozen-patched.cpp").read_text()).encode()
    for role, expected in (("without-0019", before), ("with-0019", after)):
        assert (source / f"{role}.cpp").read_bytes() == expected, f"exact observer/patch recipe: {role}"
        expected_inventory = {**base, VIDEO: hashlib.sha256(expected).hexdigest(),
                              "src/libprojectM/analysis_hooks.hpp": sha(root / "harness/analysis_hooks.hpp")}
        assert workers[role]["source"] == expected_inventory, f"complete source inventory: {role}"
        assert workers[role]["role"] == role
        assert workers[role]["worker_sha256"] == TIMED_WORKERS[role], "frozen timed executable"
        harness = workers[role]["harness"]
        assert set(harness) == {"CMakeLists.txt", "worker.cpp", "gl_capture.hpp", "analysis_hooks.hpp",
                               "vendor/json.hpp", "vendor/LICENSE.json"}
        for name, expected_hash in harness.items():
            if name.startswith("vendor/"):
                assert expected_hash == catalog_worker["harness"][name], "frozen vendored harness"
            else:
                assert sha(root / "harness" / name) == expected_hash, f"timing harness: {name}"
    assert workers["without-0019"]["harness"] == workers["with-0019"]["harness"]

# These observer workers linked the unchanged timed-role static libraries. They
# are separate executables; readback/hash/PNG work remains outside timed jobs.
VISUAL_IDENTITIES = {
    "with-0019": ("a225930be2ec56136dd06bf7921fb18cd96fc699f5021efd8108f606ccb31b96",
                  "37109ee97c61b3c0b2bfc230edf77596ce2674cdad0f8f3b157e39bd9c8f4628"),
    "without-0019": ("51823fcb49326deefa987ee7dea22bbd598a35a054f824549702700cbf071218",
                     "1d937835e9a060989a77d5e4f9d9425f8d8d6122faa5ab199d607fa8c088b393"),
}
SELECTED_FRAMES = (119, 239, 479)

def verify_visual(root, workers, inputs, records, observers, results, replay):
    expected_names = {f"{profile}-{role}-{repeat}" for profile in ("classic", "standard")
                      for role in VISUAL_IDENTITIES for repeat in (0, 1)}
    assert set(records) == expected_names and set(observers) == set(VISUAL_IDENTITIES), "visual job/role set"
    assert set(results) == {"classic", "standard"}, "visual profile set"
    canonical_harness = None
    for role, observer in observers.items():
        assert set(observer) == {"observer_worker_sha256", "engine_library_sha256", "harness"}
        assert (observer["observer_worker_sha256"], observer["engine_library_sha256"]) == VISUAL_IDENTITIES[role], "frozen visual worker/library"
        harness = observer["harness"]
        assert set(harness) == set(workers[role]["harness"]), "visual harness file set"
        for name, expected in harness.items():
            if name.startswith("vendor/"):
                assert expected == workers[role]["harness"][name], "visual vendored harness"
            elif name == "CMakeLists.txt":
                # Observer executable is linked by link_images.py; the workspace
                # inventory also records the unchanged shared engine CMake file.
                assert sha(root / "harness" / name) == expected, "shared visual CMake bytes"
            else:
                assert sha(root / "image-harness" / name) == expected, f"visual harness bytes: {name}"
        if canonical_harness is None:
            canonical_harness = harness
        assert harness == canonical_harness, "shared visual observer harness"
    snapshots = {"preset_sha256": inputs["preset_sha256"]["original.milk"],
                 "pcm_sha256": inputs["pcm_sha256"], "texture_inventory": inputs["textures"]}
    rebuilt = {}
    output_roots = set()
    capture_states = 0
    for profile in ("classic", "standard"):
        rebuilt[profile] = {}
        for role in VISUAL_IDENTITIES:
            hashes = []
            for repeat in (0, 1):
                name = f"{profile}-{role}-{repeat}"
                record = records[name]
                assert set(record) == {"job", "manifest", "inputs_before", "inputs_after", "observer_worker_sha256",
                                       "linked_engine_library_sha256", "frame_sha256", "selected_pngs", "observer_harness"}, "visual record fields"
                job, manifest = record["job"], record["manifest"]
                assert set(job) == {"schema_version", "config", "pcm_path", "preset_path", "texture_root", "manifest_path", "identity"}
                assert type(job["schema_version"]) is int and job["schema_version"] == 1
                assert canonical(job["config"]) == canonical(manifest["config"]) == canonical(config(profile)), "visual complete profile/config"
                identity = {"role": role, "kind": "selected-frame verification, outside timedjobs",
                            "observer_worker_sha256": observers[role]["observer_worker_sha256"],
                            "engine_library_sha256": observers[role]["engine_library_sha256"]}
                assert job["identity"] == manifest["identity"] == identity, "visual request/manifest/role identity"
                assert record["observer_worker_sha256"] == identity["observer_worker_sha256"]
                assert record["linked_engine_library_sha256"] == identity["engine_library_sha256"]
                assert record["observer_harness"] == canonical_harness
                work = Path(workers[role]["worker"]).parents[2]
                request_repo = work.parent.parent
                assert job["preset_path"] == str(work / "original.milk"), "visual preset path"
                assert job["pcm_path"] == str(request_repo / inputs["pcm_path"]), "visual PCM path"
                assert job["texture_root"] == str(request_repo / "core/src/main/assets/textures"), "visual texture path"
                manifest_path = Path(job["manifest_path"])
                assert manifest_path.parts[-3:] == ("visual", name, "manifest.json"), "visual output name"
                output_roots.add(manifest_path.parents[2])
                assert record["inputs_before"] == record["inputs_after"] == snapshots, "observed visual inputs"
                assert manifest["status"] == "success" and manifest["gl_error_frames"] == 0
                assert manifest["gl_renderer"] == "Apple M4 Pro" and manifest["gl_version"] == "4.1 Metal - 89.4"
                assert manifest["width"] == 3840 and manifest["height"] == 2160 and manifest["frames"] == 480
                assert manifest["fps"] == 30 and manifest["seed"] == 12345
                states = manifest["readback_states"]
                assert [state["frame"] for state in states] == list(SELECTED_FRAMES), "selected readback frames"
                for state in states:
                    assert set(state) == {"frame", "capture_framebuffer", "before_read_framebuffer", "after_read_framebuffer",
                                          "before_read_buffer", "after_read_buffer", "before_pack_alignment", "after_pack_alignment"}
                    assert all(type(value) is int for value in state.values()), "readback state types"
                    assert state["capture_framebuffer"] > 0
                    assert state["before_read_framebuffer"] >= 0 and state["before_read_framebuffer"] != state["capture_framebuffer"], "distinct caller read framebuffer"
                    assert state["before_pack_alignment"] in (1, 2, 4, 8)
                    for field in ("read_framebuffer", "read_buffer", "pack_alignment"):
                        assert state["before_" + field] == state["after_" + field], f"caller {field} restoration"
                    capture_states += 1
                frames = record["frame_sha256"]
                assert len(frames) == 3 and all(len(value) == 64 and all(c in "0123456789abcdef" for c in value) for value in frames), "selected RGB hashes"
                pngs = record["selected_pngs"]
                assert set(pngs) == ({f"frame-{frame:03d}.png" for frame in SELECTED_FRAMES} if repeat == 0 else set()), "selected PNG set"
                assert all(len(value) == 64 and all(c in "0123456789abcdef" for c in value) for value in pngs.values())
                hashes.append(frames)
            assert hashes[0] == hashes[1], "independent visual repeat hashes"
            rebuilt[profile][role] = {"repeat_equal": True, "hashes": hashes}
        assert rebuilt[profile]["with-0019"]["hashes"] == rebuilt[profile]["without-0019"]["hashes"], "RGB equality between roles"
        assert records[f"{profile}-with-0019-0"]["selected_pngs"] == records[f"{profile}-without-0019-0"]["selected_pngs"], "lossless PNG role equality"
        rebuilt[profile]["frame_differences"] = {str(frame): {"total_rgb_difference": 0, "changed_pixels": 0,
                                                           "max_channel_difference": 0, "mae": 0.0}
                                                  for frame in SELECTED_FRAMES}
    assert len(output_roots) == 1, "single selected-frame replay output"
    assert canonical(results) == canonical(rebuilt), "visual results regenerated from independent job hashes"
    assert replay["timed_benchmark_replayed"] is False and replay["runs"] == len(records) == 8
    assert replay["capture_states"] == capture_states == 24
    return capture_states

def verify(root=ROOT, repo=REPO, *, data=None, visuals=True):
    data = data or {}
    get = lambda name: data[name] if name in data else load(root, name)
    workers, schedule, inputs, requests, custody = (get(name) for name in
        ("workers.json", "schedule.json", "inputs.json", "requests.json", "custody.json"))
    if "runs" in data:
        runs = data["runs"]
    else:
        with gzip.open(root / "timed-runs.json.gz", "rt") as stream:
            runs = json.load(stream)
    assert digest(runs) == custody["timed_corpus_sha256"] == TIMED_CORPUS_SHA256, "frozen original timed corpus"
    assert schedule == schedule_recipe(), "balanced canonical case/profile/schedule"
    assert set(runs) == set(requests["requests"]) == {job["name"] for job in schedule}, "complete run/request set"
    assert custody["schema_version"] == requests["schema_version"] == 1
    assert custody["source_base"] == inputs["source_base"] == SOURCE
    assert custody["engine_commit"] == inputs["engine_commit"] == ENGINE
    assert custody["evaluator_commit"] == inputs["evaluator_commit"] == EVALUATOR
    assert inputs["only_removed_patch"] == PATCH
    assert digest(inputs) == INPUTS_SHA256, "frozen input inventory"
    for field, value in (("workers", workers), ("schedule", schedule), ("inputs", inputs), ("requests", requests)):
        assert digest(value) == custody[f"{field}_sha256"], f"canonical {field} custody"
    verify_sources(root, repo, workers, custody)
    pcm = repo / inputs["pcm_path"]
    assert inputs["pcm_path"] == "docs/superpowers/evidence/patch-visual-catalog/audio/frozen-480-frames.f32"
    assert sha(pcm) == inputs["pcm_sha256"] and pcm.stat().st_size == 480 * 1470 * 4, "frozen float32 PCM"
    assert set(inputs["preset_sha256"]) == {"original.milk", "inactive-gamma2.milk"}
    for name, expected in inputs["preset_sha256"].items():
        assert sha(root / name) == expected, f"preset bytes: {name}"
    catalog = repo / "docs/superpowers/evidence/patch-visual-catalog"
    assert inputs["textures"] == load(catalog, "textures.json"), "frozen texture inventory"
    textures = repo / "core/src/main/assets/textures"
    assert {p.relative_to(textures).as_posix(): sha(p) for p in sorted(textures.rglob("*")) if p.is_file()} == inputs["textures"], "runtime texture bytes"
    measured_frames = 0
    for job in schedule:
        run = runs[job["name"]]
        receipt = requests["requests"][job["name"]]
        request = receipt["request"]
        assert digest(request) == receipt["request_sha256"], "complete request digest"
        assert set(request) == {"schema_version", "config", "pcm_path", "preset_path", "texture_root", "manifest_path", "identity"}
        assert request["schema_version"] == 1
        assert canonical(request["config"]) == canonical(run["config"]) == canonical(config(job["profile"])), "complete profile configuration/types"
        work_root = Path(workers[job["role"]]["worker"]).parents[2]
        request_repo = work_root.parent.parent
        assert request["preset_path"] == str(work_root / job["preset"]), "scheduled preset path"
        assert request["pcm_path"] == str(request_repo / inputs["pcm_path"]), "PCM request path"
        assert request["texture_root"] == str(request_repo / "core/src/main/assets/textures"), "texture request path"
        assert request["manifest_path"] == str(work_root / "runs" / job["name"] / "result.json"), "result/request name"
        assert receipt["input_hashes"] == {"preset_sha256": inputs["preset_sha256"][job["preset"]],
                                           "pcm_sha256": inputs["pcm_sha256"], "textures_sha256": digest(inputs["textures"])}
        expected_identity = {"role": job["role"], "worker_sha256": workers[job["role"]]["worker_sha256"],
                             "source_tree_sha256": digest(workers[job["role"]]["source"])}
        assert run["identity"] == request["identity"] == expected_identity, "worker/source/request binding"
        assert run["status"] == "success" and run["gl_error_frames"] == 0
        assert run["gl_renderer"] == "Apple M4 Pro" and run["gl_version"] == "4.1 Metal - 89.4"
        assert run["width"] == 3840 and run["height"] == 2160 and run["fps_clock"] == 30
        assert run["frames"] == 480 and run["warmup_frames"] == 120
        assert run["gpu_timer_valid"] is True and run["gpu_probe_nonzero"] == 10 and run["gpu_timer_bits"] == 32
        assert len(run["samples"]) == 480
        expected_draws = 2 if job["case"] == "inactive-classic" or job["role"] == "with-0019" else 3
        expected_gamma = 2.0 if job["case"] == "inactive-classic" else 2.000999927520752
        for frame, sample in enumerate(run["samples"]):
            assert sample["frame"] == frame and sample["measured"] is (frame >= 120), "warmup/frame sequence"
            assert sample["gamma_draws"] == expected_draws and sample["gamma_invocations"] == 1
            assert sample["gamma"] == expected_gamma, "active/control gamma binding"
            assert sample["gpu_ns"] > 0
            assert all(math.isfinite(sample[key]) and sample[key] > 0 for key in ("submit_ms", "complete_ms", "gpu_ns"))
        measured_frames += 360
    assert canonical(get("analysis.json")) == canonical(analyze(schedule, runs)), "all published analysis statistics"
    if visuals:
        verify_visual(root, workers, inputs, get("visual-jobs.json"), get("visual-workers.json"),
                      get("visual-results.json"), get("observer-replay.json"))
    return measured_frames

if __name__ == "__main__":
    frames = verify()
    print(f"PASS: 80 complete requests, {frames} measured frames, frozen source/input/harness bindings, "
          "exact 0019 ablation, all means/block deltas/100000-bootstrap statistics; selected RGB/repeats match")
