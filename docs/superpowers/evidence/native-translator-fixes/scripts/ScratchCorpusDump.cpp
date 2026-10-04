// SCRATCH: not for commit. Loads every preset in $PM_CORPUS_DIR so MilkdropShader dumps its HLSL.
#include <ProjectM.hpp>
#include <Renderer/Shader.hpp>
#include <projectM-opengl.h>
#include <gtest/gtest.h>
#include <OpenGL/OpenGL.h>
#include <algorithm>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <vector>

TEST(ScratchCorpusDump, Dump)
{
    const char* corpus = std::getenv("PM_CORPUS_DIR");
    const char* out = std::getenv("PM_DUMP_HLSL_DIR");
    if (!corpus || !out) GTEST_SKIP();
    CGLPixelFormatAttribute attributes[] = {
        kCGLPFAOpenGLProfile, static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_3_2_Core),
        static_cast<CGLPixelFormatAttribute>(0)};
    CGLPixelFormatObj format{};
    GLint count{};
    ASSERT_EQ(CGLChoosePixelFormat(attributes, &format, &count), kCGLNoError);
    CGLContextObj context{};
    CGLCreateContext(format, nullptr, &context);
    CGLSetCurrentContext(context);
    GLuint fbo{}, tex{};
    glGenFramebuffers(1, &fbo);
    glGenTextures(1, &tex);
    glBindTexture(GL_TEXTURE_2D, tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 64, 48, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0);

    std::vector<std::filesystem::path> presets;
    for (const auto& entry : std::filesystem::directory_iterator(corpus))
        if (entry.path().extension() == ".milk") presets.push_back(entry.path());
    std::sort(presets.begin(), presets.end());
    std::ofstream index(std::string(out) + "/index.tsv");
    libprojectM::ProjectM engine;
    engine.SetWindowSize(64, 48);
    engine.SetPresetLocked(true);
    engine.SetHardCutEnabled(false);
    engine.SetEasterEgg(0);
    for (size_t i = 0; i < presets.size(); ++i)
    {
        const std::string prefix = std::to_string(i);
        setenv("PM_DUMP_HLSL_PREFIX", prefix.c_str(), 1);
        index << prefix << '\t' << presets[i].filename().string() << '\n';
        index.flush();
        engine.LoadPresetFile(presets[i].string(), false);
        engine.RenderFrame(fbo);
    }
}
