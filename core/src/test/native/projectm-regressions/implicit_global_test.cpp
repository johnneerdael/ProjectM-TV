// Classification must preserve HLSL input storage, not initialize arbitrary locals.
#include <HLSLParser.h>
#include <HLSLTree.h>
#include <GLSLGenerator.h>
#include <iostream>
#include <stdexcept>
#include <string>

int main() {
    M4::Allocator allocator;
    M4::HLSLTree tree(&allocator);
    M4::HLSLParser parser(&allocator,&tree);
    const std::string source="float3 mus; float dist_c; float2 uv3; float a=.1,b; static float s; "
        "float3 f() { float local; local=.25; float before=dist_c; dist_c=.4; uv3=.4*cos(42*uv3); return mus+before+uv3.x+local+a+b; } "
        "void PS(out float4 r:COLOR0) { r=float4(f(),1); }";
    if (!parser.Parse("globals",source.data(),source.size())) return 1;
    tree.ReplaceUniformsAssignments();
    const auto* mus=tree.FindGlobalDeclaration("mus");
    const auto* dist=tree.FindGlobalDeclaration("dist_c");
    const auto* uv3=tree.FindGlobalDeclaration("uv3");
    if (!(mus->type.flags & M4::HLSLTypeFlag_Uniform) ||
        !(dist->type.flags & M4::HLSLTypeFlag_Uniform) ||
        !(uv3->type.flags & M4::HLSLTypeFlag_Uniform)) {
        std::cerr<<"Plain global inputs lost uniform classification\n";return 1;
    }
    if ((tree.FindGlobalDeclaration("a")->type.flags | tree.FindGlobalDeclaration("s")->type.flags) & M4::HLSLTypeFlag_Uniform) {
        std::cerr<<"Initialized/static controls became implicit inputs\n";return 1;
    }
    M4::GLSLGenerator generator;
    if (!generator.Generate(&tree,M4::GLSLGenerator::Target_FragmentShader,M4::GLSLGenerator::Version_300_ES,"PS")) return 1;
    const std::string glsl=generator.GetResult();
    for (const char* declaration:{"uniform vec3 mus;","uniform float dist_c;","uniform vec2 uv3;","uniform float b;"})
        if(glsl.find(declaration)==std::string::npos){std::cerr<<"Missing "<<declaration<<"\n";return 1;}
    if(glsl.find("uniform float local")!=std::string::npos){std::cerr<<"Local promoted\n";return 1;}
    std::cout<<"Implicit global classification and controls passed\n";
}
