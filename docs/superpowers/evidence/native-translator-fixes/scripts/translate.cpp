// Translates each HLSL file named on stdin to GLES 3.00 GLSL as MilkdropShader does; writes <out>/<base>.frag.
#include <GLSLGenerator.h>
#include <HLSLParser.h>
#include <HLSLTree.h>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
int main(int argc, char** argv)
{
    std::string out = argv[1], path;
    while (std::getline(std::cin, path))
    {
        std::ifstream in(path);
        std::stringstream buffer; buffer << in.rdbuf();
        std::string src = buffer.str();
        auto base = path.substr(path.find_last_of('/') + 1);
        base = base.substr(0, base.size() - 5);
        M4::Allocator allocator;
        M4::HLSLTree tree(&allocator);
        M4::HLSLParser parser(&allocator, &tree);
        M4::GLSLGenerator generator;
        if (!parser.Parse("", src.c_str(), src.size())) { std::cout << "\n@@" << base << "\tPARSE_FAIL\n"; continue; }
        if (!generator.Generate(&tree, M4::GLSLGenerator::Target_FragmentShader, M4::GLSLGenerator::Version_300_ES, "PS",
                                M4::GLSLGenerator::Options(M4::GLSLGenerator::Flag_AlternateNanPropagation)))
        { std::cout << "\n@@" << base << "\tGEN_FAIL\n"; continue; }
        std::ofstream(out + "/" + base + ".frag") << generator.GetResult();
        std::cout << "\n@@" << base << "\tOK\n";
    }
}
