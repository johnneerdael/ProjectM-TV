#pragma once
#include "vendor/json.hpp"
#include <Renderer/OpenGL.h>
#include <Renderer/TextureAttachment.hpp>
#include <array>
#include <vector>
#include <stdexcept>

namespace proof {
constexpr int HistoryWidth = 64, HistoryHeight = 48;
inline PFNGLTEXIMAGE2DPROC realTexImage2D{};
inline size_t historyAllocations{};
inline std::vector<unsigned char> Pattern(std::array<unsigned char, 4> colour) {
    std::vector<unsigned char> pixels(HistoryWidth * HistoryHeight * 4);
    for (size_t i = 0; i < pixels.size(); i += 4)
        for (size_t j = 0; j < 4; ++j) pixels[i + j] = colour[j];
    return pixels;
}
inline void GLAD_API_PTR DefinedAllocation(GLenum target, GLint level, GLint format,
        GLsizei width, GLsizei height, GLint border, GLenum channels, GLenum type, const void* data) {
    realTexImage2D(target, level, format, width, height, border, channels, type, data);
    if (target == GL_TEXTURE_2D && level == 0 && format == GL_RGBA8 &&
            channels == GL_RGBA && type == GL_UNSIGNED_BYTE && !data &&
            width == HistoryWidth && height == HistoryHeight) {
        ++historyAllocations;
        const auto pixels = Pattern({0, 160, 80, 255});
        glTexSubImage2D(target, 0, 0, 0, width, height, channels, type, pixels.data());
    }
}
class AllocationControl {
public:
    AllocationControl() {
        historyAllocations = 0; realTexImage2D = glad_glTexImage2D;
        if (!realTexImage2D) throw std::runtime_error("allocation control requires loaded GL functions");
        glad_glTexImage2D = DefinedAllocation;
    }
    ~AllocationControl() { glad_glTexImage2D = realTexImage2D; }
    AllocationControl(const AllocationControl&) = delete;
    AllocationControl& operator=(const AllocationControl&) = delete;
};
inline std::vector<unsigned char> ReadHistory(GLuint texture) {
    GLint previous = 0; glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &previous);
    GLuint fbo = 0; glGenFramebuffers(1, &fbo);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, fbo);
    glFramebufferTexture2D(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    if (glCheckFramebufferStatus(GL_READ_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
        throw std::runtime_error("history diagnostic framebuffer incomplete");
    glReadBuffer(GL_COLOR_ATTACHMENT0);
    std::vector<unsigned char> pixels(HistoryWidth * HistoryHeight * 4);
    glReadPixels(0, 0, HistoryWidth, HistoryHeight, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    glBindFramebuffer(GL_READ_FRAMEBUFFER, static_cast<GLuint>(previous));
    glDeleteFramebuffers(1, &fbo);
    return pixels;
}
inline GLuint AttachmentId(const libprojectM::Renderer::TextureAttachment& attachment) {
    attachment.Texture()->Bind(0);
    GLint id = 0; glGetIntegerv(GL_TEXTURE_BINDING_2D, &id);
    return static_cast<GLuint>(id);
}
inline nlohmann::json RasterState() {
    GLint draw = 0, read = 0; std::array<GLint, 4> box{};
    std::array<GLfloat, 4> colour{}; std::array<GLboolean, 4> mask{};
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &draw);
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &read);
    glGetIntegerv(GL_SCISSOR_BOX, box.data());
    glGetFloatv(GL_COLOR_CLEAR_VALUE, colour.data());
    glGetBooleanv(GL_COLOR_WRITEMASK, mask.data());
    return {{"draw", draw}, {"read", read}, {"scissor_box", box}, {"clear_colour", colour},
            {"colour_mask", mask}, {"scissor_enabled", glIsEnabled(GL_SCISSOR_TEST) == GL_TRUE}};
}
inline nlohmann::json TextureHistoryProbe() {
    AllocationControl control;
    // Demonstrate that the shared allocation control really writes the specified bytes.
    GLuint testTexture = 0; glGenTextures(1, &testTexture); glBindTexture(GL_TEXTURE_2D, testTexture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, HistoryWidth, HistoryHeight, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    const bool poisonPassed = ReadHistory(testTexture) == Pattern({0, 160, 80, 255});
    glDeleteTextures(1, &testTexture); historyAllocations = 0;
    if (!poisonPassed || glGetError() != GL_NO_ERROR)
        throw std::runtime_error("defined allocation control did not preserve its requested pixels");
    const auto originalState = RasterState();
    glClearColor(0.17f, 0.29f, 0.43f, 0.61f);
    glColorMask(GL_FALSE, GL_TRUE, GL_FALSE, GL_TRUE);
    glEnable(GL_SCISSOR_TEST); glScissor(3, 5, 7, 11);
#ifdef PATCH_PROOF_TV
    libprojectM::Renderer::Texture::SetPoolLimit(32768);
#endif
    std::vector<unsigned char> fresh, recreated;
    std::vector<bool> statePreserved;
    {
        const auto before = RasterState();
        libprojectM::Renderer::TextureAttachment attachment(
            GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, HistoryWidth, HistoryHeight);
        statePreserved.push_back(before == RasterState());
        const auto id = AttachmentId(attachment);
        fresh = ReadHistory(id);
        const auto oldContents = Pattern({32, 64, 192, 255});
        glBindTexture(GL_TEXTURE_2D, id);
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, HistoryWidth, HistoryHeight,
                       GL_RGBA, GL_UNSIGNED_BYTE, oldContents.data());
    }
    size_t retiredBytes = 0;
#ifdef PATCH_PROOF_TV
    retiredBytes = libprojectM::Renderer::Texture::PoolBytes();
#endif
    {
        const auto before = RasterState();
        libprojectM::Renderer::TextureAttachment attachment(
            GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, HistoryWidth, HistoryHeight);
        statePreserved.push_back(before == RasterState());
        recreated = ReadHistory(AttachmentId(attachment));
    }
#ifdef PATCH_PROOF_TV
    libprojectM::Renderer::Texture::SetPoolLimit(0);
#endif
    glBindTexture(GL_TEXTURE_2D, 0);
    auto colour = originalState.at("clear_colour").get<std::array<GLfloat, 4>>();
    auto mask = originalState.at("colour_mask").get<std::array<GLboolean, 4>>();
    auto box = originalState.at("scissor_box").get<std::array<GLint, 4>>();
    glClearColor(colour[0], colour[1], colour[2], colour[3]);
    glColorMask(mask[0], mask[1], mask[2], mask[3]);
    glScissor(box[0], box[1], box[2], box[3]);
    if (originalState.at("scissor_enabled").get<bool>()) glEnable(GL_SCISSOR_TEST);
    else glDisable(GL_SCISSOR_TEST);
    if (glGetError() != GL_NO_ERROR) throw std::runtime_error("history diagnostic GL error");
    return {{"kind", "texture-history"}, {"width", HistoryWidth}, {"height", HistoryHeight},
            {"controlled_poison_rgba", std::array<int, 4>{0, 160, 80, 255}},
            {"poison_control_passed", poisonPassed}, {"fresh_rgba", fresh}, {"recreated_rgba", recreated},
            {"driver_allocations", historyAllocations}, {"pool_bytes_after_retire", retiredBytes},
            {"pool_available", retiredBytes > 0}, {"caller_state_preserved", statePreserved},
            {"observer_gl_error", 0}};
}
} // namespace proof
