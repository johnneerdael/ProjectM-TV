from pathlib import Path
from generate_composite_adapter import generate

def test_split_buffer_native_math_omits_only_gpu_uploads(tmp_path):
    engine=tmp_path/'engine';folder=engine/'src/libprojectM/MilkdropPreset';folder.mkdir(parents=True)
    context=engine/'src/libprojectM/Renderer';context.mkdir();(context/'RenderContext.hpp').write_text('context')
    (folder/'FinalComposite.cpp').write_text("""void FinalComposite::InitializeMesh(const PresetState& presetState)
{
 auto& vertices=m_compositeMesh.Vertices();
 vertices[0]={.25f,.75f};
 // Update mesh geometry and indices.
 m_compositeMesh.Update();
 m_radiusAngle.Update();
}
float FinalComposite::SquishToCenter(float x,float exponent){return x;}
void FinalComposite::ApplyHueShaderColors(const PresetState& presetState){
 auto& colors=m_compositeMesh.Colors();
 colors[0]={1,0,0,1};
 // Only update color buffer.
 m_compositeMesh.Bind();
 m_compositeMesh.Colors().Update();
}
} // namespace MilkdropPreset
""")
    (folder/'PresetState.cpp').write_text('    std::uniform_int_distribution<> distrib(0, std::numeric_limits<int>::max());\n    hueRandomOffsets[3] = distrib(randomGenerator);\n')
    output=tmp_path/'generated.hpp';generate(engine,output);text=output.read_text()
    assert '#define MILK_COMPOSITE_SPLIT_MESH 1' in text
    assert 'vertices[0]={.25f,.75f};' in text
    assert 'colors[0]={1,0,0,1};' in text
    assert 'm_compositeMesh.Update()' not in text
    assert 'm_radiusAngle.Update()' not in text
    assert 'm_compositeMesh.Bind()' not in text
    assert '.Colors().Update()' not in text
