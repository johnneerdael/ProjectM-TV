"""Slang exports derivative programs without replacing authored/native math."""
import json
import os
from pathlib import Path

import pytest

from source_shader_compiler import CompilerTools, analyze_case
from source_shader_slang import export_derivative


@pytest.fixture
def vortex():
    root=Path(__file__).resolve().parents[2]
    saved=root/'build/preset-corpus/source-shape-flash-size-2000-2026-10-10/compatibility/flexi - target practice-5-liquid-2-twitch-2.json'
    compiler=os.environ.get('SOURCE_SHADER_SLANG_COMPILER')
    if not saved.exists() or not compiler:
        pytest.skip('optional Slang compiler and exact saved vortex source fixture required')
    case=json.loads(saved.read_text());inspection=analyze_case(case,CompilerTools())
    helpers=case['reports']['warp']['request']['code'].split('shader_body',1)[0]
    entry='''[shader("compute")] [numthreads(1,1,1)]
void main(uint3 tid: SV_DispatchThreadID, RWStructuredBuffer<float2> result) {
 DifferentialPair<float2> p=fwd_diff(vortex)(diffPair(result[tid.x],float2(1,0)),diffPair(float2(.5),float2(0)),diffPair(float2(0),float2(0)),diffPair(float4(1),float4(0)),diffPair(.07,0.0),diffPair(50.0,0.0),diffPair(1.0,0.0),diffPair(4.0,0.0));
 result[tid.x]=p.d;
}
'''
    return case,inspection,dict(stage='warp',helper_text=helpers,functions=['sigmoid','vortex'],derivative_function='vortex',entry_text=entry,slangc=compiler)


def test_actual_pure_vortex_derivative_program_and_scope(vortex):
    case,inspection,kwargs=vortex;r=export_derivative(case,inspection,**kwargs)
    assert r['status']=='generated'
    assert 's_fwd_vortex' in r['generated_program']
    assert r['native_numeric_equivalence_verified'] is False
    assert r['range_bounds_verified'] is False
    assert r['source_sha256']==case['reports']['warp']['source_sha256']


@pytest.mark.parametrize('change',[
    {'helper_text':'float vortex(float x){return x;}'},
    {'entry_text':'void main(){}'},
    {'entry_text':'void main(){fwd_diff(vortex); TreatAsDifferentiable();}'},
    {'entry_text':'float exp(float x){return 0;} [shader("compute")] [numthreads(1,1,1)] void main(){fwd_diff(vortex);}'},
    {'entry_text':'[shader("compute")] [numthreads(1,1,1)] void main(){/* fwd_diff(vortex)(...) */}'},
    {'functions':['sigmoid','vortex','not_in_source']},
])
def test_unbound_rewritten_or_override_helpers_rejected(vortex,change):
    case,inspection,kwargs=vortex;kwargs.update(change)
    with pytest.raises(ValueError):export_derivative(case,inspection,**kwargs)
