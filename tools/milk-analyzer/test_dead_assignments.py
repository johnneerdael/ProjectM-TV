import pytest
import numpy as np
from test_shader_loops import lower
from field_math import evaluate


def test_discarded_noise_chain_does_not_require_unwritten_coordinate():
    model,result=lower('float noise;float2 uv3;shader_body {'
                       'noise=tex2D(sampler_main,uv3).x;noise*=noise>=.9;ret=.4;}')
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),[.4]*3)


@pytest.mark.historical_profile("legacy_pre30")
def test_live_noise_chain_still_requires_coordinate():
    model,result=lower('float noise;float2 uv3;shader_body {'
                       'noise=tex2D(sampler_main,uv3).x;noise*=noise>=.9;ret=noise;}')
    assert not model.complete


def test_helper_observing_global_keeps_earlier_assignment():
    model,result=lower('float g;float f(){return g;}shader_body {g=.7;ret=f();}')
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),[.7]*3)


def test_discarded_assignment_keeps_helper_side_effect():
    model,result=lower('float g=0;float f(){g=1;return 2;}'
                       'shader_body {float x;x=f();ret=g;}')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[1]*3)


def test_branch_assignment_is_live_outside_branch():
    model,result=lower('shader_body {float x=0;if(bass>0){x=.8;}ret=x;}')
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result,inputs={'_c3':[1,0,0,0]}),[.8]*3)


def test_discarded_index_write_remains_domain_obligation():
    model,result=lower('shader_body {float3 x=0;x[4]=1;ret=.4;}')
    assert model.effects


def test_discarded_assignment_cannot_hide_output_parameter_effect():
    model,result=lower('shader_body {float whole;float unused;unused=modf(1.5,whole);ret=whole;}')
    assert model.complete,model.unknown
    np.testing.assert_array_equal(evaluate(result),[1]*3)
