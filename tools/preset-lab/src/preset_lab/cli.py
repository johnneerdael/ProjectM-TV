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
    args = parser.parse_args(argv)
    try:
        records, metadata = inventory(args.presets, args.index, args.textures)
        json.dump({"presets": [asdict(record) for record in records], "metadata": metadata},
                  sys.stdout, ensure_ascii=False, allow_nan=False)
        sys.stdout.write("\n")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
