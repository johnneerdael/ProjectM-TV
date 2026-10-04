"""Generate research kernels to test the handover's cost/fidelity tradeoff on Mali.

Five taps retain the original 1D Gaussian marginal on both axes: centre c and
four diagonal taps of weight s/2 each at the same offset. Sum = c+2s=1;
per-axis second moment is unchanged. Only the joint 2D frequency response differs.
Four taps use offset n+(V-n*n)/(2*n+1), n=floor(sqrt(V)), including the
bilinear split exactly. They have poorer Gaussian frequency response at 4K.
These are experimental variants, excluded from the product patch series.
"""
import difflib
from measure import EVIDENCE, REPO

def patch(kind,mediump=False):
    path="src/libprojectM/MilkdropPreset/FeedbackDiffusion.cpp"
    original=(REPO/"third_party/projectm"/path).read_text()
    text=original
    edges="""    vec4 edges = texture(source, uv - dx) + texture(source, uv + dx) +
                 texture(source, uv - dy) + texture(source, uv + dy);
"""
    assert edges in text
    text=text.replace(edges,"")
    if kind=="five":
        text=text.replace("color = c * c * center + c * s * edges + s * s * corners;",
                          "color = c * center + 0.5 * s * corners;")
    elif kind=="four":
        text=text.replace("    vec4 center = texture(source, uv);\n","")
        text=text.replace("color = c * c * center + c * s * edges + s * s * corners;","color = 0.25 * corners;")
        needle="    m_kernel = DiffusionKernelFor(scale);"
        assert needle in text
        text=text.replace(needle,needle+"""
    if (m_kernel.variance > 0.0f)
    {
        const float near = std::floor(std::sqrt(m_kernel.variance));
        m_kernel.sideOffset = near + (m_kernel.variance-near*near)/(2.0f*near+1.0f);
    }""")
    else:raise ValueError(kind)
    if mediump:
        text=text.replace("vec4 center =", "mediump vec4 center =").replace("vec4 corners =","mediump vec4 corners =")
    return f"diff --git a/{path} b/{path}\n"+"".join(difflib.unified_diff(original.splitlines(keepends=True),text.splitlines(keepends=True),fromfile="a/"+path,tofile="b/"+path))

if __name__=="__main__":
    for kind in ["five","four"]:
        for mediump in [False,True]:
            (EVIDENCE/f"0027-research-{kind}{'-mediump' if mediump else ''}.patch").write_text(patch(kind,mediump))
