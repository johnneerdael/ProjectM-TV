"""Return boundaries exclude unreachable arithmetic and shared-state writes."""
import numpy as np
import pytest

from test_helper_state import lower
from field_math import evaluate
from grid_math import evaluate_grid


@pytest.mark.parametrize('helper,body,expected',[
    ('float f(){return .25;return .75;}','ret=float3(f());',[.25]*3),
    ('float g=1;float f(){g=2;return g;g=9;return g;}',
     'float a=f();ret=float3(a,g,0);',[2,2,0]),
    ('float f(){return .25;float a;return a;}',
     'ret=float3(f());',[.25]*3),
    ('float f(){return .25;return 1./0.;}',
     'ret=float3(f());',[.25]*3),
    ('float g=1;float f(){return .25;for(int i=0;i<3;i++){g+=1;}return g;}',
     'float a=f();ret=float3(a,g,0);',[.25,1,0]),
    ('float g=1;float f(){g+=1;return g;g=9;return g;}',
     'for(int i=0;i<3;i++){f();}ret=float3(g);',[4]*3),
    ('float g=1;float f(){return 2;g=9;return g;}',
     'ret=float3(f()+g);',[3]*3),
])
def test_first_unconditional_return_excludes_dead_tail(helper,body,expected):
    model,result=lower(body,helper)
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(result),expected)
    np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,)),[expected,expected])


def test_branch_dependent_return_does_not_become_last_return():
    model,result=lower('ret=float3(f(uv.x));',
                       'float f(float v){if(v>0){return .2;}return .8;}')
    assert not model.complete
    assert result.op=='unknown'
