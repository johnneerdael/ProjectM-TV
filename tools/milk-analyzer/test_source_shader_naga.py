"""Naga bridge is optional, source-bound and rejects unqualified semantics."""
import os
from pathlib import Path

import pytest

from source_shader_compiler import CompilerTools, analyze_case
from source_shader_naga import scalarize_output_interface
from test_source_shader_compiler import case, GLSL


HLSL = '''static float4 colour[2];
struct SPIRV_Cross_Output
{
    float4 colour[2] : SV_Target0;
};
void body() { colour[0]=1; colour[1]=2; }
SPIRV_Cross_Output main()
{
    SPIRV_Cross_Output stage_output;
    stage_output.colour = colour;
    return stage_output;
}
'''


def test_scalarization_preserves_global_array_and_values():
    result, count = scalarize_output_interface(HLSL)
    assert count == 2
    assert 'static float4 colour[2];' in result
    assert 'colour[0]=1; colour[1]=2;' in result
    assert 'float4 colour_inspection1 : SV_Target1;' in result
    assert 'stage_output.colour_inspection1 = colour[1];' in result


@pytest.mark.parametrize('source', [
    HLSL.replace('colour[1]=2', 'colour[2]=2'),
    HLSL.replace('colour[1]=2', 'colour[i]=2'),
    HLSL.replace('colour[2]', 'colour[3]'),
    HLSL.replace('stage_output.colour = colour;', ''),
    HLSL.replace('float4 colour[2] : SV_Target0;', 'half4 colour[2] : SV_Target0;'),
])
def test_other_output_accesses_are_not_silently_rewritten(source):
    with pytest.raises(ValueError, match='unqualified'):
        scalarize_output_interface(source)


@pytest.fixture
def naga_compiler():
    worker = os.environ.get('SOURCE_SHADER_NAGA_WORKER')
    if not worker or not Path(worker).is_file():
        pytest.skip('optional pinned Naga worker not configured')
    return CompilerTools(naga_worker=worker)


def test_official_typed_ir_full_validation_preserves_calls_conversions_samples(naga_compiler):
    glsl = GLSL.replace('out vec4 colour;', 'out vec4 colour[2];').replace(
        'colour = texture(sampler_main, uv) * helper(bass);',
        'colour[0] = texture(sampler_main, uv) * helper(bass); colour[1] = vec4(uv,0,1);')
    r = analyze_case(case(glsl), naga_compiler)['stages']['composite']['inspection']['naga']
    assert r['typed_ir']['status'] == 'validated_inspection_ir'
    assert r['typed_ir']['validation_flags'] == 'all'
    assert r['original_opengl_spirv_attempt']['status'] == 'unsupported'
    assert 'UnsupportedExecutionMode' in r['original_opengl_spirv_attempt']['reason']
    assert 'BindingCollision' in r['unadapted_vulkan_hlsl_attempt']['reason']
    assert r['sample_count_preserved'] and r['conversion_count_preserved']
    assert any('helper' in n for n in r['bridge_summary']['functions'])
    assert r['native_numeric_equivalence_verified'] is False
    assert any(f['info']['expressions'] for f in r['typed_ir']['functions'])
    assert r['typed_ir']['entries'][0]['info']['sampling_set']


def test_nonuniform_implicit_sample_validation_does_not_certify_native_semantics(naga_compiler):
    glsl = GLSL.replace('out vec4 colour;', 'out vec4 colour[1];').replace(
        'colour = texture(sampler_main, uv) * helper(bass);',
        'if (uv.x > .5) colour[0] = texture(sampler_main, uv); else colour[0] = vec4(0);')
    r = analyze_case(case(glsl), naga_compiler)['stages']['composite']['inspection']['naga']
    # This frontend/validator accepts this particular source. Keep the actual
    # nonuniform metadata and Auto sample instead of inventing a rejection.
    assert r['typed_ir']['status'] == 'validated_inspection_ir'
    assert any(e['uniformity']['non_uniform_result'] is not None
               for f in r['typed_ir']['functions'] for e in f['info']['expressions'])
    assert any(e.get('ImageSample', {}).get('level') == 'Auto'
               for f in r['typed_ir']['module']['functions'] for e in f['expressions'] if isinstance(e,dict))
    assert r['native_numeric_equivalence_verified'] is False
