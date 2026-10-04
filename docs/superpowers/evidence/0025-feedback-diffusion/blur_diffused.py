"""Research only: test matching main/blur input diffusion, preserving y orientation."""
import difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]/"third_party/projectm"
def patch():
    output=[]
    edits={
      "src/libprojectM/MilkdropPreset/BlurTexture.hpp":[
       ("float referenceScale = 0.0f);","float referenceScale = 0.0f, bool sourceFlipped = false);")],
      "src/libprojectM/MilkdropPreset/BlurTexture.cpp":[
       ("float referenceScale)\n{","float referenceScale, bool sourceFlipped)\n{"),
       ('blurShader->SetUniformInt("flipVertical", 1);','blurShader->SetUniformInt("flipVertical", sourceFlipped ? 0 : 1);')],
      "src/libprojectM/MilkdropPreset/MilkdropPreset.cpp":[
       ("const auto warpedImage = m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0);",
        "const auto warpedImage = m_feedbackDiffusion.Active() ? m_feedbackDiffusion.Texture() : m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0);"),
       ("m_state.renderContext.lineReferenceWidth, m_state.renderContext.lineReferenceHeight));",
        "m_state.renderContext.lineReferenceWidth, m_state.renderContext.lineReferenceHeight), m_feedbackDiffusion.Active());")]
    }
    for name,pairs in edits.items():
        before=(ROOT/name).read_text();after=before
        for old,new in pairs:
            assert after.count(old)==1,(name,old,after.count(old));after=after.replace(old,new)
        output.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile="a/"+name,tofile="b/"+name))
    return "".join(output)
