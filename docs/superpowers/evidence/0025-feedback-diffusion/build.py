"""Build isolated desktop variants with preset-lab; no other worktree is modified."""
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from preset_lab.build_worker import build_worker, prepare_engine
from diagnostic import patch as diagnostic_patch
from optimization import patch as optimization_patch
from point_separated import patch as point_separated_patch
from blur_diffused import patch as blur_diffused_patch

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
SCRATCH = REPO / "build/diffusion"

def build(variant):
    kind = variant.removeprefix("gated-").split("-")[0]
    if variant == "four-corrected": kind = "corrected"
    repo = SCRATCH / ("repo-" + variant)
    patches = repo / "tools/projectm-patches"
    patches.mkdir(parents=True, exist_ok=True)
    if variant == "four-corrected":
        for name in ["0026-research-p2.patch","0027-research-kernel.patch"]:
            (patches/name).unlink(missing_ok=True)
    source = repo / "third_party"
    source.mkdir(exist_ok=True)
    link = source / "projectm"
    if not link.exists():
        link.symlink_to(REPO / "third_party/projectm", target_is_directory=True)
    for patch in sorted((REPO / "tools/projectm-patches").glob("*.patch")):
        if variant.startswith("baseline") and patch.name.startswith("0025-"):
            continue
        text = patch.read_text()
        if variant == "p1-corrected" and patch.name.startswith("0025-"):
            needle = "const bool diffuseAtOutput = m_feedbackDiffusion.Active() && !motionVectorsDrawn;"
            assert text.count(needle) == 1
            text = text.replace(needle, "const bool diffuseAtOutput = false; // Research: sharp composite, P1 input filtering.")
        if variant == "four-corrected" and patch.name.startswith("0025-"):
            for needle in ["if (weights.x <= 2.0 / 3.0)", "if (kernel.variance <= 2.0f / 3.0f)"]:
                assert text.count(needle)==1
                text=text.replace(needle,"if (false) // Research: symmetric four taps at every active variance.")
        if variant == "half-float" and patch.name.startswith("0025-"):
            needle="m_framebuffer.CreateColorAttachment(0, 0);"
            assert text.count(needle)==1
            text=text.replace(needle,"m_framebuffer.CreateColorAttachment(0, 0, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT);")
        if variant == "compile-failure" and patch.name.startswith("0025-"):
            needle = 'm_shader.CompileProgram(vertexShader, fragmentShader);'
            assert text.count(needle) == 1, 'compile-failure injection no longer matches'
            text = text.replace(needle, 'm_shader.CompileProgram(vertexShader, fragmentShader + "invalid_shader_token");')
        (patches / patch.name).write_text(text)
    if variant == "p2" or kind in ("five", "four", "adaptive34"):
        (patches / "0026-research-p2.patch").write_text(diagnostic_patch(default="p2"))
    if kind in ("five", "four"):
        (patches / "0027-research-kernel.patch").write_text(optimization_patch(kind, "mediump" in variant))
    if kind == "adaptive34":
        (patches / "0027-research-adaptive34.patch").write_text((EVIDENCE / "0027-research-adaptive34.patch").read_text())
    if variant.endswith("-mv"):
        (patches / "0028-research-motion-minimum.patch").write_text((EVIDENCE / "0028-research-motion-minimum.patch").read_text())
    if variant == "point-separated":
        (patches / "0026-research-point-separated.patch").write_text(point_separated_patch())
    if variant == "blur-diffused":
        (patches / "0026-research-blur-diffused.patch").write_text(blur_diffused_patch())
    work = SCRATCH / ("work-" + variant)
    exe = build_worker(repo, work)
    snapshot, identity = prepare_engine(repo, work)
    result = {"exe": str(exe), "snapshot": str(snapshot), "identity": asdict(identity)}
    (EVIDENCE / ("worker-" + variant + ".json")).write_text(json.dumps(result, indent=2) + "\n")
    print(variant, exe, flush=True)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", choices=["baseline", "p1", "p2", "compile-failure", "five", "four", "five-mediump", "four-mediump", "baseline-mv", "p1-mv", "five-mv", "four-mv", "gated", "gated-five", "gated-four", "gated-adaptive34", "final", "release", "production", "corrected", "reviewed", "p1-corrected", "four-corrected", "point-separated", "blur-diffused", "half-float"])
    build(parser.parse_args().variant)
