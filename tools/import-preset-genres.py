#!/usr/bin/env python3
"""Import or verify a measured genre bundle against the current app assets."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).parent/"preset-lab/src"))
from preset_lab.export import import_bundle


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle",type=Path,required=True)
    parser.add_argument("--repo",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    try:
        print(import_bundle(args.bundle,args.repo,args.check))
        return 0
    except (OSError,ValueError) as error:
        print(f"error: {error}",file=sys.stderr)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
