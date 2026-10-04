"""Approved throwaway probe: reference-grid feedback, native warp and fresh primitives.

The previous frame is sampled into a reference-sized texture before the warp.
The preset's existing linear/point samplers then define its footprint on that grid.
No Gaussian pass, preset-name rule, or production option is introduced.
"""

import argparse
import difflib
import json
import shlex
import shutil
from dataclasses import asdict
from pathlib import Path

from measure import ROOT
from preset_lab.build_worker import build_worker, prepare_engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--linear", action="store_true")
    args = parser.parse_args()
    work = ROOT / "build/follow-ups"
    source, _ = prepare_engine(ROOT, work / "lab-samplers-fixed")
    relative = "src/libprojectM/MilkdropPreset/MilkdropPreset.cpp"
    before = (source / relative).read_text()
    after = before.replace('#include "MilkdropPreset.hpp"', '#include "MilkdropPreset.hpp"\n#include <cstdlib>')
    old = '''    if (m_isFirstFrame || motionVectorsDrawn || !m_flipHoldsPreviousFrame)
    {
        m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), nullptr, true, false);
    }
    m_flipHoldsPreviousFrame = false;
    m_state.mainTexture = m_flipTexture.Texture();'''
    new = '''    bool referenceFeedback = false;
    const char* const referenceProbe = std::getenv("PMX_REF_FEEDBACK");
    if (referenceProbe != nullptr && referenceProbe[0] == '1' && !m_pmxReferenceShaderFailed &&
        LineScale(renderContext.viewportSizeX, renderContext.viewportSizeY,
                  renderContext.lineReferenceWidth, renderContext.lineReferenceHeight) > 1.0f)
    {
        try
        {
            if (!m_pmxReferenceCopy)
            {
                m_pmxReferenceCopy = std::make_unique<Renderer::CopyTexture>();
            }
            const auto canvas = ShaderCanvasSize(renderContext.viewportSizeX, renderContext.viewportSizeY,
                                                 renderContext.lineReferenceWidth, renderContext.lineReferenceHeight);
            if (!m_pmxReferenceFramebuffer)
            {
                m_pmxReferenceFramebuffer = std::make_unique<Renderer::Framebuffer>(1);
                m_pmxReferenceFramebuffer->CreateColorAttachment(0, 0);
            }
            m_pmxReferenceFramebuffer->SetSize(canvas.width, canvas.height);
            glViewport(0, 0, canvas.width, canvas.height);
            m_pmxReferenceCopy->Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0),
                                     *m_pmxReferenceFramebuffer, 0, true, false);
            glViewport(0, 0, renderContext.viewportSizeX, renderContext.viewportSizeY);
            m_state.mainTexture = m_pmxReferenceFramebuffer->GetColorAttachmentTexture(0, 0);
            referenceFeedback = true;
        }
        catch (const Renderer::ShaderException&)
        {
            // A rejected optional copy program leaves the existing rendering path available.
            m_pmxReferenceShaderFailed = true;
        }
    }
    if (!referenceFeedback)
    {
        if (m_isFirstFrame || motionVectorsDrawn || !m_flipHoldsPreviousFrame)
        {
            m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), nullptr, true, false);
        }
        m_state.mainTexture = m_flipTexture.Texture();
    }
    m_flipHoldsPreviousFrame = false;'''
    if after.count(old) != 1 or after == before:
        raise ValueError("reference probe does not match current production source")
    after = after.replace(old, new)
    patch = "Subject: [EXPERIMENT] Sample feedback on the reference grid before the native warp\n\n"
    patch += "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                        fromfile="a/"+relative, tofile="b/"+relative))
    relative = "src/libprojectM/MilkdropPreset/MilkdropPreset.hpp"
    before = (source / relative).read_text()
    old = "    Renderer::CopyTexture m_flipTexture;"
    new = '''    std::unique_ptr<Renderer::CopyTexture> m_pmxReferenceCopy; //!< EXPERIMENT: optional reference-grid copy.
    std::unique_ptr<Renderer::Framebuffer> m_pmxReferenceFramebuffer; //!< EXPERIMENT: warp input only.
    bool m_pmxReferenceShaderFailed{false}; //!< EXPERIMENT: fallback to original path.
    Renderer::CopyTexture m_flipTexture;'''
    if before.count(old) != 1:
        raise ValueError("reference probe member insertion does not match source")
    after = before.replace(old, new)
    patch += "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                        fromfile="a/"+relative, tofile="b/"+relative))
    if args.linear:
        for relative, old, new in (
            ("src/libprojectM/Renderer/CopyTexture.hpp", "    CopyTexture();", "    explicit CopyTexture(bool linearSource = false);"),
            ("src/libprojectM/Renderer/CopyTexture.cpp", "CopyTexture::CopyTexture()\n{", "CopyTexture::CopyTexture(bool linearSource)\n{\n    if (linearSource) m_sampler.FilterMode(GL_LINEAR);"),
        ):
            before = (source / relative).read_text()
            if before.count(old) != 1:
                raise ValueError(f"linear copy probe does not match {relative}")
            after = before.replace(old, new)
            patch += "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                                fromfile="a/"+relative, tofile="b/"+relative))
        patch = patch.replace("std::make_unique<Renderer::CopyTexture>();", "std::make_unique<Renderer::CopyTexture>(true);")
    name = "reference-feedback-linear" if args.linear else "reference-feedback"
    Path(__file__).with_name(name+"-probe.patch").write_text(patch)
    repo = work / ("repo-"+name)
    patches = repo / "tools/projectm-patches"
    patches.mkdir(parents=True, exist_ok=True)
    for path in (ROOT / "tools/projectm-patches").glob("*.patch"):
        shutil.copyfile(path, patches / path.name)
    (patches / "0027-reference-feedback-probe.patch").write_text(patch)
    if not (repo / "third_party").exists():
        (repo / "third_party").symlink_to(work / "pristine-source", target_is_directory=True)
    build = work / ("lab-"+name)
    _, identity = prepare_engine(repo, build)
    exe = build_worker(repo, build)
    for variant, value in (("on", "1"), ("off", "0")):
        wrapper = work / f"worker-{name}-{variant}.sh"
        wrapper.write_text(f'#!/bin/sh\nexport PMX_REF_FEEDBACK={value}\nexec {shlex.quote(str(exe))} "$@"\n')
        wrapper.chmod(0o755)
        metadata = {"exe": str(wrapper), "identity": asdict(identity), "diagnostic_switches": {"PMX_REF_FEEDBACK": value}}
        (work / f"worker-{name}-{variant}.json").write_text(json.dumps(metadata, indent=2))
    print("reference feedback probe built", flush=True)


if __name__ == "__main__":
    main()
