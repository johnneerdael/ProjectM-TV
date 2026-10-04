"""Native witness hashes are checked on each test invocation."""
import hashlib
from pathlib import Path
import subprocess
import sys


CHECK = Path(__file__).resolve().parents[2] / 'core/src/test/native/projectm-regressions/check_preset_hashes.py'


def test_changed_preset_blocks_native_compiler_without_reconfiguration(tmp_path):
    assets = tmp_path / 'assets'
    presets = assets / 'presets'
    presets.mkdir(parents=True)
    preset = presets / 'witness.milk'
    preset.write_bytes(b'original')
    manifest = tmp_path / 'witnesses.tsv'
    manifest.write_text(hashlib.sha256(preset.read_bytes()).hexdigest() + '\twarp\twitness.milk\n')
    marker = tmp_path / 'compiler-ran'
    compiler = tmp_path / 'compiler.py'
    compiler.write_text(f'from pathlib import Path\nPath({str(marker)!r}).write_text("ran")\n')
    # The wrapper forwards its mode as the first argument to the executable.
    # Python can act as the executable with this script as its mode argument.
    command = [sys.executable, str(CHECK), sys.executable, str(compiler), str(assets), str(manifest)]
    subprocess.run(command, check=True)
    assert marker.read_text() == 'ran'
    marker.unlink()
    preset.write_bytes(b'changed')
    assert subprocess.run(command, capture_output=True).returncode != 0
    assert not marker.exists()
