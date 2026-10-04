// Real GL binding and numerical controls for random texture aliases.
#include "gl_context.hpp"
#include <MilkdropPreset/MilkdropShader.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/MilkdropPreset.hpp>
#include <MilkdropPreset/FinalComposite.hpp>
#include <Renderer/TextureManager.hpp>
#include <vendor/json.hpp>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
namespace fs = std::filesystem;
using nlohmann::json;
static json observations = json::array();
static json presetResults = json::array();
static json numericalResults = json::array();

static void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}

class Fixtures
{
public:
    fs::path directory;
    explicit Fixtures(const fs::path& path) : directory(path)
    {
        Check(fs::create_directory(directory), "fixture directory must be new");
        Write("red.tga", 2, 2, 64, 0, 0);
        Write("green.tga", 4, 2, 0, 128, 0);
    }
    ~Fixtures() { fs::remove_all(directory); }
private:
    void Write(const char* name, int width, int height, unsigned char r, unsigned char g, unsigned char b)
    {
        std::ofstream file(directory / name, std::ios::binary);
        unsigned char header[18]{};
        header[2] = 2; header[12] = width; header[14] = height; header[16] = 24;
        file.write(reinterpret_cast<char*>(header), sizeof(header));
        for (int i = 0; i < width * height; ++i)
        {
            const unsigned char pixel[]{b, g, r};
            file.write(reinterpret_cast<const char*>(pixel), sizeof(pixel));
        }
        Check(file.good(), "could not write fixture texture");
    }
};

static void Setup(PresetState& state, TextureManager& textures)
{
    state.renderContext.textureManager = &textures;
    state.renderContext.viewportSizeX = 16;
    state.renderContext.viewportSizeY = 16;
    state.renderContext.aspectX = state.renderContext.aspectY = 1;
    state.renderContext.invAspectX = state.renderContext.invAspectY = 1;
    state.renderContext.fps = 30;
}

static GLint BoundTexture(MilkdropShader& shader, PresetState& state, const std::string& alias,
                          GLint wrap = GL_REPEAT, GLint filter = GL_LINEAR)
{
    PerFrameContext frame(state.globalMemory, &state.globalRegisters);
    frame.RegisterBuiltinVariables();
    shader.LoadVariables(state, frame);
    GLint program{}, unit{}, texture{}, sampler{}, actual{};
    glGetIntegerv(GL_CURRENT_PROGRAM, &program);
    const auto location = glGetUniformLocation(program, ("sampler_" + alias).c_str());
    Check(location >= 0, "active uniform missing: " + alias);
    glGetUniformiv(program, location, &unit);
    Check(unit > 0, "random uniform still points at main (unit zero): " + alias);
    glActiveTexture(GL_TEXTURE0 + unit);
    glGetIntegerv(GL_TEXTURE_BINDING_2D, &texture);
    glGetIntegerv(GL_SAMPLER_BINDING, &sampler);
    glGetSamplerParameteriv(sampler, GL_TEXTURE_WRAP_S, &actual);
    Check(actual == wrap, "wrong wrap mode: " + alias);
    glGetSamplerParameteriv(sampler, GL_TEXTURE_MIN_FILTER, &actual);
    Check(actual == filter, "wrong filter mode: " + alias);
    const auto base = alias.size() > 3 && alias[2] == '_' ? alias.substr(3) : alias;
    const auto slot = std::stoi(base.substr(4, 2));
    const auto selected = state.randomTextureDescriptors.at(slot).Texture();
    Check(selected && texture == static_cast<GLint>(selected->TextureID()), "uniform points at another texture: " + alias);
    Check(!selected->Name().empty() && !selected->SourcePath().empty(), "selected asset identity missing");
    observations.push_back({{"requested_alias", alias}, {"slot", slot},
        {"prefix", base.size() > 7 ? base.substr(7) : ""},
        {"asset_name", selected->Name()}, {"asset_path", selected->SourcePath()},
        {"width", selected->Width()}, {"height", selected->Height()},
        {"target", selected->Type()}, {"wrap", wrap}, {"filter", filter},
        {"unit", unit}, {"uniform", "sampler_" + alias}, {"texsize_uniform", "texsize_" + base}});
    std::cout << alias << " uniform=sampler_" << alias << " unit=" << unit
              << " texture=" << texture << " wrap=" << wrap << " filter=" << filter << '\n';
    return texture;
}

// Draw the actual translated composite shader, then compare with known fixture bytes.
static void ExpectPixel(MilkdropShader& shader, PresetState& state, int red, int green)
{
    PerFrameContext frame(state.globalMemory, &state.globalRegisters);
    frame.RegisterBuiltinVariables();
    auto target = std::make_shared<Texture>("result", 16, 16, false);
    GLuint framebuffer{}, vao{}, buffer{};
    glGenFramebuffers(1, &framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, target->TextureID(), 0);
    Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "numerical target incomplete");
    glViewport(0, 0, 16, 16);
    glDisable(GL_BLEND);
    glDisable(GL_DEPTH_TEST);
    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);
    glGenBuffers(1, &buffer);
    glBindBuffer(GL_ARRAY_BUFFER, buffer);
    const float vertices[]{-1,-1, 3,-1, -1,3};
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, nullptr);
    glVertexAttrib4f(1, 1, 1, 1, 1);
    glVertexAttrib2f(2, 0.5, 0.5);
    shader.LoadVariables(state, frame);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    unsigned char pixel[4]{};
    glReadPixels(8, 8, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
    glDeleteBuffers(1, &buffer);
    glDeleteVertexArrays(1, &vao);
    glDeleteFramebuffers(1, &framebuffer);
    numericalResults.push_back({{"expected_rgb", {red, green, 0}},
        {"actual_rgb", {pixel[0], pixel[1], pixel[2]}}, {"tolerance_bytes", 1}});
    Check(std::abs(static_cast<int>(pixel[0]) - red) <= 1 &&
          std::abs(static_cast<int>(pixel[1]) - green) <= 1 && pixel[2] == 0,
          "source-predicted RGB does not match sampled aliases");
}

static void NumericalControls(TextureManager& manager)
{
    PresetState state;
    Setup(state, manager);
    for (const auto& alias : std::vector<std::string>{"rand00_red", "rand01_green"})
    {
        MilkdropShader comp(MilkdropShader::ShaderType::CompositeShader);
        comp.LoadCode("shader_body { ret=tex2D(sampler_" + alias + ",uv).rgb; }");
        comp.LoadTexturesAndCompile(state);
        BoundTexture(comp, state, alias);
        ExpectPixel(comp, state, alias == "rand00_red" ? 64 : 0, alias == "rand01_green" ? 128 : 0);
    }
    MilkdropShader combined(MilkdropShader::ShaderType::CompositeShader);
    combined.LoadCode("shader_body { ret=tex2D(sampler_rand00,uv).rgb+tex2D(sampler_rand01,uv).rgb; }");
    combined.LoadTexturesAndCompile(state);
    ExpectPixel(combined, state, 64, 128);
    // Same slot, several aliases in one shader: independently requested modes, shared image.
    MilkdropShader mixed(MilkdropShader::ShaderType::CompositeShader);
    mixed.LoadCode("shader_body { ret=(tex2D(sampler_fc_rand00,uv).rgb+tex2D(sampler_fw_rand00,uv).rgb"
                   "+tex2D(sampler_pc_rand00,uv).rgb+tex2D(sampler_pw_rand00,uv).rgb)*0.25; }");
    mixed.LoadTexturesAndCompile(state);
    for (const auto& mode : std::vector<std::string>{"fw_", "fc_", "pw_", "pc_"})
        BoundTexture(mixed, state, mode + "rand00", mode[1]=='c' ? GL_CLAMP_TO_EDGE : GL_REPEAT,
                     mode[0]=='p' ? GL_NEAREST : GL_LINEAR);
    ExpectPixel(mixed, state, 64, 0);
    for (const auto& expression : std::vector<std::string>{
        "tex2D(sampler_pc_rand00_red,uv).rgb+tex2D(sampler_pc_rand00,uv).rgb",
        "tex2D(sampler_rand00_red,uv).rgb+tex2D(sampler_rand00_green,uv).rgb+tex2D(sampler_rand00,uv).rgb"})
    {
        MilkdropShader aliases(MilkdropShader::ShaderType::CompositeShader);
        aliases.LoadCode("shader_body { ret=" + expression + "; }");
        aliases.LoadTexturesAndCompile(state);
        ExpectPixel(aliases, state, expression.find("green") == std::string::npos ? 128 : 192, 0);
    }
    PresetState prefixFirst;
    Setup(prefixFirst, manager);
    MilkdropShader prefixed(MilkdropShader::ShaderType::CompositeShader);
    prefixed.LoadCode("shader_body { ret=(tex2D(sampler_fc_rand00,uv).rgb+tex2D(sampler_pw_rand00_red,uv).rgb)*0.5; }");
    prefixed.LoadTexturesAndCompile(prefixFirst);
    ExpectPixel(prefixed, prefixFirst, 64, 0);
    PresetState spelling;
    Setup(spelling, manager);
    MilkdropShader caseSensitive(MilkdropShader::ShaderType::CompositeShader);
    caseSensitive.LoadCode("sampler sampler_pc_rand00_red=sampler_state {AddressU=WRAP;};\n"
                           "shader_body { ret=tex2D(sampler_pc_RAND00,uv).rgb; }");
    caseSensitive.LoadTexturesAndCompile(spelling);
    BoundTexture(caseSensitive, spelling, "pc_RAND00", GL_CLAMP_TO_EDGE, GL_NEAREST);
    ExpectPixel(caseSensitive, spelling, 64, 0);
}

static void LifecycleControls(TextureManager& manager)
{
    PresetState state;
    Setup(state, manager);
    MilkdropShader first(MilkdropShader::ShaderType::CompositeShader);
    first.LoadCode("sampler sampler_rand00_red=sampler_state {AddressU=CLAMP;AddressV=CLAMP;};\n"
                   "shader_body { ret=tex2D(sampler_rand00_red,uv).rgb; }");
    first.LoadTexturesAndCompile(state);
    const auto selected = BoundTexture(first, state, "rand00_red");
    for (int frame = 0; frame < 3; ++frame)
    {
        state.renderContext.frame = frame;
        Check(BoundTexture(first, state, "rand00_red") == selected, "selection changed within a preset");
    }
    MilkdropShader reload(MilkdropShader::ShaderType::CompositeShader);
    reload.LoadCode("sampler sampler_pc_rand00_green = sampler_state {AddressU=WRAP;};\n"
                    "shader_body { ret=tex2D(sampler_pc_rand00_green,uv).rgb; }");
    reload.LoadTexturesAndCompile(state);
    Check(BoundTexture(reload, state, "pc_rand00_green", GL_CLAMP_TO_EDGE, GL_NEAREST) == selected,
          "reload discarded the preset slot's image");
    ExpectPixel(reload, state, 64, 0);
    PresetState next;
    Setup(next, manager);
    MilkdropShader switched(MilkdropShader::ShaderType::CompositeShader);
    switched.LoadCode("shader_body { ret=tex2D(sampler_rand00_green,uv).rgb; }");
    switched.LoadTexturesAndCompile(next);
    Check(BoundTexture(switched, next, "rand00_green") != selected, "new preset inherited the old slot");
    ExpectPixel(switched, next, 0, 128);
    TextureManager empty(std::vector<std::string>{});
    Check(empty.GetRandomTexture("rand00").Empty(), "empty texture path selected an image");
    PresetState missing;
    Setup(missing, empty);
    MilkdropShader rejected(MilkdropShader::ShaderType::CompositeShader);
    rejected.LoadCode("shader_body { ret=tex2D(sampler_rand00,uv).rgb; }");
    bool failed = false;
    try { rejected.LoadTexturesAndCompile(missing); }
    catch (const ShaderException&) { failed = true; }
    Check(failed, "missing random asset unexpectedly compiled with a substitute texture");
}

static void PresetControls()
{
    const fs::path assets(BUNDLED_ASSETS);
    TextureManager manager({(assets / "textures").string()});
    for (const char* name : {
         "EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3 2.milk",
         "EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3.milk",
         "midgitstraights of majillaen - featy sweet.milk"})
    {
        PresetFileParser parsed;
        const auto path = assets / "presets" / name;
        Check(parsed.Read(path.string()), "exact preset did not parse");
        PresetState state;
        state.Initialize(parsed);
        Setup(state, manager);
        state.renderContext.viewportSizeX = 128;
        state.renderContext.viewportSizeY = 96;
        auto main = std::make_shared<Texture>("main", 128, 96, false);
        state.mainTexture = main;
        MilkdropShader warp(MilkdropShader::ShaderType::WarpShader);
        warp.LoadCode(state.warpShader);
        warp.LoadTexturesAndCompile(state);
        MilkdropShader comp(MilkdropShader::ShaderType::CompositeShader);
        comp.LoadCode(state.compositeShader);
        comp.LoadTexturesAndCompile(state);
        const auto start = observations.size();
        BoundTexture(comp, state, "rand00");
        BoundTexture(comp, state, "rand01");
        for (size_t i = start; i < observations.size(); ++i)
        {
            observations[i]["preset_path"] = path.string();
            observations[i]["stage"] = "composite";
        }
        Check(glGetError() == GL_NO_ERROR, "GL error before composite selection control");
        FinalComposite composite;
        composite.LoadCompositeShader(state);
        composite.CompileCompositeShader(state);
        Check(composite.HasCompositeShader(), "exact preset has no composite program");
        Check(glGetError() == GL_NO_ERROR, "GL error after composite selection control");
        libprojectM::MilkdropPreset::MilkdropPreset full(path.string());
        full.Initialize(state.renderContext);
        auto output = std::make_shared<Texture>("output", 128, 96, false);
        GLuint target{};
        glGenFramebuffers(1, &target);
        glBindFramebuffer(GL_FRAMEBUFFER, target);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output->TextureID(), 0);
        Check(full.SetOutputTarget(true, target), "exact preset cannot use the offscreen output target");
        Check(glGetError() == GL_NO_ERROR, "GL error before full render control");
        full.RenderFrame(state.audioData, state.renderContext);
        glDeleteFramebuffers(1, &target);
        const auto renderError = glGetError();
        presetResults.push_back({{"preset_path", path.string()}, {"raw_source_parse", "accepted"},
            {"custom_warp_compile", "accepted"}, {"custom_composite_compile", "accepted"},
            {"full_preset_load", "accepted"}, {"full_stage_selection", "retain debug compiler log; program unbound after draw"},
            {"full_render_gl_error", renderError},
            {"appearance_verified", false}});
        std::cout << name << " parsed; custom warp/comp compiled; full preset loaded; render_gl_error="
                  << renderError << " (appearance unverified)\n";
    }
}

// Allocation is part of Update: it must preserve distinct caller read/draw targets
// on the first frame, after resizing, and when reference-scale blur is enabled.
static void BlurFramebufferControls(TextureManager& manager)
{
    PresetState state;
    Setup(state, manager);
    PerFrameContext frame(state.globalMemory, &state.globalRegisters);
    frame.RegisterBuiltinVariables();
    frame.LoadStateVariables(state);
    *frame.blur1_min = *frame.blur2_min = *frame.blur3_min = 0;
    *frame.blur1_max = *frame.blur2_max = *frame.blur3_max = 1;
    *frame.blur1_edge_darken = 0;
    auto output = std::make_shared<Texture>("caller-output", 256, 192, false);
    GLuint read{}, draw{};
    glGenFramebuffers(1, &read);
    glGenFramebuffers(1, &draw);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, draw);
    glFramebufferTexture2D(GL_DRAW_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output->TextureID(), 0);
    for (const auto level : {BlurTexture::BlurLevel::Blur1, BlurTexture::BlurLevel::Blur3})
    {
        BlurTexture blur;
        blur.SetRequiredBlurLevel(level);
        struct Case { const char* name; int width; int height; float scale; };
        for (const auto& test : {
            Case{"first", 128, 96, 0}, Case{"same-size", 128, 96, 0},
            Case{"resize", 192, 128, 0}, Case{"scaled", 192, 128, 2},
            Case{"scaled-same-size", 192, 128, 2}})
        {
            auto source = std::make_shared<Texture>("source", test.width, test.height, false);
            glBindFramebuffer(GL_FRAMEBUFFER, read);
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, source->TextureID(), 0);
            Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "blur source incomplete");
            glClearColor(.25f, .5f, .75f, 1);
            glClear(GL_COLOR_BUFFER_BIT);
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER, draw);
            glViewport(0, 0, test.width, test.height);
            Check(glGetError() == GL_NO_ERROR, "GL error before blur update");
            blur.Update(*source, frame, test.scale);
            GLint actualRead{}, actualDraw{};
            glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &actualRead);
            glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &actualDraw);
            std::cout << "blur " << static_cast<int>(level) << ' ' << test.name
                      << " read=" << actualRead << '/' << read << " draw=" << actualDraw << '/' << draw << '\n';
            Check(actualRead == static_cast<GLint>(read) && actualDraw == static_cast<GLint>(draw),
                  std::string("blur changed caller framebuffer: ") + test.name);
            Check(glGetError() == GL_NO_ERROR, "GL error in blur update");
            glClear(GL_COLOR_BUFFER_BIT); // The next caller draw must still have a complete target.
            for (const auto& descriptor : blur.GetDescriptorsForBlurLevel(level))
            {
                glBindFramebuffer(GL_READ_FRAMEBUFFER, read);
                const auto texture = descriptor.Texture();
                glFramebufferTexture2D(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture->TextureID(), 0);
                glReadBuffer(GL_COLOR_ATTACHMENT0);
                unsigned char pixel[4]{};
                glReadPixels(texture->Width()/2, texture->Height()/2, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
                Check(glGetError() == GL_NO_ERROR, "blur readback failed");
                Check(std::abs(int(pixel[0])-64) <= 2 && std::abs(int(pixel[1])-128) <= 2 &&
                      std::abs(int(pixel[2])-191) <= 2, "blur lost constant source color");
            }
        }
    }
    glDeleteFramebuffers(1, &read);
    glDeleteFramebuffers(1, &draw);
}

static void MidgitRenderControls(TextureManager& manager)
{
    // Use the exact bundled source with the two generated TGA assets. JPEG decoder
    // warnings and production-random image choice are separate from FBO ownership.
    const fs::path path = fs::path(BUNDLED_ASSETS) / "presets" / "midgitstraights of majillaen - featy sweet.milk";
    PresetState state;
    Setup(state, manager);
    state.renderContext.viewportSizeX = 128;
    state.renderContext.viewportSizeY = 96;
    libprojectM::MilkdropPreset::MilkdropPreset preset(path.string());
    preset.Initialize(state.renderContext);
    auto output = std::make_shared<Texture>("output", 256, 192, false);
    GLuint target{};
    glGenFramebuffers(1, &target);
    glBindFramebuffer(GL_FRAMEBUFFER, target);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output->TextureID(), 0);
    Check(preset.SetOutputTarget(true, target), "midgit output target rejected");
    Check(glGetError() == GL_NO_ERROR, "GL error before midgit render");
    for (int frame = 0; frame < 4; ++frame)
    {
        state.renderContext.frame = frame;
        if (frame == 2)
        {
            state.renderContext.viewportSizeX = 192;
            state.renderContext.viewportSizeY = 128;
        }
        preset.RenderFrame(state.audioData, state.renderContext);
        const auto error = glGetError();
        std::cout << "midgit frame=" << frame << " render_gl_error=" << error << '\n';
        Check(error == GL_NO_ERROR, "midgit full render framebuffer failure");
        glBindFramebuffer(GL_READ_FRAMEBUFFER, target);
        unsigned char pixel[4]{};
        glReadPixels(64, 48, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
        Check(glGetError() == GL_NO_ERROR, "midgit output readback failed");
    }
    glDeleteFramebuffers(1, &target);
}

static void ManagerControls(TextureManager& manager)
{
    for (const auto& mode : std::vector<std::string>{"", "fw_", "fc_", "pw_", "pc_"})
    {
        const auto name = mode + "rand00_red";
        const auto desc = manager.GetRandomTexture(name);
        Check(!desc.Empty(), "prefix match was lost: " + name);
        Check(desc.Texture() == manager.GetTexture("red").Texture(), "wrong prefix asset: " + name);
        Check(desc.Sampler() == manager.GetSampler(name), "random sampler ignored named mode: " + name);
        Check(desc.SamplerDeclaration().find("sampler_" + name + ";") != std::string::npos,
              "descriptor lost full alias: " + name);
        Check(desc.TexSizeDeclaration().find("texsize_rand00_red;") != std::string::npos,
              "texsize did not use unqualified alias: " + name);
    }
    Check(manager.GetRandomTexture("rand00_absent").Empty(), "prefix miss did not remain empty");
    Check(manager.GetRandomTexture("pc_rand00_absent").Empty(), "qualified prefix miss selected an unrelated file");
}

static void StageControls(TextureManager& manager)
{
    PresetState state;
    Setup(state, manager);
    MilkdropShader warp(MilkdropShader::ShaderType::WarpShader);
    warp.LoadCode("shader_body { ret=tex2D(sampler_rand00_red,uv).rgb; }");
    warp.LoadTexturesAndCompile(state);
    const auto selected = state.randomTextureDescriptors.at(0).Texture();
    BoundTexture(warp, state, "rand00_red");
    for (const auto& mode : std::vector<std::string>{"fw_", "fc_", "pw_", "pc_"})
    {
        const auto alias = mode + "rand00";
        MilkdropShader comp(MilkdropShader::ShaderType::CompositeShader);
        comp.LoadCode("shader_body { ret=tex2D(sampler_" + alias + ",uv).rgb; }");
        comp.LoadTexturesAndCompile(state);
        Check(BoundTexture(comp, state, alias, mode[1] == 'c' ? GL_CLAMP_TO_EDGE : GL_REPEAT,
                           mode[0] == 'p' ? GL_NEAREST : GL_LINEAR) == static_cast<GLint>(selected->TextureID()),
              "same slot selected another texture across stages");
    }
}

static void ShorthandControls(TextureManager& manager)
{
    PresetState state;
    Setup(state, manager);
    MilkdropShader comp(MilkdropShader::ShaderType::CompositeShader);
    comp.LoadCode("shader_body { ret=tex2D(sampler_rand00_red,uv).rgb+tex2D(sampler_rand00,uv).rgb; }");
    comp.LoadTexturesAndCompile(state);
    Check(BoundTexture(comp, state, "rand00_red") == BoundTexture(comp, state, "rand00"),
          "short and long aliases selected different textures");
}

int main(int argc, char** argv)
{
    try
    {
        Check(argc == 3, "expected control name and isolated fixture directory");
        GLContext gl;
        Fixtures fixtures(argv[2]);
        TextureManager manager({fixtures.directory.string()});
        const std::string mode(argv[1]);
        if (mode == "manager") ManagerControls(manager);
        else if (mode == "stages") StageControls(manager);
        else if (mode == "shorthand") ShorthandControls(manager);
        else if (mode == "numerical") NumericalControls(manager);
        else if (mode == "lifecycle") LifecycleControls(manager);
        else if (mode == "presets") PresetControls();
        else if (mode == "blur-framebuffers") BlurFramebufferControls(manager);
        else if (mode == "midgit-render") MidgitRenderControls(manager);
        else throw std::runtime_error("unknown control");
        Check(glGetError() == GL_NO_ERROR, "GL error in random texture control");
        std::ofstream report(fixtures.directory.string() + ".json");
        report << json{{"profile", "host-real-GL-production-random-device-v1"},
            {"control", mode}, {"bindings", observations}, {"numerical_checks", numericalResults},
            {"preset_results", presetResults}, {"gl_renderer", reinterpret_cast<const char*>(glGetString(GL_RENDERER))},
            {"gl_version", reinterpret_cast<const char*>(glGetString(GL_VERSION))}}.dump(2) << '\n';
        report.close();
        for (const auto& result : presetResults)
            Check(result["full_render_gl_error"] == 0, "exact-preset render diagnostic failed; source-bound manifest preserved");
        std::cout << mode << " controls passed\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
