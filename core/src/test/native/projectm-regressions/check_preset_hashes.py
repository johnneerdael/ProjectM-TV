"""Verify authored preset witnesses immediately before the native compiler test."""
import hashlib
from pathlib import Path
import subprocess
import sys


def main() -> None:
    executable, mode, assets_arg, manifest_arg = sys.argv[1:]
    assets = Path(assets_arg)
    manifest = Path(manifest_arg)
    for row in manifest.read_text().splitlines():
        expected, stage, name = row.split('\t', 2)
        if stage not in {'warp', 'composite'}:
            raise ValueError(f'invalid preset stage: {stage}')
        actual = hashlib.sha256((assets / 'presets' / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'preset witness changed: {name}')
    subprocess.run([executable, mode, assets_arg, manifest_arg], check=True)


if __name__ == '__main__':
    main()
