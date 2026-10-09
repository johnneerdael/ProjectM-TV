#include "CustomShape.hpp"
#include "GeometryTargets.hpp"
#include <glm/gtc/matrix_transform.hpp>

#include "MilkdropPresetExceptions.hpp"
#include "PresetFileParser.hpp"

#include <Renderer/TextureManager.hpp>
#include <Renderer/Color.hpp>

#include <cassert>
#include <cmath>
#include <vector>

namespace libprojectM {
namespace MilkdropPreset {

CustomShape::CustomShape(PresetState& presetState)
    : m_presetState(presetState)
    , m_perFrameContext(presetState.globalMemory, &presetState.globalRegisters)
{
    std::vector<TexturedPoint> vertexData;
    vertexData.resize(102);

    glGenBuffers(1, &m_vboIdUntextured); // one vertex buffer for fills and outlines, see Draw()

    m_texturedArray.Bind();
    glBindBuffer(GL_ARRAY_BUFFER, m_vboIdUntextured);

    glEnableVertexAttribArray(0);
    glEnableVertexAttribArray(1);
    glEnableVertexAttribArray(2);

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(TexturedPoint), reinterpret_cast<void*>(offsetof(TexturedPoint, x))); // Position
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, sizeof(TexturedPoint), reinterpret_cast<void*>(offsetof(TexturedPoint, r))); // Color
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(TexturedPoint), reinterpret_cast<void*>(offsetof(TexturedPoint, u))); // Texture coordinate

    m_untexturedArray.Bind();
    glBindBuffer(GL_ARRAY_BUFFER, m_vboIdUntextured);

    glEnableVertexAttribArray(0);
    glEnableVertexAttribArray(1);

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(TexturedPoint), reinterpret_cast<void*>(offsetof(TexturedPoint, x))); // Position
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, sizeof(TexturedPoint), reinterpret_cast<void*>(offsetof(TexturedPoint, r))); // Color

    glBufferData(GL_ARRAY_BUFFER, sizeof(TexturedPoint) * vertexData.size(), vertexData.data(), GL_STREAM_DRAW);

    Renderer::VertexArray::Unbind();
    glBindBuffer(GL_ARRAY_BUFFER, 0);

    m_perFrameContext.RegisterBuiltinVariables();
}

CustomShape::~CustomShape()
{
    glDeleteBuffers(1, &m_vboIdUntextured);
}

void CustomShape::Initialize(PresetFileParser& parsedFile, int index)
{
    std::string const shapecodePrefix = "shapecode_" + std::to_string(index) + "_";

    m_index = index;
    m_enabled = parsedFile.GetBool(shapecodePrefix + "enabled", m_enabled);
    m_sides = parsedFile.GetInt(shapecodePrefix + "sides", m_sides);
    m_additive = parsedFile.GetBool(shapecodePrefix + "additive", m_additive);
    m_thickOutline = parsedFile.GetBool(shapecodePrefix + "thickOutline", m_thickOutline);
    m_textured = parsedFile.GetBool(shapecodePrefix + "textured", m_textured);
    m_instances = parsedFile.GetInt(shapecodePrefix + "num_inst", m_instances);
    m_x = parsedFile.GetFloat(shapecodePrefix + "x", m_x);
    m_y = parsedFile.GetFloat(shapecodePrefix + "y", m_y);
    m_radius = parsedFile.GetFloat(shapecodePrefix + "rad", m_radius);
    m_angle = parsedFile.GetFloat(shapecodePrefix + "ang", m_angle);
    m_tex_ang = parsedFile.GetFloat(shapecodePrefix + "tex_ang", m_tex_ang);
    m_tex_zoom = parsedFile.GetFloat(shapecodePrefix + "tex_zoom", m_tex_zoom);
    m_r = parsedFile.GetFloat(shapecodePrefix + "r", m_r);
    m_g = parsedFile.GetFloat(shapecodePrefix + "g", m_g);
    m_b = parsedFile.GetFloat(shapecodePrefix + "b", m_b);
    m_a = parsedFile.GetFloat(shapecodePrefix + "a", m_a);
    m_r2 = parsedFile.GetFloat(shapecodePrefix + "r2", m_r2);
    m_g2 = parsedFile.GetFloat(shapecodePrefix + "g2", m_g2);
    m_b2 = parsedFile.GetFloat(shapecodePrefix + "b2", m_b2);
    m_a2 = parsedFile.GetFloat(shapecodePrefix + "a2", m_a2);
    m_border_r = parsedFile.GetFloat(shapecodePrefix + "border_r", m_border_r);
    m_border_g = parsedFile.GetFloat(shapecodePrefix + "border_g", m_border_g);
    m_border_b = parsedFile.GetFloat(shapecodePrefix + "border_b", m_border_b);
    m_border_a = parsedFile.GetFloat(shapecodePrefix + "border_a", m_border_a);

    // projectM addition: texture name to use for rendering the shape
    m_image = parsedFile.GetString(shapecodePrefix + "image", "");
}

void CustomShape::CompileCodeAndRunInitExpressions(std::vector<std::string>& warnings)
{
    m_perFrameContext.LoadStateVariables(m_presetState, *this, 0);
    bool initCompiled{true};
    try
    {
        m_perFrameContext.EvaluateInitCode(m_presetState.customShapeInitCode[m_index], *this);
    }
    catch (const MilkdropCompileException& error)
    {
        initCompiled = false;
        warnings.emplace_back(error.what());
    }

    // MilkDrop starts the t variables at zero if the init code fails.
    for (int t = 0; t < TVarCount; t++)
    {
        m_tValuesAfterInitCode[t] = initCompiled ? *m_perFrameContext.t_vars[t] : 0.0;
    }

    try
    {
        m_perFrameContext.CompilePerFrameCode(m_presetState.customShapePerFrameCode[m_index], *this);
    }
    catch (const MilkdropCompileException& error)
    {
        warnings.emplace_back(error.what());
    }
}

void CustomShape::Draw(GeometryTargets* targets)
{
    static constexpr float pi = 3.141592653589793f;

    if (!m_enabled)
    {
        return;
    }

    m_geometryTargets = targets;
    // The instances are evaluated in order and their geometry collected in batches (m_vertices);
    // each batch is uploaded once and drawn in instance order (FlushBatch). The result is the same
    // as drawing every instance on its own, but without per-instance buffer uploads and state
    // changes, each of which made the GPU driver revalidate its state at the next draw call.
    glEnable(GL_BLEND);
    glLineWidth(1);
#ifndef USE_GLES
    glEnable(GL_LINE_SMOOTH);
#endif

    auto shader = m_presetState.untexturedShader.lock();
    shader->Bind();
    shader->SetUniformMat4x4("vertex_transformation", PresetState::orthogonalProjection);
    shader->SetUniformFloat("vertex_point_size", 1.0f);
    m_texturedShaderReady = false;
    m_imageLookedUp = false;
    m_lastBlendDestination = 0;

    const float lineScale = LineScale(m_presetState.renderContext.viewportSizeX, m_presetState.renderContext.viewportSizeY,
                                      m_presetState.renderContext.lineReferenceWidth, m_presetState.renderContext.lineReferenceHeight);
    m_quadBorders = lineScale > 0.0f && m_presetState.lineRenderer.Usable();
    m_borderStyle = LineStyleFor(LineKind::ShapeBorder, m_thickOutline, lineScale,
                                 m_presetState.renderContext.viewportSizeX, m_presetState.renderContext.viewportSizeY);
    m_lineBatch.Clear();

    // Need to use +/- 1.0 here instead of 2.0 used in Milkdrop to achieve the same rendering result.
    const auto incrementX = 1.0f / static_cast<float>(m_presetState.renderContext.viewportSizeX);
    const auto incrementY = 1.0f / static_cast<float>(m_presetState.renderContext.viewportSizeY);

    for (int instance = 0; instance < m_instances; instance++)
    {
        m_perFrameContext.LoadStateVariables(m_presetState, *this, instance);
        m_perFrameContext.ExecutePerFrameCode();

        int sides = static_cast<int>(*m_perFrameContext.sides);
        if (sides < 3)
        {
            sides = 3;
        }
        if (sides > 100)
        {
            sides = 100;
        }

        InstanceDraw draw;
        draw.additive = static_cast<int>(*m_perFrameContext.additive) != 0;
        draw.textured = static_cast<int>(*m_perFrameContext.textured) != 0;
        draw.sides = sides;
        // GL lines: a thick outline is drawn four times with slight offsets. Quad lines: one strip per
        // outline; LineRenderer draws m_borderStyle's passes (four offset passes when thick).
        draw.borderIterations = *m_perFrameContext.border_a > 0.0001f ? (m_quadBorders ? 1 : (m_thickOutline ? 4 : 1)) : 0;

        const size_t neededVertices = static_cast<size_t>(sides + 2 + (m_quadBorders ? 0 : draw.borderIterations * sides));
        const size_t neededLinePoints = (m_quadBorders || m_geometryTargets) && draw.borderIterations > 0 ? static_cast<size_t>(sides + 3) : 0;
        if (m_vertices.size() + neededVertices > maxBatchVertices || m_lineBatch.Points().size() + neededLinePoints > maxBatchVertices)
        {
            FlushBatch();
        }

        draw.fillFirst = static_cast<GLint>(m_vertices.size());
        m_vertices.resize(m_vertices.size() + sides + 2);
        TexturedPoint* vertexData = &m_vertices[draw.fillFirst];

        vertexData[0].x = static_cast<float>(*m_perFrameContext.x * 2.0 - 1.0);
        vertexData[0].y = static_cast<float>(*m_perFrameContext.y * -2.0 + 1.0);

        vertexData[0].u = 0.5f;
        vertexData[0].v = 0.5f;

        // x = f*255.0 & 0xFF = (f*255.0) % 256
        // f' = x/255.0 = f % (256/255)
        // 1.0 -> 255 (0xFF)
        // 2.0 -> 254 (0xFE)
        // -1.0 -> 0x01

        vertexData[0].r = Renderer::Color::Modulo(static_cast<float>(*m_perFrameContext.r));
        vertexData[0].g = Renderer::Color::Modulo(static_cast<float>(*m_perFrameContext.g));
        vertexData[0].b = Renderer::Color::Modulo(static_cast<float>(*m_perFrameContext.b));
        vertexData[0].a = Renderer::Color::Modulo(static_cast<float>(*m_perFrameContext.a));

        vertexData[1].r = Renderer::Color::Modulo(static_cast<float>(*m_perFrameContext.r2));
        vertexData[1].g = Renderer::Color::Modulo(static_cast<float>(*m_perFrameContext.g2));
        vertexData[1].b = Renderer::Color::Modulo(static_cast<float>(*m_perFrameContext.b2));
        vertexData[1].a = Renderer::Color::Modulo(static_cast<float>(*m_perFrameContext.a2));

        for (int i = 1; i < sides + 1; i++)
        {
            const float cornerProgress = static_cast<float>(i - 1) / static_cast<float>(sides);
            const float angle = cornerProgress * pi * 2.0f + static_cast<float>(*m_perFrameContext.ang) + pi * 0.25f;

            // Todo: There's still some issue with aspect ratio here, as everything gets squashed horizontally if Y > x.
            vertexData[i].x = vertexData[0].x + static_cast<float>(*m_perFrameContext.rad) * cosf(angle) * m_presetState.renderContext.aspectY;
            vertexData[i].y = vertexData[0].y + static_cast<float>(*m_perFrameContext.rad) * sinf(angle);

            vertexData[i].r = vertexData[1].r;
            vertexData[i].g = vertexData[1].g;
            vertexData[i].b = vertexData[1].b;
            vertexData[i].a = vertexData[1].a;
        }

        if (draw.textured)
        {
            // Textured shape, either main texture or texture from "image" key
            if (!m_imageLookedUp)
            {
                m_imageLookedUp = true;
                m_imageTexture = m_image.empty() ? Renderer::TextureSamplerDescriptor()
                                                 : m_presetState.renderContext.textureManager->GetTexture(m_image);
            }
            const auto textureAspectY = m_imageTexture.Empty() ? m_presetState.renderContext.aspectY : 1.0f;

            for (int i = 1; i < sides + 1; i++)
            {
                const float cornerProgress = static_cast<float>(i - 1) / static_cast<float>(sides);
                const float angle = cornerProgress * pi * 2.0f + static_cast<float>(*m_perFrameContext.tex_ang) + pi * 0.25f;

                vertexData[i].u = 0.5f + 0.5f * cosf(angle) / static_cast<float>(*m_perFrameContext.tex_zoom) * textureAspectY;
                vertexData[i].v = 1.0f - (0.5f - 0.5f * sinf(angle) / static_cast<float>(*m_perFrameContext.tex_zoom)); // Vertical flip required!
            }
        }

        // Duplicate last vertex.
        vertexData[sides + 1] = vertexData[1];

        if (draw.borderIterations > 0 && !m_quadBorders)
        {
            // The outline as vertices in the border color (drawn with the untextured shader), offset
            // like MilkDrop's thick outline: top left, top right, bottom right, bottom left.
            TexturedPoint border;
            border.r = static_cast<float>(*m_perFrameContext.border_r);
            border.g = static_cast<float>(*m_perFrameContext.border_g);
            border.b = static_cast<float>(*m_perFrameContext.border_b);
            border.a = static_cast<float>(*m_perFrameContext.border_a);
            draw.borderFirst = static_cast<GLint>(m_vertices.size());
            static constexpr float offsetX[4] = {0.0f, 1.0f, 1.0f, 0.0f};
            static constexpr float offsetY[4] = {0.0f, 0.0f, 1.0f, 1.0f};
            for (int iteration = 0; iteration < draw.borderIterations; iteration++)
            {
                for (int i = 0; i < sides; i++)
                {
                    // vertexData may move when m_vertices grows: index it through the vector.
                    const TexturedPoint& corner = m_vertices[draw.fillFirst + i + 1];
                    border.x = corner.x + offsetX[iteration] * incrementX;
                    border.y = corner.y + offsetY[iteration] * incrementY;
                    m_vertices.push_back(border);
                }
            }
        }

        if (draw.borderIterations > 0 && (m_quadBorders || m_geometryTargets))
        {
            m_borderPoints.resize(static_cast<size_t>(sides));
            for (int i = 0; i < sides; i++)
            {
                const TexturedPoint& corner = m_vertices[draw.fillFirst + i + 1];
                auto& point = m_borderPoints[static_cast<size_t>(i)];
                point.x = corner.x;
                point.y = corner.y;
                point.r = static_cast<float>(*m_perFrameContext.border_r);
                point.g = static_cast<float>(*m_perFrameContext.border_g);
                point.b = static_cast<float>(*m_perFrameContext.border_b);
                point.a = static_cast<float>(*m_perFrameContext.border_a);
            }
            draw.borderStrip = m_lineBatch.Append(m_borderPoints.data(), m_borderPoints.size(), true);
        }

        m_draws.push_back(draw);
    }

    FlushBatch();
    m_geometryTargets=nullptr;

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);

#ifndef USE_GLES
    glDisable(GL_LINE_SMOOTH);
#endif
}

void CustomShape::FlushBatch()
{
    if (m_draws.empty())
    {
        return;
    }

    // One upload per batch; orphaning the buffer lets the GPU keep reading the previous batch.
    glBindBuffer(GL_ARRAY_BUFFER, m_vboIdUntextured);
    glBufferData(GL_ARRAY_BUFFER, static_cast<GLsizeiptr>(sizeof(TexturedPoint) * maxBatchVertices), nullptr, GL_STREAM_DRAW);
    glBufferSubData(GL_ARRAY_BUFFER, 0, static_cast<GLsizeiptr>(sizeof(TexturedPoint) * m_vertices.size()), m_vertices.data());
    DrawBatch(false);
    if (m_geometryTargets) {
        m_geometryTargets->Native();
        DrawBatch(true);
        m_geometryTargets->Authored();
    }
    m_lineBatch.Clear();
    m_vertices.clear();
    m_draws.clear();
}

void CustomShape::DrawBatch(bool nativePass)
{
    if (m_geometryTargets) {
        glEnable(GL_BLEND);
        m_lastBlendDestination=0;
        m_texturedShaderReady=false;
    }
    auto untexturedShader = m_presetState.untexturedShader.lock();
    auto texturedShader = m_presetState.texturedShader.lock();
    const auto& context=m_presetState.renderContext;
    // MilkDrop 2's D3D9 viewport samples integer pixel centres. GLES/OpenGL
    // samples half-integers; move the geometry by half a destination pixel.
    // Y is flipped by orthogonalProjection and by the GL framebuffer convention.
    const auto shapeProjection = context.viewportSizeX > 0 && context.viewportSizeY > 0
        ? glm::translate(PresetState::orthogonalProjection,
                         glm::vec3(1.0f / context.viewportSizeX, 1.0f / context.viewportSizeY, 0.0f))
        : PresetState::orthogonalProjection;
    untexturedShader->Bind();
    untexturedShader->SetUniformMat4x4("vertex_transformation", shapeProjection);
    texturedShader->Bind();
    texturedShader->SetUniformMat4x4("vertex_transformation", shapeProjection);
    const float scale=LineScale(context.viewportSizeX,context.viewportSizeY,
                                context.lineReferenceWidth,context.lineReferenceHeight);
    const bool quadBorders=nativePass ? scale>0 && m_presetState.lineRenderer.Usable() : m_quadBorders;
    const auto style=nativePass ? LineStyleFor(LineKind::ShapeBorder,m_thickOutline,scale,
                                              context.viewportSizeX,context.viewportSizeY) : m_borderStyle;
    if (quadBorders && !m_lineBatch.Points().empty()) m_presetState.lineRenderer.Upload(m_lineBatch);
    m_linesBegun=false;
    for (const auto& draw : m_draws)
    {
        // Additive Drawing or Overwrite
        GLenum blendDestination = draw.additive ? GL_ONE : GL_ONE_MINUS_SRC_ALPHA;
        if (blendDestination != m_lastBlendDestination)
        {
            glBlendFunc(GL_SRC_ALPHA, blendDestination);
            m_lastBlendDestination = blendDestination;
        }

        if (draw.textured)
        {
            texturedShader->Bind();
            if (!m_texturedShaderReady)
            {
                m_texturedShaderReady = true;
                texturedShader->SetUniformMat4x4("vertex_transformation", shapeProjection);
                texturedShader->SetUniformInt("texture_sampler", 0);
            }

            if (!m_imageTexture.Empty())
            {
                m_imageTexture.Bind(0, *texturedShader);
            }
            else
            {
                // No "image" texture (or not found): the main texture.
                assert(!m_presetState.mainTexture.expired());
                m_presetState.mainTexture.lock()->Bind(0, m_mainTextureSampler);
            }

            m_texturedArray.Bind();
            if (m_geometryTargets) {
                // Filled geometry consumes per-vertex positions/colors/UV, not instanced line inputs.
                for (GLuint location=0;location<3;++location) glVertexAttribDivisor(location,0);
            }
            glDrawArrays(GL_TRIANGLE_FAN, draw.fillFirst, draw.sides + 2);

            glBindTexture(GL_TEXTURE_2D, 0);
            Renderer::Sampler::Unbind(0);
        }
        else
        {
            // Untextured (creates a color gradient: center=r/g/b/a to border=r2/b2/g2/a2)
            untexturedShader->Bind();
            m_untexturedArray.Bind();
            if (m_geometryTargets) {
                // Filled geometry consumes per-vertex positions/colors/UV, not instanced line inputs.
                for (GLuint location=0;location<3;++location) glVertexAttribDivisor(location,0);
            }
            glDrawArrays(GL_TRIANGLE_FAN, draw.fillFirst, draw.sides + 2);
        }

        if (draw.borderIterations > 0 && quadBorders)
        {
            auto& lines = m_presetState.lineRenderer;
            if (!m_linesBegun)
            {
                lines.Begin(shapeProjection, m_presetState.renderContext);
                m_linesBegun = true;
            }
            lines.Draw(draw.borderStrip, style);
        }
        else if (draw.borderIterations > 0)
        {
            untexturedShader->Bind();
            m_untexturedArray.Bind();
            if (m_geometryTargets) {
                // Filled geometry consumes per-vertex positions/colors/UV, not instanced line inputs.
                for (GLuint location=0;location<3;++location) glVertexAttribDivisor(location,0);
            }
            for (int iteration = 0; iteration < draw.borderIterations; iteration++)
            {
                if (nativePass && m_geometryTargets) {
                    static constexpr float dx[4]={0,1,1,0}, dy[4]={0,0,1,1};
                    // MilkdropPreset sets the reference to the actual rounded authored canvas.
                    const float sourceScale=std::sqrt((double(context.viewportSizeX)*context.viewportSizeY) /
                                                      (double(context.lineReferenceWidth)*context.lineReferenceHeight));
                    const auto translation=glm::vec3(dx[iteration]*(1-sourceScale)/context.viewportSizeX,
                                                     dy[iteration]*(1-sourceScale)/context.viewportSizeY,0);
                    untexturedShader->SetUniformMat4x4("vertex_transformation",
                        glm::translate(shapeProjection,translation));
                }
                glDrawArrays(GL_LINE_LOOP, draw.borderFirst + iteration * draw.sides, draw.sides);
            }
            if (nativePass) untexturedShader->SetUniformMat4x4("vertex_transformation",shapeProjection);
        }
    }

    if (m_linesBegun)
    {
        m_presetState.lineRenderer.End();
        m_linesBegun = false;
    }
    // Both shaders are shared with other geometry effects.
    untexturedShader->Bind();
    untexturedShader->SetUniformMat4x4("vertex_transformation", PresetState::orthogonalProjection);
    texturedShader->Bind();
    texturedShader->SetUniformMat4x4("vertex_transformation", PresetState::orthogonalProjection);
}

} // namespace MilkdropPreset
} // namespace libprojectM
