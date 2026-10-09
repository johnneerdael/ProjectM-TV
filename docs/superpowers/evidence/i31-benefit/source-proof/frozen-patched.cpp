#include "VideoEcho.hpp"

#include <Renderer/BlendMode.hpp>

#include <cmath>
#include <limits>

namespace libprojectM {
namespace MilkdropPreset {

VideoEcho::VideoEcho(const PresetState& presetState)
    : m_presetState(presetState)
    , m_echoMesh(Renderer::VertexBufferUsage::DynamicDraw, true, true)
{
    m_echoMesh.SetRenderPrimitiveType(Renderer::Mesh::PrimitiveType::TriangleStrip);
    m_echoMesh.SetVertexCount(4);
}

void VideoEcho::Draw(const PerFrameContext& perFrameContext)
{
    float const aspect = m_presetState.renderContext.viewportSizeX / static_cast<float>(m_presetState.renderContext.viewportSizeY * m_presetState.renderContext.invAspectY);
    float aspectMultX = 1.0f;
    float aspectMultY = 1.0f;

    if (aspect > 1)
    {
        aspectMultY = aspect;
    }
    else
    {
        aspectMultX = 1.0f / aspect;
    }

    float const fOnePlusInvWidth = 1.0f + 1.0f / static_cast<float>(m_presetState.renderContext.viewportSizeX);
    float const fOnePlusInvHeight = 1.0f + 1.0f / static_cast<float>(m_presetState.renderContext.viewportSizeY);
    m_echoMesh.Vertices().Set({{-fOnePlusInvWidth * aspectMultX, -fOnePlusInvHeight * aspectMultY},
                               {fOnePlusInvWidth * aspectMultX, -fOnePlusInvHeight * aspectMultY},
                               {-fOnePlusInvWidth * aspectMultX, fOnePlusInvHeight * aspectMultY},
                               {fOnePlusInvWidth * aspectMultX, fOnePlusInvHeight * aspectMultY}});

    // MilkDrop 2.25c leaves legacy output untinted when fShader is disabled.
    const float shaderAmount = m_presetState.shader;
    auto& colors = m_echoMesh.Colors();
    for (int i = 0; i < 4; i++)
    {
        auto const indexFloat = static_cast<float>(i);
        m_shade[i][0] = 0.6f + 0.3f * sinf(m_presetState.renderContext.time * 30.0f * 0.0143f + 3 + indexFloat * 21 + m_presetState.hueRandomOffsets[3]);
        m_shade[i][1] = 0.6f + 0.3f * sinf(m_presetState.renderContext.time * 30.0f * 0.0107f + 1 + indexFloat * 13 + m_presetState.hueRandomOffsets[1]);
        m_shade[i][2] = 0.6f + 0.3f * sinf(m_presetState.renderContext.time * 30.0f * 0.0129f + 6 + indexFloat * 9 + m_presetState.hueRandomOffsets[2]);

        float const max = std::max(m_shade[i][0], std::max(m_shade[i][1], m_shade[i][2]));

        for (int k = 0; k < 3; k++)
        {
            m_shade[i][k] /= max;
            m_shade[i][k] = 0.5f + 0.5f * m_shade[i][k];
            m_shade[i][k] = shaderAmount > 0.001f
                                ? m_shade[i][k] * shaderAmount + 1.0f * (1.0f - shaderAmount)
                                : 1.0f;
        }

        colors[i] = {m_shade[i][0],
                     m_shade[i][1],
                     m_shade[i][2],
                     1.0f};
    }

    auto shader = m_presetState.texturedShader.lock();
    shader->Bind();
    shader->SetUniformMat4x4("vertex_transformation", PresetState::orthogonalProjection);
    shader->SetUniformInt("texture_sampler", 0);

    auto mainTexture = m_presetState.mainTexture.lock();
    if (mainTexture)
    {
        mainTexture->Bind(0);
        m_sampler.Bind(0);
    }


    // The first draw covers the whole viewport (aspectMult >= 1) without depending on the target
    // (GL_ONE/GL_ZERO or no blending), so tile-based GPUs need not load the old contents.
    {
        const GLenum attachment = m_presetState.compositeToDefaultFramebuffer ? GL_COLOR : GL_COLOR_ATTACHMENT0;
        glInvalidateFramebuffer(GL_DRAW_FRAMEBUFFER, 1, &attachment);
    }

    if (static_cast<float>(*perFrameContext.echo_alpha) > 0.001f)
    {
        DrawVideoEcho(perFrameContext);
    }
    else
    {
        DrawGammaAdjustment(perFrameContext);
    }

    Renderer::BlendMode::SetBlendActive(false);
    Renderer::Mesh::Unbind();
    Renderer::Shader::Unbind();

    if (mainTexture)
    {
        mainTexture->Unbind(0);
        Renderer::Sampler::Unbind(0);
    }
}

void VideoEcho::DrawVideoEcho(const PerFrameContext& perFrameContext)
{
    auto const videoEchoZoom = static_cast<float>(*perFrameContext.echo_zoom);
    auto const videoEchoAlpha = static_cast<float>(*perFrameContext.echo_alpha);
    const auto orientationValue = std::trunc(*perFrameContext.echo_orient);
    if (!std::isfinite(orientationValue) || orientationValue < std::numeric_limits<int>::min() ||
        orientationValue > std::numeric_limits<int>::max())
    {
        // Undefined float-to-int input: omit echo, retaining gamma-only output.
        DrawGammaAdjustment(perFrameContext);
        return;
    }
    auto const videoEchoOrientation = static_cast<int>(orientationValue) % 4;
    auto const gammaAdj = static_cast<float>(*perFrameContext.gamma);

    Renderer::BlendMode::Set(true, Renderer::BlendMode::Function::One, Renderer::BlendMode::Function::Zero);

    for (int pass = 0; pass < 2; pass++)
    {
        float const zoom = (pass == 0) ? 1.0f : videoEchoZoom;

        float const tempLow = 0.5f - 0.5f / zoom;
        float const tempHigh = 0.5f + 0.5f / zoom;

        m_echoMesh.UVs().Set({{tempLow, tempLow},
                              {tempHigh, tempLow},
                              {tempLow, tempHigh},
                              {tempHigh, tempHigh}});

        // Flipping
        if (pass == 1)
        {
            for (int vertex = 0; vertex < 4; vertex++)
            {
                if (videoEchoOrientation % 2 != 0)
                {
                    m_echoMesh.UVs()[vertex].SetU(1.0f - m_echoMesh.UVs()[vertex].U());
                }
                if (videoEchoOrientation >= 2)
                {
                    m_echoMesh.UVs()[vertex].SetV(1.0f - m_echoMesh.UVs()[vertex].V());
                }
            }
        }

        float const mix = (pass == 1) ? videoEchoAlpha : 1.0f - videoEchoAlpha;
        for (int vertex = 0; vertex < 4; vertex++)
        {
            m_echoMesh.Colors()[vertex] = {
                mix * m_shade[vertex][0],
                mix * m_shade[vertex][1],
                mix * m_shade[vertex][2],
                1.0f};
        }

        m_echoMesh.Update();
        m_echoMesh.Draw();

        if (pass == 0)
        {
            Renderer::BlendMode::SetBlendFunction(Renderer::BlendMode::Function::One, Renderer::BlendMode::Function::One);
        }

        if (gammaAdj > 0.001f)
        {
            int const redrawCount = static_cast<int>(gammaAdj - 0.0001f);

            for (int redraw = 0; redraw < redrawCount; redraw++)
            {
                float gamma;
                if (redraw == redrawCount - 1)
                {
                    gamma = gammaAdj - static_cast<float>(static_cast<int>(gammaAdj - 0.0001f));
                }
                else
                {
                    gamma = 1.0f;
                }

                for (int vertex = 0; vertex < 4; vertex++)
                {
                    m_echoMesh.Colors()[vertex] = {
                        gamma * mix * m_shade[vertex][0],
                        gamma * mix * m_shade[vertex][1],
                        gamma * mix * m_shade[vertex][2],
                        1.0f};
                }

                m_echoMesh.Colors().Update();
                m_echoMesh.Draw();
            }
        }
    }
}

void VideoEcho::DrawGammaAdjustment(const PerFrameContext& perFrameContext)
{
    m_echoMesh.UVs().Set({{0.0f, 0.0f},
                          {1.0f, 0.0f},
                          {0.0f, 1.0f},
                          {1.0f, 1.0f}});

    Renderer::BlendMode::Set(true, Renderer::BlendMode::Function::One, Renderer::BlendMode::Function::Zero);

    auto const gammaAdj = static_cast<float>(*perFrameContext.gamma);
    // MilkDrop's gamma-only path has a distinct epsilon from echo redraws.
    int const redrawCount = static_cast<int>(gammaAdj - 0.001f) + 1;

    for (int redraw = 0; redraw < redrawCount; redraw++)
    {
        float gamma;
        if (redraw == redrawCount - 1)
        {
            gamma = gammaAdj - static_cast<float>(redraw);
        }
        else
        {
            gamma = 1.0f;
        }

        for (int vertex = 0; vertex < 4; vertex++)
        {
            m_echoMesh.Colors()[vertex] = {
                gamma * m_shade[vertex][0],
                gamma * m_shade[vertex][1],
                gamma * m_shade[vertex][2],
                1.0f};
        }

        m_echoMesh.Update();
        m_echoMesh.Draw();

        if (redraw == 0)
        {
            Renderer::BlendMode::Set(true, Renderer::BlendMode::Function::One, Renderer::BlendMode::Function::One);
        }
    }
}

} // namespace MilkdropPreset
} // namespace libprojectM
