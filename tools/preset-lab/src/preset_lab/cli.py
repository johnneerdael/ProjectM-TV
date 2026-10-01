import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .inventory import inventory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="preset-lab", allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("inventory", help="Identify presets, weights and textures")
    for name in ("presets", "textures", "index"):
        command.add_argument(f"--{name}", type=Path, required=True)
    command = commands.add_parser("doctor", help="Build and verify deterministic native rendering")
    command.add_argument("--repo", type=Path, default=Path.cwd())
    command.add_argument("--work", type=Path, default=Path("build/preset-lab"))
    command.add_argument("--worker", type=Path)
    command = commands.add_parser("corpus", help="Decode music samples and measure audio descriptors")
    command.add_argument("--audio", type=Path, required=True)
    command.add_argument("--work", type=Path, default=Path("build/preset-lab/audio"))
    command.add_argument("--manifest", type=Path)
    command = commands.add_parser("trace", help="Trace static audio dependencies in one preset")
    command.add_argument("preset", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "trace":
            from .preset_parser import parse_preset
            from .dependencies import trace_dependencies
            evidence = trace_dependencies(parse_preset(args.preset))
            json.dump(dict(asdict(evidence), schema_version=1), sys.stdout,
                      ensure_ascii=False, allow_nan=False)
            sys.stdout.write("\n")
            return 0
        if args.command == "corpus":
            from .audio import load_corpus
            corpus = load_corpus(args.audio, args.manifest, args.work)
            records = [dict(asdict(track), path=str(track.path)) for track in corpus.tracks]
            json.dump({"identity": corpus.identity, "tracks": records, "descriptors": corpus.descriptors},
                      sys.stdout, ensure_ascii=False, allow_nan=False)
            sys.stdout.write("\n")
            return 0
        if args.command == "doctor":
            from .doctor import doctor
            report = doctor(args.repo.resolve(), args.work.resolve(), args.worker)
            json.dump(report, sys.stdout, ensure_ascii=False, allow_nan=False)
            sys.stdout.write("\n")
            return 0 if report["healthy"] else 1
        records, metadata = inventory(args.presets, args.index, args.textures)
        json.dump({"presets": [asdict(record) for record in records], "metadata": metadata},
                  sys.stdout, ensure_ascii=False, allow_nan=False)
        sys.stdout.write("\n")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
