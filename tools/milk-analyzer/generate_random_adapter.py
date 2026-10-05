"""Extract pinned shader random initialization/math into a data-only adapter."""
import argparse
import hashlib
from pathlib import Path


def generate(engine: Path, output: Path) -> None:
    raw = (engine / 'src/libprojectM/MilkdropPreset/MilkdropShader.cpp').read_bytes()
    source = raw.decode()
    start = source.index('static auto floatRand = ')
    end = source.index('\n', start)
    random_function = source[start:end]
    if random_function.count('rand()') != 1:
        raise ValueError('native random expression changed')
    # Count calls without changing rand's implementation or arithmetic.
    random_function = random_function.replace('rand()', 'countedRand()')
    start = source.index('MilkdropShader::MilkdropShader(')
    end = source.index('void MilkdropShader::LoadCode(', start)
    constructor = source[start:end]
    start = source.index('    m_shader.SetUniformFloat4("rand_frame"')
    frame_cache = '    const bool reuseRandom =' in source
    if frame_cache:
        start = source.index('    const bool reuseRandom =')
    end = source.index('    m_shader.SetUniformFloat4("_c0"', start)
    vectors = source[start:end]
    start = source.index('    std::array<glm::mat4, 24> tempMatrices{};')
    end = source.index('    // set program uniform "_q', start)
    matrices = source[start:end]
    bodies = constructor + vectors + matrices
    glm_root = engine / 'vendor/glm'
    glm_hash = hashlib.sha256()
    for path in sorted(glm_root.rglob('*')):
        if path.is_file():
            glm_hash.update(str(path.relative_to(glm_root)).encode() + b'\0')
            glm_hash.update(hashlib.sha256(path.read_bytes()).digest())
    renderer = (engine / 'src/libprojectM/Renderer/Shader.cpp').read_bytes()
    output.write_text('#pragma once\n' +
        f'inline constexpr const char* kRandomSourceSha="{hashlib.sha256(raw).hexdigest()}";\n' +
        f'inline constexpr const char* kRandomBodiesSha="{hashlib.sha256(bodies.encode()).hexdigest()}";\n' +
        f'inline constexpr const char* kRandomGlmSha="{glm_hash.hexdigest()}";\n' +
        f'inline constexpr const char* kRandomUploadSourceSha="{hashlib.sha256(renderer).hexdigest()}";\n' +
        f'inline constexpr bool kRandomFrameCache={str(frame_cache).lower()};\n' +
        random_function + '\n' + constructor +
        'void MilkdropShader::LoadRandomVariables(float floatTime, const PresetState& presetState) {\n' + vectors + matrices + '}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    generate(args.engine, args.output)
