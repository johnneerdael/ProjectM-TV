"""Export verified actual-core coverage without modifying render evidence."""

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

import run


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_producer(path, job, protocol, record, role):
    producer = path.parent / "output/result.json"
    result = job.get("result")
    if not producer.exists() and result is None:
        require(job["status"] in ("failed", "timeout") and isinstance(job.get("error"), str)
                and bool(job["error"].strip()), "missing producer and explicit host failure evidence")
        return None
    require(producer.is_file() and isinstance(result, dict), "missing retained producer result")
    require(any(f["path"] == "output/result.json" for f in job["retained_files"]),
            "producer result is not declared in retained evidence")
    require(json.loads(producer.read_text()) == result, "row result differs from retained producer result")
    for field, expected in {"schema_version": 2, "job_id": job["key"],
                            "protocol_sha256": protocol["sha256"]}.items():
        require(result.get(field) == expected, "producer provenance mismatch: " + field)
    require(result.get("status") in ("failed", "success"), "invalid producer status")
    if result["status"] == "failed":
        require(job["status"] != "success" and isinstance(result.get("error"), str)
                and bool(result["error"].strip()), "failed producer lacks failure status or diagnostic")
    elif job["status"] in ("failed", "timeout"):
        require(bool(job.get("error")), "producer success lacks an explicit host failure reason")
    config = protocol["config"]
    expected_fields = {"width": config["width"], "height": config["height"], "fps": config["fps"],
                       "seed": config["seed"], "preset_filename": record["path"],
                       "capture_mode": "selected", "capture_frames": run.capture_indices(360),
                       "core_sha256": protocol["roles"][role]["core_sha256"],
                       "requested_preset_sha256": record["sha256"]}
    # A genuine failure before initialization cannot supply a runtime ELF or source hash.
    # Validate every field that is available; successful jobs require all of them.
    for field, expected in expected_fields.items():
        if field in result or job["status"] == "success":
            require(result.get(field) == expected, "producer provenance mismatch: " + field)
    return result


def verify_job(work, relative, protocol, record, role, repeat):
    key = run.job_key(protocol["sha256"], record, role, "selected", repeat)
    path = work / relative
    require(path.resolve().is_relative_to(work.resolve()), "job path escapes dataset")
    require(path == work / "jobs" / key / "row.json", "unexpected job path or repeat")
    job = run.read_cached(path, key, protocol["sha256"])
    require(job is not None, "invalid job checksum or retained file")
    require(job["preset"] == record and job["role"] == role and job["repeat"] == repeat,
            "job source/role/repeat mismatch")
    require(job["capture_mode"] == "selected" and job["measurement_frames"] == 360,
            "job capture window mismatch")
    result = verify_producer(path, job, protocol, record, role)
    if job["status"] != "success":
        return job
    require(result.get("status") == "success", "successful job lacks producer success")
    require(result.get("core_sha256") == protocol["roles"][role]["core_sha256"], "runtime core mismatch")
    require(result.get("requested_preset_sha256") == record["sha256"], "runtime preset source mismatch")
    trace = run.safe_member(path.parent, job["frame_trace"]["path"])
    raw = gzip.decompress(trace.read_bytes()) if trace.suffix == ".gz" else trace.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == result["frames_metadata_sha256"], "producer trace checksum mismatch")
    frames = [json.loads(line) for line in raw.splitlines() if line.strip()]
    require(len(frames) == result.get("rendered_frames") == 480, "incomplete frame trace")
    require([f.get("frame") for f in frames] == list(range(480)), "noncontiguous frame trace")
    require(all(f.get("preset_filename") == record["path"] and f.get("pcm_bytes") == 1470
                and f.get("change_counter") == frames[0].get("change_counter") for f in frames),
            "requested preset, switch counter or PCM mismatch")
    indices = run.capture_indices(360)
    require(all(f.get("captured") == (f["frame"] in indices) for f in frames), "readback coverage mismatch")
    require([s["frame"] for s in result["selected_files"]] == indices, "selected sample coverage mismatch")
    hashes = {str(s["frame"]): s["sha256"] for s in result["selected_files"]}
    require(hashes == job["selected_native_sha256"], "selected hash mismatch")
    require(all(frames[i].get("sha256") == hashes[str(i)] and len(hashes[str(i)]) == 64 for i in indices),
            "selected/trace hash mismatch")
    require(all(f.get("sha256") is None for f in frames if f["frame"] not in indices),
            "unread frame has an invented hash")
    return job


def export(work, families_path, role):
    work = Path(work)
    protocol = json.loads((work / "protocol.json").read_text())
    require(run.digest({k: v for k, v in protocol.items() if k != "sha256"}) == protocol["sha256"],
            "protocol checksum mismatch")
    require(protocol["backend"] == "production-projectm-tv-core-ProjectMJNI-EGL-GLES3", "not actual-core evidence")
    require(role in protocol["roles"], "role is absent from protocol")
    inventory = json.loads((work / "inventory.json").read_text())
    require(len(inventory["presets"]) == inventory["count"], "inventory count mismatch")
    require(run.digest(inventory["presets"]) == inventory["corpus_sha256"] == protocol["corpus_sha256"],
            "inventory checksum mismatch")
    families = json.loads(Path(families_path).read_text())
    family_index = {f["filename"]: f for f in families["presets"]}
    require(len(family_index) == len(families["presets"]) == inventory["count"], "family membership mismatch")
    require(set(family_index) == {r["path"] for r in inventory["presets"]}, "family membership mismatch")
    rows, issues, pending = [], [], []
    groups = defaultdict(Counter)
    for record in inventory["presets"]:
        family = family_index[record["path"]]
        require(family["sha256"] == record["sha256"], "family source mismatch: " + record["path"])
        key = run.digest({"protocol_sha256": protocol["sha256"], "preset": record, "role": role})
        path = work / "rows" / (key + ".json")
        if not path.exists():
            pending.append(record["path"])
            continue
        try:
            pair = run.read_cached(path, key, protocol["sha256"])
            require(pair is not None, "invalid pair checksum")
            require(pair["preset"] == record and pair["role"] == role, "pair source/role mismatch")
            require(len(pair["runs"]) == 2, "pair requires two distinct repeats")
            jobs = [verify_job(work, rel, protocol, record, role, i)
                    for i, rel in enumerate(pair["runs"], 1)]
            statuses = [j["status"] for j in jobs]
            exact = statuses == ["success", "success"] and jobs[0]["selected_native_sha256"] == jobs[1]["selected_native_sha256"]
            expected = ("success" if exact else "nondeterministic") if statuses == ["success", "success"] else next(s for s in statuses if s != "success")
            require(pair["status"] == expected and pair["repeat_exact_selected"] == exact, "pair repeat/status mismatch")
            require(pair["hash_coverage"] == run.capture_indices(360), "pair hash coverage mismatch")
            require(pair["render_input_sha256"] == run.render_input_signature(protocol, role, record, pair["driver"]),
                    "render input signature mismatch")
            if exact:
                require(all(j["result"].get(k) == v for j in jobs for k, v in pair["driver"].items()),
                        "runtime driver differs between repeats")
            samples = [{"frame": s["frame"], "native_sha256": s["sha256"], "metrics": s.get("metrics", {}),
                        "thumbnail": str((Path(pair["runs"][0]).parent / "output" / s["thumbnail_path"]))
                        if s.get("thumbnail_path") else None} for s in jobs[0].get("result", {}).get("selected_files", [])] if exact else []
            rows.append({"preset": record, "status": pair["status"], "row": str(path.relative_to(work)),
                         "original_protocol_sha256": protocol["sha256"], "render_input_sha256": pair["render_input_sha256"],
                         "runs": pair["runs"], "features": family["feature_names"], "shader_hashes": family["shader_hashes"],
                         "unclassified": family["unclassified"], "driver": pair["driver"], "samples": samples})
            for feature in family["feature_names"]:
                groups[feature][pair["status"]] += 1
        except (OSError, ValueError, KeyError, TypeError) as error:
            issues.append({"preset": record["path"], "row": str(path.relative_to(work)), "error": str(error)})
    return {"protocol_sha256": protocol["sha256"], "role": role, "inventory_count": inventory["count"],
            "verified_terminal_presets": len(rows), "remaining_presets": inventory["count"] - len(rows),
            "complete_coverage": len(rows) == inventory["count"] and not issues,
            "statuses": dict(Counter(r["status"] for r in rows)), "integrity_issues": issues, "pending_presets": pending,
            "source_family_index_sha256": run.file_hash(families_path),
            "feature_status_counts": {k: dict(v) for k, v in sorted(groups.items())}, "rows": rows,
            "limitations": "Attempted coverage includes explicit failures. Selected native hashes cover 16 frames only. Native colour metrics and APK thumbnails are screening evidence, not authored1182 fidelity error. Source features overlap and do not prove execution/compilation. One bass signal cannot establish chill/normal/party labels or improvement/degradation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--families", type=Path, required=True)
    parser.add_argument("--role", choices=("baseline", "candidate"), default="baseline")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.resolve().is_relative_to(args.work.resolve()), "export outside immutable render dataset")
    report = export(args.work, args.families, args.role)
    run.atomic(args.output, report)
    print(run.canonical({k: v for k, v in report.items() if k not in ("rows", "pending_presets", "feature_status_counts")}))
    if report["integrity_issues"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
