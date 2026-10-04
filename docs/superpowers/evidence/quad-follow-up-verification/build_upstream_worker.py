"""Build stock 4.1.7 with only lab target-FBO/API compatibility and compile logging."""

import difflib
import json
from dataclasses import asdict
from pathlib import Path

from measure import ROOT
from preset_lab.build_worker import build_worker, prepare_engine


def main():
    work = ROOT / "build/follow-ups"
    source = work / "pristine-source/projectm"
    replacements = {
        "src/libprojectM/ProjectM.hpp": [
            ("#include <memory>", "#include <memory>\n#include <stdexcept>"),
            ("    void RenderFrame();", "    void RenderFrame(uint32_t targetFramebufferObject = 0);"),
            ("    void SetWindowSize(uint32_t width, uint32_t height);",
             "    void SetWindowSize(uint32_t width, uint32_t height);\n"
             "    // Lab-only compatibility: stock rendering supports classic lines only.\n"
             "    void SetLineReferenceSize(int width, int height)\n"
             "    { if (width != 0 || height != 0) throw std::invalid_argument(\"stock worker requires classic lines\"); }\n"
             "    void SetLineAntialiasing(bool enabled)\n"
             "    { if (enabled) throw std::invalid_argument(\"stock worker has no quad antialiasing\"); }")],
        "src/libprojectM/ProjectM.cpp": [
            ("void ProjectM::RenderFrame()", "void ProjectM::RenderFrame(uint32_t targetFramebufferObject)"),
            ("    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);", "    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, targetFramebufferObject);")],
    }
    patch = "Subject: [LAB ONLY] Capture stock 4.1.7 into the laboratory FBO\n\nNo preset, feedback, blur, shader or primitive algorithm changes. Reject quad-only options.\n\n"
    for relative, changes in replacements.items():
        before = (source / relative).read_text()
        after = before
        for old, new in changes:
            if after.count(old) != 1:
                raise ValueError(f"unexpected match count: {relative}: {old}")
            after = after.replace(old, new)
        patch += "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                            fromfile="a/"+relative, tofile="b/"+relative))
    for name in ("PerPixelMesh.cpp", "FinalComposite.cpp"):
        relative = "src/libprojectM/MilkdropPreset/"+name
        before = (source / relative).read_text()
        after = "#define MILKDROP_PRESET_DEBUG\n"+before
        patch += "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                            fromfile="a/"+relative, tofile="b/"+relative))
    Path(__file__).with_name("upstream-lab-compatibility.patch").write_text(patch)
    repo = work / "repo-upstream"
    patches = repo / "tools/projectm-patches"
    patches.mkdir(parents=True, exist_ok=True)
    (patches / "0000-upstream-lab-compatibility.patch").write_text(patch)
    if not (repo / "third_party").exists():
        (repo / "third_party").symlink_to(work / "pristine-source", target_is_directory=True)
    build = work / "lab-upstream"
    _, identity = prepare_engine(repo, build)
    exe = build_worker(repo, build)
    metadata = {"exe": str(exe), "identity": asdict(identity), "upstream": "4.1.7 + lab-only API/FBO compatibility"}
    (work / "worker-upstream.json").write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
