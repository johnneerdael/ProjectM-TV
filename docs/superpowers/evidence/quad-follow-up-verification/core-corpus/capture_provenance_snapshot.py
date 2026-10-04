"""Record the exact inputs to a read-only producer-provenance snapshot."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

import checkpoint
import run


def snapshot(work, output):
    work, output = Path(work).resolve(), Path(output).resolve()
    if output.is_relative_to(work):
        raise ValueError("snapshot output must be outside the immutable dataset")
    source_paths = {"snapshot_script_sha256": Path(__file__),
                    "validator_sha256": Path(checkpoint.__file__),
                    "validation_helper_sha256": Path(run.__file__)}
    source_hashes = {key: run.file_hash(path) for key, path in source_paths.items()}
    protocol_path = work / "protocol.json"
    protocol_bytes = protocol_path.read_bytes()
    protocol = json.loads(protocol_bytes)
    if run.digest({k: v for k, v in protocol.items() if k != "sha256"}) != protocol["sha256"]:
        raise ValueError("protocol checksum mismatch")
    inventory_path = work / "inventory.json"
    inventory_bytes = inventory_path.read_bytes()
    inventory = json.loads(inventory_bytes)
    if (len(inventory["presets"]) != inventory["count"]
            or run.digest(inventory["presets"]) != inventory["corpus_sha256"]
            or inventory["corpus_sha256"] != protocol["corpus_sha256"]):
        raise ValueError("immutable inventory/corpus mismatch")
    checked, counts = [], Counter()
    # Freeze membership before checking: later scanner jobs are outside this snapshot.
    paths = sorted((work / "jobs").glob("*/row.json"))
    for row_path in paths:
        row_bytes = row_path.read_bytes()
        row = json.loads(row_bytes)
        directory = row_path.parent
        inputs = [row_path, directory / "job.json"]
        if row.get("result") is not None:
            result_path = directory / row.get("result_path", "output/result.json")
            if not result_path.resolve().is_relative_to(directory.resolve()):
                raise ValueError("unsafe producer input path")
            inputs.append(result_path)
        inputs = [p for p in inputs if p.is_file()]
        hashes = {p: run.file_hash(p) for p in inputs}
        hashes[row_path] = hashlib.sha256(row_bytes).hexdigest()
        verified = checkpoint.verify_job(work, protocol, inventory, directory.name)
        if verified is None:
            raise ValueError("missing terminal row provenance")
        if any(run.file_hash(p) != checksum for p, checksum in hashes.items()):
            raise ValueError("checked input changed during validation")
        checked.append({"key": row["key"], "status": row["status"],
                        "inputs": [{"path": p.relative_to(work).as_posix(), "sha256": checksum,
                                    "bytes": p.stat().st_size} for p, checksum in hashes.items()]})
        counts[row["status"]] += 1
    if protocol_path.read_bytes() != protocol_bytes or inventory_path.read_bytes() != inventory_bytes:
        raise ValueError("protocol/inventory changed during validation")
    if not checked:
        raise ValueError("empty snapshot")
    if any(run.file_hash(source_paths[key]) != checksum for key, checksum in source_hashes.items()):
        raise ValueError("validation source changed during generation")
    manifest = {"protocol_sha256": protocol["sha256"],
                "dataset_inputs": [{"path": "protocol.json", "sha256": hashlib.sha256(protocol_bytes).hexdigest()},
                                   {"path": "inventory.json", "sha256": hashlib.sha256(inventory_bytes).hexdigest()}],
                "jobs": checked}
    manifest_path = output.with_suffix(".inputs.json.gz")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(gzip.compress((run.canonical(manifest) + "\n").encode(), mtime=0))
    report = {"protocol_sha256": protocol["sha256"], "jobs_checked": len(checked),
              "statuses": dict(counts), "integrity_issues": [],
              "input_manifest": manifest_path.name, "input_manifest_sha256": run.file_hash(manifest_path),
              "input_records_sha256": run.digest(checked),
              **source_hashes,
              "scope": "Existing checkpoint row/job/inventory provenance, retained-file and successful-observer validation; partial baseline, not complete corpus coverage",
              "limitations": "Membership and exact checked row/packet/result hashes are frozen in the input manifest. Later jobs or storage annotations are different snapshots; these hashes do not assert equality with older remote checkpoint row metadata."}
    run.atomic(output, report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("work", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(run.canonical(snapshot(args.work, args.output)))
