"""Research only: keep warp point reads on raw feedback, with its y orientation fixed."""
import difflib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]/"third_party/projectm"

def patch():
    result=[]
    def edit(name,transform):
        before=(ROOT/name).read_text();after=transform(before)
        assert before!=after,name
        result.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
                                          fromfile="a/"+name,tofile="b/"+name))
    def replace(s,old,new):
        assert s.count(old)==1,(old,s.count(old));return s.replace(old,new)
    edit("src/libprojectM/MilkdropPreset/PresetState.hpp",lambda s:replace(s,
        "    std::weak_ptr<Renderer::Texture> mainTexture;",
        "    std::weak_ptr<Renderer::Texture> rawPointMainTexture;\n    bool rawPointMainFlip{};\n    std::weak_ptr<Renderer::Texture> mainTexture;"))
    edit("src/libprojectM/MilkdropPreset/MilkdropPreset.cpp",lambda s:replace(s,
        "    m_flipHoldsPreviousFrame = false;\n    m_diffusionHoldsPreviousFrame = false;\n\n    // Update blur textures.",
        "    m_state.rawPointMainTexture = m_feedbackDiffusion.Active()\n"
        "        ? m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0) : m_state.mainTexture;\n"
        "    m_state.rawPointMainFlip = m_feedbackDiffusion.Active();\n"
        "    m_flipHoldsPreviousFrame = false;\n    m_diffusionHoldsPreviousFrame = false;\n\n    // Update blur textures."))
    def header(s):
        s=replace(s,"    ShaderType m_type{ShaderType::WarpShader};",
                    "    auto PreparePointFeedbackGlsl(const std::string& source) const -> std::string;\n"
                    "    std::vector<bool> m_mainPointDescriptors;\n    bool m_hasPointFeedback{};\n"
                    "    GLint m_pointFlipLocation{-1};\n    ShaderType m_type{ShaderType::WarpShader};")
        return s
    edit("src/libprojectM/MilkdropPreset/MilkdropShader.hpp",header)
    def implementation(s):
        s=replace(s,"            m_mainTextureDescriptors.push_back(std::move(desc));",
                    "            const bool point = !name.empty() && (name[0] == 'p' || name[0] == 'P');\n"
                    "            m_mainPointDescriptors.push_back(point);\n            m_hasPointFeedback |= point;\n"
                    "            m_mainTextureDescriptors.push_back(std::move(desc));")
        s=replace(s,"    GLint textureUnit{0};\n    for (auto& desc : m_mainTextureDescriptors)",
                    "    if (m_type == ShaderType::WarpShader && m_pointFlipLocation >= 0)\n"
                    "        glUniform1i(m_pointFlipLocation, presetState.rawPointMainFlip ? 1 : 0);\n"
                    "    size_t mainIndex = 0;\n    GLint textureUnit{0};\n    for (auto& desc : m_mainTextureDescriptors)")
        s=replace(s,"        desc.Texture(presetState.mainTexture);",
                    "        const bool point = m_type == ShaderType::WarpShader && m_mainPointDescriptors[mainIndex++];\n"
                    "        desc.Texture(point ? presetState.rawPointMainTexture : presetState.mainTexture);")
        s=replace(s,"        m_shader.CompileProgram(vertexShader, cachedGlsl);",
                    "        m_shader.CompileProgram(vertexShader, PreparePointFeedbackGlsl(cachedGlsl));\n"
                    "        m_pointFlipLocation = m_shader.UniformLocation(\"projectm_point_main_flip\");")
        s=replace(s,"    m_shader.CompileProgram(vertexShader, generator.GetResult());",
                    "    m_shader.CompileProgram(vertexShader, PreparePointFeedbackGlsl(generator.GetResult()));\n"
                    "    m_pointFlipLocation = m_shader.UniformLocation(\"projectm_point_main_flip\");")
        anchor="void MilkdropShader::LoadCode(const std::string& presetShaderCode)"
        helper=r'''auto MilkdropShader::PreparePointFeedbackGlsl(const std::string& source) const -> std::string
{
    if (m_type != ShaderType::WarpShader || !m_hasPointFeedback) return source;
    const std::regex read(R"(\btexture\s*\(\s*(sampler_p[cw]_main)\s*,)");
    std::string code = std::regex_replace(source, read, "projectm_point_main($1,");
    const auto position = code.find("uniform ");
    if (position == std::string::npos) throw Renderer::ShaderException("Point feedback has no uniform declarations");
    const char* helper = R"(
uniform bool projectm_point_main_flip;
highp vec4 projectm_point_main(lowp sampler2D source, highp vec2 uv) {
    if (projectm_point_main_flip) uv.y = 1.0 - uv.y;
    return texture(source, uv);
}
highp vec4 projectm_point_main(lowp sampler2D source, highp vec2 uv, highp float bias) {
    if (projectm_point_main_flip) uv.y = 1.0 - uv.y;
    return texture(source, uv, bias);
}
)";
    code.insert(position, helper);
    return code;
}

'''
        return replace(s,anchor,helper+anchor)
    edit("src/libprojectM/MilkdropPreset/MilkdropShader.cpp",implementation)
    return "".join(result)

if __name__=="__main__":print(patch(),end="")
