"""Core policy: implicit globals retain uniform inputs and invocation copies."""
from pathlib import Path
import hashlib
import json
import subprocess
import pytest
import numpy as np
import test_native_reader
from shader_fields import ShaderFields
from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid
from equation_domains import q_uniform_domains

POLICY='projectmtv-implicit-extern-zero-v1'
CASES=[
 ('Serge + martin - crystal palace tunnel003.milk','f4ab74c7f561e50177b1b68ecf647045de78582ba378e39bb9295d26a55fd4e2','warp_'),
 ('martin - ludicrous speed.milk','9a99802ec59187a9f635f615db07622c5feaa15d02ed64beefb8156e68d48b22','warp_'),
 ('martin - mandelbox explorer - wreck diver nz+ liquititty.milk','2d767a8f65168592fc25b0e70accb968fa5b118296b64f66a62e5f889a9faddd','comp_'),
 ('martin - organic light.milk','71c481a0ebc470c3a9e717630cdd3785f4217248f81cbe6157cf1da99914698e','comp_')]


def lower(declarations,body,*,policy=POLICY,bindings=None):
    source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=3\ncomp_1=`'+declarations+'shader_body {'+body+'}\n')
    model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False,global_input_policy=policy,known_uniforms=bindings)
    return model,model.lower(source['sections']['comp_']['tree'])


@pytest.mark.parametrize('declarations,body,want',[
 ('float3 mus;','ret=mus+.25;',[.25,.25,.25]),
 ('float dist_c;','float before=dist_c;dist_c=.4;ret=before+.25;',[.25,.25,.25]),
 ('float2 uv3;','uv3=.4*cos(42*uv3);ret=float3(uv3,0);',[.4,.4,0]),
 ('float a=.1,b;','ret=a+b;',[.1,.1,.1]),
])
def test_unbound_global_inputs_are_defined_by_link_initialization(declarations,body,want):
    model,result=lower(declarations,body)
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),want,atol=1e-6)
    np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,)),[want,want],atol=1e-6)


def test_nonzero_external_binding_initializes_writable_copy_before_first_read():
    model,result=lower('float dist_c;','float before=dist_c;dist_c=.4;ret=before+.25;',bindings={'dist_c':.2})
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),[.45,.45,.45],atol=1e-6)


@pytest.mark.parametrize('declarations,body,name,value,want',[
    ('float3 mus;','ret=mus+.25;','mus',[.1,.2,.3],[.35,.45,.55]),
    ('float dist_c;','float before=dist_c;dist_c=.4;ret=before+.25;','dist_c',.2,[.45,.45,.45]),
    ('float2 uv3;','uv3+=.25;ret=float3(uv3,0);','uv3',[.2,.3],[.45,.55,0]),
])
def test_runtime_binding_overrides_unbound_default_after_lowering(declarations,body,name,value,want):
    model,result=lower(declarations,body)
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),[.25,.25,.25] if name=='mus' else
        ([.25,.25,.25] if name=='dist_c' else [.25,.25,0]),atol=1e-6)
    np.testing.assert_allclose(evaluate(result,inputs={name:value}),want,atol=1e-6)
    np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,),inputs={name:value}),
                               [want,want],atol=1e-6)


def test_runtime_binding_accepts_distinct_grid_lanes():
    model,result=lower('float dist_c;','float before=dist_c;dist_c=.4;ret=before+.25;')
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,),
        inputs={'dist_c':np.array([.2,.3])}),[[.45]*3,[.55]*3],atol=1e-6)


def test_strict_mode_keeps_external_inputs_symbolic_instead_of_assuming_zero():
    model,result=lower('float3 mus;','ret=mus;',policy='strict-v1')
    assert model.complete,model.unknown
    with pytest.raises(UnresolvedMath):evaluate(result)
    with pytest.raises(UnresolvedMath):evaluate_grid(result,batch_shape=(2,))
    np.testing.assert_allclose(evaluate(result,inputs={'mus':[.1,.2,.3]}),[.1,.2,.3])


@pytest.mark.parametrize('declarations,body',[
 ('','float3 mus;ret=mus;'),
 ('static float s;','ret=s;'),
])
def test_local_and_static_storage_do_not_borrow_external_defaults(declarations,body):
    model,_=lower(declarations,body)
    assert not model.complete


@pytest.mark.parametrize('name,digest,prefix',CASES)
def test_exact_authored_presets_clear_only_the_initialization_obligation(name,digest,prefix):
    root=Path(__file__).resolve().parents[2]
    preset=root/'core/src/main/assets/presets'/name
    assert hashlib.sha256(preset.read_bytes()).hexdigest()==digest
    source=json.loads(subprocess.check_output([str(test_native_reader.READER),str(preset)]))
    section=source['sections'][prefix]
    assert section['implicit_global_input_policy']==POLICY
    model=ShaderFields(stage='warp' if prefix=='warp_' else 'composite',frame=1,warp_reads_blur=False,
        known_uniform_component_domains=q_uniform_domains(source,policy='projectmtv-core-2.2.8-v1'),
        global_input_policy=POLICY,array_initializer_policy=section['array_initializer_policy'])
    model.lower(section['tree'])
    assert model.complete,model.unknown


def test_generated_helper_scratch_copies_are_independent_only_after_complete_writes():
    model,result=lower('float2 scratch;float h(float x){scratch.x=x;scratch.y=x*2;return scratch.x+scratch.y;}',
                       'ret=h(.1)+h(.2);')
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),[.9,.9,.9],atol=1e-6)
    model,_=lower('float2 scratch;float h(float x){scratch.x=x;return scratch.x+scratch.y;}',
                  'ret=h(.1)+h(.2);')
    assert not model.complete
    model,_=lower('float scratch;float h(float x){scratch=x;return scratch;}',
                  'ret=h(.1)+h(.2)+scratch;')
    assert not model.complete
