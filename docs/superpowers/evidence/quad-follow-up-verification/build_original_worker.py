"""Build a research-only sampler exposing the existing unfiltered feedback flip.

Preset copies can preserve individual undisplaced reads while other reads use P1.
There is no automatic shader rewrite or preset-name rule in this experiment.
"""

import difflib
import json
import shlex
import shutil
from dataclasses import asdict
from pathlib import Path

from measure import ROOT
from preset_lab.build_worker import build_worker, prepare_engine


def main():
    work = ROOT / "build/follow-ups"
    metadata = json.loads((work / "worker-diffusion-safe.json").read_text())
    source_tree = next(path.parent for path in (work / "lab-diffusion-safe/engines").glob("*/preset-lab-identity.json")
                       if json.loads(path.read_text()) == metadata["identity"])
    edits = {
        "src/libprojectM/MilkdropPreset/PresetState.hpp": [
            ("    std::weak_ptr<Renderer::Texture> mainTexture;", "    bool pmxWantsOriginalFeedback{false}; //!< EXPERIMENT\n    std::weak_ptr<Renderer::Texture> pmxOriginalTexture; //!< EXPERIMENT: unfiltered flip.\n    std::weak_ptr<Renderer::Texture> mainTexture;")],
        "src/libprojectM/MilkdropPreset/MilkdropPreset.cpp": [
            ("    if (m_feedbackDiffusion.Active())", "    if (m_feedbackDiffusion.Active() && m_state.pmxWantsOriginalFeedback &&\n        (m_isFirstFrame || motionVectorsDrawn || !m_flipHoldsPreviousFrame))\n    {\n        m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), nullptr, true, false);\n    }\n    if (m_feedbackDiffusion.Active())"),
            ("    m_flipHoldsPreviousFrame = false;\n\n    // Update blur textures.", "    m_state.pmxOriginalTexture = m_flipTexture.Texture();\n    m_flipHoldsPreviousFrame = false;\n\n    // Update blur textures.")],
        "src/libprojectM/MilkdropPreset/MilkdropShader.hpp": [
            ("    std::vector<Renderer::TextureSamplerDescriptor> m_mainTextureDescriptors;", "    std::vector<Renderer::TextureSamplerDescriptor> m_pmxOriginalDescriptors; //!< EXPERIMENT\n    std::vector<Renderer::TextureSamplerDescriptor> m_mainTextureDescriptors;")],
        "src/libprojectM/MilkdropPreset/MilkdropShader.cpp": [
            ("        if (lowerCaseName == \"main\")", "        if (lowerCaseName == \"pmx_original\")\n        {\n            presetState.pmxWantsOriginalFeedback = true;\n            Renderer::TextureSamplerDescriptor desc(presetState.mainTexture.lock(),\n                presetState.renderContext.textureManager->GetSampler(name), name, \"pmx_original\");\n            m_pmxOriginalDescriptors.push_back(std::move(desc));\n            continue;\n        }\n        if (lowerCaseName == \"main\")"),
            ("    if (!m_mainTextureDescriptors.empty() &&", "    for (auto& desc : m_pmxOriginalDescriptors)\n    {\n        desc.Texture(presetState.pmxOriginalTexture);\n        desc.Bind(textureUnit, m_shader);\n        textureUnit++;\n    }\n    if (!m_mainTextureDescriptors.empty() &&"),
            ("    std::set<std::string> texSizeDeclarations;", "    std::set<std::string> texSizeDeclarations;\n    for (const auto& desc : m_pmxOriginalDescriptors)\n    {\n        samplerDeclarations.insert(desc.SamplerDeclaration());\n        texSizeDeclarations.insert(desc.TexSizeDeclaration());\n    }")],
    }
    patch = "Subject: [EXPERIMENT] Expose original feedback for individual-read ablations\n\n"
    for relative, replacements in edits.items():
        before = (source_tree / relative).read_text()
        after = before
        for old, new in replacements:
            if after.count(old) != 1:
                raise ValueError(f"unexpected match count: {relative}: {old}")
            after = after.replace(old, new)
        patch += "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                            fromfile="a/"+relative, tofile="b/"+relative))
    Path(__file__).with_name("feedback-original-sampler.patch").write_text(patch)
    repo = work / "repo-diffusion-original"
    patches = repo / "tools/projectm-patches"
    patches.mkdir(parents=True, exist_ok=True)
    for path in (work / "repo-diffusion-safe/tools/projectm-patches").glob("*.patch"):
        shutil.copyfile(path, patches / path.name)
    (patches / "0028-feedback-original-sampler.patch").write_text(patch)
    if not (repo / "third_party").exists():
        (repo / "third_party").symlink_to(work / "pristine-source", target_is_directory=True)
    build = work / "lab-diffusion-original"
    _, identity = prepare_engine(repo, build)
    exe = build_worker(repo, build)
    for variant in ("on", "off"):
        wrapper = work / f"worker-diffusion-original-{variant}.sh"
        value = "1" if variant == "on" else "0"
        wrapper.write_text(f"#!/bin/sh\nexport PMX_DIFF={value}\nexec {shlex.quote(str(exe))} \"$@\"\n")
        wrapper.chmod(0o755)
        item = {"exe": str(wrapper), "identity": asdict(identity), "diagnostic_switches": {"PMX_DIFF": value}}
        (work / f"worker-diffusion-original-{variant}.json").write_text(json.dumps(item, indent=2))
    print("original sampler worker built", flush=True)


if __name__ == "__main__":
    main()
