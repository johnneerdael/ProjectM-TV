"""Research-only P1/P2/off selector; generated patch is excluded from the product series."""
import difflib
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent

def replace(text, old, new, count=1):
    assert text.count(old) == count, old
    return text.replace(old, new)

def patch(default="p1", android=False):
    source = REPO / "third_party/projectm"
    files = ["src/libprojectM/MilkdropPreset/MilkdropPreset.cpp", "src/libprojectM/MilkdropPreset/MilkdropPreset.hpp"]
    originals = {f:(source/f).read_text() for f in files}
    texts = dict(originals)
    cpp, hpp = files
    t = texts[cpp]
    t = "#include <cstdlib>\n#ifdef USE_GLES\n#include <sys/system_properties.h>\n#endif\n" + t
    start = "    // Above the line reference size, the warp reads the previous frame through a small blur that gives"
    i, j = t.index(start), t.index("    m_framebuffer.Bind(m_previousFrameBuffer);",t.index(start))
    t = t[:i] + """    // RESEARCH ONLY: select identical code paths within one benchmark APK.
#ifdef USE_GLES
    char mode[PROP_VALUE_MAX]{};
    __system_property_get("debug.projectmtv.diffusion", mode);
#else
    const char* mode = std::getenv("PROJECTM_DIFFUSION_PLACEMENT");
#endif
    const bool off = mode != nullptr && mode[0] == '0';
    m_feedbackDiffusion.SetScale(off ? 0.0f : LineScale(renderContext.viewportSizeX, renderContext.viewportSizeY,
                                           renderContext.lineReferenceWidth, renderContext.lineReferenceHeight));
    const bool diffuseAfterDrawing = m_feedbackDiffusion.Active() && mode != nullptr && mode[0] == '2';

""" + t[j:]
    if "m_diffusionAllowed" in originals[cpp]:
        t = t.replace("SetScale(off ? 0.0f", "SetScale((off || !m_diffusionAllowed) ? 0.0f")
    if default == "p2" and not android:
        t = t.replace("const bool diffuseAfterDrawing = m_feedbackDiffusion.Active() && mode != nullptr && mode[0] == '2';",
                      "const bool diffuseAfterDrawing = m_feedbackDiffusion.Active() && (mode == nullptr || mode[0] == '2');")
    t = replace(t, 'if (m_feedbackDiffusion.Active())', 'if (m_feedbackDiffusion.Active() && !diffuseAfterDrawing)')
    needle = """        m_state.mainTexture = m_feedbackDiffusion.Texture();
    }
    else
"""
    t = replace(t, needle, """        m_state.mainTexture = m_feedbackDiffusion.Texture();
    }
    else if (diffuseAfterDrawing)
    {
        if (m_isFirstFrame || motionVectorsDrawn || !m_diffusionHoldsPreviousFrame)
        {
            m_feedbackDiffusion.Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), true);
        }
        m_state.mainTexture = m_feedbackDiffusion.Texture();
    }
    else
""")
    t = t.replace('m_flipHoldsPreviousFrame = false;', 'm_flipHoldsPreviousFrame = false;\n    m_diffusionHoldsPreviousFrame = false;')
    t = replace(t, """    m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_currentFrameBuffer, 0), nullptr, true, false);
    m_state.mainTexture = m_flipTexture.Texture();""", """    if (diffuseAfterDrawing)
    {
        m_feedbackDiffusion.Draw(m_framebuffer.GetColorAttachmentTexture(m_currentFrameBuffer, 0), true);
        m_state.mainTexture = m_feedbackDiffusion.Texture();
    }
    else
    {
        m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_currentFrameBuffer, 0), nullptr, true, false);
        m_state.mainTexture = m_flipTexture.Texture();
    }""")
    t = replace(t, 'm_flipHoldsPreviousFrame = true;', 'm_flipHoldsPreviousFrame = !diffuseAfterDrawing;\n    m_diffusionHoldsPreviousFrame = diffuseAfterDrawing;')
    texts[cpp] = t
    texts[hpp] = replace(texts[hpp], '    bool m_isFirstFrame{true};', '    bool m_diffusionHoldsPreviousFrame{false};\n    bool m_isFirstFrame{true};')
    out = []
    for f in files:
        out.append(f"diff --git a/{f} b/{f}\n")
        out.extend(difflib.unified_diff(originals[f].splitlines(keepends=True), texts[f].splitlines(keepends=True),
                                        fromfile="a/"+f,tofile="b/"+f))
    return "".join(out)

if __name__ == "__main__":
    (EVIDENCE / "0026-benchmark-selector.patch").write_text(patch(android=True))
