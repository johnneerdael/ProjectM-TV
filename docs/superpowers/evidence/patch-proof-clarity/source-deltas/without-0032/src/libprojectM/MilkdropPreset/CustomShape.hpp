#pragma once

#include "Constants.hpp"
#include "LineGeometry.hpp"
#include "PresetState.hpp"
#include "ShapePerFrameContext.hpp"

#include <Renderer/VertexArray.hpp>
#include <Renderer/TextureSamplerDescriptor.hpp>

#include <projectm-eval.h>

#include <string>
#include <vector>

namespace libprojectM {
class FeedbackDetailTestAccess;
namespace MilkdropPreset {

class PresetFileParser;
class GeometryTargets;

/**
 * @brief Renders a custom shape with or without a texture.
 *
 * The class creates two sets of VBO/VAO as it's only known later (in the Draw() call) whether the shape is textured
 * or not.
 */
class CustomShape
{
public:
    CustomShape(PresetState& presetState);

    virtual ~CustomShape();

    /**
     * @brief Loads the initial values and code from the preset file.
     * @param parsedFile The file parser with the preset data.
     * @param index The waveform index.
     */
    void Initialize(PresetFileParser& parsedFile, int index);

    /**
     * @brief Compiles all code blocks and runs the init expression.
     * A code block that doesn't compile is left out and its message added to warnings.
     * @param warnings Receives one message per code block that couldn't be compiled.
     */
    void CompileCodeAndRunInitExpressions(std::vector<std::string>& warnings);

    /**
     * @brief Renders the shape.
     */
    void Draw(GeometryTargets* targets = nullptr);

private:
    // Mesh stores attributes separately and cannot draw batched ranges. Keep one bounded
    // interleaved upload for ordered fills/outlines, with upstream VAO ownership.
    struct TexturedPoint {
        float x{0.0f}, y{0.0f};
        float r{0.0f}, g{0.0f}, b{0.0f}, a{0.0f};
        float u{0.0f}, v{0.0f};
    };

    std::string m_image; //!< Texture filename to be rendered on this shape

    int m_index{0};        //!< The custom shape index in the preset.
    bool m_enabled{false};      //!< If false, the shape isn't drawn.
    int m_sides{4};        //!< Number of sides (vertices)
    bool m_additive{false};     //!< Flag that specifies whether the shape should be drawn additive.
    bool m_thickOutline{false}; //!< If true, the shape is rendered with a thick line, otherwise a single-pixel line.
    bool m_textured{false};     //!< If true, the shape will be rendered with the given texture.
    int m_instances{1};    //!< Number of shape instances to render

    float m_x{0.5f};      //!< The shape x position.
    float m_y{0.5f};      //!< The shape y position.
    float m_radius{0.1f}; //!< The shape radius (1.0 fills the whole screen).
    float m_angle{0.0f};  //!< The shape rotation.

    float m_r{1.0f}; ///!< Red color value.
    float m_g{0.0f}; ///!< Green color value.
    float m_b{0.0f}; ///!< Blue color value.
    float m_a{1.0f}; ///!< Alpha color value.

    float m_r2{0.0f}; ///!< Second red color value.
    float m_g2{1.0f}; ///!< Second green color value.
    float m_b2{0.0f}; ///!< Second blue color value.
    float m_a2{0.0f}; ///!< Second alpha color value.

    float m_border_r{1.0f}; //!< Red color value.
    float m_border_g{1.0f}; //!< Green color value.
    float m_border_b{1.0f}; //!< Blue color value.
    float m_border_a{0.0f}; //!< Alpha color value

    float m_tex_ang{0.0f};  //!< Texture rotation angle.
    float m_tex_zoom{1.0f}; //!< Texture zoom value.

    std::string m_initCode;     //!< Init expression code, run once on preset load.
    std::string m_perFrameCode; //!< Per-frame expression code, run once per frame and instance.

    PRJM_EVAL_F m_tValuesAfterInitCode[TVarCount]{};

    PresetState& m_presetState; //!< The global preset state.
    ShapePerFrameContext m_perFrameContext;

    Renderer::VertexArray m_texturedArray; //!< Reads the shared interleaved buffer.
    GLuint m_vboIdUntextured{0}; //!< Vertex buffer object with a batch of fills and outlines.
    Renderer::VertexArray m_untexturedArray; //!< Reads the same buffer without UVs.

    /**
     * @brief One instance's draw calls into the current batch of vertices.
     */
    struct InstanceDraw {
        bool additive{false};
        bool textured{false};
        int sides{0};
        GLint fillFirst{0};      //!< First fill vertex (a triangle fan of sides + 2 vertices).
        GLint borderFirst{0};    //!< First outline vertex (borderIterations line loops of sides vertices).
        int borderIterations{0}; //!< 0 without outline; GL lines: 4 for a thick outline, else 1; quad lines: 1 (passes in m_borderStyle).
        LineBatch::Strip borderStrip; //!< The outline in m_lineBatch (quad lines).
    };

    static constexpr size_t maxBatchVertices = 8192; //!< 256 KB per shape.

    /**
     * @brief Uploads the collected vertices once and draws the collected instances in order.
     */
    void FlushBatch();
    void DrawBatch(bool nativePass);
    GeometryTargets* m_geometryTargets{nullptr};

    std::vector<TexturedPoint> m_vertices; //!< Current batch: fills and outlines of several instances.
    std::vector<InstanceDraw> m_draws;     //!< Draw calls of the current batch, in instance order.
    LineBatch m_lineBatch;                                     //!< Outlines of the current batch (quad lines).
    std::vector<ColoredPoint> m_borderPoints; //!< One outline, for the line batch.
    bool m_quadBorders{false};                                 //!< This frame draws outlines as quads (reference size set, line program usable).
    LineStyle m_borderStyle;                                   //!< Outline width, passes and pass offsets this frame (quad lines).
    bool m_linesBegun{false};                                  //!< LineRenderer::Begin() called for this batch.
    Renderer::Sampler::Ptr m_mainTextureSampler{std::make_shared<Renderer::Sampler>(GL_REPEAT, GL_LINEAR)}; //!< The main-textured shape sampling contract.
    Renderer::TextureSamplerDescriptor m_imageTexture; //!< The "image" texture, looked up once per frame.
    bool m_imageLookedUp{false};
    bool m_texturedShaderReady{false}; //!< Textured shader uniforms set in this frame.
    GLenum m_lastBlendDestination{0};  //!< Blend function set last in this frame.

    friend class ShapePerFrameContext;
    friend class ::libprojectM::FeedbackDetailTestAccess;
};

} // namespace MilkdropPreset
} // namespace libprojectM
