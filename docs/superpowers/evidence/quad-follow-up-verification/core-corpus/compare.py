"""Offline actual-core comparison; retain original evidence and screen for review."""
import argparse
from collections import Counter
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat
import audit
import checkpoint
import run

require = audit.require
BACKEND = "production-projectm-tv-core-ProjectMJNI-EGL-GLES3"
DRIVER = ("gl_vendor", "gl_renderer", "gl_version", "egl_version", "android_fingerprint", "abi")
CATEGORIES = ("unchanged_native_samples", "changed_needs_visual_review", "recovered_load_compatibility",
              "new_failure", "both_failed", "nondeterministic_uncomparable", "missing_pending")
LIMITATIONS = ("Selected native hashes cover 16 frames, not the unread stream. Thumbnail RGB MAE and "
               "adjacent-pair motion rank visual review; they are not authored1182 img_err. Native colour "
               "metrics are preserved without brightness-derived quality labels or a 10% gate. One signal, "
               "seed and driver cannot establish fidelity improvement or chill/normal/party labels. "
               "No full-corpus quality verdict is emitted, even with complete attempted coverage.")


def load_dataset(work, role):
    """Verify recorded bytes offline; never consult a device or the current runner."""
    work = Path(work).resolve()
    protocol = json.loads((work / "protocol.json").read_text())
    require(run.digest({k: v for k, v in protocol.items() if k != "sha256"}) == protocol["sha256"],
            "protocol checksum mismatch")
    require(protocol.get("schema_version") == 2 and protocol.get("backend") == BACKEND,
            "not schema-2 actual-core evidence")
    require(role in protocol["roles"], "role absent from protocol")
    inventory = json.loads((work / "inventory.json").read_text())
    records = inventory["presets"]
    require(len(records) == inventory["count"] == len({r["path"] for r in records}), "inventory count/duplicates")
    require(run.digest(records) == inventory["corpus_sha256"] == protocol["corpus_sha256"], "preset inventory checksum")
    require(run.digest(inventory["textures"]) == inventory["textures_sha256"] == protocol["textures_sha256"],
            "texture inventory checksum")
    identity = protocol["roles"][role]
    require(identity["backend_identity"].get("backend") == "projectmtv-core-android-v1", "not actual-core embedded backend")
    verified = run.artifact(Path(identity["apk_path"]), role, inventory)
    require(all(verified[k] == identity[k] for k in ("apk_sha256", "core_sha256", "backend_identity", "backend_identity_sha256")),
            "APK/core/source identity mismatch")
    for audio in protocol["pcm"].values():
        path = Path(audio["path"])
        require(path.stat().st_size == audio["bytes"] and run.file_hash(path) == audio["sha256"], "PCM checksum/size mismatch")
    require(Path(protocol["pcm"]["480"]["path"]).read_bytes().startswith(Path(protocol["pcm"]["240"]["path"]).read_bytes()),
            "PCM short input is not exact prefix")
    config = protocol["config"]
    require(config == dict(width=2364, height=1330, fps=30, seed=12345, warmup_frames=120,
                           measurement_frames=360, capture_frames=run.capture_indices(360)), "unsupported render configuration")
    require(protocol["pcm"]["480"]["bytes"] == 480 * 1470 and protocol["pcm"]["240"]["bytes"] == 240 * 1470,
            "PCM frame block coverage mismatch")
    return {"work": work, "role": role, "protocol": protocol, "inventory": inventory}


def verify_compatible(first, second):
    a, b = first["protocol"], second["protocol"]
    for field in ("backend", "config", "device_serial", "device", "corpus_sha256", "textures_sha256",
                  "pcm_protocol", "capture_format", "capture_hash_coverage", "retention"):
        require(field in a and field in b and a[field] == b[field], "render identity mismatch: " + field)
    require(first["inventory"] == second["inventory"], "asset inventory mismatch")
    require({k: {f: v[f] for f in ("sha256", "bytes")} for k, v in a["pcm"].items()} ==
            {k: {f: v[f] for f in ("sha256", "bytes")} for k, v in b["pcm"].items()}, "PCM identity mismatch")
    x = a["roles"][first["role"]]["backend_identity"]
    y = b["roles"][second["role"]]["backend_identity"]
    for field in ("backend", "instrumentation_sha256", "harness_sources_sha256", "clock_instrumentation_diff_sha256",
                  "engine_instrumentation_diff_sha256", "prewarm_setting", "core_library_entry"):
        require(bool(x.get(field)) and x.get(field) == y.get(field), "observer/settings mismatch: " + field)


def verify_pair(dataset, record):
    work, role, protocol = dataset["work"], dataset["role"], dataset["protocol"]
    key = run.digest(dict(protocol_sha256=protocol["sha256"], preset=record, role=role))
    path = work / "rows" / (key + ".json")
    if not path.exists():
        return None
    pair = run.read_cached(path, key, protocol["sha256"])
    require(pair is not None, "invalid pair checksum or retained files")
    require(pair["preset"] == record and pair["role"] == role, "pair source/role mismatch")
    expected_runs = ["jobs/" + run.job_key(protocol["sha256"], record, role, "selected", repeat) + "/row.json"
                     for repeat in (1, 2)]
    require(pair["runs"] == expected_runs, "pair requires two distinct correctly ordered repeats")
    require(pair["hash_coverage"] == protocol["config"]["capture_frames"], "pair selected coverage mismatch")
    require(pair["render_input_sha256"] == run.render_input_signature(protocol, role, record, pair["driver"]),
            "render input signature mismatch")
    jobs = []
    for relative in expected_runs:
        job_path = work / relative
        if not job_path.exists():
            return None
        checkpoint.verify_job(work, protocol, dataset["inventory"], job_path.parent.name)
        row = run.read_cached(job_path, job_path.parent.name, protocol["sha256"])
        require(row is not None, "job changed during verification")
        packet = json.loads((job_path.parent / "job.json").read_text())
        expected = run.make_job(protocol, record, role, "selected", row["repeat"], 360)
        for field, value in expected.items():
            # Output attempts and native-proof retention do not affect rendered pixels.
            if field not in ("output_directory", "retain_native_frames"):
                require(packet.get(field) == value, "input job mismatch: " + field)
        require(type(packet.get("retain_native_frames")) is bool, "invalid native retention flag")
        require(row["capture_mode"] == "selected" and row["measurement_frames"] == 360, "job selected window mismatch")
        manifest = {f["path"]: f for f in row["retained_files"]}
        require(len(manifest) == len(row["retained_files"]) and "job.json" in manifest, "missing/duplicate retained input")
        for relative_file, info in manifest.items():
            retained = run.safe_member(job_path.parent, relative_file)
            require(retained.stat().st_size == info["bytes"], "retained file size mismatch")
        result = row.get("result", {})
        for field, value in (("backend_identity", protocol["roles"][role]["backend_identity"]),
                             ("pcm_uint8_sha256", protocol["pcm"]["480"]["sha256"])):
            if field in result or row["status"] == "success":
                require(result.get(field) == value, "runtime observer/input mismatch: " + field)
        if row["status"] == "success":
            audit.verify_job(work, relative, protocol, record, role, row["repeat"])
            require("output/frames.jsonl" in manifest or "output/frames.jsonl.gz" in manifest, "trace not retained")
            for sample in result["selected_files"]:
                require("output/" + sample["thumbnail_path"] in manifest, "thumbnail not retained")
                with Image.open(job_path.parent / "output" / sample["thumbnail_path"]) as image:
                    require(image.format == "PNG" and image.size == (256, 144) and image.mode in ("RGB", "RGBA"), "invalid RGB thumbnail")
                    image.load()
                    if image.mode == "RGBA":
                        require(image.getchannel("A").getextrema() == (255, 255), "nonopaque RGB thumbnail")
        # Available driver fields must agree even in a failed producer.
        for field in DRIVER:
            if field in result and pair["driver"].get(field) is not None:
                require(result[field] == pair["driver"].get(field), "runtime driver differs between repeats: " + field)
        jobs.append(row)
    statuses = [j["status"] for j in jobs]
    exact = statuses == ["success", "success"] and jobs[0]["selected_native_sha256"] == jobs[1]["selected_native_sha256"]
    expected_status = ("success" if exact else "nondeterministic") if statuses == ["success", "success"] else next(s for s in statuses if s != "success")
    require(pair["status"] == expected_status and pair["repeat_exact_selected"] == exact, "pair repeat/status mismatch")
    return {"pair": pair, "jobs": jobs, "row": path.relative_to(work).as_posix(), "row_sha256": run.file_hash(path)}


def evidence(dataset, verified):
    pair = verified["pair"]
    return dict(status=pair["status"], original_protocol_sha256=dataset["protocol"]["sha256"],
                render_input_sha256=pair["render_input_sha256"], row=verified["row"], row_sha256=verified["row_sha256"],
                runs=[dict(path=path, row_sha256=run.file_hash(dataset["work"] / path), status=job["status"],
                           error=job.get("error"), producer_error=job.get("result", {}).get("error"),
                           result_path=job.get("result_path", "output/result.json") if job.get("result") else None)
                      for path, job in zip(pair["runs"], verified["jobs"])], driver=pair["driver"])


def mae(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / (3 * 255)


def screen_samples(first, second, a, b):
    samples, images = [], [[], []]
    for index, (left, right) in enumerate(zip(a["jobs"][0]["result"]["selected_files"], b["jobs"][0]["result"]["selected_files"])):
        entry = {"frame": left["frame"]}
        for side, dataset, verified, sample in ((0, first, a, left), (1, second, b, right)):
            path = Path(verified["pair"]["runs"][0]).parent / "output" / sample["thumbnail_path"]
            with Image.open(dataset["work"] / path) as image:
                images[side].append(image.convert("RGB"))
            entry[("baseline", "candidate")[side]] = dict(native_sha256=sample["sha256"], metrics=sample.get("metrics", {}),
                                                          thumbnail=path.as_posix(), thumbnail_sha256=sample["thumbnail_sha256"])
        entry["thumbnail_rgb_mae"] = mae(images[0][index], images[1][index])
        samples.append(entry)
    motion = [dict(frames=[samples[i]["frame"], samples[i + 1]["frame"]],
                   baseline=mae(images[0][i], images[0][i + 1]), candidate=mae(images[1][i], images[1][i + 1]))
              for i in range(0, len(samples), 2)]
    for item in motion:
        item["absolute_delta"] = abs(item["candidate"] - item["baseline"])
    return dict(samples=samples, thumbnail_rgb_mae=sum(s["thumbnail_rgb_mae"] for s in samples) / len(samples),
                adjacent_thumbnail_motion=motion, motion_absolute_delta=sum(s["absolute_delta"] for s in motion) / len(motion))


def compare_datasets(baseline, candidate, limit=None, offset=0):
    require(limit is None or type(limit) is int and limit > 0, "limit must be positive")
    require(type(offset) is int and offset >= 0, "offset must be nonnegative")
    first, second = load_dataset(baseline, "baseline"), load_dataset(candidate, "candidate")
    verify_compatible(first, second)
    records = first["inventory"]["presets"]
    selected = records[offset:None if limit is None else offset + limit]
    require(bool(selected), "selection is empty")
    issues, cases = [], []
    verified_counts, rendered_counts = Counter(), Counter()
    for record in selected:
        case, checked = {"preset": record}, []
        for label, dataset in (("baseline", first), ("candidate", second)):
            try:
                verified = verify_pair(dataset, record)
                checked.append(verified)
                if verified:
                    verified_counts[label] += 1
                    rendered_counts[label] += sum(j["status"] == "success" for j in verified["jobs"])
                    case[label] = evidence(dataset, verified)
            except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
                issues.append(dict(preset=record["path"], dataset=label, error=str(error)))
                checked.append(False)
        a, b = checked
        if a is False or b is False:
            category = "nondeterministic_uncomparable"
            case["reason"] = "invalid retained evidence; see integrity_issues"
        elif a is None or b is None:
            category = "missing_pending"
            case["missing_datasets"] = [label for label, value in zip(("baseline", "candidate"), checked) if value is None]
        elif any(v["pair"]["status"] == "nondeterministic" or len({j["status"] for j in v["jobs"]}) != 1 for v in checked):
            category = "nondeterministic_uncomparable"
            case["reason"] = "repeats differ in samples or terminal outcome"
        elif any(not all(v["pair"]["driver"].get(f) and all(j.get("result", {}).get(f) == v["pair"]["driver"][f] for j in v["jobs"]) for f in DRIVER) for v in checked) or a["pair"]["driver"] != b["pair"]["driver"]:
            category = "nondeterministic_uncomparable"
            case["reason"] = "runtime driver differs or is unavailable in a repeat"
        else:
            ok_a, ok_b = a["pair"]["status"] == "success", b["pair"]["status"] == "success"
            if ok_a and ok_b:
                category = "unchanged_native_samples" if a["jobs"][0]["selected_native_sha256"] == b["jobs"][0]["selected_native_sha256"] else "changed_needs_visual_review"
                case.update(screen_samples(first, second, a, b))
            else:
                category = "new_failure" if ok_a else "recovered_load_compatibility" if ok_b else "both_failed"
        case["category"] = category
        cases.append(case)
    counts = Counter(case["category"] for case in cases)
    ranked = sorted((c for c in cases if c["category"] == "changed_needs_visual_review"),
                    key=lambda c: (-c["thumbnail_rgb_mae"], -c["motion_absolute_delta"], c["preset"]["path"]))
    for rank, case in enumerate(ranked, 1):
        case["visual_review_rank"] = rank
    return dict(schema_version=1, datasets={label: dict(path=str(d["work"]), role=d["role"], protocol=d["protocol"],
                protocol_file_sha256=run.file_hash(d["work"] / "protocol.json"), inventory_file_sha256=run.file_hash(d["work"] / "inventory.json"))
                for label, d in (("baseline", first), ("candidate", second))}, inventory_count=len(records),
                selected_presets=len(selected), unselected_presets=len(records) - len(selected), offset=offset, limit=limit,
                verified_pairs={k: verified_counts[k] for k in ("baseline", "candidate")},
                rendered_successful_runs={k: rendered_counts[k] for k in ("baseline", "candidate")},
                counts={k: counts[k] for k in CATEGORIES}, recovered_presets=counts["recovered_load_compatibility"],
                complete_coverage=len(selected) == len(records) and not issues and all(verified_counts[k] == len(records) for k in ("baseline", "candidate")),
                integrity_issues=issues, visual_review_order=[c["preset"]["path"] for c in ranked], cases=cases, limitations=LIMITATIONS)


def write_report(baseline, candidate, output, **selection):
    output = Path(output).resolve()
    require(not any(output.is_relative_to(Path(work).resolve()) for work in (baseline, candidate)),
            "write comparison outside immutable datasets")
    report = compare_datasets(baseline, candidate, **selection)
    run.atomic(output, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, help="explicit partial preview; default evaluates every inventory preset")
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()
    report = write_report(args.baseline, args.candidate, args.output, limit=args.limit, offset=args.offset)
    print(run.canonical({k: report[k] for k in ("inventory_count", "selected_presets", "unselected_presets", "verified_pairs", "rendered_successful_runs", "counts", "complete_coverage")}))
    if report["integrity_issues"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
