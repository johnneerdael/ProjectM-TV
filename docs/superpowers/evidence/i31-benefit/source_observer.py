"""The exact shared gamma-only observer recipe; never modify shipping source."""

def observe(content):
    start = content.index("void VideoEcho::DrawGammaAdjustment(")
    gamma = content[start:]
    anchor = "    auto const gammaAdj = static_cast<float>(*perFrameContext.gamma);"
    draw = "        m_echoMesh.Draw();"
    if gamma.count(anchor) != 1 or gamma.count(draw) != 1:
        raise ValueError("Gamma observer anchors differ")
    gamma = gamma.replace(anchor, anchor + "\n    ++lab::gamma_invocations;\n    lab::gamma_value = gammaAdj;", 1)
    gamma = gamma.replace(draw, draw + "\n        ++lab::gamma_draw_calls;", 1)
    return content[:start] + gamma
