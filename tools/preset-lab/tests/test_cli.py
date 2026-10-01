import json
import os
import subprocess
import sys
from pathlib import Path


def invoke(*args):
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).parents[1] / "src"))
    return subprocess.run([sys.executable, "-m", "preset_lab", *args], env=env,
                          text=True, capture_output=True)


def test_bad_arguments_exit_two():
    result = invoke("unknown-command")
    assert result.returncode == 2
    assert result.stderr
    assert result.stdout == ""


def test_failed_inventory_exits_one(tmp_path):
    result = invoke("inventory", "--presets", str(tmp_path / "absent"),
                    "--textures", str(tmp_path), "--index", str(tmp_path / "absent.idx"))
    assert result.returncode == 1
    assert "error" in result.stderr.lower()
    assert result.stdout == ""


def test_inventory_stdout_is_machine_readable(tmp_path):
    presets = tmp_path / "presets"
    textures = tmp_path / "textures"
    presets.mkdir()
    textures.mkdir()
    (presets / "One.milk").write_bytes(b"preset")
    index = tmp_path / "presets.idx"
    index.write_text("One.milk\t5\n")
    result = invoke("inventory", "--presets", str(presets), "--textures", str(textures),
                    "--index", str(index))
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["metadata"]["preset_count"] == 1
    assert data["presets"][0]["path"] == "One.milk"
    assert data["presets"][0]["weight_mb"] == 5
