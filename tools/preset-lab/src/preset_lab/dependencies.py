import re

from .eel import Expr, parse_eel
from .models import StaticEvidence
from .shader import parse_shader

SOURCES = ("bass", "mid", "treb", "bass_att", "mid_att", "treb_att", "value1", "value2")
PURE = set("sin cos tan asin acos atan atan2 abs floor ceil int sqrt sqr pow exp log log10 min max sign rand rnd sigmoid above below equal band bor bnot exec2 exec3 lerp saturate clamp frac fmod float float2 float3 float4 int2 int3 int4 uint2 uint3 uint4 length distance dot cross normalize tex2d tex3d tex2dlod tex3dlod getpixel getblur1 getblur2 getblur3 lum luminosity lerp smoothstep step trunc mul transpose reflect refract rsqrt log2 exp2 round".split())
STRUCTURAL = set("zoom zoomexp rot warp dx dy sx sy cx cy uv uv_orig tex_zoom tex_ang".split())
GEOMETRY = set("x y rad ang sides samples wave_x wave_y wave_mystery mv_x mv_y mv_dx mv_dy mv_l".split())
VISIBILITY = set("a a2 border_a wave_a ob_a ib_a mv_a decay".split())
COLOR = set("r g b r2 g2 b2 border_r border_g border_b wave_r wave_g wave_b ob_r ob_g ob_b ib_r ib_g ib_b mv_r mv_g mv_b gammaadj ret".split())


def q_variable(name: str) -> bool:
    return bool(re.fullmatch(r"q(?:[1-9]|[12]\d|3[0-2])", name))


def merge(*dependencies: dict) -> dict:
    result = {}
    for deps in dependencies:
        for source, path in deps.items():
            if source not in result or (len(path), path) < (len(result[source]), result[source]):
                result[source] = path
    return result


def member_name(node: Expr) -> str | None:
    if node.kind == "var":
        return node.value
    if node.kind == "member":
        parent = member_name(node.children[0])
        return f"{parent}.{node.value}" if parent else None
    return None


class Tracer:
    def __init__(self):
        self.unsupported = []
        self.locations = {}

    def read(self, env: dict, name: str) -> dict:
        if "." in name and name in env:
            return env[name]
        return merge(env.get(name, {}), *(value for key, value in env.items() if key.startswith(name + ".")))

    def assign(self, env: dict, name: str, value: dict, line: int):
        if "." not in name:
            for key in list(env):
                if key.startswith(name + "."):
                    del env[key]
        env[name] = {source: path if name in path else path + (name,) for source, path in value.items()}
        self.locations[name] = line

    def evaluate(self, node: Expr, env: dict, control: dict | None = None) -> dict:
        control = control or {}
        if node.kind == "constant":
            return {}
        if node.kind in ("var", "member"):
            name = member_name(node)
            if name and re.fullmatch(r"reg\d\d", name):
                self.unsupported.append("shared register inter-context propagation")
            return self.read(env, name) if name else self.evaluate(node.children[0], env, control)
        if node.kind in ("sequence", "scope"):
            result = {}
            before = dict(env)
            locals_ = {c.value for c in node.children if c.kind == "declare"}
            for child in node.children:
                if child.kind == "sequence":
                    locals_.update(c.value for c in child.children if c.kind == "declare")
                result = self.evaluate(child, env, control)
            if node.kind == "scope":
                for name in locals_:
                    for key in list(env):
                        if key == name or key.startswith(name + "."):
                            del env[key]
                    if name in before:
                        env[name] = before[name]
            return result
        if node.kind == "declare":
            value = merge(control, self.evaluate(node.children[0], env))
            self.assign(env, node.value, value, node.line)
            return value
        if node.kind == "assign":
            target = member_name(node.children[0])
            value = self.evaluate(node.children[1], env, control)
            if not target:
                self.unsupported.append("indexed or memory-buffer assignment")
                return value
            if node.value != "=":
                value = merge(value, self.read(env, target))
            self.assign(env, target, merge(value, control), node.line)
            return self.read(env, target)
        if node.kind == "branch" or (node.kind == "call" and node.value.lower() == "if"):
            if len(node.children) != 3:
                self.unsupported.append("invalid conditional arity")
                return {}
            condition = merge(control, self.evaluate(node.children[0], env))
            yes, no = dict(env), dict(env)
            y = self.evaluate(node.children[1], yes, condition)
            n = self.evaluate(node.children[2], no, condition)
            for key in yes.keys() | no.keys():
                env[key] = merge(yes.get(key, {}), no.get(key, {}))
            return merge(condition, y, n)
        if node.kind == "call" and node.value.lower() == "loop":
            if len(node.children) != 2:
                self.unsupported.append("invalid loop arity")
                return {}
            count = merge(control, self.evaluate(node.children[0], env))
            before = dict(env)
            result = self.evaluate(node.children[1], env, count)
            for key in before.keys() | env.keys():
                env[key] = merge(before.get(key, {}), env.get(key, {}))
            return merge(count, result)
        if node.kind == "call" and node.value.lower() not in PURE:
            self.unsupported.append(f"unsupported function/memory access: {node.value}")
        return merge(*(self.evaluate(child, env, control) for child in node.children))


def trace_dependencies(parsed: dict) -> StaticEvidence:
    tracer = Tracer()
    trees = {}
    for section, contents in parsed["sections"].items():
        try:
            trees[section] = (parse_shader if section in ("warp_", "comp_") else parse_eel)(contents["code"])
        except (ValueError, RecursionError) as error:
            tracer.unsupported.append(f"{section}: {error}")
    sources = {name: {name: (name,)} for name in SOURCES[:6]}
    main = dict(sources)
    if "per_frame_init_" in trees:
        tracer.evaluate(trees["per_frame_init_"], main)
    if "per_frame_" in trees:
        for _ in range(64):
            before = dict(main)
            main.update(sources)
            tracer.evaluate(trees["per_frame_"], main)
            if before == main:
                break
        else:
            tracer.unsupported.append("per-frame dependency state did not converge")
    output = []
    def emit(section, env):
        for sink in STRUCTURAL | GEOMETRY | VISIBILITY | COLOR:
            if sink not in tracer.locations:
                continue
            impact = ("structural" if sink in STRUCTURAL else "geometry" if sink in GEOMETRY
                      else "visibility" if sink in VISIBILITY else "color")
            for source, path in tracer.read(env, sink).items():
                relative = tracer.locations.get(sink, 1)
                mapping = parsed["sections"].get(section, {}).get("lines", [1])
                line = mapping[min(max(relative - 1, 0), len(mapping) - 1)]
                output.append({"audio_input": source, "sink": sink, "via": list(path),
                               "impact": impact, "section": section, "line": line})
    if "per_frame_" in trees:
        emit("per_frame_", main)
    for section in ("per_pixel_", "warp_", "comp_"):
        if section in trees:
            child = dict(sources)
            transferred = STRUCTURAL | GEOMETRY | VISIBILITY | COLOR if section == "per_pixel_" else set()
            child.update({k: v for k, v in main.items() if k in transferred or q_variable(k)})
            tracer.locations = {}
            tracer.evaluate(trees[section], child)
            emit(section, child)
    for kind in ("wave", "shape"):
        for index in range(4):
            enabled = parsed["values"].get(f"{kind}code_{index}_enabled", "0")
            try:
                active = float(enabled) > 0
            except ValueError:
                active = False
            if not active:
                continue
            prefix = f"{kind}_{index}_"
            child = dict(sources)
            child.update({k: v for k, v in main.items() if q_variable(k)})
            for phase in ("init", "per_frame", "per_point"):
                section = prefix + phase
                if phase == "per_point":
                    child = {k: v for k, v in child.items()
                             if k in SOURCES[:6] or k in COLOR | VISIBILITY
                             or q_variable(k) or re.fullmatch(r"t[1-8]", k)}
                    child.update({name: {name: (name,)} for name in SOURCES[6:]})
                    child["x"] = {"value1": ("value1", "x")}
                    child["y"] = {"value2": ("value2", "y")}
                if section in trees:
                    tracer.locations = {}
                    tracer.evaluate(trees[section], child)
                    emit(section, child)
    try:
        visible_builtin = float(parsed["values"].get("fWaveAlpha", "0")) > 0
    except ValueError:
        visible_builtin = False
    if visible_builtin:
        output.append({"audio_input": "waveform_pcm", "sink": "builtin_wave_geometry",
                       "via": ["waveform_pcm", "builtin_wave_geometry"], "impact": "geometry",
                       "section": "builtin_wave", "line": parsed["positions"]["fWaveAlpha"]})
    return StaticEvidence(not tracer.unsupported,
                          sorted(output, key=lambda p: (p["section"], p["sink"], p["audio_input"])),
                          sorted(set(tracer.unsupported)))
