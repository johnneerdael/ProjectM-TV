// Search paths must remain attached to live presets during texture changes and fades.
#include "gl_context.hpp"
#include <ProjectM.hpp>
#include <projectM-4/projectM.h>
#include <MilkdropPreset/MilkdropPreset.hpp>
#include <Renderer/TextureManager.hpp>
#include <filesystem>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>

namespace fs = std::filesystem;
namespace libprojectM {
class FeedbackDetailTestAccess {
public:
    static Preset* Active(ProjectM& engine) { return engine.m_activePreset.get(); }
    static Preset* Incoming(ProjectM& engine) { return engine.m_transitioningPreset.get(); }
    static Renderer::TextureManager* Textures(Preset* preset) {
        return dynamic_cast<MilkdropPreset::MilkdropPreset*>(preset)->m_state.renderContext.textureManager;
    }
    static std::shared_ptr<Renderer::Texture> ShapeImage(Preset* preset) {
        return dynamic_cast<MilkdropPreset::MilkdropPreset*>(preset)->m_customShapes[0]->m_imageTexture.Texture();
    }
};
}
using Access = libprojectM::FeedbackDetailTestAccess;
static void Check(bool value, const char* message) {
    if (!value) throw std::runtime_error(message);
}
static void Write(const fs::path& file, unsigned char red, unsigned char green) {
    std::ofstream out(file, std::ios::binary);
    unsigned char header[18]{};
    header[2] = 2; header[12] = 2; header[14] = 2; header[16] = 24;
    out.write(reinterpret_cast<char*>(header), sizeof(header));
    for (int i = 0; i < 4; ++i) {
        const unsigned char pixel[]{0, green, red};
        out.write(reinterpret_cast<const char*>(pixel), sizeof(pixel));
    }
    Check(out.good(), "fixture write failed");
}
static void Load(libprojectM::ProjectM& engine, bool smooth) {
    std::istringstream data("MILKDROP_PRESET_VERSION=201\nPSVERSION_WARP=2\nPSVERSION_COMP=2\n"
        "[preset00]\nfDecay=1\nfWaveAlpha=0\nfGammaAdj=1\n"
        "shapecode_0_enabled=1\nshapecode_0_textured=1\nshapecode_0_num_inst=1\n"
        "shapecode_0_sides=4\nshapecode_0_rad=.7\nshapecode_0_image=shared\n"
        "warp_1=shader_body { ret=tex2D(sampler_shared,uv).rgb; }\n"
        "comp_1=shader_body { ret=tex2D(sampler_shared,uv).rgb; }\n");
    engine.LoadPresetData(data, smooth);
}
static std::string Source(libprojectM::Preset* preset, const char* name = "shared") {
    auto texture = Access::Textures(preset)->GetTexture(name).Texture();
    Check(texture != nullptr, "texture not loaded");
    return texture->SourcePath();
}
static void ExpectColor(libprojectM::Preset* preset, unsigned char red, unsigned char green, bool renderedOutput = false) {
    auto texture = renderedOutput ? preset->OutputTexture() : Access::Textures(preset)->GetTexture("shared").Texture();
    GLint previousRead{}, previousDraw{};
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &previousRead);
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &previousDraw);
    GLuint framebuffer{};
    glGenFramebuffers(1, &framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture->TextureID(), 0);
    Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "texture read target incomplete");
    unsigned char pixel[4]{};
    glReadPixels(1, 1, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, previousRead);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, previousDraw);
    glDeleteFramebuffers(1, &framebuffer);
    if (std::abs(int(pixel[0]) - int(red)) > 1 || std::abs(int(pixel[1]) - int(green)) > 1 || pixel[2] != 0) {
        std::cerr << "image " << texture->SourcePath() << " expected RGB=" << int(red) << ',' << int(green)
                  << ",0 actual=" << int(pixel[0]) << ',' << int(pixel[1]) << ',' << int(pixel[2]) << '\n';
        throw std::runtime_error("decoded image differs from expected pack bytes");
    }
}
int main(int argc, char** argv) {
    try {
        Check(argc == 2, "fixture path required");
        fs::path root(argv[1]);
        fs::remove_all(root);
        fs::create_directories(root / "bundled");
        fs::create_directories(root / "pack-one");
        fs::create_directories(root / "pack-two");
        Write(root / "bundled/shared.tga", 64, 0);
        Write(root / "bundled/fallback.tga", 0, 32);
        Write(root / "pack-one/shared.tga", 0, 128);
        Write(root / "pack-two/shared.tga", 0, 192);
        GLContext context;
        {
            libprojectM::ProjectM engine;
            engine.SetWindowSize(16, 16);
            engine.SetSoftCutDuration(60);
            engine.SetTexturePaths({(root / "bundled").string()});
            Load(engine, false);
            engine.RenderFrame();
            auto* outgoing = Access::Active(engine);
            ExpectColor(outgoing, 64, 0, true);
            const auto feedback = outgoing->OutputTexture()->TextureID();
            auto original = Access::Textures(outgoing)->GetTexture("shared").Texture();
            std::weak_ptr<libprojectM::Renderer::Texture> retained = original;
            original.reset();
            engine.SetTexturePaths({(root / "pack-one").string(), (root / "bundled").string()});
            Check(!retained.expired(), "changing paths discarded an outgoing preset's image");
            Check(outgoing->OutputTexture()->TextureID() == feedback, "changing paths reset feedback");
            engine.RenderFrame();
            Check(Source(outgoing) == (root / "bundled/shared.tga").string(), "outgoing changed its lookup after paths changed");
            Load(engine, true);
            Check(engine.IsTransitioning(), "soft cut does not report both live presets");
            engine.RenderFrame();
            Check(Source(Access::Active(engine)) == (root / "bundled/shared.tga").string(), "fade outgoing uses incoming pack");
            Check(Source(Access::Incoming(engine)) == (root / "pack-one/shared.tga").string(), "custom pack does not precede bundled textures");
            ExpectColor(Access::Active(engine), 64, 0);
            ExpectColor(Access::Incoming(engine), 0, 128);
            ExpectColor(Access::Active(engine), 64, 0, true);
            ExpectColor(Access::Incoming(engine), 0, 128, true);
            Check(Source(Access::Incoming(engine), "fallback") == (root / "bundled/fallback.tga").string(), "bundled fallback missing");
            auto packImage = Access::Textures(Access::Incoming(engine))->GetTexture("shared").Texture();
            const auto beforePackReset = packImage->TextureID();
            const auto beforeBundledReset = Access::Textures(Access::Active(engine))->GetTexture("shared").Texture()->TextureID();
            packImage.reset();
            auto lateImage = Access::Textures(Access::Incoming(engine))->GetTexture("late");
            Check(lateImage.Texture()->SourcePath().empty(), "missing texture did not use placeholder");
            Write(root / "pack-one/late.tga", 16, 0);
            engine.ResetTextures();
            Check(Access::Textures(Access::Incoming(engine))->GetTexture("late").Texture()->SourcePath() == (root / "pack-one/late.tga").string(), "reset did not discover a newly added image");
            Check(Access::Textures(Access::Incoming(engine))->GetTexture("shared").Texture()->TextureID() != beforePackReset, "incoming manager cache did not reload");
            Check(Access::Textures(Access::Active(engine))->GetTexture("shared").Texture()->TextureID() != beforeBundledReset, "outgoing manager cache did not reload");
            engine.RenderFrame();
            Check(Source(Access::Active(engine)) == (root / "bundled/shared.tga").string(), "reset redirected outgoing lookup");
            Check(Source(Access::Incoming(engine)) == (root / "pack-one/shared.tga").string(), "reset redirected incoming lookup");
            Check(Access::ShapeImage(Access::Active(engine)) && Access::ShapeImage(Access::Incoming(engine)), "reset did not reload named shape images");
            Check(Access::ShapeImage(Access::Active(engine))->SourcePath() == (root / "bundled/shared.tga").string(), "reset changed outgoing shape image");
            Check(Access::ShapeImage(Access::Incoming(engine))->SourcePath() == (root / "pack-one/shared.tga").string(), "reset changed incoming shape image");
            ExpectColor(Access::Active(engine), 64, 0);
            ExpectColor(Access::Incoming(engine), 0, 128);
            retained = Access::Textures(Access::Active(engine))->GetTexture("shared").Texture();
            engine.SetTexturePaths({(root / "pack-two").string(), (root / "bundled").string()});
            Load(engine, true); // Interrupt a fade: the preceding incoming preset becomes outgoing.
            engine.RenderFrame();
            Check(retained.expired(), "replaced outgoing manager is retained indefinitely");
            Check(Source(Access::Active(engine)) == (root / "pack-one/shared.tga").string(), "interrupted fade lost previous incoming manager");
            Check(Source(Access::Incoming(engine)) == (root / "pack-two/shared.tga").string(), "replacement retained stale images");
            ExpectColor(Access::Incoming(engine), 0, 192);
            ExpectColor(Access::Incoming(engine), 0, 192, true);
            std::weak_ptr<libprojectM::Renderer::Texture> replacementImage =
                Access::Textures(Access::Incoming(engine))->GetTexture("shared").Texture();
            engine.SetTexturePaths({(root / "bundled").string()});
            Load(engine, false);
            engine.RenderFrame();
            Check(Access::Incoming(engine) == nullptr, "hard cut left a prior incoming preset alive");
            Check(!engine.IsTransitioning(), "hard cut still reports outgoing readers");
            Check(replacementImage.expired(), "hard cut retained a retired pack manager");
            Check(Source(Access::Active(engine)) == (root / "bundled/shared.tga").string(), "bundled preset inherited custom lookup");
        }
        auto api = projectm_create();
        Check(api != nullptr && !projectm_is_transitioning(api), "new C API instance reports a transition");
        projectm_set_window_size(api, 16, 16);
        projectm_set_soft_cut_duration(api, 0);
        projectm_load_preset_data(api, "[preset00]\nfDecay=1\nfWaveAlpha=0\n", true);
        Check(projectm_is_transitioning(api), "C API did not report retained outgoing preset");
        projectm_opengl_render_frame(api);
        Check(!projectm_is_transitioning(api), "C API did not report completed soft cut retirement");
        projectm_destroy(api);
        fs::remove_all(root);
        std::cout << "TEXTURE ROUTING TESTS PASSED\n";
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
