"""Copy native CPU translation bodies; provide data-only shader/header views."""
import argparse
import hashlib
from pathlib import Path


def generate(engine: Path, output: Path) -> None:
    source = (engine/'src/libprojectM/MilkdropPreset/MilkdropShader.cpp').read_text()
    start = source.index('void MilkdropShader::PreprocessPresetShader(')
    end = source.index('void MilkdropShader::GetReferencedSamplers(', start)
    preprocess = source[start:end]
    start = source.index('void MilkdropShader::GetReferencedSamplers(')
    end = source.index('\n}',start)+2
    references = source[start:end]
    start = source.index('void MilkdropShader::UpdateMaxBlurLevel(')
    end = source.index('\n}',start)+2
    blur = source[start:end]
    start = source.index('void MilkdropShader::TranspileHLSLShader(')
    start = source.index('    M4::GLSLGenerator generator;', start)
    end = source.index('    // Now we have GLSL source', start)
    translation = source[start:end]
    output.write_text('#pragma once\n' +
        f'inline constexpr const char* kNativeShaderSourceSha = "{hashlib.sha256(source.encode()).hexdigest()}";\n' +
        f'inline constexpr const char* kNativePreprocessBodySha = "{hashlib.sha256(preprocess.encode()).hexdigest()}";\n' +
        f'inline constexpr const char* kNativeTranslationBodySha = "{hashlib.sha256(translation.encode()).hexdigest()}";\n' +
        f'inline constexpr const char* kNativeSamplerReferenceBodySha = "{hashlib.sha256(references.encode()).hexdigest()}";\n' +
        preprocess + '\n' + references + '\n' + blur + '\nstd::string targetTranslate(std::string program, const std::string& shaderTypeString,\n'
        '    const std::set<std::string>& samplerDeclarations, const std::set<std::string>& texSizeDeclarations) {\n' +
        translation + '\nreturn generator.GetResult();\n}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    generate(args.engine, args.output)
