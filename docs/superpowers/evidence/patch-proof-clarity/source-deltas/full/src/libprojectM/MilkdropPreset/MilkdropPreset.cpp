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
#include "GeometryTargets.hpp"
#include "MotionUV.hpp"
#include <optional>

#include "Factory.hpp"
#include "LineGeometry.hpp"
#include "MilkdropPresetExceptions.hpp"
#include "PresetFileParser.hpp"

#include <Logging.hpp>
#include <algorithm>
#include <cctype>
#include <cstdio>

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
    m_state.blurTexture.Initialize(renderContext);
    m_state.LoadShaders();

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

    glViewport(0, 0, renderContext.viewportSizeX, renderContext.viewportSizeY);

    // Create/rebuild L from the scaled native feedback on enable, resize or gain-class change.
    // A failed driver shader disables the layer only for this preset; the ordinary path remains usable.
    auto canvas = FeedbackDetailCanvas(renderContext.viewportSizeX, renderContext.viewportSizeY,
                                       renderContext.lineReferenceWidth, renderContext.lineReferenceHeight);
    const bool detailRequested = renderContext.feedbackDetailAlpha >= 0.0f;
#ifdef PROJECTMTV_DISABLE_FEEDBACK_DIFFUSION
    canvas = {}; // capped-library policy also excludes the detail layer.
#endif
    if (!detailRequested || canvas.scale == 0 || m_detailFailed) m_feedbackDetail.reset();
    else if (!m_feedbackDetail || m_feedbackDetail->Width() != renderContext.viewportSizeX ||
             m_feedbackDetail->Height() != renderContext.viewportSizeY ||
             m_feedbackDetail->Canvas().scale != canvas.scale ||
             m_feedbackDetail->RetainsDetail() != (renderContext.feedbackDetailAlpha > 0.0f))
    {
        m_feedbackDetail.reset(); // release/return old textures before allocating a replacement
        try {
            m_feedbackDetail = std::make_unique<FeedbackDetail>(renderContext.viewportSizeX,
                renderContext.viewportSizeY, canvas, renderContext.feedbackDetailAlpha > 0.0f);
            m_feedbackDetail->Initialize(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0));
            m_motionVectorUVMap->SetSize(canvas.width, canvas.height);
            m_isFirstFrame = true;
        } catch (const std::exception& error) {
            m_feedbackDetail.reset();
            m_detailFailed = true;
            std::fprintf(stderr, "projectM authored feedback disabled: %s\n", error.what());
        }
    }
    auto* detail = m_feedbackDetail.get();
    if (detail) {
        // Integer canvases can differ from 1280x720 during scaled transitions. Every texsize,
        // blur/sample decision and line scale must use the actual authored state of this preset.
        m_state.renderContext.lineReferenceWidth = canvas.width;
        m_state.renderContext.lineReferenceHeight = canvas.height;
    }
    PerFrameUpdate();

    m_detailStatus = !detailRequested ? -1 : detail ? canvas.scale : m_detailFailed ? -3 : -2;
    if (detailRequested && !detail && !m_detailFallbackLogged) {
        std::fprintf(stderr, "projectM authored feedback fallback at %dx%d\n",
                     renderContext.viewportSizeX, renderContext.viewportSizeY);
        m_detailFallbackLogged = true;
    }
    if (!detail) {
        const auto uv = m_motionVectorUVMap->Texture();
        if (uv->Width() != renderContext.viewportSizeX || uv->Height() != renderContext.viewportSizeY) {
            m_motionVectorUVMap->SetSize(renderContext.viewportSizeX, renderContext.viewportSizeY);
            // Returning from the canvas replaces/clears the UV map. Its first native warp must
            // populate normalized coordinates before motion vectors can consume them.
            m_isFirstFrame = true;
        }
    }
    else if (m_isFirstFrame) detail->Initialize(m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0));

    // Above the line reference size, the warp reads the previous frame through a small blur that gives
    // back the per-frame smoothing feedback presets get at the reference size (see FeedbackDiffusion.hpp).
    if (m_feedbackDiffusion.SetScale(m_diffusionAllowed && !detail ? LineScale(renderContext.viewportSizeX, renderContext.viewportSizeY,
                                           renderContext.lineReferenceWidth, renderContext.lineReferenceHeight) : 0.0f))
    {
        m_diffusionHoldsPreviousFrame = false;
    }

    // Authored-state initialization draws at canvas size. Restore the native viewport before
    // motion vectors and the first native flip/warp, including presets that read previous blur.
    glViewport(0, 0, renderContext.viewportSizeX, renderContext.viewportSizeY);
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
            m_flipTexture.Draw(*m_state.renderContext.shaderCache, m_framebuffer.GetColorAttachmentTexture(m_previousFrameBuffer, 0), nullptr, true, false);
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
        if (detail) m_state.blurTexture.Update(*detail->Previous(), m_perFrameContext, 1.0f);
        else updateBlur();
        glViewport(0, 0, renderContext.viewportSizeX, renderContext.viewportSizeY);
    }

    // We now draw to the current framebuffer.
    m_framebuffer.Bind(m_currentFrameBuffer);

    // Publish the real warp's u/v output every completed frame, independently of motion-vector
    // visibility. Both consumers above/below run before their producer, so re-enabling vectors
    // samples the latest compatible previous field. Keep the actual fragment shader: custom
    // coordinate writes and discarded pixels cannot be reconstructed by a UV-only replay.
    // The authored path publishes at canvas size; native/fallback publishes at native size.
    if (!detail)
    {
        // Add motion vector u/v texture for the warp mesh draw and clean both buffers.
        m_framebuffer.SetAttachment(m_currentFrameBuffer, 1, m_motionVectorUVMap);
    }

    // Draw previous frame image warped via per-pixel mesh and warp shader
    if (detail && renderContext.feedbackDetailAlpha == 0.0f)
        m_perPixelMesh.Prepare(m_state, m_perFrameContext, m_perPixelContext);
    else m_perPixelMesh.Draw(m_state, m_perFrameContext, m_perPixelContext);

    if (!detail)
    {
        // Stop writing to the u/v texture, but keep it attached until the frame's drawing is done:
        // changing the attachments here would end the render pass.
        const GLenum buffers[] = {GL_COLOR_ATTACHMENT0, GL_NONE};
        glDrawBuffers(2, buffers);
    }

    if (m_warpSamplesBlur && !detail)
    {
        // Binds the blur framebuffer and then restores the current one (keeping its draw buffers).
        updateBlur();
    }

    if (detail)
    {
        // Motion vectors are part of feedback. Their normalized UV map is written by the canvas warp,
        // so Standard needs no native warp even when vectors are visible.
        if (!m_isFirstFrame) {
            const auto savedContext = m_state.renderContext;
            m_state.renderContext.viewportSizeX = canvas.width;
            m_state.renderContext.viewportSizeY = canvas.height;
            m_state.renderContext.lineReferenceWidth = 0;
            m_state.renderContext.lineReferenceHeight = 0;
            detail->CanvasFramebuffer().Bind(detail->PreviousIndex());
            glViewport(0, 0, canvas.width, canvas.height);
            m_motionVectors.Draw(m_perFrameContext, m_motionVectorUVMap->Texture(), false);
            m_state.renderContext = savedContext;
        }
        glViewport(0, 0, canvas.width, canvas.height);
        detail->flip.Draw(*m_state.renderContext.shaderCache, detail->Previous(), nullptr, true, false);
        const auto nativeMain = m_state.mainTexture;
        m_state.mainTexture = detail->flip.Texture();
        auto& target = detail->CanvasFramebuffer();
        target.SetAttachment(detail->WarpedIndex(), 1, m_motionVectorUVMap);
        target.Bind(detail->WarpedIndex());
        glViewport(0, 0, canvas.width, canvas.height);
        m_perPixelMesh.DrawAgain(m_state, m_perFrameContext);
        target.RemoveColorAttachment(detail->WarpedIndex(), 1);
        m_state.mainTexture = nativeMain;
        if (m_warpSamplesBlur) m_state.blurTexture.Update(*detail->Previous(), m_perFrameContext, 1.0f);
        detail->Combine(m_framebuffer.GetColorAttachmentTexture(m_currentFrameBuffer, 0),
                        renderContext.feedbackDetailAlpha, m_framebuffer, m_currentFrameBuffer);
        glViewport(0, 0, renderContext.viewportSizeX, renderContext.viewportSizeY);
    }

    // The native framebuffer already holds Hc. Evaluate geometry once at authored
    // size; the same prepared vertices also draw at native size for presentation.
    std::optional<GeometryTargets> geometry;
    if (detail) {
        geometry.emplace(m_state,detail->CanvasFramebuffer(),detail->WarpedIndex(),
                         canvas.width,canvas.height,detail->flip.Texture(),m_framebuffer,m_currentFrameBuffer);
        geometry->Authored();
    }
    auto* targets=geometry ? &*geometry : nullptr;
    // Draw audio-data-related stuff
    for (auto& shape : m_customShapes)
    {
        shape->Draw(targets);
    }
    for (auto& wave : m_customWaveforms)
    {
        wave->Draw(m_perFrameContext,targets);
    }
    m_waveform.Draw(m_perFrameContext,targets);

    // Done in DrawSprites() in Milkdrop
    if (*m_perFrameContext.darken_center > 0)
    {
        m_darkenCenter.Draw();
    }
    m_border.Draw(m_perFrameContext);

    if (!detail)
    {
        // Remove the u/v texture from the framebuffer.
        m_framebuffer.RemoveColorAttachment(m_currentFrameBuffer, 1);
    }

    if (detail) {
        geometry->Native();
        if (*m_perFrameContext.darken_center > 0) m_darkenCenter.Draw();
        m_border.Draw(m_perFrameContext);
        // Lw now includes authored geometry. Swap its role with the previous
        // canvas without sampling native rasterization or allocating/copying.
        detail->FinishGeometry();
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
        m_flipTexture.Draw(*m_state.renderContext.shaderCache, m_framebuffer.GetColorAttachmentTexture(m_currentFrameBuffer, 0), nullptr, true, false);
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
    m_flipTexture.Draw(*m_state.renderContext.shaderCache, image, m_framebuffer, m_previousFrameBuffer);
    m_flipHoldsPreviousFrame = false;
    m_diffusionHoldsPreviousFrame = false;
    m_feedbackDetail.reset();
    m_isFirstFrame = true;
}

void MilkdropPreset::BindFramebuffer()
{
    m_flipHoldsPreviousFrame = false;
    m_diffusionHoldsPreviousFrame = false;
    // The caller can burn into native feedback. Rebuild the authored canvas from
    // that modified feedback before the next warp instead of hiding the write.
    m_feedbackDetail.reset();
    if (m_framebuffer.Width() > 0 && m_framebuffer.Height() > 0)
    {
        m_framebuffer.BindDraw(m_previousFrameBuffer);
    }
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
    LOG_DEBUG("[MilkdropPreset] Loading preset from file \"" + pathname + "\".")

    SetFilename(ParseFilename(pathname));

    PresetFileParser parser;

    if (!parser.Read(pathname))
    {
        const std::string error = "[MilkdropPreset] Could not parse preset file \"" + pathname + "\".";
        LOG_ERROR(error)
        throw MilkdropPresetLoadException(error);
    }

    InitializePreset(parser);
}

void MilkdropPreset::Load(std::istream& stream)
{
    LOG_DEBUG("[MilkdropPreset] Loading preset from stream.");

    PresetFileParser parser;

    if (!parser.Read(stream))
    {
        const std::string error =  "[MilkdropPreset] Could not parse preset data.";
        LOG_ERROR(error)
        throw MilkdropPresetLoadException(error);
    }

    InitializePreset(parser);
}

void MilkdropPreset::InitializePreset(PresetFileParser& parsedFile)
{
    // Create the offscreen rendering surfaces.
    m_state.motionUVPacked = !MotionUVFloatRenderable();
    m_motionVectorUVMap = m_state.motionUVPacked
        ? std::make_shared<Renderer::TextureAttachment>(GL_RG16UI, GL_RG_INTEGER, GL_UNSIGNED_SHORT, 0, 0)
        : std::make_shared<Renderer::TextureAttachment>(GL_RG16F, GL_RG, GL_FLOAT, 0, 0);
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
