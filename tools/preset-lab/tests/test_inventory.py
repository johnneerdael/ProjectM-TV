import hashlib

import pytest

from preset_lab.identity import load_json
from preset_lab.inventory import inventory


@pytest.fixture
def library(tmp_path):
    presets = tmp_path / "presets"
    textures = tmp_path / "textures"
    presets.mkdir()
    textures.mkdir()
    (presets / "Martin's café & waves.milk").write_bytes(b"wave_a=bass;\n")
    (presets / "duplicate.milk").write_bytes(b"wave_a=bass;\n")
    (textures / "noise.png").write_bytes(b"texture content")
    index = tmp_path / "presets.idx"
    index.write_text("duplicate.milk\t0\nMartin's café & waves.milk\t37\n")
    return presets, index, textures


def test_inventory_preserves_names_weights_and_duplicate_content(library):
    records, metadata = inventory(*library)
    assert [(r.path, r.weight_mb) for r in records] == [
        ("Martin's café & waves.milk", 37), ("duplicate.milk", 0)
    ]
    digest = hashlib.sha256(b"wave_a=bass;\n").hexdigest()
    assert records[0].sha256 == digest == records[1].sha256
    assert metadata["duplicates"] == {digest: [r.path for r in records]}
    assert metadata["preset_count"] == 2


def test_reordering_index_does_not_change_identity(library):
    before = inventory(*library)[1]
    lines = library[1].read_text().splitlines()
    library[1].write_text("\n".join(reversed(lines)) + "\n")
    assert inventory(*library)[1] == before


def test_asset_or_weight_change_changes_library_identity(library):
    before = inventory(*library)[1]["library_sha256"]
    library[1].write_text(library[1].read_text().replace("\t37", "\t38"))
    weighted = inventory(*library)[1]["library_sha256"]
    assert before != weighted
    (library[0] / "duplicate.milk").write_bytes(b"modified preset")
    assert inventory(*library)[1]["library_sha256"] not in (before, weighted)


def test_texture_change_is_separate_from_library_identity(library):
    before = inventory(*library)[1]
    (library[2] / "noise.png").write_bytes(b"changed texture")
    after = inventory(*library)[1]
    assert before["texture_sha256"] != after["texture_sha256"]
    assert before["library_sha256"] == after["library_sha256"]


@pytest.mark.parametrize("row,reason", [
    ("../escape.milk\t0", "unsafe"),
    ("/absolute.milk\t0", "unsafe"),
    ("folder/preset.milk\t0", "unsafe"),
    ("bad.milk\t-1", "weight"),
    ("bad.milk\t1.5", "weight"),
    ("bad.milk\tgarbage", "weight"),
    ("bad.milk\t0\textra", "row"),
])
def test_rejects_malformed_index(library, row, reason):
    library[1].write_text(row + "\n")
    with pytest.raises(ValueError, match=reason):
        inventory(*library)


def test_rejects_duplicate_index_rows(library):
    library[1].write_text(library[1].read_text() + "duplicate.milk\t0\n")
    with pytest.raises(ValueError, match="duplicate"):
        inventory(*library)


def test_rejects_missing_or_unindexed_presets(library):
    (library[0] / "duplicate.milk").unlink()
    with pytest.raises(ValueError, match="missing"):
        inventory(*library)
    (library[0] / "duplicate.milk").write_bytes(b"restored")
    (library[0] / "unindexed.milk").write_bytes(b"extra")
    with pytest.raises(ValueError, match="unindexed"):
        inventory(*library)


def test_rejects_symlink_outside_library(library, tmp_path):
    outside = tmp_path / "outside.milk"
    outside.write_bytes(b"external")
    (library[0] / "duplicate.milk").unlink()
    (library[0] / "duplicate.milk").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        inventory(*library)


@pytest.mark.parametrize("text", ['{"x": NaN}', '{"x": Infinity}', '{"x": 1, "x": 2}'])
def test_json_rejects_nonfinite_and_duplicate_keys(tmp_path, text):
    path = tmp_path / "invalid.json"
    path.write_text(text)
    with pytest.raises(ValueError):
        load_json(path)
