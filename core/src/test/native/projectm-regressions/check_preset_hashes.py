"""Verify authored preset witnesses immediately before the native compiler test."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main() -> None:
    executable, mode, assets_arg, manifest_arg = sys.argv[1:]
    assets = Path(assets_arg)
    manifest = Path(manifest_arg)
    if manifest.suffix == '.json':
        # Share the exact authored witnesses with the source-reader round-trip tests.
        witnesses = json.loads(manifest.read_text())['rows']
        rows = ['\t'.join((row['sha256'], stage, row['preset']))
                for row in witnesses for stage in sorted({value['section'] for value in row['literals']})]
    else:
        rows = manifest.read_text().splitlines()
    for row in rows:
        expected, stage, name = row.split('\t', 2)
        if stage not in {'warp', 'composite'}:
            raise ValueError(f'invalid preset stage: {stage}')
        actual = hashlib.sha256((assets / 'presets' / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'preset witness changed: {name}')
    with tempfile.TemporaryDirectory() as directory:
        native_manifest = Path(directory) / 'presets.tsv'
        native_manifest.write_text('\n'.join(rows) + '\n')
        subprocess.run([executable, mode, assets_arg, str(native_manifest)], check=True)


if __name__ == '__main__':
    main()
