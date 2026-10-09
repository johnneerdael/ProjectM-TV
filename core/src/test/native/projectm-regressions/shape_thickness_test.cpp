// Actual production draws; expected geometry follows MilkDrop's independent
// per-instance pass order and preserves the current Native I23 width policy.
// Source preparation only: these controls have not been built or run.
#include "gl_context.hpp"
#include <MilkdropPreset/CustomShape.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/GeometryTargets.hpp>
#include <Renderer/Framebuffer.hpp>
#include <Renderer/ShaderCache.hpp>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
using RGBA = std::array<float, 4>;
using XY = std::array<float, 2>;
static void Check(bool value, const std::string& message)
{
    if (!value) throw std::runtime_error(message);
}
#include "shape_attribute_probe.hpp"
namespace libprojectM {
class FeedbackDetailTestAccess {
public:
    static void DisableLines(LineRenderer& lines) { lines.m_usable = false; }
    static GLuint FillBuffer(const CustomShape& shape) { return shape.m_vboIdUntextured; }
    static double RawThickness(const CustomShape& shape) { return *shape.m_perFrameContext.thick; }
};
}
static auto Bits(double value) -> std::uint64_t
{
    std::uint64_t bits{}; std::memcpy(&bits, &value, sizeof(bits)); return bits;
}
static auto Value(std::uint64_t bits) -> double
{
    double value{}; std::memcpy(&value, &bits, sizeof(value)); return value;
}
static bool Near(float a, float b) { return std::abs(a - b) < 4e-6f; }
static void Equal(XY a, XY b, const char* label)
{
    Check(Near(a[0], b[0]) && Near(a[1], b[1]), label);
}
static GLint Target()
{
    GLint value{}; glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &value); return value;
}
static XY Position(const Attribute& attribute, size_t row)
{
    return {attribute.Component(row, 0), attribute.Component(row, 1)};
}
struct Capture {
    GLenum primitive{};
    GLint target{}, blendDestination{}, texture{}, sampler{};
    bool instanced{}, textured{};
    std::vector<XY> a, b;
    std::vector<RGBA> rgba, rgbaB;
    XY passOffset{};
    float halfWidth{}, antialias{};
    std::array<float, 16> projection{};
};
static std::vector<Capture> captured;
static PFNGLDRAWARRAYSPROC originalArrays{};
static PFNGLDRAWARRAYSINSTANCEDPROC originalInstanced{};
static PFNGLBUFFERDATAPROC originalBufferData{};
static GLuint shapeBuffer{};
static int uploads{};
static Capture Current(GLenum mode)
{
    Capture c; c.primitive = mode; c.target = Target();
    glGetIntegerv(GL_BLEND_DST_RGB, &c.blendDestination);
    GLint program{}; glGetIntegerv(GL_CURRENT_PROGRAM, &program);
    const GLint location = glGetUniformLocation(program, "vertex_transformation");
    Check(location >= 0, "live projection uniform");
    glGetUniformfv(program, location, c.projection.data());
    return c;
}
static void ObserveArrays(GLenum mode, GLint first, GLsizei count)
{
    auto c = Current(mode); Attribute p(0), rgba(1);
    for (int i = 0; i < count; ++i) {
        c.a.push_back(Position(p, first + i)); c.rgba.push_back(rgba.Color(first + i));
    }
    GLint program{}; glGetIntegerv(GL_CURRENT_PROGRAM, &program);
    c.textured = mode == GL_TRIANGLE_FAN && glGetUniformLocation(program, "texture_sampler") >= 0;
    if (c.textured) {
        glGetIntegerv(GL_TEXTURE_BINDING_2D, &c.texture);
        glGetIntegerv(GL_SAMPLER_BINDING, &c.sampler);
        Check(c.texture > 0 && c.sampler > 0, "owned textured fill texture/sampler");
        for (const auto entry : std::array<std::pair<GLenum, GLint>, 4>{{
                 {GL_TEXTURE_WRAP_S, GL_REPEAT}, {GL_TEXTURE_WRAP_T, GL_REPEAT},
                 {GL_TEXTURE_MIN_FILTER, GL_LINEAR}, {GL_TEXTURE_MAG_FILTER, GL_LINEAR}}}) {
            GLint actual{}; glGetSamplerParameteriv(c.sampler, entry.first, &actual);
            Check(actual == entry.second, "main-textured shape repeat/linear contract");
        }
    }
    captured.push_back(std::move(c)); originalArrays(mode, first, count);
}
static void ObserveInstanced(GLenum mode, GLint first, GLsizei count, GLsizei instances)
{
    Check(mode == GL_TRIANGLE_STRIP && first == 0 && count == 4, "Native quad primitive contract");
    auto c = Current(mode); c.instanced = true;
    Attribute a(1), b(2), rgbaA(4), rgbaB(5);
    Check(a.divisor == 1 && b.divisor == 1 && rgbaA.divisor == 1 && rgbaB.divisor == 1,
          "actual line instance attribute divisors");
    GLint program{}; glGetIntegerv(GL_CURRENT_PROGRAM, &program);
    for (const auto entry : std::array<std::pair<const char*, float*>, 3>{{
             {"pass_offset", c.passOffset.data()}, {"half_width", &c.halfWidth},
             {"antialias", &c.antialias}}}) {
        const GLint location = glGetUniformLocation(program, entry.first);
        Check(location >= 0, "live line uniform"); glGetUniformfv(program, location, entry.second);
    }
    for (int i = 0; i < instances; ++i) {
        c.a.push_back(Position(a, i)); c.b.push_back(Position(b, i));
        c.rgba.push_back(rgbaA.Color(i)); c.rgbaB.push_back(rgbaB.Color(i));
    }
    captured.push_back(std::move(c)); originalInstanced(mode, first, count, instances);
}
static void ObserveBufferData(GLenum target, GLsizeiptr size, const void* data, GLenum usage)
{
    GLint buffer{}; if (target == GL_ARRAY_BUFFER) glGetIntegerv(GL_ARRAY_BUFFER_BINDING, &buffer);
    if (target == GL_ARRAY_BUFFER && GLuint(buffer) == shapeBuffer && !data) ++uploads;
    originalBufferData(target, size, data, usage);
}
struct Hook {
    explicit Hook(GLuint buffer) {
        captured.clear(); uploads = 0; shapeBuffer = buffer;
        originalArrays = glad_glDrawArrays; originalInstanced = glad_glDrawArraysInstanced;
        originalBufferData = glad_glBufferData;
        glad_glDrawArrays = ObserveArrays; glad_glDrawArraysInstanced = ObserveInstanced;
        glad_glBufferData = ObserveBufferData;
    }
    ~Hook() {
        glad_glDrawArrays = originalArrays; glad_glDrawArraysInstanced = originalInstanced;
        glad_glBufferData = originalBufferData;
    }
};
struct Scenario {
    std::string name, expression;
    std::array<bool, 3> thick{};
    int saved{}, instances{3}, sides{4};
    bool replay{true}, overlap{}, opaque{}, textured{}, zeroBorder{}, fallback{}, aa{}, directNative{};
    int authoredWidth{64}, authoredHeight{64}, nativeWidth{128}, nativeHeight{128};
    std::array<std::uint64_t, 3> qBits{};
    bool checkRaw{};
};
static int PaletteId(int instance) { return instance % 3; }
static RGBA Palette(int instance) {
    const int id = PaletteId(instance);
    return {id == 0 ? 1.f : 0.f, id == 1 ? 1.f : 0.f, id == 2 ? 1.f : 0.f, .2f + .1f * id};
}
static void PaletteCheck(const RGBA& actual, int instance)
{
    const auto expected = Palette(instance);
    for (int k = 0; k < 4; ++k) Check(Near(actual[k], expected[k]), "instance float RGBA retained");
}
static XY Center(const Scenario& s, int instance)
{
    return {s.overlap ? 0.f : -.6f + .6f * PaletteId(instance), 0.f};
}
static XY Corner(const Scenario& s, int instance, int edge)
{
    constexpr float pi = 3.141592653589793f;
    const float angle = float(edge) / float(s.sides) * pi * 2.f + pi * .25f;
    const float aspectY = float(s.authoredHeight) / float(s.authoredWidth);
    const auto center = Center(s, instance);
    return {center[0] + .12f * cosf(angle) * aspectY, center[1] + .12f * sinf(angle)};
}
static XY Offset(int pass, float x, float y)
{
    return {(pass == 1 || pass == 2) ? x : 0.f, (pass == 2 || pass == 3) ? y : 0.f};
}
static void Projection(const Capture& c, int width, int height, XY translation = {0.f, 0.f})
{
    for (int i = 0; i < 16; ++i) {
        const float expected = i == 0 || i == 15 ? 1.f : i == 5 ? -1.f : i == 10 ? -.025f :
                               i == 12 ? 1.f / width + translation[0] : i == 13 ? -1.f / height - translation[1] : 0.f;
        Check(Near(c.projection[i], expected), "destination half-pixel projection retained");
    }
}
static void Run(ShaderCache& cache, const Scenario& s)
{
    PresetState state;
    std::ostringstream text;
    text << "[preset00]\nshapecode_0_enabled=1\nshapecode_0_sides=" << s.sides
         << "\nshapecode_0_num_inst=" << s.instances << "\nshapecode_0_textured=" << s.textured
         << "\nshapecode_0_thickOutline=" << s.saved << "\nshapecode_0_rad=.12\n"
         << "shape_0_init1=reg02+=1;\nshape_0_per_frame1=" << s.expression
         << "x=" << (s.overlap ? ".5" : ".2+.3*(instance%3)")
         << ";y=.5;a=" << (s.opaque ? 1 : 0) << ";a2=a;"
         << "border_r=equal(instance%3,0);border_g=equal(instance%3,1);border_b=equal(instance%3,2);"
         << "border_a=" << (s.zeroBorder ? "0" : ".2+.1*(instance%3)")
         << ";additive=equal(instance%2,1);reg00+=1;reg01=thick;reg03=rand(1000000);\n";
    std::istringstream input(text.str()); PresetFileParser parser;
    Check(parser.Read(input), s.name + ": real parser"); state.Initialize(parser);
    for (int i = 0; i < 3; ++i) state.frameQVariables[i] = Value(s.qBits[i]);
    auto& rc = state.renderContext;
    rc.shaderCache = &cache; rc.viewportSizeX = s.nativeWidth; rc.viewportSizeY = s.nativeHeight;
    rc.lineReferenceWidth = s.authoredWidth; rc.lineReferenceHeight = s.authoredHeight;
    rc.aspectX = 1; rc.aspectY = float(s.authoredHeight) / float(s.authoredWidth);
    rc.invAspectX = 1; rc.invAspectY = 1 / rc.aspectY; rc.lineAntialiasing = s.aa;
    state.LoadShaders(); Check(state.lineRenderer.Usable(), s.name + ": real line program");
    if (s.fallback) libprojectM::FeedbackDetailTestAccess::DisableLines(state.lineRenderer);
    const auto mainTexture = std::make_shared<Texture>("native-main", GL_TEXTURE_2D, 2, 2, 1,
        GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
    const auto authoredTexture = std::make_shared<Texture>("authored-main", GL_TEXTURE_2D, 2, 2, 1,
        GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
    const std::array<unsigned char, 16> pixels{{240,0,0,255, 0,160,0,255, 0,0,80,255, 40,120,200,255}};
    for (const auto& texture : {mainTexture, authoredTexture}) {
        glBindTexture(GL_TEXTURE_2D, texture->TextureID());
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 2, 2, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    }
    state.mainTexture = mainTexture;
    CustomShape shape(state); shape.Initialize(parser, 0); std::vector<std::string> warnings;
    shape.CompileCodeAndRunInitExpressions(warnings);
    Check(warnings.empty(), s.name + ": real shape compilation");
    Framebuffer canvas(1), native(1);
    canvas.CreateColorAttachment(0, 0, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE);
    native.CreateColorAttachment(0, 0, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE);
    canvas.SetSize(s.authoredWidth, s.authoredHeight); native.SetSize(s.nativeWidth, s.nativeHeight);
    GeometryTargets targets(state, canvas, 0, s.authoredWidth, s.authoredHeight,
                            authoredTexture, native, 0);
    native.Bind(0); const GLint nativeId = Target(); targets.Authored(); const GLint authoredId = Target();
    for (int frame = 0; frame < 2; ++frame) {
        native.Bind(0); glClearColor(0, 0, 0, 0); glClear(GL_COLOR_BUFFER_BIT);
        targets.Authored(); glClear(GL_COLOR_BUFFER_BIT);
        if (s.directNative) targets.Native();
        {
            Hook hook(libprojectM::FeedbackDetailTestAccess::FillBuffer(shape));
            shape.Draw(s.replay ? &targets : nullptr);
        }
        Check(glGetError() == GL_NO_ERROR, s.name + ": actual renderer GL error");
        Check(Target() == (s.directNative ? nativeId : authoredId),
              s.name + ": restore owned target after replay");
        Check(state.globalRegisters[0] == s.instances * (frame + 1) && state.globalRegisters[2] == 1,
              s.name + ": once-only per-instance/RNG equations, init once, replay unevaluated");
        if (s.checkRaw) {
            const auto expected = s.qBits[(s.instances - 1) % 3];
            Check(Bits(libprojectM::FeedbackDetailTestAccess::RawThickness(shape)) == expected &&
                  Bits(state.globalRegisters[1]) == expected,
                  s.name + ": preserve raw invalid/finite thickness and dependent equation");
        }
        if (s.instances == 100) Check(uploads > 1, s.name + ": actual bounded batch flush exercised");
        std::map<GLint, std::vector<const Capture*>> byTarget;
        for (const auto& c : captured) byTarget[c.target].push_back(&c);
        const int targetCount = s.replay ? 2 : 1;
        Check(int(byTarget.size()) == targetCount, s.name + ": only owned destinations");
        for (int target = 0; target < targetCount; ++target) {
            const bool nativePass = target == 1 || s.directNative;
            const int width = nativePass ? s.nativeWidth : s.authoredWidth;
            const int height = nativePass ? s.nativeHeight : s.authoredHeight;
            const bool quad = nativePass && !s.fallback;
            const float scale = std::max(1.f, std::sqrt(float(width) * height /
                                    (float(s.authoredWidth) * s.authoredHeight)));
            const auto& calls = byTarget[nativePass ? nativeId : authoredId];
            size_t cursor = 0;
            for (int instance = 0; instance < s.instances; ++instance) {
                Check(cursor < calls.size(), s.name + ": missing ordered fill");
                const auto& fill = *calls[cursor++];
                Check(fill.primitive == GL_TRIANGLE_FAN && !fill.instanced &&
                      int(fill.a.size()) == s.sides + 2, s.name + ": fill before own outline");
                Equal(fill.a[0], Center(s, instance), "prepared fill instance center");
                Check(Near(fill.rgba[0][3], s.opaque ? 1.f : 0.f), "preserve fill alpha");
                Check(fill.textured == s.textured, "textured versus untextured fill path");
                if (s.textured) Check(fill.texture == GLint((nativePass ? mainTexture : authoredTexture)->TextureID()),
                                      "destination owns correct main texture");
                Projection(fill, width, height);
                const GLint destination = instance % 2 ? GL_ONE : GL_ONE_MINUS_SRC_ALPHA;
                Check(fill.blendDestination == destination, "per-instance fill blend/order");
                const int passes = s.zeroBorder ? 0 : s.thick[instance % 3] ? 4 : 1;
                for (int pass = 0; pass < passes; ++pass) {
                    Check(cursor < calls.size(), s.name + ": missing evaluated outline pass");
                    const auto& border = *calls[cursor++];
                    Check(border.instanced == quad && border.blendDestination == destination,
                          "own outline blend/style before next fill");
                    const auto correction = s.replay && nativePass && s.fallback
                        ? Offset(pass, (1.f-scale)/width, (1.f-scale)/height) : XY{0.f,0.f};
                    Projection(border, width, height, correction);
                    Check(int(border.a.size()) == s.sides, "closed outline, no extra connectors");
                    const auto offset = Offset(pass,
                        1.f / (s.directNative ? s.nativeWidth : s.authoredWidth),
                        1.f / (s.directNative ? s.nativeHeight : s.authoredHeight));
                    if (quad) {
                        Check(border.primitive == GL_TRIANGLE_STRIP, "Native quad outline");
                        const auto nativeOffset = Offset(pass, scale / width, scale / height);
                        Equal(border.passOffset, nativeOffset, "retain Native I23 thick offset policy");
                        Check(Near(border.halfWidth, .5f * scale) && Near(border.antialias, s.aa ? 1.f : 0.f),
                              "target width/AA retained for each instance style");
                    } else Check(border.primitive == GL_LINE_LOOP, "authored/fallback loop primitive");
                    for (int edge = 0; edge < s.sides; ++edge) {
                        auto expected = Corner(s, instance, edge);
                        if (!quad) { expected[0] += offset[0]; expected[1] += offset[1]; }
                        Equal(border.a[edge], expected, "prepared per-pass positions retained");
                        PaletteCheck(border.rgba[edge], instance);
                        if (quad) {
                            Equal(border.b[edge], Corner(s, instance, (edge + 1) % s.sides),
                                  "no false inter-outline Native connector");
                            PaletteCheck(border.rgbaB[edge], instance);
                        }
                    }
                }
            }
            Check(cursor == calls.size(), s.name + ": no extra draw/grouped outline or replay");
        }
    }
    std::cout << s.name << " actual renderer control passed\n";
}

// Independent original49-instance source trace at frozen q2=q3=0,q32=1.
struct OriginalInstance{float x,y,rad;bool thick;float alpha;};
static OriginalInstance Original49(int instance){const int nx=instance%6,ny=instance/6;OriginalInstance o{.5f+(nx-3)/4.f,.5f+(ny-3)/4.f,.04f,false,1};if(instance>35&&instance<38)o={.5f-.47f*(instance%2-.5f),.5f,.06f,false,1};else if(instance>=38&&instance<45)o={.5f,.5f-.47f*((instance/3)%2-.5f),.06f,false,1};else if(instance>=45)o={.5f+((instance/2)%2-.5f)*.5f,.5f+(instance%2-.5f)*.5f,.04f,true,0};return o;}
static void City(ShaderCache&cache,const char*path){PresetFileParser parser;Check(parser.Read(path),"exact original parser");PresetState state;state.Initialize(parser);state.frameQVariables.fill(0);state.frameQVariables[31]=1;state.customShapePerFrameCode[0]+="reg00+=1;";auto&rc=state.renderContext;rc.shaderCache=&cache;rc.viewportSizeX=rc.viewportSizeY=128;rc.lineReferenceWidth=rc.lineReferenceHeight=64;rc.aspectX=rc.aspectY=rc.invAspectX=rc.invAspectY=1;state.LoadShaders();CustomShape shape(state);shape.Initialize(parser,0);std::vector<std::string>warnings;shape.CompileCodeAndRunInitExpressions(warnings);Check(warnings.empty(),"exact49 shape compilation");Framebuffer canvas(1),native(1);canvas.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);native.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);canvas.SetSize(64,64);native.SetSize(128,128);GeometryTargets targets(state,canvas,0,64,64,{},native,0);native.Bind(0);const int nativeId=Target();targets.Authored();const int canvasId=Target();{Hook hook(libprojectM::FeedbackDetailTestAccess::FillBuffer(shape));shape.Draw(&targets);}int authoredFills=0,nativeFills=0,loops=0,quads=0,segmentPasses=0;for(const auto&c:captured){if(c.primitive==GL_TRIANGLE_FAN){const int instance=c.target==canvasId?authoredFills++:nativeFills++;Check(instance<49,"exact49 fill count");const auto expected=Original49(instance);Equal(c.a[0],{expected.x*2-1,expected.y*-2+1},"exact49 source instance center");Check(Near(c.rgba[0][3],expected.alpha),"exact49 per-instance fill alpha");}else if(c.instanced){Check(c.target==nativeId,"city Native target");++quads;segmentPasses+=int(c.a.size());for(const auto&rgba:c.rgba)Check(Near(rgba[3],.2f),"city floating border alpha retained");}else{++loops;Check(c.target==canvasId,"city authored target");}}
 Check(authoredFills==49&&nativeFills==49&&loops==61&&quads==61&&segmentPasses==244,"original49 pass trace and captured Native61-call contract");Check(state.globalRegisters[0]==49,"no last-instance reuse or Native equation replay");Check(glGetError()==GL_NO_ERROR,"exact49 GL state");std::cout<<"city original49 source trace: authored61, Native61calls/244segment instances, fills49+49\n";}

static void Styles(ShaderCache& cache)
{
    for (bool replay : {false, true}) {
        const std::vector<Scenario> basics{
            {"alternating", "thick=equal(instance%3,1);", {false,true,false}, 0},
            {"dynamic-all-thick", "thick=1;", {true,true,true}, 0},
            {"dynamic-negative", "thick=-1;", {true,true,true}, 0},
            {"fraction-positive", "thick=.5;", {false,false,false}, 1},
            {"fraction-negative", "thick=-.5;", {false,false,false}, 1},
            {"zero-overrides-saved", "thick=0;", {false,false,false}, 1},
            {"static-positive", "", {true,true,true}, 1},
            {"static-zero", "", {false,false,false}, 0},
            {"static-negative-parsed-off", "", {false,false,false}, -1}
        };
        for (auto scenario : basics) { scenario.replay = replay; Run(cache, scenario); }
        for (const std::string mode : {"overlap", "opaque", "textured", "zero-border",
                                       "batch-flush", "line-fallback", "aa", "wide", "portrait"}) {
            Scenario s{"alternating-" + mode, "thick=equal(instance%3,1);", {false,true,false}, 0};
            s.replay = replay;
            if (mode == "overlap") s.overlap = true;
            if (mode == "opaque") { s.overlap = true; s.opaque = true; }
            if (mode == "textured") { s.overlap = true; s.opaque = true; s.textured = true; }
            if (mode == "zero-border") s.zeroBorder = true;
            if (mode == "batch-flush") { s.instances = 100; s.sides = 100; s.textured = true; }
            if (mode == "line-fallback") s.fallback = true;
            if (mode == "aa") s.aa = true;
            if (mode == "wide") {
                s.authoredWidth = 96; s.authoredHeight = 64; s.nativeWidth = 288; s.nativeHeight = 192;
            }
            if (mode == "portrait") {
                s.authoredWidth = 64; s.authoredHeight = 96; s.nativeWidth = 128; s.nativeHeight = 192;
            }
            Run(cache, s);
        }
        Scenario fallbackBatch{"fallback-batch-flush", "thick=equal(instance%3,1);", {false,true,false}, 0};
        fallbackBatch.replay = replay; fallbackBatch.fallback = true;
        fallbackBatch.instances = 100; fallbackBatch.sides = 100; Run(cache, fallbackBatch);
    }
    for (bool aa : {false, true}) for (bool fallback : {false, true}) {
        Scenario native{"direct-Native", "thick=equal(instance%3,1);", {false,true,false}, 0};
        native.replay = false; native.directNative = true; native.aa = aa; native.fallback = fallback;
        native.textured = true; Run(cache, native);
    }
}
static void Domain(ShaderCache& cache)
{
    struct Input { const char* name; std::uint64_t bits; bool defined, nonzero; };
    // Independent explicit expected results; no production helper or unsafe cast in this oracle.
    const std::vector<Input> inputs{
        {"positive-zero", UINT64_C(0x0000000000000000), true, false},
        {"negative-zero", UINT64_C(0x8000000000000000), true, false},
        {"positive-subnormal", UINT64_C(0x0000000000000001), true, false},
        {"negative-subnormal", UINT64_C(0x8000000000000001), true, false},
        {"positive-half", UINT64_C(0x3fe0000000000000), true, false},
        {"negative-half", UINT64_C(0xbfe0000000000000), true, false},
        {"positive-below-one", UINT64_C(0x3fefffffffffffff), true, false},
        {"negative-below-one", UINT64_C(0xbfefffffffffffff), true, false},
        {"positive-one", UINT64_C(0x3ff0000000000000), true, true},
        {"negative-one", UINT64_C(0xbff0000000000000), true, true},
        {"positive-one-half", UINT64_C(0x3ff8000000000000), true, true},
        {"negative-one-half", UINT64_C(0xbff8000000000000), true, true},
        {"positive-int-max", UINT64_C(0x41dfffffffc00000), true, true},
        {"positive-int-max-half", UINT64_C(0x41dfffffffe00000), true, true},
        {"positive-upper-predecessor", UINT64_C(0x41dfffffffffffff), true, true},
        {"positive-exclusive-bound", UINT64_C(0x41e0000000000000), false, false},
        {"negative-int-min", UINT64_C(0xc1e0000000000000), true, true},
        {"negative-int-min-half", UINT64_C(0xc1e0000000100000), true, true},
        {"negative-bound-predecessor", UINT64_C(0xc1e00000001fffff), true, true},
        {"negative-exclusive-bound", UINT64_C(0xc1e0000000200000), false, false},
        {"positive-max-finite", UINT64_C(0x7fefffffffffffff), false, false},
        {"negative-max-finite", UINT64_C(0xffefffffffffffff), false, false},
        {"positive-infinity", UINT64_C(0x7ff0000000000000), false, false},
        {"negative-infinity", UINT64_C(0xfff0000000000000), false, false},
        {"positive-NaN-payload", UINT64_C(0x7ff800000000cafe), false, false},
        {"negative-NaN-payload", UINT64_C(0xfff800000000cafe), false, false}
    };
    for (int saved : {0, 1}) for (const auto& input : inputs) {
        const bool thick = input.defined ? input.nonzero : saved > 0;
        Scenario s{std::string(input.name) + "-saved" + std::to_string(saved), "thick=q1;",
                   {thick,thick,thick}, saved};
        s.qBits.fill(input.bits); s.checkRaw = true; Run(cache, s);
    }
    for (int saved : {0, 1}) {
        // Invalid first instance must not inherit the final instance's evaluated style.
        Scenario s{"mixed-invalid-finite", "thick=if(equal(instance%3,0),q1,if(equal(instance%3,1),q2,q3));",
                   {saved > 0,false,true}, saved};
        s.qBits = {UINT64_C(0x7ff800000000cafe), UINT64_C(0x3fe0000000000000), UINT64_C(0xbff0000000000000)};
        s.checkRaw = true; Run(cache, s);
        s.name = "mixed-invalid-line-fallback"; s.fallback = true; Run(cache, s);
    }
}
int main(int argc, char** argv)
{
    try {
        GLContext gl; ShaderCache cache;
        const std::string mode = argc > 1 ? argv[1] : "style";
        if (mode == "style") Styles(cache);
        else if (mode == "domain") Domain(cache);
        else if (mode == "original") {
            Check(argc == 4, "original mode requires both exact city-lights preset paths");
            City(cache, argv[2]); City(cache, argv[3]);
        } else throw std::runtime_error("unknown shape-thickness control mode");
        std::cout << "actual per-instance thickness controls passed: " << mode << '\n';
    } catch (const std::exception& error) {
        std::cerr << "FAIL " << error.what() << '\n'; return 1;
    }
    return 0;
}
