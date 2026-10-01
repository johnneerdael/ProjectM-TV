from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

from .identity import digest, file_digest
from .models import PresetRecord


def valid_filename(name: str) -> bool:
    return (bool(name) and name not in (".", "..")
            and not any(c in name for c in "/\\\t\r\n\0")
            and name.lower().endswith(".milk"))


def read_index(index: Path) -> dict[str, int]:
    weights = {}
    for number, line in enumerate(index.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        columns = line.split("\t")
        if len(columns) not in (1, 2):
            raise ValueError(f"invalid index row {number}")
        name = columns[0]
        if not valid_filename(name):
            raise ValueError(f"unsafe preset filename in row {number}: {name!r}")
        if name in weights:
            raise ValueError(f"duplicate index row for {name}")
        weight = columns[1] if len(columns) == 2 else "0"
        if not weight or any(c not in "0123456789" for c in weight):
            raise ValueError(f"invalid memory weight in row {number}")
        weights[name] = int(weight)
    if not weights:
        raise ValueError("preset index is empty")
    return weights


def inventory(presets: Path, index: Path, textures: Path) -> tuple[list[PresetRecord], dict]:
    if not presets.is_dir() or not textures.is_dir():
        raise ValueError("preset and texture directories must exist")
    weights = read_index(index)
    actual = {p.name for p in presets.iterdir() if p.name.lower().endswith(".milk")}
    missing, extra = weights.keys() - actual, actual - weights.keys()
    if missing:
        raise ValueError(f"indexed presets missing: {sorted(missing)}")
    if extra:
        raise ValueError(f"unindexed presets: {sorted(extra)}")
    records = []
    groups = defaultdict(list)
    for name in sorted(weights, key=lambda value: value.encode("utf-8")):
        path = presets / name
        if path.is_symlink():
            raise ValueError(f"preset symlink is not supported: {name}")
        if not path.is_file():
            raise ValueError(f"preset is not a file: {name}")
        fingerprint = file_digest(path)
        records.append(PresetRecord(name, fingerprint, weights[name]))
        groups[fingerprint].append(name)
    texture_records = []
    for path in sorted(textures.rglob("*"), key=lambda p: str(p.relative_to(textures)).encode()):
        if path.is_symlink():
            raise ValueError(f"texture symlink is not supported: {path.name}")
        if path.is_file() and path.name != ".DS_Store":
            texture_records.append({"path": path.relative_to(textures).as_posix(),
                                    "sha256": file_digest(path)})
    return records, {
        "schema_version": 1,
        "preset_count": len(records),
        "library_sha256": digest([asdict(record) for record in records]),
        "texture_sha256": digest(texture_records),
        "textures": texture_records,
        "duplicates": {key: names for key, names in sorted(groups.items()) if len(names) > 1},
    }
