// Exercise production formatting and AST emission, including signed zero and locale independence.
#include <Engine.h>
#include <GLSLGenerator.h>
#include <HLSLParser.h>
#include <HLSLTree.h>

#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <locale>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

static uint32_t Bits(float value)
{
    uint32_t bits;
    std::memcpy(&bits, &value, sizeof(bits));
    return bits;
}

static std::string Format(float value)
{
    char buffer[64];
    const int length = M4::String_FormatFloat(buffer, sizeof(buffer), value);
    if (length <= 0 || length >= int(sizeof(buffer))) throw std::runtime_error("literal formatting failed");
    return buffer;
}

static void RoundTrip(float value)
{
    const std::string text = Format(value);
    const std::string number = text.substr(6, text.size() - 7);
    std::istringstream input(number);
    input.imbue(std::locale::classic());
    double parsedDouble = 0;
    input >> parsedDouble;
    const float parsed = static_cast<float>(parsedDouble);
    if (input.fail() || !input.eof() || Bits(parsed) != Bits(value))
        throw std::runtime_error("float32 round-trip lost bits: " + std::to_string(Bits(value)) + " -> " + text);
    if (number.find_first_of(".eE") == std::string::npos)
        throw std::runtime_error("float literal emitted as integer: " + text);
}

struct CommaDecimal : std::numpunct<char>
{
    char do_decimal_point() const override { return ','; }
    char do_thousands_sep() const override { return '.'; }
    std::string do_grouping() const override { return "\3"; }
};

int main(int argc, char** argv)
{
    try
    {
        const std::vector<float> values = {
            1.00000011920928955078125f, 4194304.0f, 0.0f, -0.0f, 1.0f, -1.0f,
            std::nextafter(1.0f, 0.0f), .3456787f, .2233333f, .7464526f, .9875432f,
            6.2831853f, 3.14159265f, 1.0078125f, 1e-30f, -1e30f,
            std::numeric_limits<float>::min(), std::numeric_limits<float>::denorm_min(),
            std::numeric_limits<float>::max(), std::numeric_limits<float>::lowest()};
        for (float value : values) RoundTrip(value);
        std::mt19937 rng(0x3f800001);
        int finite = 0;
        for (int i = 0; i < 100000; ++i)
        {
            const uint32_t bits = rng();
            float value;
            std::memcpy(&value, &bits, sizeof(value));
            if (std::isfinite(value)) { RoundTrip(value); ++finite; }
        }
        const auto previous = std::locale();
        std::locale::global(std::locale(previous, new CommaDecimal));
        for (float value : values) RoundTrip(value);
        std::locale::global(previous);

        // Formatter retains diagnostic nan/inf text; generator must reject it before emission.
        for (float value : {std::numeric_limits<float>::infinity(), -std::numeric_limits<float>::infinity(),
                            std::numeric_limits<float>::quiet_NaN()})
        {
            const std::string text = Format(value);
            if (text.find(std::isnan(value) ? "nan" : "inf") == std::string::npos)
                throw std::runtime_error("nonfinite value silently changed: " + text);
        }
        for (float value : {std::numeric_limits<float>::infinity(), -std::numeric_limits<float>::infinity(),
                            std::numeric_limits<float>::quiet_NaN()})
        {
            M4::Allocator allocator;
            M4::HLSLTree tree(&allocator);
            M4::HLSLParser parser(&allocator, &tree);
            const std::string source = "float value=.5; void PS(out float4 r:COLOR0){float inf=.5;float nan=.25;r=float4(value,inf,nan,1);}";
            if (!parser.Parse("nonfinite-control", source.c_str(), source.size())) throw std::runtime_error("nonfinite control parse failed");
            static_cast<M4::HLSLLiteralExpression*>(tree.FindGlobalDeclaration("value")->assignment)->fValue = value;
            M4::GLSLGenerator generator;
            if (generator.Generate(&tree, M4::GLSLGenerator::Target_FragmentShader,
                                   M4::GLSLGenerator::Version_300_ES, "PS"))
                throw std::runtime_error("nonfinite literal accepted as authored inf/nan identifier");
        }

        // Mutate a real parsed AST so generator coverage includes negative literal nodes,
        // which ordinary authored negatives represent as unary operators.
        for (size_t i = 0; i < values.size(); ++i)
        {
            M4::Allocator allocator;
            M4::HLSLTree tree(&allocator);
            M4::HLSLParser parser(&allocator, &tree);
            const std::string source = "float value=.5; void PS(out float4 r:COLOR0){int n=7;bool b=true;r=float4(value,n,b,1);}";
            if (!parser.Parse("float-control", source.c_str(), source.size())) throw std::runtime_error("control parse failed");
            auto* literal = static_cast<M4::HLSLLiteralExpression*>(tree.FindGlobalDeclaration("value")->assignment);
            literal->fValue = values[i];
            M4::GLSLGenerator generator;
            if (!generator.Generate(&tree, M4::GLSLGenerator::Target_FragmentShader,
                                    M4::GLSLGenerator::Version_300_ES, "PS")) throw std::runtime_error("control generation failed");
            const std::string glsl = generator.GetResult();
            if (glsl.find(Format(values[i])) == std::string::npos || glsl.find("int n = int( 7 );") == std::string::npos ||
                glsl.find("bool b = bool( true );") == std::string::npos) throw std::runtime_error("AST literal emission mismatch:\n" + glsl);
            if (argc == 2)
            {
                std::filesystem::create_directories(argv[1]);
                std::ofstream out(std::filesystem::path(argv[1]) / ("float-" + std::to_string(i) + ".frag"));
                out << glsl;
                if (!out.good()) throw std::runtime_error("cannot write GLSL control");
            }
        }
        std::cout << values.size() << " boundary values and " << finite << " random finite float32 values round-trip; AST/locale controls passed\n";
        return 0;
    }
    catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
