#!/usr/bin/env python3
"""Read a preset corpus into native syntax trees without rendering or audio input."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import time
import tempfile


def read_preset(binary: Path, path: Path, output: Path, reader_sha: str) -> dict:
    raw=path.read_bytes()
    source_sha = hashlib.sha256(raw).hexdigest()
    reader_bytes=Path(binary).resolve(strict=True).read_bytes()
    if hashlib.sha256(reader_bytes).hexdigest()!=reader_sha:
        raise ValueError('corpus reader identity mismatch')
    result = {"preset": path.name, "preset_sha256": source_sha, "reader_sha256": reader_sha,
              "semantics_complete": False}
    try:
        with tempfile.TemporaryDirectory(prefix='milk-scan-inputs-') as directory:
            source=Path(directory)/path.name;source.write_bytes(raw)
            adapter_dir=Path(directory)/'adapter';adapter_dir.mkdir()
            adapter=adapter_dir/'reader';adapter.write_bytes(reader_bytes);adapter.chmod(0o700)
            process = subprocess.run([str(adapter), str(source)], capture_output=True, text=True,
                                     errors="replace", timeout=5)
        result["diagnostics"] = process.stderr
        if process.returncode:
            result.update(syntax_complete=False, error=f"native reader exit {process.returncode}")
        else:
            parsed = json.loads(process.stdout)
            result.update(parsed)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        result.update(syntax_complete=False, error=str(error))
    # Both source and reader identities are part of the cache location.
    target = output / "trees" / reader_sha / (source_sha + ".json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    return {"preset": path.name, "preset_sha256": source_sha, "tree": str(target),
            "syntax_complete": result["syntax_complete"],
            "unknown": {name: row.get("reason") for name, row in result.get("sections", {}).items()
                        if row["status"] != "parsed"}, "error": result.get("error")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reader", type=Path, required=True)
    parser.add_argument("--presets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("workers must be between 1 and 8")
    binary = args.reader.resolve()
    paths = sorted(args.presets.glob("*.milk"))
    if not paths:
        parser.error("no .milk presets found")
    reader_sha = hashlib.sha256(binary.read_bytes()).hexdigest()
    begin = time.monotonic()
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = executor.map(lambda path: read_preset(binary, path, args.output, reader_sha), paths)
        for count, row in enumerate(futures, 1):
            rows.append(row)
            if count % 1000 == 0:
                print(f"Read {count}/{len(paths)} in {time.monotonic()-begin:.1f}s", flush=True)
    summary = {"presets": len(rows), "syntax_complete": sum(row["syntax_complete"] for row in rows),
               "elapsed_seconds": time.monotonic()-begin, "reader_sha256": reader_sha,
               "semantics_complete": False, "rows": rows}
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "rows"}), flush=True)


if __name__ == "__main__":
    main()
