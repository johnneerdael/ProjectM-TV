#include "CustomWaveform.hpp"
#include "GeometryTargets.hpp"

#include "LineGeometry.hpp"
#include "LineRenderer.hpp"
#include "MilkdropPresetExceptions.hpp"
#include "PerFrameContext.hpp"
#include "PresetFileParser.hpp"

#include <Renderer/BlendMode.hpp>

#include <algorithm>
#include <cassert>
#include <cmath>

namespace libprojectM {
namespace MilkdropPreset {

static constexpr int CustomWaveformMaxSamples = std::max(Audio::WaveformSamples, Audio::SpectrumSamples);

CustomWaveform::CustomWaveform(PresetState& presetState)
    : m_presetState(presetState)
    , m_perFrameContext(presetState.globalMemory, &presetState.globalRegisters)
    , m_perPointContext(presetState.globalMemory, &presetState.globalRegisters)
    , m_mesh(Renderer::VertexBufferUsage::StreamDraw, true, false)
{
    m_perFrameContext.RegisterBuiltinVariables();
    m_perPointContext.RegisterBuiltinVariables();

    // Allocate space for max number of vertices possible, so we won't have to resize the vertex
    // buffers, which may change on each frame.
    m_mesh.SetVertexCount(std::max(Audio::SpectrumSamples, Audio::WaveformSamples) * 2 + 2);
}

void CustomWaveform::Initialize(PresetFileParser& parsedFile, int index)
{
    std::string const wavecodePrefix = "wavecode_" + std::to_string(index) + "_";
    std::string const wavePrefix = "wave_" + std::to_string(index) + "_";

    m_index = index;
    m_enabled = parsedFile.GetBool(wavecodePrefix + "enabled", m_enabled);
    m_samples = parsedFile.GetInt(wavecodePrefix + "samples", m_samples);
    m_sep = parsedFile.GetInt(wavecodePrefix + "sep", m_sep);
    m_spectrum = parsedFile.GetBool(wavecodePrefix + "bSpectrum", m_spectrum);
    m_useDots = parsedFile.GetBool(wavecodePrefix + "bUseDots", m_useDots);
    m_drawThick = parsedFile.GetBool(wavecodePrefix + "bDrawThick", m_drawThick);
    m_additive = parsedFile.GetBool(wavecodePrefix + "bAdditive", m_additive);
    m_scaling = parsedFile.GetFloat(wavecodePrefix + "scaling", m_scaling);
    m_smoothing = parsedFile.GetFloat(wavecodePrefix + "smoothing", m_smoothing);
    m_r = parsedFile.GetFloat(wavecodePrefix + "r", m_r);
    m_g = parsedFile.GetFloat(wavecodePrefix + "g", m_g);
    m_b = parsedFile.GetFloat(wavecodePrefix + "b", m_b);
    m_a = parsedFile.GetFloat(wavecodePrefix + "a", m_a);

    m_mesh.SetRenderPrimitiveType(m_useDots ? Renderer::Mesh::PrimitiveType::Points : Renderer::Mesh::PrimitiveType::LineStrip);
}

void CustomWaveform::CompileCodeAndRunInitExpressions(const PerFrameContext& presetPerFrameContext, std::vector<std::string>& warnings)
{
    m_perFrameContext.LoadStateVariables(m_presetState, presetPerFrameContext, *this);
    bool initCompiled{true};
    try
    {
        m_perFrameContext.EvaluateInitCode(m_presetState.customWaveInitCode[m_index], *this);
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
        m_perFrameContext.CompilePerFrameCode(m_presetState.customWavePerFrameCode[m_index], *this);
    }
    catch (const MilkdropCompileException& error)
    {
        warnings.emplace_back(error.what());
    }
    try
    {
        m_perPointContext.CompilePerPointCode(m_presetState.customWavePerPointCode[m_index], *this);
    }
    catch (const MilkdropCompileException& error)
    {
        warnings.emplace_back(error.what());
    }
}

void CustomWaveform::Draw(const PerFrameContext& presetPerFrameContext, GeometryTargets* targets)
{
    static_assert(Audio::WaveformSamples <= WaveformMaxPoints, "WaveformMaxPoints is larger than WaveformSamples");
    static_assert(Audio::SpectrumSamples <= WaveformMaxPoints, "WaveformMaxPoints is larger than SpectrumSamples");

    if (!m_enabled)
    {
        return;
    }

    int const maxInputSampleCount{m_spectrum ? Audio::SpectrumSamples : Audio::WaveformSamples};

    // Initialize and execute per-frame code
    LoadPerFrameEvaluationVariables(presetPerFrameContext);
    m_perFrameContext.ExecutePerFrameCode();

    // Copy Q and T vars to per-point context
    InitPerPointEvaluationVariables();

    const int sampleCount = std::min(CustomWaveformMaxSamples, std::max(0, static_cast<int>(*m_perFrameContext.samples)));
    const int separation = std::min(sampleCount - 1, std::max(0, m_sep));

    // If there aren't enough samples to draw a single line or dot, skip drawing the waveform.
    if ((m_useDots && sampleCount < 1) || sampleCount < 2)
    {
        return;
    }

    const auto* pcmL = m_spectrum
                           ? m_presetState.audioData.spectrumLeft.data()
                           : m_presetState.audioData.waveformLeft.data();
    const auto* pcmR = m_spectrum
                           ? m_presetState.audioData.spectrumRight.data()
                           : m_presetState.audioData.waveformRight.data();

    const float mult = m_scaling * m_presetState.waveScale * (m_spectrum ? 0.15f : 0.004f);

    // PCM data smoothing
    float scaling{1.0f};
    if (m_spectrum)
    {
        // In spectrum mode, "separation" is the amount of spectrum samples to cut off of the right
        // side of the frequency bands. The remaining samples will be scaled to the number of requested samples.
        scaling = static_cast<float>(maxInputSampleCount - separation) / static_cast<float>(sampleCount);
    }
    else if (sampleCount > maxInputSampleCount)
    {
        // In oscilloscope mode, we ignore "separation", but use the scaling factor
        // to eventually scale up the 480 waveform samples to a larger, requested amount.
        scaling = static_cast<float>(maxInputSampleCount) / static_cast<float>(sampleCount);
    }
    const float mix1 = std::pow(m_smoothing * 0.98f, 0.5f);
    const float mix2 = 1.0f - mix1;

    // MilkDrop centers finite oscilloscope windows and shifts the channels
    // in opposite directions. Retain upstream resampling/bounds safety for
    // oversized requests and separations outside the original valid window.
    int offsetL = 0;
    int offsetR = 0;
    if (!m_spectrum && sampleCount <= maxInputSampleCount)
    {
        const int center = (maxInputSampleCount - sampleCount) / 2;
        const int left = center - m_sep / 2;
        const int right = center + m_sep / 2;
        const int maxOffset = maxInputSampleCount - sampleCount;
        if (left >= 0 && right >= 0 && left <= maxOffset && right <= maxOffset)
        {
            offsetL = left;
            offsetR = right;
        }
    }

    std::array<float, CustomWaveformMaxSamples> sampleDataL{};
    std::array<float, CustomWaveformMaxSamples> sampleDataR{};

    sampleDataL[0] = pcmL[offsetL];
    sampleDataR[0] = pcmR[offsetR];

    // Smooth forward
    for (int sample = 1; sample < sampleCount; sample++)
    {
        const int pcmSample = static_cast<int>(static_cast<float>(sample) * scaling);
        assert(pcmSample >= 0);
        assert(pcmSample < maxInputSampleCount);
        sampleDataL[sample] = pcmL[pcmSample + offsetL] * mix2 + sampleDataL[sample - 1] * mix1;
        sampleDataR[sample] = pcmR[pcmSample + offsetR] * mix2 + sampleDataR[sample - 1] * mix1;
    }

    // Smooth backwards (this fixes the asymmetry of the beginning & end)
    for (int sample = sampleCount - 2; sample >= 0; sample--)
    {
        sampleDataL[sample] = sampleDataL[sample] * mix2 + sampleDataL[sample + 1] * mix1;
        sampleDataR[sample] = sampleDataR[sample] * mix2 + sampleDataR[sample + 1] * mix1;
    }

    // Scale waveform to final size
    for (int sample = 0; sample < sampleCount; sample++)
    {
        sampleDataL[sample] *= mult;
        sampleDataR[sample] *= mult;
    }

    std::vector<Renderer::Point> points(sampleCount);
    std::vector<Renderer::Color> colors(sampleCount);

    float const sampleMultiplicator = sampleCount > 1 ? 1.0f / static_cast<float>(sampleCount - 1) : 0.0f;
    for (int sample = 0; sample < sampleCount; sample++)
    {
        float const sampleIndex = static_cast<float>(sample) * sampleMultiplicator;
        LoadPerPointEvaluationVariables(sampleIndex, sampleDataL[sample], sampleDataR[sample]);

        m_perPointContext.ExecutePerPointCode();

        points[sample] = Renderer::Point(static_cast<float>((*m_perPointContext.x * 2.0 - 1.0) * m_presetState.renderContext.invAspectX),
                                         static_cast<float>((*m_perPointContext.y * -2.0 + 1.0) * m_presetState.renderContext.invAspectY));

        colors[sample] = Renderer::Color::Modulo(Renderer::Color(static_cast<float>(*m_perPointContext.r),
                                                                 static_cast<float>(*m_perPointContext.g),
                                                                 static_cast<float>(*m_perPointContext.b),
                                                                 static_cast<float>(*m_perPointContext.a)));
    }

    SmoothWave(points, colors);

    const auto count = m_mesh.Indices().Size();
    const auto& smoothedPoints = m_mesh.Vertices().Get();
    const auto& smoothedColors = m_mesh.Colors().Get();
    std::vector<Renderer::Point> preparedPoints(smoothedPoints.begin(), smoothedPoints.begin() + count);
    std::vector<Renderer::Color> preparedColors(smoothedColors.begin(), smoothedColors.begin() + count);
    if (targets)
    {
        DrawPrepared(preparedPoints, preparedColors);
        targets->Native();
        DrawPrepared(std::move(preparedPoints), std::move(preparedColors));
        targets->Authored();
    }
    else
    {
        DrawPrepared(std::move(preparedPoints), std::move(preparedColors));
    }
}

void CustomWaveform::DrawPrepared(std::vector<Renderer::Point> points, std::vector<Renderer::Color> colors)
{
#ifndef USE_GLES
    glDisable(GL_LINE_SMOOTH);
#endif
    const float lineScale = LineScale(m_presetState.renderContext.viewportSizeX, m_presetState.renderContext.viewportSizeY,
                                      m_presetState.renderContext.lineReferenceWidth, m_presetState.renderContext.lineReferenceHeight);
    const bool scaledDots = lineScale > 0.0f && m_useDots;
    const auto dot = DotStyleFor(LineKind::CustomWave, m_drawThick, lineScale);
    if (scaledDots && dot.alphaScale < 1.0f)
    {
        for (auto& color : colors)
        {
            color.SetA(color.A() * dot.alphaScale);
        }
    }

    if (lineScale > 0.0f && !m_useDots && m_presetState.lineRenderer.Usable())
    {
        m_lineBatch.Clear();
        std::vector<ColoredPoint> linePoints(points.size());
        for (size_t point = 0; point < points.size(); ++point)
        {
            linePoints[point] = {points[point].X(), points[point].Y(), colors[point].R(),
                                 colors[point].G(), colors[point].B(), colors[point].A()};
        }
        const auto strip = m_lineBatch.Append(linePoints.data(), linePoints.size(), false);
        if (strip.segments == 0)
        {
            return;
        }

        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, m_additive ? GL_ONE : GL_ONE_MINUS_SRC_ALPHA);

        auto& lines = m_presetState.lineRenderer;
        lines.Upload(m_lineBatch);
        lines.Begin(PresetState::orthogonalProjection, m_presetState.renderContext);
        lines.Draw(strip, LineStyleFor(LineKind::CustomWave, m_drawThick, lineScale,
                                       m_presetState.renderContext.viewportSizeX, m_presetState.renderContext.viewportSizeY));
        lines.End();

        glDisable(GL_BLEND);
        return;
    }

    glLineWidth(1);

    // Additive wave drawing (vice overwrite)
    if (m_additive)
    {
        Renderer::BlendMode::Set(true, Renderer::BlendMode::Function::SourceAlpha, Renderer::BlendMode::Function::One);
    }
    else
    {
        Renderer::BlendMode::Set(true, Renderer::BlendMode::Function::SourceAlpha, Renderer::BlendMode::Function::OneMinusSourceAlpha);
    }

    auto shader = m_presetState.untexturedShader.lock();
    shader->Bind();
    shader->SetUniformMat4x4("vertex_transformation", PresetState::orthogonalProjection);
    shader->SetUniformFloat("vertex_point_size", scaledDots ? dot.size : (m_drawThick ? 2.0f : 1.0f));
    const ScopedProgramPointSize programPointSize(scaledDots);

    auto iterations = (m_drawThick && !m_useDots) ? 4 : 1;

    // Need to use +/- 1.0 here instead of 2.0 used in Milkdrop to achieve the same rendering result.
    auto incrementX = 1.0f / static_cast<float>(m_presetState.renderContext.viewportSizeX);
    auto incrementY = 1.0f / static_cast<float>(m_presetState.renderContext.viewportSizeX);

    const size_t smoothedVertexCount = points.size();
    // Each target starts from the same unmodified geometry and color alpha.
    // Keep the upstream maximum-sized buffers: smoothing may need more points next frame.
    std::copy(points.begin(), points.end(), m_mesh.Vertices().Get().begin());
    std::copy(colors.begin(), colors.end(), m_mesh.Colors().Get().begin());
    m_mesh.Indices().Resize(smoothedVertexCount);
    m_mesh.Indices().MakeContinuous();
    auto& vertices = m_mesh.Vertices();

    // If thick outline is used, draw the shape four times with slight offsets
    // (top left, top right, bottom right, bottom left).
    for (auto iteration = 0; iteration < iterations; iteration++)
    {
        switch (iteration)
        {
            case 0:
            default:
                break;

            case 1:
                for (size_t j = 0; j < smoothedVertexCount; j++)
                {
                    vertices[j].SetX(vertices[j].X() + incrementX);
                }
                break;

            case 2:
                for (size_t j = 0; j < smoothedVertexCount; j++)
                {
                    vertices[j].SetY(vertices[j].Y() + incrementY);
                }
                break;

            case 3:
                for (size_t j = 0; j < smoothedVertexCount; j++)
                {
                    vertices[j].SetX(vertices[j].X() - incrementX);
                }
                break;
        }

        m_mesh.Update();
        m_mesh.Draw();
    }

    m_mesh.Unbind();
    Renderer::Shader::Unbind();
    Renderer::BlendMode::SetBlendActive(false);
}

void CustomWaveform::LoadPerFrameEvaluationVariables(const PerFrameContext& presetPerFrameContext)
{
    m_perFrameContext.LoadStateVariables(m_presetState, presetPerFrameContext, *this);
    m_perPointContext.LoadReadOnlyStateVariables(m_perFrameContext);
}

void CustomWaveform::InitPerPointEvaluationVariables()
{
    for (int q = 0; q < QVarCount; q++)
    {
        *m_perPointContext.q_vars[q] = *m_perFrameContext.q_vars[q];
    }
    for (int t = 0; t < TVarCount; t++)
    {
        *m_perPointContext.t_vars[t] = *m_perFrameContext.t_vars[t];
    }
}

void CustomWaveform::LoadPerPointEvaluationVariables(float sample, float value1, float value2)
{
    *m_perPointContext.sample = static_cast<double>(sample);
    *m_perPointContext.value1 = static_cast<double>(value1);
    *m_perPointContext.value2 = static_cast<double>(value2);
    *m_perPointContext.x = static_cast<double>(0.5f + value1);
    *m_perPointContext.y = static_cast<double>(0.5f + value2);
    *m_perPointContext.r = *m_perFrameContext.r;
    *m_perPointContext.g = *m_perFrameContext.g;
    *m_perPointContext.b = *m_perFrameContext.b;
    *m_perPointContext.a = *m_perFrameContext.a;
}

void CustomWaveform::SmoothWave(const std::vector<Renderer::Point>& points, const std::vector<Renderer::Color>& colors)
{
    constexpr float c1{-0.15f};
    constexpr float c2{1.15f};
    constexpr float c3{1.15f};
    constexpr float c4{-0.15f};
    constexpr float inverseSum{1.0f / (c1 + c2 + c3 + c4)};

    size_t outputIndex = 0;
    size_t iBelow = 0;
    size_t iAbove2 = 1;

    size_t vertexCount = points.size();

    auto& outVertices = m_mesh.Vertices();
    auto& outColors = m_mesh.Colors();

    for (size_t inputIndex = 0; inputIndex < vertexCount - 1; inputIndex++)
    {
        size_t const iAbove = iAbove2;
        iAbove2 = std::min(vertexCount - 1, inputIndex + 2);
        outVertices[outputIndex] = points[inputIndex];
        outColors[outputIndex] = colors[inputIndex];
        outColors[outputIndex + 1] = colors[inputIndex];
        auto& smoothedPoint = outVertices[outputIndex + 1];
        smoothedPoint = points[inputIndex];
        smoothedPoint.SetX((c1 * points[iBelow].X() + c2 * points[inputIndex].X() + c3 * points[iAbove].X() + c4 * points[iAbove2].X()) * inverseSum);
        smoothedPoint.SetY((c1 * points[iBelow].Y() + c2 * points[inputIndex].Y() + c3 * points[iAbove].Y() + c4 * points[iAbove2].Y()) * inverseSum);
        iBelow = inputIndex;
        outputIndex += 2;
    }

    outVertices[outputIndex] = points[vertexCount - 1];
    outColors[outputIndex] = colors[vertexCount - 1];

    auto& indices = m_mesh.Indices();
    indices.Resize(outputIndex + 1);
    indices.MakeContinuous();
}

} // namespace MilkdropPreset
} // namespace libprojectM
