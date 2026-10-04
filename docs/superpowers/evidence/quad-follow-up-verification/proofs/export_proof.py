"""Package recorded evidence. All writes stay in this script's directory."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import textwrap

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
os.environ["MPLCONFIGDIR"] = str(OUT / ".matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

RAW = OUT / "raw"
RAW.mkdir(exist_ok=True)
sources = {}
visuals = []
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "svg.fonttype": "none"})
RED = "#a43835"
GREEN = "#21715b"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source(path, key, ranges=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    record = {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
    if ranges:
        lines = path.read_text().splitlines()
        target = RAW / (key + ".txt")
        chunks = []
        for low, high in ranges:
            assert 1 <= low <= high <= len(lines)
            chunks.extend(f"{i}: {lines[i - 1]}" for i in range(low, high + 1))
        target.write_text("\n".join(chunks) + "\n")
        record.update({"source_line_ranges": ranges, "excerpt": str(target.relative_to(OUT)),
                       "excerpt_sha256": sha(target)})
    else:
        target = RAW / (key + path.suffix)
        shutil.copyfile(path, target)
        record.update({"copy": str(target.relative_to(OUT)), "copy_sha256": sha(target)})
    sources[key] = record
    return record


def panel(ax, heading, body, color):
    ax.set_axis_off()
    ax.text(0, 1, heading, va="top", fontsize=16, weight="bold", color=color, transform=ax.transAxes)
    wrapped = "\n".join(textwrap.fill(line, 78, subsequent_indent="   ") if line else "" for line in body.splitlines())
    ax.text(0, .86, wrapped, va="top", fontsize=11, fontfamily="DejaVu Sans Mono",
            linespacing=1.5, transform=ax.transAxes)


def save(fig, name, title, subtitle, footer, prove, limits, used, identity=None):
    fig.suptitle(title, x=.045, y=.965, ha="left", fontsize=22, weight="bold")
    fig.text(.045, .902, subtitle, fontsize=12, va="top")
    fig.text(.045, .028, footer, fontsize=9, va="bottom", color="#444444", linespacing=1.5)
    for ext in ["png", "svg"]:
        fig.savefig(OUT / (name + "." + ext), dpi=150, facecolor="white")
    plt.close(fig)
    visuals.append({"id": name, "artifacts": [name + ".png", name + ".svg"], "what_it_proves": prove,
                    "limitations": limits, "source_keys": used, "build_identities": identity or []})


# 1: A deliberately artificial message tests the ordinary std::exception handler.
diag_red = source("build/follow-ups/shader-message-red.log", "diagnostic-red", [(196, 203)])
diag_green = source("build/follow-ups/shader-message-green.log", "diagnostic-green", [(142, 145)])
test = ROOT / "third_party/projectm/tests/libprojectM/ShaderExceptionTest.cpp"
test_lines = test.read_text().splitlines()
diag_test = source(test, "diagnostic-test", [(1, len(test_lines))])
fig, axes = plt.subplots(1, 2, figsize=(15, 8.2))
fig.subplots_adjust(left=.045, right=.975, top=.77, bottom=.20, wspace=.14)
panel(axes[0], "Before — detail lost in what()", "shader-message-red.log, L199–203\n\n" +
      "error.what()\n  Which is: \"std::exception\"\nExpected:\n  \"fragment shader: unsupported driver instruction\"\n\n[ FAILED ] standard-handler regression test", RED)
panel(axes[1], "After — same assertion passes", "shader-message-green.log, L142–145\n\n" +
      "[ OK ] ShaderException.\nPreservesDriverDiagnosticThroughStandardExceptionHandler\n\nThe test throws the same artificial message and checks\nwhat() through catch (const std::exception&).\n\nThis is test input, not an actual driver's wording.", GREEN)
save(fig, "01-diagnostic-preserved", "ShaderException preserves its owned diagnostic",
     "Standard-handler regression • artificial diagnostic string, honestly labeled",
     f"Sources: {diag_red['path']} (L196–203) SHA256 {diag_red['sha256'][:16]}\n"
     f"{diag_green['path']} (L142–145) SHA256 {diag_green['sha256'][:16]} • full hashes and test source in manifest.json / raw/",
     "The RED assertion reports std::exception; the GREEN standard-handler assertion succeeds for the artificial owned message.",
     ["The string is artificial unit-test input, not a captured GPU driver diagnostic.",
      "GREEN log records assertion success, not a printed what() string.",
      "Historical unit logs contain no immutable build identity; current test source is provided and hashed separately."],
     ["diagnostic-red", "diagnostic-green", "diagnostic-test"])


# 2: Fresh rerun logs print actual glIsShader endpoints, not extrapolated samples.
allocation_builds = json.loads((OUT / "allocation-builds.json").read_text())
endpoints = []
alloc_keys = []
for build in allocation_builds:
    log = OUT / build["log_path"]
    lines = log.read_text().splitlines()
    positions = [i for i, line in enumerate(lines, 1) if line.startswith("RESOURCE_ENDPOINT")]
    key = "allocation-" + build["state"]
    source(log, key, [(i, i) for i in positions])
    alloc_keys.append(key)
    for i in positions:
        match = re.fullmatch(r"RESOURCE_ENDPOINT (fragment_attempts|repeated_attempts)=(\d+) live_shaders=(\d+)", lines[i - 1])
        assert match
        endpoints.append({"state": build["state"], "attempts": int(match[2]), "live_shaders": int(match[3]),
                          "source_key": key, "source_line": i, "measurement": "glIsShader on tracked real driver objects"})
(RAW / "allocation-endpoints.json").write_text(json.dumps(endpoints, indent=2))
fig, ax = plt.subplots(figsize=(15, 8.2))
fig.subplots_adjust(left=.085, right=.96, top=.76, bottom=.24)
x = np.array([0, 1])
for state, delta, color, label in [("red", -.18, RED, "Pre-fix snapshot"), ("green", .18, GREEN, "Fixed snapshot")]:
    values = [next(e["live_shaders"] for e in endpoints if e["state"] == state and e["attempts"] == n) for n in [1, 16]]
    bars = ax.bar(x + delta, values, .36, color=color, label=label)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, value + .45, str(value), ha="center", weight="bold", fontsize=16, color=color)
ax.set_xticks(x, ["After 1 fragment rejection", "After 16 repeated attempts"])
ax.set_ylabel("Live shader objects at measured endpoint")
ax.set_ylim(0, 18.8)
ax.set_yticks([0, 4, 8, 12, 16])
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="upper left", frameon=False)
ax.grid(axis="y", alpha=.15)
save(fig, "02-vertex-shader-lifetime", "Failed fragment compilation releases the vertex shader",
     "Fresh real CGL rerun • measured endpoints only • no intermediate counts or memory estimates",
     "Sources: allocation/red/run.log and allocation/green/run.log — source line numbers in raw/allocation-endpoints.json\n"
     "Each repeated attempt exercises vertex, fragment and link rejection; one fragment rejection per attempt.\n"
     "Original session RED log was not saved; these are new reruns. Snapshot identities and every source/binary/log SHA256: allocation-builds.json",
     "The pre-fix driver retains 1 shader after one fragment rejection and 16 after 16 repeated attempts; fixed driver retains zero at both measured endpoints.",
     ["Fresh CGL reproduction, not the unsaved original session transcript.",
      "Chart contains only two observed endpoints per build; it claims no intermediate trajectory, RSS size, or field failure rate.",
      "Copied fixture omits the separately-tested what() comparison and adds explicit endpoint printing; copied-source hashes and commands are recorded.",
      "Desktop macOS CGL driver; no Android GPU resource measurement."], alloc_keys,
     [{"state": b["state"], "identity": b["worker_identity"], "snapshot": b["snapshot"]} for b in allocation_builds])


# 3: A real frame exists only for the successful fallback run.
jobs = ROOT / "build/follow-ups/verification/shader-fallback/jobs"
red_job = ROOT / "build/follow-ups/verification/shader-reject-red/jobs/Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-r1/worker/run-en_sw9nr"
green_case = jobs / "Geiss - Surface (1-02 Version).milk-c665-diffusion-reject-safe-on-r1"
baseline_case = jobs / "Geiss - Surface (1-02 Version).milk-c665-final-r1"
red_stderr = source(red_job / "stderr.log", "fallback-red-stderr", [(1, 1)])
source(red_job / "manifest.json", "fallback-red-manifest")
source(red_job / "job.json", "fallback-red-job")
source("build/follow-ups/shader-reject-red.log", "fallback-red-orchestrator", [(1, 7)])
red_manifest = json.loads((red_job / "manifest.json").read_text())
assert red_manifest["status"] == "failed" and red_manifest["observed_frames"] == 0
red_identity = json.loads((red_job / "job.json").read_text())["identity"]
green_worker = next((green_case / "worker").iterdir())
source(green_worker / "manifest.json", "fallback-green-manifest")
source(green_worker / "job.json", "fallback-green-job")
green_manifest = json.loads((green_worker / "manifest.json").read_text())
green_metrics = json.loads((green_case / "metrics.json").read_text())
baseline_metrics = json.loads((baseline_case / "metrics.json").read_text())
source(green_case / "metrics.json", "fallback-green-metrics")
source(baseline_case / "metrics.json", "fallback-baseline-metrics")
source("docs/superpowers/evidence/quad-follow-up-verification/results-shader-fallback.json", "fallback-matrix-summary")
snapshot_path = green_case / "five.npz"
snapshot = np.load(snapshot_path)["frames"][-1]
baseline_snapshot = np.load(baseline_case / "five.npz")["frames"][-1]
assert np.array_equal(snapshot, baseline_snapshot)
assert green_metrics["size"] == [1182, 665] and snapshot.shape == (665, 1182, 3)
pixel_sha = hashlib.sha256(snapshot.tobytes()).hexdigest()
assert pixel_sha == green_metrics["sha256_measurement_frames"][-1]
assert green_metrics["sha256_all_frames"] == baseline_metrics["sha256_all_frames"]
frame_path = OUT / "03-fallback-geiss-frame-239.png"
Image.fromarray(snapshot).save(frame_path)
assert np.array_equal(np.asarray(Image.open(frame_path)), snapshot)
np.savez_compressed(RAW / "fallback-frame-239.npz", rgb=snapshot)
sources["fallback-frame"] = {"path": str(snapshot_path.relative_to(ROOT)), "sha256": sha(snapshot_path),
    "npz_key": "frames", "npz_index": 4, "engine_frame_index_zero_based": 239,
    "width": 1182, "height": 665, "pixel_sha256_rgb": pixel_sha,
    "pixel_hash_verified_against_metrics_measurement_index": 119,
    "export": str(frame_path.relative_to(OUT)), "export_sha256": sha(frame_path),
    "source_data_copy": "raw/fallback-frame-239.npz", "source_data_copy_sha256": sha(RAW / "fallback-frame-239.npz"),
    "processing": "Native size equals five.npz snapshot target. Export RGB uint8 to lossless PNG with no resampling, color adjustment or generative changes."}
sources["fallback-baseline-frame"] = {"path": str((baseline_case / "five.npz").relative_to(ROOT)),
    "sha256": sha(baseline_case / "five.npz"), "npz_key": "frames", "npz_index": 4,
    "engine_frame_index_zero_based": 239, "pixel_sha256_rgb": hashlib.sha256(baseline_snapshot.tobytes()).hexdigest(),
    "validation": "The selected baseline RGB array equals the fallback array byte for byte."}
fig, axes = plt.subplots(1, 2, figsize=(15, 8.2), gridspec_kw={"width_ratios": [1, 1.3]})
fig.subplots_adjust(left=.045, right=.98, top=.77, bottom=.22, wspace=.09)
panel(axes[0], "Before — preset load failed", "Worker stderr.log, L1:\n\n" +
      "preset-lab-worker: .../Geiss - Surface\n(1-02 Version).milk: std::exception\n\nWorker manifest.json:\n  status: failed\n  exit_code: 1\n  observed_frames: 0\n\nNo image was emitted.\nThis panel is a log excerpt, not a black frame.", RED)
axes[1].imshow(snapshot, interpolation="none")
axes[1].set_axis_off()
axes[1].set_title("After — actual fallback output\nGeiss • frame 239 • 1182 × 665", color=GREEN, fontsize=15, loc="left", pad=16)
save(fig, "03-optional-shader-fallback", "An optional rejected shader no longer rejects the preset",
     "Forced fragment-shader rejection • real Geiss output • classic 1182 × 665 test case",
     f"RED stderr source SHA256 {red_stderr['sha256'][:16]}; full source path and log L1 in raw/fallback-red-stderr.txt\n"
     f"GREEN 240-frame SHA256 equals baseline: {green_metrics['sha256_all_frames']}\n"
     "Lossless full-size frame: 03-fallback-geiss-frame-239.png • Apple M4 Pro / OpenGL 4.1 Metal • identities and hashes in manifest.json",
     "The rejected-shader pre-fix worker failed before emitting any frame. The fallback worker emitted 240 frames and matches the baseline all-frame hash in this recorded case.",
     ["Shader rejection is deliberately injected by a test-only invalid fragment token; not an observed retail-driver incompatibility.",
      "The failed worker emitted zero frames; no before-rendered image exists or was fabricated.",
      "Displayed frame is engine frame 239 from a recorded classic-size case; it demonstrates successful fallback rather than visual diffusion quality.",
      "Recorded artifacts identify a research diffusion PoC build; these are not screenshots of the final APK.",
      "Image proof is one Geiss case; separate matrix summary records the broader byte-parity checks."],
     [k for k in sources if k.startswith("fallback-")],
     [{"state": "rejected-before-fallback", "identity": red_identity},
      {"state": "fallback", "identity": green_metrics["identity"]},
      {"state": "baseline", "identity": baseline_metrics["identity"]}])
visuals[-1]["artifacts"].append(frame_path.name)


# 4: Show the precise flaky test failure and deterministic policy contrast, not a flake-rate claim.
native_red = source("build/follow-ups/native-shader-failure.log", "transition-red", [(365, 366), (446, 447)])
native_green = source("build/follow-ups/native-deterministic-policy-green.log", "transition-green", [(365, 385), (415, 415), (416, 425)])
positive = source("build/follow-ups/native-deterministic-policy-positive.log", "transition-positive", [(1, 5), (27, 27)])
source("build/follow-ups/native-deterministic-policy-negative.log", "transition-negative", [(1, 4)])
source("build/follow-ups/native-deterministic-policy-concurrent-load.json", "transition-concurrent-load")
engine_test = ROOT / "core/src/test/native/engine_test.cpp"
test_lines = engine_test.read_text().splitlines()
start = next(i for i, line in enumerate(test_lines, 1) if "auto sampledBlend" in line)
end = next(i for i, line in enumerate(test_lines, 1) if "sampledBlend(0.0001, false)" in line)
source(engine_test, "transition-test-source", [(start, end)])
fig, axes = plt.subplots(1, 2, figsize=(15, 9.3))
fig.subplots_adjust(left=.045, right=.98, top=.79, bottom=.18, wspace=.13)
panel(axes[0], "Before — timing-sensitive host assertion", "native-shader-failure.log, L365–366 / L446–447\n\n" +
      "auto: a slow blend that is CPU-bound keeps\nits resolution\n\nTRANSITION auto: blend at 60.1 fps\n(228.3 before), lowering it to 60% now\n\nFAIL engine_test.cpp:574 g_windowW == 960\n\nThe fake workload spun to a wall-time deadline.\nHost preemption can reduce measured thread CPU share.", RED)
panel(axes[1], "After — deterministic policy inputs", "63 samples through transition end:\n  wall: 16 ms / frame; baseline input: 250 fps\n\n15 ms CPU input:\n  scale=75%, cpu=92%, outgoing_rate=1/2\n  next blends at 100%\n\n0.1 ms CPU input:\n  scale=60%, cpu=1%, outgoing_rate=1/1\n\nnative-deterministic-policy-green.log L415:\n  ALL TESTS PASSED\n\nScratch negative control (threshold 80% → 99%)\nfailed the expected width assertion.", GREEN)
save(fig, "04-deterministic-transition-test", "CPU-bound transition coverage no longer depends on host timing",
     "TEST-ONLY fix • real policy, synthetic timing samples • production adaptation policy unchanged",
     f"RED source: {native_red['path']} SHA256 {native_red['sha256'][:16]}\n"
     f"GREEN source: {native_green['path']} SHA256 {native_green['sha256'][:16]}\n"
     "Sample-derived values are not app performance measurements. Exact line excerpts, negative control and source hashes: raw/ and manifest.json",
     "Recorded old harness failed its width assertion; deterministic CPU/low-CPU inputs exercise the real policy and the full subsequent harness passes.",
     ["Test-only fix: no claim that production engine policy changed.",
      "CPU percentages and frame rates in the deterministic control are consequences of supplied synthetic timings, not benchmark measurements.",
      "One observed flaky failure and one passing full run do not measure statistical flake rate.",
      "Historical native logs do not carry immutable build identities; current test source is hashed separately.",
      "Concurrent-load observation is a point-in-time worker inventory, not a continuous utilization trace."],
     [k for k in sources if k.startswith("transition-")])


manifest = {"schema_version": 1, "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "workspace": str(ROOT), "workspace_head_at_export": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "generator": "export_proof.py", "generator_sha256": sha(Path(__file__)), "allocation_build_records": "allocation-builds.json",
    "sources": sources, "visuals": visuals,
    "proof_gaps": ["Original allocation RED console output was not saved; proof uses explicitly-labeled fresh snapshot reruns.",
                   "No before-rendered frame exists for failed shader loading (zero frames emitted).",
                   "No historical immutable build ID is embedded in diagnostic unit logs or native host logs.",
                   "No retail-device screenshot or quantitative field/performance claim is established by these host/research artifacts."],
    "exported_artifacts": []}
for p in sorted(OUT.glob("*.png")) + sorted(OUT.glob("*.svg")) + [OUT / "allocation-builds.json"]:
    manifest["exported_artifacts"].append({"path": p.name, "sha256": sha(p)})
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
readme = ["# Per-fix image proof", "", "All charts and log images use Matplotlib. The Geiss image is a lossless export of actual recorded engine RGB output; no generative images were used.", "",
          "Do not publish the isolated `venv/`, `.matplotlib/` cache or compiled allocation binaries as review attachments. The PNG/SVG files, manifest, raw excerpts, source copies and scripts are the review package.", "",
          "## Images", ""]
for v in visuals:
    readme += ["### " + v["id"], "", "Artifacts: " + ", ".join("`" + a + "`" for a in v["artifacts"]), "", "Proves: " + v["what_it_proves"], "", "Limits:", ""]
    readme += ["- " + limit for limit in v["limitations"]]
    readme += ["", "Sources (full hashes and line ranges are in `manifest.json`):", ""]
    for key in v["source_keys"]:
        s = sources[key]
        readme += [f"- `{s['path']}` — SHA256 `{s['sha256']}`" + (f" — lines {s['source_line_ranges']}" if "source_line_ranges" in s else "")]
    if v["build_identities"]:
        readme += ["", "Recorded build identities:", "", "```json", json.dumps(v["build_identities"], indent=2), "```"]
    readme += [""]
readme += ["## Reproduction", "", "Run from the workspace root:", "", "```sh", "python3 build/follow-ups/proof-export/reproduce_allocations.py", "build/follow-ups/proof-export/venv/bin/python build/follow-ups/proof-export/export_proof.py", "```", "",
           "`allocation-builds.json` records exact compile/run commands and hashes for the fresh real CGL RED/GREEN runs. Both builds use copied source from the immutable engine snapshot identified by the corresponding worker configuration. Endpoint output is printed by the copied production fixture after querying real GL objects. The separately-tested `what()` comparison is omitted in this copied allocation fixture so diagnostic behavior does not contaminate allocation isolation.", "",
           "The standalone native focused controls and complete host harness are pre-existing recorded evidence. Their exact full-run command was:", "", "```sh", "JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home bash core/src/test/native/run_native_tests.sh > build/follow-ups/native-deterministic-policy-green.log 2>&1", "```", "",
           "For the Geiss frame, the native size and measurement snapshot size are both 1182 × 665. Array index 4 is engine frame 239 (zero-based): 120 warm-up frames and 120 measurement frames at 30 FPS. Exported RGB bytes match the last measurement-frame SHA256 and the baseline snapshot exactly. Both complete 240-frame recordings also share the same all-frame SHA256. The unsuccessful RED worker has `observed_frames: 0`; its panel intentionally contains only the actual log evidence.", "",
           "## Proof gaps", ""]
readme += ["- " + gap for gap in manifest["proof_gaps"]]
(OUT / "README.md").write_text("\n".join(readme) + "\n")
index = []
for p in sorted(OUT.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(OUT)
    if rel.parts[0] in {"venv", ".matplotlib", "tmp"} or p.name in {"shader-failure-test", "artifact-index.json"}:
        continue
    index.append({"path": str(rel), "sha256": sha(p), "bytes": p.stat().st_size})
(OUT / "artifact-index.json").write_text(json.dumps(index, indent=2) + "\n")
print(json.dumps({"visuals": [v["id"] for v in visuals], "proof_gaps": manifest["proof_gaps"]}, indent=2))
