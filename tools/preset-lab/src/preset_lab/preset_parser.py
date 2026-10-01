import re
from pathlib import Path


def parse_preset(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) > 0x100000 or b"\0" in data:
        raise ValueError("preset exceeds engine size limit or contains NUL")
    values, positions = {}, {}
    for number, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
        match = re.search(r"[ =]", line)
        if not match or match.start() == 0:
            continue
        key, value = line[:match.start()], line[match.start() + 1:]
        if key not in values:
            values[key], positions[key] = value, number
    prefixes = ["per_frame_init_", "per_frame_", "per_pixel_", "warp_", "comp_"]
    for i in range(4):
        prefixes.extend(f"wave_{i}_{part}" for part in ("init", "per_frame", "per_point"))
        prefixes.extend(f"shape_{i}_{part}" for part in ("init", "per_frame"))
    sections = {}
    for prefix in prefixes:
        code, lines = [], []
        index = 1
        while prefix + str(index) in values:
            key = prefix + str(index)
            value = values[key]
            code.append(value[1:] if value.startswith("`") else value)
            lines.append(positions[key])
            index += 1
        if code:
            sections[prefix] = {"code": "\n".join(code) + "\n", "lines": lines}
    return {"path": path.name, "values": values, "positions": positions, "sections": sections}
