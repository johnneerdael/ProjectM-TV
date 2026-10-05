"""Extract native composite CPU math; omit the final GL buffer upload only."""
import argparse
import hashlib
from pathlib import Path


def generate(engine,output):
    source=(engine/'src/libprojectM/MilkdropPreset/FinalComposite.cpp').read_text()
    context=(engine/'src/libprojectM/Renderer/RenderContext.hpp').read_bytes()
    start=source.index('void FinalComposite::InitializeMesh(')
    end=source.index('    // Store indices.',start)
    mesh=source[start:end]+'}\n'
    start=source.index('float FinalComposite::SquishToCenter(')
    end=source.index('} // namespace MilkdropPreset',start)
    math=source[start:end]
    output.write_text('#pragma once\n'+
        f'inline constexpr const char* kCompositeSourceSha="{hashlib.sha256(source.encode()).hexdigest()}";\n'+
        f'inline constexpr const char* kCompositeBodiesSha="{hashlib.sha256((mesh+math).encode()).hexdigest()}";\n'+
        f'inline constexpr const char* kCompositeRenderContextSha="{hashlib.sha256(context).hexdigest()}";\n'+mesh+math)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();generate(args.engine,args.output)
