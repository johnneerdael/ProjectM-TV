"""Runtime name bindings must not pretend authored sampler directives apply."""
import numpy as np
from pathlib import Path

import test_native_reader
from shader_fields import ShaderFields
from field_math import evaluate
from shader_compat import check_shader
from pipeline_fields import SourcePipeline
from field_math import UnresolvedMath
import pytest


def source(declaration,body):
    return test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'+
        '\n'.join('comp_'+str(i)+'=`'+line for i,line in enumerate(
            (declaration+'\nshader_body {'+body+'}').splitlines(),1))+'\n')


def test_explicit_native_binding_ignores_declared_filter_and_wrap():
    parsed=source('sampler sampler_main=sampler_state {AddressU=CLAMP;AddressV=CLAMP;MinFilter=POINT;MagFilter=POINT;};',
                  'ret=tex2D(sampler_main,float2(1.25,.5)).xyz;')['sections']['comp_']
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
    field=model.lower(parsed['tree'],native_samplers={'sampler_main':'sampler2D'})
    assert model.complete,model.unknown
    seen=[]
    def sample(detail,coordinates):
        seen.append(detail)
        assert detail['sampling_policy']['wrap'] is True
        assert detail['sampling_policy']['linear'] is True
        return [np.mod(coordinates[0],1),coordinates[1],.75,1]
    np.testing.assert_allclose(evaluate(field,sample=sample),[.25,.5,.75])
    assert seen[0]['canonical_texture']=='main'


def test_missing_native_binding_keeps_sampler_state_unresolved():
    parsed=source('sampler sampler_main=sampler_state {AddressU=CLAMP;};',
                  'ret=tex2D(sampler_main,uv).xyz;')['sections']['comp_']
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
    field=model.lower(parsed['tree'])
    assert not model.complete
    assert field.op=='unknown'


def test_name_qualifiers_control_native_policy_instead_of_state_block():
    parsed=source('sampler sampler_fc_main=sampler_state {AddressU=WRAP;AddressV=WRAP;};',
                  'ret=tex2D(sampler_fc_main,float2(1.25,.5)).xyz;')['sections']['comp_']
    model=ShaderFields(stage='composite',frame=3,warp_reads_blur=False)
    field=model.lower(parsed['tree'],native_samplers={'sampler_fc_main':'sampler2D'})
    assert model.complete,model.unknown
    def sample(detail,coordinates):
        assert detail['sampling_policy']['wrap'] is False
        return [np.clip(coordinates[0],0,1),coordinates[1],.75,1]
    np.testing.assert_allclose(evaluate(field,sample=sample),[1,.5,.75])


def compatibility(parsed):
    native=Path(__file__).resolve().parents[2]/'build/milk-analyzer/native'
    return check_shader(parsed['sections']['comp_']['source'],stage='composite',profile='glsl330',
        translator=native/'milk-shader-translate',validator=Path('/opt/homebrew/bin/glslangValidator'),
        samplers={'sampler_main':'sampler2D'},texture_sizes=[])


def test_source_pipeline_only_binds_state_after_source_matched_compiler_acceptance():
    parsed=source('', '\nsampler sampler_main = sampler_state {AddressU=CLAMP;};\n'
                  'ret=tex2D(sampler_main,float2(1.25,.5)).xyz;\n')
    proof=compatibility(parsed);assert proof['offline_accepted'] is True
    initial=np.broadcast_to([.25,.5,.75,1],(16,16,4)).copy()
    pipeline=SourcePipeline.from_source(parsed,profile='glsl330',compatibility={'composite':proof},
        initial_feedback=initial,warp_reads_blur=False,blur_levels=0,quantize=False)
    result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,decay=1)
    np.testing.assert_allclose(result.display,initial,atol=1e-6)
    assert result.history['composite_kind']=='custom_composite'


def test_multiline_rejection_predicts_default_composite_not_authored_colour():
    parsed=source('sampler sampler_main=sampler_state {\nAddressU=CLAMP;\n};',
                  'ret=float3(.9,.1,.2);')
    proof=compatibility(parsed);assert proof['offline_accepted'] is False
    initial=np.broadcast_to([.25,.5,.75,1],(16,16,4)).copy()
    pipeline=SourcePipeline.from_source(parsed,profile='glsl330',compatibility={'composite':proof},
        initial_feedback=initial,warp_reads_blur=False,blur_levels=0,quantize=False)
    result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,decay=1)
    np.testing.assert_allclose(result.display,initial,atol=1e-6)
    assert result.history['composite_kind']=='default_composite'


def test_old_ast_only_proof_cannot_enable_sampler_state_binding():
    parsed=source('', '\nsampler sampler_main=sampler_state {AddressU=CLAMP;};\n'
                  'ret=tex2D(sampler_main,float2(1.25,.5)).xyz;\n')
    proof=compatibility(parsed)
    proof['offline_accepted']=True
    proof['translation'].pop('sampler_reference_body_sha256',None)
    proof['translation'].pop('referenced_samplers',None)
    with pytest.raises(UnresolvedMath,match='stage selection'):
        SourcePipeline.from_source(parsed,profile='glsl330',compatibility={'composite':proof},
            initial_feedback=np.zeros((16,16,4)),warp_reads_blur=False,blur_levels=0)
