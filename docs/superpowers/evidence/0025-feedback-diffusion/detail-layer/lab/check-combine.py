"""Execute the prototype's actual shaders against RGBA8 clipping fixtures."""
import argparse
from pathlib import Path
import re
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, default=Path("build/detail-clipping/combine-test"))
    parser.add_argument("--prototype", type=Path)
    parser.add_argument("--gles", action="store_true", help="also link the GLSL ES 3.00 variants")
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
    shaders = {}
    for name in ("CombineFragment", "DownFragment"):
        match = re.search(r'const char\* ' + name + r' = R"\((.*?)\)";', source, re.S)
        path = build / f"{name}.frag"
        if match:
            path.write_text(match[1])
            shaders[name] = match[1]
        else:
            raise ValueError(f"missing prototype shader: {name}")
        paths.append(str(path))
    if args.gles:
        vertex = build / "pass.vert"
        vertex.write_text("#version 300 es\nprecision highp float;\n"
                          "void main() { vec2 p = vec2(gl_VertexID == 1 ? 3.0 : -1.0, "
                          "gl_VertexID == 2 ? 3.0 : -1.0); gl_Position = vec4(p, 0.0, 1.0); }\n")
        for name, shader in shaders.items():
            fragment = build / f"{name}-es.frag"
            fragment.write_text("#version 300 es\nprecision highp float;\nprecision highp int;\n"
                                "precision highp sampler2D;\n" + shader.split("\n", 1)[1])
            subprocess.run(["glslangValidator", "-l", str(vertex), str(fragment)], check=True)
    subprocess.run(["cmake", "-S", str(here), "-B", str(build), f"-DREPO_ROOT={repo}"], check=True)
    subprocess.run(["cmake", "--build", str(build), "-j", "4"], check=True)
    subprocess.run([str(build / "detail-combine-test"), *paths], check=True)


if __name__ == "__main__":
    main()
