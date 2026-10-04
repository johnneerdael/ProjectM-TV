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
    protocol_path = work / "protocol.json"
    protocol_bytes = protocol_path.read_bytes()
    protocol = json.loads(protocol_bytes)
    if run.digest({k: v for k, v in protocol.items() if k != "sha256"}) != protocol["sha256"]:
        raise ValueError("protocol checksum mismatch")
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
        checkpoint.verify_terminal_producer(directory, row, protocol, row["preset"])
        if any(run.file_hash(p) != checksum for p, checksum in hashes.items()):
            raise ValueError("checked input changed during validation")
        checked.append({"key": row["key"], "status": row["status"],
                        "inputs": [{"path": p.relative_to(work).as_posix(), "sha256": checksum,
                                    "bytes": p.stat().st_size} for p, checksum in hashes.items()]})
        counts[row["status"]] += 1
    if protocol_path.read_bytes() != protocol_bytes:
        raise ValueError("protocol changed during validation")
    if not checked:
        raise ValueError("empty snapshot")
    manifest = {"protocol_sha256": protocol["sha256"], "jobs": checked}
    manifest_path = output.with_suffix(".inputs.json.gz")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(gzip.compress((run.canonical(manifest) + "\n").encode(), mtime=0))
    report = {"protocol_sha256": protocol["sha256"], "jobs_checked": len(checked),
              "statuses": dict(counts), "integrity_issues": [],
              "input_manifest": manifest_path.name, "input_manifest_sha256": run.file_hash(manifest_path),
              "input_records_sha256": run.digest(checked),
              "validator_sha256": run.file_hash(Path(checkpoint.__file__)),
              "snapshot_script_sha256": run.file_hash(Path(__file__)),
              "scope": "Available terminal producer identity and immutable capture schedule; partial baseline, not full retained-file/frame audit",
              "limitations": "Membership and exact checked row/packet/result hashes are frozen in the input manifest. Later jobs or storage annotations are different snapshots; these hashes do not assert equality with older remote checkpoint row metadata."}
    run.atomic(output, report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("work", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(run.canonical(snapshot(args.work, args.output)))
