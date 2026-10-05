"""Execute the prototype's actual shaders against RGBA8 clipping fixtures."""
import argparse
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=Path("build/detail-clipping/combine-test"))
    parser.add_argument("--prototype", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    repo = next(parent for parent in here.parents if (parent / ".git").exists())
    prototype = args.prototype or here.parent / "detail-layer-prototype.diff"
    # Read shader bodies from added lines, so this tests the shader that the
    # engine receives rather than a Python reimplementation of its formula.
    source = "\n".join(line[1:] for line in prototype.read_text().splitlines()
                       if line.startswith("+") and not line.startswith("+++"))
    build = args.build.resolve()
    build.mkdir(parents=True, exist_ok=True)
    paths = []
    for name in ("CombineFragment", "DownFragment", "ReanchorFragment"):
        match = re.search(r'const char\* ' + name + r' = R"\((.*?)\)";', source, re.S)
        path = build / f"{name}.frag"
        if match:
            path.write_text(match[1])
        elif name == "ReanchorFragment":
            path = Path("-")  # Original prototype has no correction pass.
        else:
            raise ValueError(f"missing prototype shader: {name}")
        paths.append(str(path))
    subprocess.run(["cmake", "-S", str(here), "-B", str(build), f"-DREPO_ROOT={repo}"], check=True)
    subprocess.run(["cmake", "--build", str(build), "-j", "4"], check=True)
    subprocess.run([str(build / "detail-combine-test"), *paths], check=True)


if __name__ == "__main__":
    main()
