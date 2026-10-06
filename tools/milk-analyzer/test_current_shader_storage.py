"""Live current reader/compiler controls paired with historical source snapshots."""
import os
import json
from pathlib import Path
import subprocess
import tempfile
import numpy as np
import pytest
import test_native_reader
from analyzer_test_profiles import validator_path
from field_math import evaluate, UnresolvedMath
from shader_fields import ShaderFields
from shader_compat import check_shader
from stage_resolution import resolve_stages


READER = Path(os.environ.get("MILK_TEST_CURRENT_BINARIES",test_native_reader.READER.parent))/"milk-native-reader"


def source(code):
    records=''.join(f'comp_{i}=`{line}\n' for i,line in enumerate(code.splitlines(),1))
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'current.milk'
        path.write_text('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\n'+records)
        return json.loads(subprocess.check_output([str(READER),str(path)]))


def lower(code):
    section=source(code)['sections']['comp_']
    assert section['status']=='parsed',section
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False,
                       array_initializer_policy=section['array_initializer_policy'])
    return model,model.lower(section['tree'])


@pytest.mark.parametrize('code,expected',[
    ('shader_body {q18=1;ret=q19;}',[.4]*3),
    ('shader_body {q18+=1;ret=q18;}',[3]*3),
    ('shader_body {q18++;ret=q18;}',[3]*3),
])
def test_current_writable_uniform_copy_retains_supplied_components(code,expected):
    model,result=lower(code)
    assert model.complete,model.unknown
    with pytest.raises(UnresolvedMath,match='missing symbolic'):
        evaluate(result)
    np.testing.assert_allclose(evaluate(result,inputs={'_qe':[0,2,.4,0]}),expected)


@pytest.mark.parametrize('code',[
    'shader_body {float g;{float g=g;ret=g;}}',
    'shader_body {float3 back;float a=dot(back,float3(1)),b=a;ret=b;}',
    'shader_body {float2 uv3;float noise=tex2D(sampler_main,uv3).x;ret=noise;}',
    'shader_body {float2 rs;float2 a=0*rs;ret=float3(rs,0);}',
])
def test_current_live_local_reads_require_initialized_storage(code):
    model,result=lower(code)
    assert not model.complete
    assert result.op=='unknown'


@pytest.mark.parametrize('expression',['0*rs','rs*0','0*rs.xy'])
def test_current_literal_zero_masks_local_storage_without_external_input(expression):
    model,result=lower('shader_body {float2 rs;ret=float3('+expression+',0);}')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[0,0,0])


@pytest.mark.parametrize('profile',['glsl330','gles300'])
@pytest.mark.parametrize('code',[
    'shader_body {q18++;ret=q18;}',
    'shader_body {float a[3]={1,2,3};ret=a[0];}',
    'shader_body {float2 a[2]={1,2,3,4};ret=a[0].x;}',
    'sampler sampler_main=sampler_state {\nAddressU=CLAMP;\n};\nshader_body {ret=float3(.9,.1,.2);}',
])
def test_current_repaired_translation_selects_custom_stage(code,profile):
    parsed=source(code)
    result=check_shader(parsed['sections']['comp_']['source'],stage='composite',profile=profile,
        translator=READER.parent/'milk-shader-translate',validator=validator_path(),
        samplers={'sampler_main':'sampler2D'},texture_sizes=['texsize_main'])
    assert result['offline_accepted'],result
    assert result['predicted_stage']=='custom_composite'
    plan=resolve_stages(parsed,profile=profile,compatibility={'composite':result})
    assert plan['composite']['kind']=='custom_composite'
    assert result['native_driver_verified'] is False
    result['source_sha256']='0'*64
    assert resolve_stages(parsed,profile=profile,compatibility={'composite':result})['composite']['kind']=='unknown'


@pytest.mark.parametrize('profile',['glsl330','gles300'])
def test_current_invalid_shader_still_selects_profile_bound_fallback(profile):
    parsed=source('shader_body {ret=missing_function(1);}')
    result=check_shader(parsed['sections']['comp_']['source'],stage='composite',profile=profile,
        translator=READER.parent/'milk-shader-translate',validator=validator_path(),
        samplers={'sampler_main':'sampler2D'},texture_sizes=['texsize_main'])
    assert result['offline_accepted'] is False
    plan=resolve_stages(parsed,profile=profile,compatibility={'composite':result})
    assert plan['composite']['kind']=='default_composite'
    assert plan['composite']['conditional_on_native_profile']



def test_current_renderer_decimal_literal_retains_exact_float32_value():
    model,result=lower('shader_body {ret=float3(16777216.);}')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[16777216]*3)
