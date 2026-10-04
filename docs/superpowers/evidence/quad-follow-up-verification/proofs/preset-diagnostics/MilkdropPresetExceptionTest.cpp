#include <MilkdropPreset/MilkdropPresetExceptions.hpp>
#include <ProjectM.hpp>
#include <PresetFactoryManager.hpp>
#include <gtest/gtest.h>
#include <exception>
#include <sstream>
#include <string>
#ifdef __APPLE__
#include <OpenGL/OpenGL.h>
#endif

using libprojectM::MilkdropPreset::MilkdropPresetLoadException;
using libprojectM::MilkdropPreset::MilkdropCompileException;

TEST(MilkdropPresetException, LoadMessageSurvivesStandardExceptionHandler) {
    try { throw MilkdropPresetLoadException("Could not parse preset data."); }
    catch (const std::exception& error) { EXPECT_STREQ(error.what(), "Could not parse preset data."); }
}
TEST(MilkdropPresetException, CompileMessageSurvivesStandardExceptionHandler) {
    try { throw MilkdropCompileException("Could not compile per-frame code"); }
    catch (const std::exception& error) { EXPECT_STREQ(error.what(), "Could not compile per-frame code"); }
}

TEST(MilkdropPresetException, FactoryMessageSurvivesStandardExceptionHandler) {
    try { throw libprojectM::PresetFactoryException("Could not parse preset data."); }
    catch (const std::exception& error) { EXPECT_STREQ(error.what(), "Could not parse preset data."); }
}

class FailureEventProjectM : public libprojectM::ProjectM {
public:
    mutable std::string failure, filename;
    mutable int failures{};
    void PresetSwitchFailedEvent(const std::string& file, const std::string& reason) const override {
        filename = file; failure = reason; ++failures;
    }
};
class MilkdropPresetFailureEventTest : public ::testing::Test {
protected:
    static void SetUpTestSuite() {
#ifdef __APPLE__
        CGLPixelFormatAttribute attrs[] = {kCGLPFAOpenGLProfile,
            static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_3_2_Core), static_cast<CGLPixelFormatAttribute>(0)};
        CGLPixelFormatObj format{}; GLint count{};
        if (CGLChoosePixelFormat(attrs, &format, &count) != kCGLNoError || !format) return;
        CGLCreateContext(format, nullptr, &context); CGLDestroyPixelFormat(format);
#endif
    }
    static void TearDownTestSuite() {
#ifdef __APPLE__
        if (context) { CGLSetCurrentContext(nullptr); CGLDestroyContext(context); context = nullptr; }
#endif
    }
    void SetUp() override {
#ifdef __APPLE__
        if (!context) GTEST_SKIP() << "no macOS CGL OpenGL context";
        ASSERT_EQ(CGLSetCurrentContext(context), kCGLNoError);
#else
        GTEST_SKIP() << "public load regression needs macOS CGL OpenGL context";
#endif
    }
#ifdef __APPLE__
    static CGLContextObj context;
#endif
};
#ifdef __APPLE__
CGLContextObj MilkdropPresetFailureEventTest::context{};
#endif

TEST_F(MilkdropPresetFailureEventTest, InvalidPresetDataReportsParseReason) {
    FailureEventProjectM engine;
    std::istringstream data("not-a-preset\n");
    engine.LoadPresetData(data, false);
    EXPECT_EQ(engine.failures, 1);
    EXPECT_TRUE(engine.filename.empty());
    EXPECT_EQ(engine.failure, "Could not parse preset data.");
}
TEST_F(MilkdropPresetFailureEventTest, InvalidPerFrameExpressionReportsCompileReason) {
    FailureEventProjectM engine;
    engine.SetWindowSize(128,96);
    std::istringstream data("[preset00]\nfDecay=1\nper_frame_1=zoom=(;\n");
    engine.LoadPresetData(data, false);
    EXPECT_EQ(engine.failures, 1);
    EXPECT_TRUE(engine.filename.empty());
    EXPECT_EQ(engine.failure, "Could not compile per-frame code");
}
TEST_F(MilkdropPresetFailureEventTest, MissingPresetFileReportsPathAndParseReason) {
    FailureEventProjectM engine;
    const std::string path = "/preset-exception-test/no-such-preset.milk";
    engine.LoadPresetFile(path, false);
    EXPECT_EQ(engine.failures, 1);
    EXPECT_EQ(engine.filename, path);
    EXPECT_EQ(engine.failure, "Could not parse preset file \"" + path + "\"");
}
