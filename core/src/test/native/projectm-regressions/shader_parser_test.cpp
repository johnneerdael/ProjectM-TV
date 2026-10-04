// Parse and generate with the production HLSL parser, without a GL context.
#include <GLSLGenerator.h>
#include <HLSLParser.h>
#include <HLSLTree.h>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct Case
{
    const char* name;
    const char* source;
    bool valid = true;
};

int main(int argc, char** argv)
{
    const std::vector<Case> cases = {
        {"sample-arithmetic", "float3 f() { float3 sample = float3(.2,.3,.4); return sample*sample*sample; }"},
        {"sample-assignment", "float3 f() { float3 sample = 0; sample = .5; sample += .1; return sample; }"},
        {"sample-shadow", "float sample = 1; float3 f() { float sample = .5; { float sample = .25; sample *= 2; } return sample; }"},
        {"sample-parentheses", "float3 f() { float3 sample = .5; return (sample).zyx; }"},
        {"modifier-control", "struct Input { sample float3 color : COLOR0; }; float3 f() { return .5; }"},
        {"identifier-control", "float3 f() { float3 sampled = .5; return sampled*sampled; }"},
        {"macro-declaration", "#define smp uniform sampler2D sampler_manyfish;\nsmp\nfloat3 f() { return tex2D(sampler_manyfish,float2(0,0)).xyz; }"},
        {"macro-statement", "#define texx float3(.25,.5,.75);\nfloat3 f() { float3 add=texx; return add; }"},
        {"macro-nested", "#define decl float3 value;\n#define alias decl\nalias\nfloat3 f() { value = .5; return value; }"},
        {"macro-function-declaration", "#define decl(n) float3 n;\ndecl(value)\nfloat3 f() { value = .5; return value; }"},
        {"macro-comment", "#define decl float3 /* gap */ value;\ndecl\nfloat3 f() { return value; }"},
        {"macro-parentheses", "#define value ((.1)+(.2))\nfloat3 f() { return value*.5; }"},
        {"macro-self-control", "#define value value\nfloat value;\nfloat3 f() { return value; }"},
        {"macro-function-control", "#define twice(x) ((x)*2)\n#define v .25\nfloat3 f() { return twice(v); }"},
        {"postfix-parenthesized-constructor", "float3 f() { return (float3(.1,.2,.3)*2).xyy; }"},
        {"postfix-nested", "float3 f() { return (((float3(.1,.2,.3)*2))).zyx.xyy; }"},
        {"postfix-index", "float3 f() { return (float3(.1,.2,.3)*2)[1]; }"},
        {"postfix-function", "float3 g() { return .5; } float3 f() { return (g()).zyx; }"},
        {"postfix-scalar", "float3 f() { return (0.5).xxx; }"},
        {"postfix-constructor-control", "float3 f() { return float3(.1,.2,.3).xyy; }"},
        {"parenthesized-binary-control", "float3 f() { return (float3(.1,.2,.3))*2+.1; }"},
        {"cast-control", "float3 f() { float v = .5; return (float3)v; }"},
        {"invalid-member", "float3 f() { return (float3(.1,.2,.3)*2).invalid; }", false},
        {"invalid-long-swizzle", "float3 f() { return (float3(.1,.2,.3)*2).xxxxx; }", false},
    };
    int failures = 0;
    for (const auto& test : cases)
    {
        if (argc == 3 && std::string(test.name).find(argv[2]) != 0) continue;
        M4::Allocator allocator;
        M4::HLSLTree tree(&allocator);
        M4::HLSLParser parser(&allocator, &tree);
        std::string input(test.source), preprocessed;
        input += "\nvoid PS(out float4 r : COLOR0) { r = float4(f(),1); }\n";
        const bool parsed = parser.ApplyPreprocessor(test.name, input.data(), input.size(), preprocessed) &&
                            parser.Parse(test.name, preprocessed.data(), preprocessed.size());
        bool ok = parsed == test.valid;
        if (parsed && test.valid)
        {
            M4::GLSLGenerator generator;
            ok = generator.Generate(&tree, M4::GLSLGenerator::Target_FragmentShader,
                                    M4::GLSLGenerator::Version_300_ES, "PS");
            if (ok && argc >= 2)
            {
                std::filesystem::create_directories(argv[1]);
                std::ofstream output(std::filesystem::path(argv[1]) / (std::string(test.name) + ".frag"));
                output << generator.GetResult();
                ok = output.good();
            }
        }
        std::cout << (ok ? "PASS " : "FAIL ") << test.name << std::endl;
        failures += !ok;
    }
    return failures ? 1 : 0;
}
