"""Shared, deterministic analysis and request recipe for the I31 evidence."""
import hashlib
import json
import numpy as np

ROLES = ("without-0019", "with-0019")
PROFILES = {
    "classic": {"line_reference_height": 0, "line_antialiasing": False, "feedback_detail": -1.0},
    "standard": {"line_reference_height": 720, "line_antialiasing": True, "feedback_detail": 0.0},
}
CASES = (("original-classic", "classic", 8, "original.milk"),
         ("original-standard", "standard", 8, "original.milk"),
         ("inactive-classic", "classic", 4, "inactive-gamma2.milk"))

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def config(profile):
    return {"width": 3840, "height": 2160, "fps": 30, "warmup_seconds": 4,
            "measurement_seconds": 12, "seed": 12345, **PROFILES[profile]}

def schedule_recipe():
    result = []
    for case, profile, blocks, preset in CASES:
        for block in range(blocks):
            roles = (ROLES[0], ROLES[1], ROLES[1], ROLES[0])
            if block % 2:
                roles = (ROLES[1], ROLES[0], ROLES[0], ROLES[1])
            for position, role in enumerate(roles):
                result.append({"case": case, "profile": profile, "block": block,
                               "position": position, "role": role, "preset": preset,
                               "name": f"{case}-b{block:02d}-p{position}-{role}"})
    return result

def analyze(schedule, runs):
    """Reproduce the executed fixed-seed paired-block bootstrap, including every block."""
    summary = {}
    rng = np.random.default_rng(12345)
    for case in sorted({job["case"] for job in schedule}):
        jobs = [job for job in schedule if job["case"] == case]
        rows = []
        for job in jobs:
            run = runs[job["name"]]
            assert run["status"] == "success" and run["gl_error_frames"] == 0 and run["gpu_timer_valid"]
            assert run["width"] == 3840 and run["height"] == 2160
            assert canonical(run["config"]) == canonical(config(job["profile"]))
            frames = [sample for sample in run["samples"] if sample["measured"]]
            assert len(run["samples"]) == 480 and len(frames) == 360
            expected = 2 if case == "inactive-classic" or job["role"] == "with-0019" else 3
            assert all(sample["gamma_draws"] == expected and sample["gamma_invocations"] == 1
                       and sample["gpu_ns"] > 0 for sample in frames)
            rows.append({**job, **{metric: float(np.mean([s[metric] for s in frames]))
                                  for metric in ("submit_ms", "complete_ms")},
                         "gpu_ms": float(np.mean([s["gpu_ns"] / 1e6 for s in frames]))})
        metrics = {}
        for metric in ("submit_ms", "complete_ms", "gpu_ms"):
            blocks = []
            for block in sorted({row["block"] for row in rows}):
                pair = {role: float(np.mean([row[metric] for row in rows
                                            if row["block"] == block and row["role"] == role]))
                        for role in ROLES}
                blocks.append({"block": block, "before": pair[ROLES[0]], "after": pair[ROLES[1]],
                               "delta_ms": pair[ROLES[1]] - pair[ROLES[0]]})
            deltas = np.array([block["delta_ms"] for block in blocks])
            resamples = rng.choice(deltas, size=(100000, len(deltas)), replace=True).mean(axis=1)
            before = float(np.mean([block["before"] for block in blocks]))
            after = float(np.mean([block["after"] for block in blocks]))
            metrics[metric] = {"before_ms": before, "after_ms": after, "delta_ms": after - before,
                               "change_percent": 100 * (after - before) / before,
                               "paired_block_bootstrap95_ms": np.percentile(resamples, [2.5, 97.5]).tolist(),
                               "all_blocks_faster": bool(np.all(deltas < 0)), "blocks": blocks}
        summary[case] = {"jobs": len(jobs), "measured_frames": len(jobs) * 360,
                         "gamma_draws_before": 2 if case == "inactive-classic" else 3,
                         "gamma_draws_after": 2, "metrics": metrics}
    return summary
