/**
 * projectM -- Milkdrop-esque visualisation SDK
 * Copyright (C)2003-2004 projectM Team
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 * See 'LICENSE.txt' included within this release
 *
 */

#include "MilkdropPreset.hpp"

#include "Factory.hpp"
#include "LineGeometry.hpp"
#include "MilkdropPresetExceptions.hpp"
#include "PresetFileParser.hpp"

#include <algorithm>
#include <cctype>

#ifdef MILKDROP_PRESET_DEBUG
#include <iostream>
#endif

namespace libprojectM {
namespace MilkdropPreset {

MilkdropPreset::MilkdropPreset(const std::string& absoluteFilePath)
    : m_absoluteFilePath(absoluteFilePath)
    , m_perFrameContext(m_state.globalMemory, &m_state.globalRegisters)
    , m_perPixelContext(m_state.globalMemory, &m_state.globalRegisters)
    , m_motionVectors(m_state)
    , m_waveform(m_state)
    , m_darkenCenter(m_state)
    , m_border(m_state)
{
    Load(absoluteFilePath);
}

MilkdropPreset::MilkdropPreset(std::istream& presetData)
    : m_perFrameContext(m_state.globalMemory, &m_state.globalRegisters)
    , m_perPixelContext(m_state.globalMemory, &m_state.globalRegisters)
    , m_motionVectors(m_state)
    , m_waveform(m_state)
    , m_darkenCenter(m_state)
    , m_border(m_state)
{
    Load(presetData);
}

void MilkdropPreset::Initialize(const Renderer::RenderContext& renderContext)
{
    assert(renderContext.textureManager);
    m_state.renderContext = renderContext;

    // Initialize variables and code now we have a proper render state.
    CompileCodeAndRunInitExpressions();

    // Update framebuffer and texture sizes if needed
    m_framebuffer.SetSize(renderContext.viewportSizeX, renderContext.viewportSizeY);
    m_motionVectorUVMap->SetSize(renderContext.viewportSizeX, renderContext.viewportSizeY);
    if (m_state.mainTexture.expired())
    {
        m_state.mainTexture = m_framebuffer.GetColorAttachmentTexture(1, 0);
    }

    m_perPixelMesh.CompileWarpShader(m_state);
    m_warpSamplesMainTexels = m_perPixelMesh.WarpSamplesMainTexels();
    m_finalComposite.CompileCompositeShader(m_state);
}

void MilkdropPreset::RenderFrame(const libprojectM::Audio::FrameAudioData& audioData, const Renderer::RenderContext& renderContext)
{
    m_state.audioData = audioData;
    m_state.renderContext = renderContext;

    // Update framebuffer and u/v texture size if needed
    if (m_framebuffer.SetSize(renderContext.viewportSizeX, renderContext.viewportSizeY))
    {
        m_motionVectorUVMap->SetSize(renderContext.viewportSizeX, renderContext.viewportSizeY);
        m_isFirstFrame = true;
        m_flipHoldsPreviousFrame = false;
        m_diffusionHoldsPreviousFrame = false;
    }

    m_state.mainTexture = m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0);

    // First evaluate per-frame code
    PerFrameUpdate();

    glViewport(0, 0, renderContext.viewportSizeX, renderContext.viewportSizeY);

    // Above the line reference size, the warp reads the previous frame through a small blur that gives
    // back the per-frame smoothing feedback presets get at the reference size (see FeedbackDiffusion.hpp).
    if (m_feedbackDiffusion.SetScale(m_diffusionAllowed ? LineScale(renderContext.viewportSizeX, renderContext.viewportSizeY,
                                           renderContext.lineReferenceWidth, renderContext.lineReferenceHeight) : 0.0f))
    {
        m_diffusionHoldsPreviousFrame = false;
    }

    m_framebuffer.Bind(m_previousFrameBuffer);
    // Motion vector field. Drawn to the previous frame texture before warping it.
    // Only do it after drawing one frame after init or resize.
    bool motionVectorsDrawn = false;
    if (!m_isFirstFrame)
    {
        motionVectorsDrawn = m_motionVectors.Draw(m_perFrameContext, m_motionVectorUVMap->Texture(), m_feedbackDiffusion.Active());
    }

    // y-flip the previous frame and assign the flipped texture as "main". The second flip of the
    // last frame already left exactly this image in the flip texture, unless motion vectors were
    // drawn onto the previous frame since, or something else replaced either texture.
    // With diffusion, the same holds for its exact and filtered copies (see FeedbackDiffusion.hpp):
    // bilinear warp reads get the filtered one, point-sampled warp reads the exact one.
    if (m_feedbackDiffusion.Active())
    {
        if (m_isFirstFrame || motionVectorsDrawn || !m_diffusionHoldsPreviousFrame)
        {
            m_feedbackDiffusion.Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), true,
                                     m_warpSamplesMainTexels);
        }
        m_state.mainTexture = m_feedbackDiffusion.Texture();
        m_state.rawMainTexture = m_feedbackDiffusion.RawTexture();
    }
    else
    {
        if (m_isFirstFrame || motionVectorsDrawn || !m_flipHoldsPreviousFrame)
        {
            m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), nullptr, true, false);
        }
        m_state.mainTexture = m_flipTexture.Texture();
        m_state.rawMainTexture.reset();
    }
    m_flipHoldsPreviousFrame = false;
    m_diffusionHoldsPreviousFrame = false;

    // Update blur textures. They are made from the previous frame, which nothing changes from
    // here on, so this can happen before the warp: the warp and everything drawn on top of it
    // then go to the current framebuffer in one render pass. Not if the warp shader reads the
    // blur textures: it gets last frame's, as in projectM, so they are updated after the warp.
    auto const updateBlur = [this]() {
        const auto warpedImage = m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0);
        assert(warpedImage.get());
        m_state.blurTexture.Update(*warpedImage, m_perFrameContext,
                                   LineScale(m_state.renderContext.viewportSizeX, m_state.renderContext.viewportSizeY,
                                             m_state.renderContext.lineReferenceWidth, m_state.renderContext.lineReferenceHeight));
    };
    if (!m_warpSamplesBlur)
    {
        updateBlur();
    }

    // We now draw to the current framebuffer.
    m_framebuffer.Bind(m_currentFrameBuffer);

    // The u/v map is only read by the next frame's motion vectors, so it is written only while the
    // preset shows them (the same test as in MotionVectors::Draw()). A full-size write is saved
    // for most presets; a preset turning them on uses a stale map for that one frame.
    bool const writeMotionUV = *m_perFrameContext.mv_a >= 0.0001f &&
                               static_cast<int>(*m_perFrameContext.mv_x) > 0 &&
                               static_cast<int>(*m_perFrameContext.mv_y) > 0;

    if (writeMotionUV)
    {
        // Add motion vector u/v texture for the warp mesh draw and clean both buffers.
        m_framebuffer.SetAttachment(m_currentFrameBuffer, 1, m_motionVectorUVMap);
    }

    // Draw previous frame image warped via per-pixel mesh and warp shader
    m_perPixelMesh.Draw(m_state, m_perFrameContext, m_perPixelContext);

    if (writeMotionUV)
    {
        // Stop writing to the u/v texture, but keep it attached until the frame's drawing is done:
        // changing the attachments here would end the render pass.
        const GLenum buffers[] = {GL_COLOR_ATTACHMENT0, GL_NONE};
        glDrawBuffers(2, buffers);
    }

    if (m_warpSamplesBlur)
    {
        // Binds the blur framebuffer and then restores the current one (keeping its draw buffers).
        updateBlur();
    }

    // Draw audio-data-related stuff
    for (auto& shape : m_customShapes)
    {
        shape->Draw();
    }
    for (auto& wave : m_customWaveforms)
    {
        wave->Draw(m_perFrameContext);
    }
    m_waveform.Draw(m_perFrameContext);

    // Done in DrawSprites() in Milkdrop
    if (*m_perFrameContext.darken_center > 0)
    {
        m_darkenCenter.Draw();
    }
    m_border.Draw(m_perFrameContext);

    if (writeMotionUV)
    {
        // Remove the u/v texture from the framebuffer.
        m_framebuffer.RemoveColorAttachment(m_currentFrameBuffer, 1);
    }

    // Todo: Song title anim would go here

    // y-flip the image for final compositing again. With diffusion, the same pass also filters
    // next frame's warp input; the composite gets the exact copy. After motion vectors the next
    // frame recomputes its inputs anyway (vectors usually stay on), so a plain flip suffices.
    const bool diffusionActive = m_feedbackDiffusion.Active() && !motionVectorsDrawn;
    if (diffusionActive)
    {
        m_feedbackDiffusion.Draw(m_framebuffer.GetColorAttachmentTexture(m_currentFrameBuffer, 0), true);
        m_state.mainTexture = m_feedbackDiffusion.RawTexture();
    }
    else
    {
        m_flipTexture.Draw(m_framebuffer.GetColorAttachmentTexture(m_currentFrameBuffer, 0), nullptr, true, false);
        m_state.mainTexture = m_flipTexture.Texture();
    }

    // We no longer need the previous frame image, use it to render the final composite, or draw
    // the composite straight into the caller's framebuffer when nothing needs it stored.
    m_framebuffer.BindRead(m_currentFrameBuffer);
    m_state.compositeToDefaultFramebuffer = false;
    if (m_directOutput)
    {
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, m_directFramebuffer);
#ifdef USE_GLES
        // The default framebuffer's draw buffer must be GL_BACK (see ProjectM::RenderFrame()).
        GLenum const drawBuffer = m_directFramebuffer == 0 ? GL_BACK : GL_COLOR_ATTACHMENT0;
        glDrawBuffers(1, &drawBuffer);
#endif
        m_state.compositeToDefaultFramebuffer = m_directFramebuffer == 0;
    }
    else
    {
        m_framebuffer.BindDraw(m_previousFrameBuffer);
    }

    m_finalComposite.Draw(m_state, m_perFrameContext);

    // ToDo: Draw user sprites (can have evaluated code)

    // Old-school effects (video echo) draw in the final orientation themselves, so no flip is
    // needed here, and the flip texture still holds the y-flipped current frame, which is next
    // frame's previous frame.
    m_flipHoldsPreviousFrame = !diffusionActive;
    m_diffusionHoldsPreviousFrame = diffusionActive;

    // Swap framebuffer IDs for the next frame.
    std::swap(m_currentFrameBuffer, m_previousFrameBuffer);

    m_isFirstFrame = false;
}

auto MilkdropPreset::OutputTexture() const -> std::shared_ptr<Renderer::Texture>
{
    // the composited image is always stored in the "current" framebuffer after a frame is rendered.
    return m_framebuffer.GetColorAttachmentTexture(m_currentFrameBuffer, 0);
}

auto MilkdropPreset::SetOutputTarget(bool direct, uint32_t targetFramebuffer) -> bool
{
    // Pixels a composite shader discards keep the target's contents: only the stored path has the
    // preset's previous frame there.
    m_directOutput = direct && !m_finalComposite.CompositeShaderDiscards();
    m_directFramebuffer = targetFramebuffer;
    return m_directOutput;
}

void MilkdropPreset::DrawInitialImage(const std::shared_ptr<Renderer::Texture>& image, const Renderer::RenderContext& renderContext)
{
    m_framebuffer.SetSize(renderContext.viewportSizeX, renderContext.viewportSizeY);

    // Render to previous framebuffer, as this is the image used to draw the next frame on.
    m_flipTexture.Draw(image, m_framebuffer, m_previousFrameBuffer);
    m_flipHoldsPreviousFrame = false;
    m_diffusionHoldsPreviousFrame = false;
}

void MilkdropPreset::PerFrameUpdate()
{
    m_perFrameContext.LoadStateVariables(m_state);
    m_perPixelContext.LoadStateReadOnlyVariables(m_state, m_perFrameContext);

    m_perFrameContext.ExecutePerFrameCode();

    m_perPixelContext.LoadPerFrameQVariables(m_state, m_perFrameContext);

    // Clamp gamma and echo zoom values
    *m_perFrameContext.gamma = std::max(0.0, std::min(8.0, *m_perFrameContext.gamma));
    *m_perFrameContext.echo_zoom = std::max(0.001, std::min(1000.0, *m_perFrameContext.echo_zoom));
}

void MilkdropPreset::Load(const std::string& pathname)
{
#ifdef MILKDROP_PRESET_DEBUG
    std::cerr << "[Preset] Loading preset from file \"" << pathname << "\"." << std::endl;
#endif

    SetFilename(ParseFilename(pathname));

    PresetFileParser parser;

    if (!parser.Read(pathname))
    {
#ifdef MILKDROP_PRESET_DEBUG
        std::cerr << "[Preset] Could not parse preset file." << std::endl;
#endif
        throw MilkdropPresetLoadException("Could not parse preset file \"" + pathname + "\"");
    }

    InitializePreset(parser);
}

void MilkdropPreset::Load(std::istream& stream)
{
#ifdef MILKDROP_PRESET_DEBUG
    std::cerr << "[Preset] Loading preset from stream." << std::endl;
#endif

    PresetFileParser parser;

    if (!parser.Read(stream))
    {
#ifdef MILKDROP_PRESET_DEBUG
        std::cerr << "[Preset] Could not parse preset data." << std::endl;
#endif
        throw MilkdropPresetLoadException("Could not parse preset data.");
    }

    InitializePreset(parser);
}

void MilkdropPreset::InitializePreset(PresetFileParser& parsedFile)
{
    // Create the offscreen rendering surfaces.
    m_motionVectorUVMap = std::make_shared<Renderer::TextureAttachment>(GL_RG16F, GL_RG, GL_FLOAT, 0, 0);
    m_framebuffer.CreateColorAttachment(0, 0); // Main image 1
    m_framebuffer.CreateColorAttachment(1, 0); // Main image 2

    Renderer::Framebuffer::Unbind();

    // Load global init variables into the state
    m_state.Initialize(parsedFile);
    m_diffusionAllowed = DiffusionWarpEligible(m_state.warpShader);

    // Register code context variables
    m_perFrameContext.RegisterBuiltinVariables();
    m_perPixelContext.RegisterBuiltinVariables();

    // Custom waveforms:
    for (int i = 0; i < CustomWaveformCount; i++)
    {
        auto wave = std::make_unique<CustomWaveform>(m_state);
        wave->Initialize(parsedFile, i);
        m_customWaveforms[i] = std::move(wave);
    }

    // Custom shapes:
    for (int i = 0; i < CustomShapeCount; i++)
    {
        auto shape = std::make_unique<CustomShape>(m_state);
        shape->Initialize(parsedFile, i);
        m_customShapes[i] = std::move(shape);
    }

    // Preload shaders
    LoadShaderCode();
}

void MilkdropPreset::CompileCodeAndRunInitExpressions()
{
    // Like MilkDrop (CState::RecompileExpressions), code that does not compile is reported and left
    // out; the rest of the preset still runs.
    m_initializationWarnings.clear();

    // Per-frame init and code
    m_perFrameContext.LoadStateVariables(m_state);
    try
    {
        m_perFrameContext.EvaluateInitCode(m_state);
    }
    catch (const MilkdropCompileException& error)
    {
        // MilkDrop starts the q variables at zero if the init code fails.
        for (int q = 0; q < QVarCount; q++)
        {
            m_perFrameContext.q_values_after_init_code[q] = 0.0;
            *m_perFrameContext.q_vars[q] = 0.0;
            m_state.frameQVariables[q] = 0.0;
        }
        m_initializationWarnings.emplace_back(error.what());
    }
    try
    {
        m_perFrameContext.CompilePerFrameCode(m_state.perFrameCode);
    }
    catch (const MilkdropCompileException& error)
    {
        m_initializationWarnings.emplace_back(error.what());
    }

    // Per-vertex code
    try
    {
        m_perPixelContext.CompilePerPixelCode(m_state.perPixelCode);
    }
    catch (const MilkdropCompileException& error)
    {
        m_initializationWarnings.emplace_back(error.what());
    }

    for (int i = 0; i < CustomWaveformCount; i++)
    {
        auto& wave = m_customWaveforms[i];
        wave->CompileCodeAndRunInitExpressions(m_perFrameContext, m_initializationWarnings);
    }

    for (int i = 0; i < CustomShapeCount; i++)
    {
        auto& shape = m_customShapes[i];
        shape->CompileCodeAndRunInitExpressions(m_initializationWarnings);
    }
}

auto MilkdropPreset::InitializationWarnings() const -> std::vector<std::string>
{
    return m_initializationWarnings;
}

void MilkdropPreset::LoadShaderCode()
{
    m_perPixelMesh.LoadWarpShader(m_state);
    m_finalComposite.LoadCompositeShader(m_state);

    // GetBlur1(), sampler_blur1, blur1_min, ...: any mention counts.
    std::string warpShader = m_state.warpShader;
    std::transform(warpShader.begin(), warpShader.end(), warpShader.begin(),
                   [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
    m_warpSamplesBlur = warpShader.find("blur") != std::string::npos;
}

auto MilkdropPreset::ParseFilename(const std::string& filename) -> std::string
{
    const std::size_t start = filename.find_last_of('/');

    if (start == std::string::npos || start >= (filename.length() - 1))
    {
        return "";
    }

    return filename.substr(start + 1, filename.length());
}

} // namespace MilkdropPreset
} // namespace libprojectM
