"""Read-only, sampled-frame corpus diagnostics; no renderer dependencies or acceptance claims."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sqlite3
import statistics
import tempfile


PROFILES = ("authored", "authored_repeat", "candidate_authored", "baseline_cap",
            "candidate_cap", "baseline_native", "candidate_native")
METRICS = ("image_mae", "brightness_absolute_error", "brightness_ratio_error",
           "centre_absolute_error", "saturation_absolute_error",
           "sharpness_native_absolute_error", "sharpness_1182_absolute_error")
CLASSES = ("gain", "worse", "mixed", "unchanged_noise_unclassified", "unclassified")
SPARSE_WINDOWS = {4: [120, 150, 180, 210, 239], 12: [120, 210, 300, 390, 479]}
# Screening triggers in each metric's units; these are not perceptual thresholds.
ABSOLUTE_TRIGGERS = dict(zip(METRICS, (.01, .01, .1, .01, .05, .001, .001)))


def window_indices(manifest, window):
    if manifest["protocol"] == "sparse":
        return manifest.get("capture_windows", {}).get(str(window),
               manifest.get("capture_windows", {}).get(window, SPARSE_WINDOWS[window]))
    return [120 + round(i * (window * 30 - 1) / 4) for i in range(5)]


def read_snapshot(path):
    """Use an ordinary SQLite RO transaction, including committed WAL rows."""
    path = Path(path).resolve()
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        db.execute("BEGIN")
        row = db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()
        if row is None:
            raise ValueError("Database has no frozen manifest")
        manifest = json.loads(row[0])
        jobs = []
        fields = ("key", "preset", "profile", "round", "status", "capture_indices",
                  "sample_hashes", "summaries", "comparisons", "comparison_eligible",
                  "comparisons_invalidated", "reference_regeneration_changed")
        for (payload,) in db.execute("SELECT payload FROM jobs"):
            raw = json.loads(payload)
            compact = {field: raw[field] for field in fields if field in raw}
            compact["config"] = {"measurement_seconds": raw.get("config", {}).get("measurement_seconds")}
            compact["diagnostics"] = {"stages": raw.get("diagnostics", {}).get("stages", {})}
            compact["_payload_sha256"] = canonical_hash(raw)
            jobs.append(compact)
        return manifest, jobs
    finally:
        db.close()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def merge_snapshots(snapshots):
    """Merge independently committed snapshots, without relaxing frozen identity."""
    manifest, frozen_hash, merged = None, None, {}
    for current, jobs in snapshots:
        current_hash = canonical_hash(current)
        if manifest is None:
            manifest, frozen_hash = current, current_hash
        elif current_hash != frozen_hash:
            raise ValueError("Frozen manifests differ across work directories")
        for job in jobs:
            key = job.get("key")
            if not key:
                raise ValueError("Stored job has no immutable key")
            if key in merged:
                first = merged[key]
                if first.get("_payload_sha256", canonical_hash(first)) != job.get("_payload_sha256", canonical_hash(job)):
                    raise ValueError(f"Conflicting duplicate job key: {key}")
            else:
                merged[key] = job
    if manifest is None:
        raise ValueError("No work directories supplied")
    return manifest, list(merged.values())


def hashes(job):
    return {str(k): value for k, value in job.get("sample_hashes", {}).items()}


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def summary_complete(summary):
    return (all(finite(summary.get(k)) for k in ("luma", "saturation", "lap_native", "lap_1182"))
            and isinstance(summary.get("centre_rgb"), list)
            and len(summary["centre_rgb"]) == 3 and all(map(finite, summary["centre_rgb"])))


def complete(job, windows, manifest):
    expected = {str(i) for w in windows for i in window_indices(manifest, w)}
    actual = hashes(job)
    return (expected == set(actual) and all(isinstance(v, str) and v for v in actual.values())
            and expected == {str(i) for i in job.get("capture_indices", [])}
            and all(summary_complete(job.get("summaries", {}).get(str(w), {})) for w in windows))


def window_complete(job, window, manifest):
    expected = {str(i) for i in window_indices(manifest, window)}
    actual = hashes(job)
    return (expected <= set(actual) and all(isinstance(actual[i], str) and actual[i] for i in expected)
            and expected <= {str(i) for i in job.get("capture_indices", [])}
            and summary_complete(job.get("summaries", {}).get(str(window), {})))


def errors(job, authored, window, dark_floor):
    summary, reference = job["summaries"][str(window)], authored["summaries"][str(window)]
    brightness = abs(summary["luma"] - reference["luma"])
    dark = reference["luma"] < dark_floor
    return {"image_mae": job.get("comparisons", {}).get(str(window), {}).get("img_err"),
            "brightness_absolute_error": brightness,
            "brightness_ratio_error": None if dark else abs(summary["luma"] / reference["luma"] - 1),
            "centre_absolute_error": statistics.mean(abs(a - b) for a, b in zip(summary["centre_rgb"], reference["centre_rgb"])),
            "saturation_absolute_error": abs(summary["saturation"] - reference["saturation"]),
            "sharpness_native_absolute_error": abs(summary["lap_native"] - reference["lap_native"]),
            "sharpness_1182_absolute_error": abs(summary["lap_1182"] - reference["lap_1182"])}, dark


def classify(values, tolerance):
    if not values or any(v is None for v in values):
        return "unclassified"
    gains, worse = any(v < -tolerance for v in values), any(v > tolerance for v in values)
    if gains and worse:
        return "mixed"
    return "gain" if gains else "worse" if worse else "unchanged_noise_unclassified"


def median(values):
    return statistics.median(values) if values else None


def population_medians(presets, comparisons, eligible_only):
    """Equal preset weighting; no pooling of the many jobs as independent presets."""
    selected = {p["preset"] for p in presets if not eligible_only or p["eligible"]}
    result = {}
    for metric in METRICS:
        by_preset = defaultdict(list)
        for comparison in comparisons:
            value = comparison["metrics"][metric]
            if comparison["preset"] in selected and finite(value["before"]) and finite(value["after"]):
                by_preset[comparison["preset"]].append(value)
        means = [{side: statistics.mean(v[side] for v in values) for side in ("before", "after", "delta")}
                 for values in by_preset.values()]
        result[metric] = {"contributing_presets": len(means),
                          **{f"{side}_median": median([v[side] for v in means]) for side in ("before", "after", "delta")}}
    return result


def summarize(manifest, jobs, repeat_all=False, round_index=0, tolerance=1e-4,
              significant_scale=1.0, significant_relative=.25):
    if manifest.get("protocol") not in ("full", "sparse"):
        raise ValueError("Unsupported screen protocol")
    windows = sorted({int(w) for w in manifest["windows"]})
    if not windows or not set(windows) <= {4, 12}:
        raise ValueError("Expected sampled windows 4 and/or 12")
    rounds = [round_index, round_index + 1] if repeat_all else [round_index]
    corpus = {record["path"]: record for record in manifest["corpus"]}
    index, duplicates, outside = {}, set(), 0
    for job in jobs:
        path = job.get("preset", {}).get("path")
        if path not in corpus:
            outside += 1
            continue
        key = (path, job.get("profile"), job.get("round"), job.get("config", {}).get("measurement_seconds"))
        if key in index:
            duplicates.add(key)
        index[key] = job
    counts = Counter({name: 0 for name in (
        "covered_presets", "all_required_profiles_presets", "successful_presets", "complete_window_presets",
        "complete_repeat_presets", "repeat_hash_stable_presets", "authored_stable_presets", "candidate_off_identical_presets",
        "eligible_presets", "validated_presets", "preliminary_presets", "failed_presets", "timeout_presets",
        "shader_fallback_presets", "shader_unknown_presets", "incomplete_window_presets", "reference_regenerated_presets")})
    presets, comparisons = [], []
    coverage = {"profiles": {p: Counter({"present_presets": 0, "successful_presets": 0, "complete_presets": 0}) for p in PROFILES},
                "windows": {str(w): Counter({"all_required_profiles_presets": 0, "successful_presets": 0, "complete_presets": 0}) for w in windows},
                "rounds": {str(r): Counter({"all_required_profiles_presets": 0, "successful_presets": 0, "complete_presets": 0}) for r in rounds}}
    for path, record in sorted(corpus.items()):
        required = {(path, profile, r, seconds): ([seconds] if manifest["protocol"] == "full" else windows)
                    for r in rounds for seconds in (windows if manifest["protocol"] == "full" else [12])
                    for profile in PROFILES}
        stored = {key: index[key] for key in required if key in index}
        all_profiles = len(stored) == len(required)
        all_success = all_profiles and all(job.get("status") == "success" for job in stored.values())
        complete_windows = all_profiles and all(complete(job, required[key], manifest) for key, job in stored.items())
        for group, selectors in (("profiles", PROFILES), ("windows", windows), ("rounds", rounds)):
            for selector in selectors:
                relevant = {key: picks for key, picks in required.items()
                            if (key[1] == selector if group == "profiles" else
                                key[2] == selector if group == "rounds" else selector in picks)}
                present = all(key in stored for key in relevant)
                successful = present and all(stored[key].get("status") == "success" for key in relevant)
                sampled = present and all(window_complete(stored[key], selector, manifest) if group == "windows"
                                          else complete(stored[key], picks, manifest) for key, picks in relevant.items())
                counter = coverage[group][str(selector) if group != "profiles" else selector]
                counter["present_presets" if group == "profiles" else "all_required_profiles_presets"] += present
                counter["successful_presets"] += successful
                counter["complete_presets"] += sampled
        failed = any(job.get("status") not in ("success", "timeout") for job in stored.values())
        timeout = any(job.get("status") == "timeout" for job in stored.values())
        fallback = any("failure_reported" in job.get("diagnostics", {}).get("stages", {}).values() for job in stored.values())
        unknown = any("unknown_no_confirmation" in job.get("diagnostics", {}).get("stages", {}).values() for job in stored.values())
        regenerated = any(job.get("reference_regeneration_changed") or job.get("comparisons_invalidated")
                          or job.get("comparison_eligible") is False for job in stored.values())
        authored_stable, off_identical = all_profiles and complete_windows, all_profiles and complete_windows
        repeat_stable = repeat_all and all_profiles and complete_windows
        for r in rounds:
            for seconds in (windows if manifest["protocol"] == "full" else [12]):
                authored = stored.get((path, "authored", r, seconds), {})
                authored_stable &= bool(hashes(authored)) and hashes(authored) == hashes(stored.get((path, "authored_repeat", r, seconds), {}))
                off_identical &= bool(hashes(authored)) and hashes(authored) == hashes(stored.get((path, "candidate_authored", r, seconds), {}))
        if repeat_all:
            for seconds in (windows if manifest["protocol"] == "full" else [12]):
                for profile in PROFILES:
                    first = stored.get((path, profile, rounds[0], seconds), {})
                    second = stored.get((path, profile, rounds[1], seconds), {})
                    repeat_stable &= bool(hashes(first)) and hashes(first) == hashes(second)
        reasons = []
        for invalid, reason in ((not all_profiles, "missing_required_jobs"), (not all_success, "non_success_jobs"),
                                (not complete_windows, "incomplete_sampled_windows"),
                                (any(key in duplicates for key in required), "duplicate_logical_jobs"),
                                (any(job.get("preset", {}).get("sha256") != record["sha256"] for job in stored.values()), "preset_identity_mismatch"),
                                (not authored_stable, "authored_repeat_hash_mismatch"),
                                (not off_identical, "candidate_off_hash_mismatch"),
                                (repeat_all and not repeat_stable, "profile_repeat_hash_mismatch"),
                                (regenerated, "reference_regenerated_or_invalidated"), (fallback, "shader_fallback_reported")):
            if invalid:
                reasons.append(reason)
        row = {"preset": path, "stored_required_jobs": len(stored), "expected_jobs": len(required),
               "all_required_profiles": all_profiles, "complete_windows": complete_windows,
               "authored_stable": bool(authored_stable), "candidate_off_identical": bool(off_identical),
               "repeat_hash_stable": bool(repeat_stable), "classification_scope": "validated" if repeat_all else "preliminary",
               "exclusion_reasons": reasons, "eligible": not reasons, "metric_classifications": {}}
        own = []
        for r in rounds:
            for window in windows:
                seconds = window if manifest["protocol"] == "full" else 12
                authored = stored.get((path, "authored", r, seconds))
                for target in ("cap", "native"):
                    baseline = stored.get((path, "baseline_" + target, r, seconds))
                    candidate = stored.get((path, "candidate_" + target, r, seconds))
                    trio = (authored, baseline, candidate)
                    if not all(job and job.get("status") == "success" and complete(job, required[(path, job["profile"], r, seconds)], manifest) for job in trio):
                        continue
                    # Invalidated references must never contribute even descriptive differences.
                    if any(job.get("reference_regeneration_changed") or job.get("comparisons_invalidated") or job.get("comparison_eligible") is False for job in trio):
                        continue
                    before, dark = errors(baseline, authored, window, manifest["dark_floor"])
                    after, _ = errors(candidate, authored, window, manifest["dark_floor"])
                    values = {}
                    for metric in METRICS:
                        a, b = before[metric], after[metric]
                        valid = finite(a) and finite(b)
                        values[metric] = {"before": a if finite(a) else None, "after": b if finite(b) else None,
                                          "delta": b - a if valid else None,
                                          "classification": classify([b - a if valid else None], tolerance)}
                    own.append({"preset": path, "round": r, "window_seconds": window, "target": target,
                                "dark_authored": dark, "metrics": values})
        if row["eligible"] and (len(own) != len(rounds) * len(windows) * 2 or
                                any(c["metrics"]["image_mae"]["delta"] is None for c in own)):
            row["eligible"] = False
            reasons.append("missing_image_comparisons")
        for metric in METRICS:
            row["metric_classifications"][metric] = classify([c["metrics"][metric]["delta"] for c in own], tolerance) if row["eligible"] else "unclassified"
        comparisons.extend(own)
        presets.append(row)
        for name, value in {"covered": bool(stored), "all_required_profiles": all_profiles, "successful": all_success,
                            "complete_window": complete_windows, "complete_repeat": repeat_all and all_profiles,
                            "repeat_hash_stable": repeat_stable, "authored_stable": authored_stable,
                            "candidate_off_identical": off_identical, "eligible": row["eligible"],
                            "validated": row["eligible"] and repeat_all, "preliminary": row["eligible"] and not repeat_all,
                            "failed": failed, "timeout": timeout, "shader_fallback": fallback, "shader_unknown": unknown,
                            "incomplete_window": not complete_windows, "reference_regenerated": regenerated}.items():
            counts[name + "_presets"] += bool(value)
    counts.update(corpus_presets=len(corpus), stored_jobs=len(jobs), jobs_outside_manifest=outside)
    counts["unstarted_presets"] = len(corpus) - counts["covered_presets"]
    eligible_paths = {p["preset"] for p in presets if p["eligible"]}
    regressions, outliers = [], []
    for metric in METRICS:
        contributing = [c for c in comparisons if c["preset"] in eligible_paths and finite(c["metrics"][metric]["delta"])]
        after_values = [c["metrics"][metric]["after"] for c in contributing]
        fence = None
        if len(after_values) >= 4:
            q1, _, q3 = statistics.quantiles(after_values, n=4, method="inclusive")
            fence = q3 + 3 * (q3 - q1)
        for comparison in contributing:
            value = comparison["metrics"][metric]
            item = {k: comparison[k] for k in ("preset", "round", "window_seconds", "target")}
            item.update(metric=metric, before=value["before"], after=value["after"], delta=value["delta"])
            threshold = max(ABSOLUTE_TRIGGERS[metric] * significant_scale, abs(value["before"]) * significant_relative)
            if value["delta"] > max(tolerance, threshold):
                regressions.append(dict(item, numerical_screening_threshold=threshold))
            if fence is not None and value["after"] > fence:
                outliers.append(dict(item, upper_error_fence=fence))
    counts["significant_regression_presets"] = len({r["preset"] for r in regressions})
    counts["outlier_presets"] = len({r["preset"] for r in outliers})
    return {"schema_version": 1, "protocol": manifest["protocol"], "windows": windows, "rounds": rounds,
            "provenance": {"frozen_manifest_sha256": canonical_hash(manifest),
                           "runner_sha256": manifest.get("runner_sha256"), "workers": manifest.get("workers", {}),
                           "sparse_metadata": manifest.get("sparse_metadata", {}),
                           "frozen_metrics_scope": manifest.get("metrics_scope"),
                           "dark_floor": manifest["dark_floor"]},
            "methodology": {
                "scope": "Five selected frames per window; these are not whole-window means.",
                "eligibility": "All required jobs successful and complete, authored-repeat and candidate-off sampled hashes identical, no regenerated references or reported shader fallbacks. Two-round validation additionally requires each profile's captured hashes identical across rounds.",
                "numerical_tolerance": f"Absolute numerical delta tolerance {tolerance:g}; not perceptual acceptance or a measured noise floor. Unchanged deltas remain noise-unclassified.",
                "direction": "Gain means lower absolute error relative to authored, including abs(luma_ratio - 1); sharpness uses Laplacian variance error. It does not establish visual quality.",
                "dark_authored": "Authored luma below dark_floor leaves exact brightness ratio error undefined; no regularized substitution.",
                "population": "Medians of per-preset mean errors across available paired targets/windows/rounds; equal preset weighting. Covered population is descriptive and includes ineligible pairs, but excludes failed/incomplete/invalidated pairs. Missing corpus presets do not contribute.",
                "regressions": "Configurable numerical screening triggers, not perceptual significance. Outliers exceed Q3 + 3 IQR of eligible paired errors; repeated comparisons are not independent samples."},
            "counts": dict(counts), "coverage": coverage, "presets": presets, "comparisons": comparisons,
            "metrics": {metric: {"preset_classifications": {label: sum(p["metric_classifications"][metric] == label for p in presets) for label in CLASSES}} for metric in METRICS},
            "populations": {"covered_descriptive": population_medians(presets, comparisons, False),
                            "eligible": population_medians(presets, comparisons, True)},
            "significant_regressions": sorted(regressions, key=lambda v: (v["metric"], -v["delta"], v["preset"])),
            "outliers": sorted(outliers, key=lambda v: (v["metric"], -v["after"], v["preset"]))}


def atomic_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_reports(result, json_path=None, csv_path=None):
    if json_path:
        atomic_text(json_path, json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    if csv_path:
        fields = ["preset", "eligible", "classification_scope", "stored_required_jobs", "expected_jobs",
                  "all_required_profiles", "complete_windows", "authored_stable", "candidate_off_identical",
                  "repeat_hash_stable", "exclusion_reasons", *METRICS]
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for preset in result["presets"]:
            row = {key: preset[key] for key in fields if key in preset}
            row["exclusion_reasons"] = ";".join(preset["exclusion_reasons"])
            row.update(preset["metric_classifications"])
            writer.writerow(row)
        atomic_text(csv_path, stream.getvalue())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, action="append", required=True,
                        help="Directory containing screen.sqlite; repeat to merge identical-manifest shards")
    parser.add_argument("--json", type=Path, help="Atomic aggregate and paired-detail JSON output")
    parser.add_argument("--csv", type=Path, help="Atomic per-preset classification CSV output")
    parser.add_argument("--repeat-all", action="store_true", help="Require round and round+1, including every profile's sampled hash identity")
    parser.add_argument("--round", type=int, default=0)
    parser.add_argument("--numeric-tolerance", type=float, default=1e-4)
    parser.add_argument("--significant-scale", type=float, default=1.0, help="Scale metric-specific absolute numerical regression triggers")
    parser.add_argument("--significant-relative", type=float, default=.25)
    args = parser.parse_args()
    if args.round < 0 or any(not math.isfinite(v) or v < 0 for v in (args.numeric_tolerance, args.significant_scale, args.significant_relative)):
        parser.error("Round and numerical thresholds must be finite and nonnegative")
    try:
        manifest, jobs = merge_snapshots(read_snapshot(work / "screen.sqlite") for work in args.work)
        result = summarize(manifest, jobs, args.repeat_all, args.round, args.numeric_tolerance,
                           args.significant_scale, args.significant_relative)
        result["provenance"]["work_directories"] = [str(work.resolve()) for work in args.work]
        result["provenance"]["snapshot_scope"] = "Independent read-only committed SQLite snapshot per shard"
        write_reports(result, args.json, args.csv)
    except (ValueError, sqlite3.Error, OSError) as error:
        parser.error(str(error))
    print(json.dumps({key: result[key] for key in ("protocol", "windows", "rounds", "counts", "coverage", "metrics", "populations")}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
