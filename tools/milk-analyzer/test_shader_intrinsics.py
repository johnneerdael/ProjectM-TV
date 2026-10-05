"""Analytic checks for intrinsics against the pinned translator's semantics."""
import numpy as np
import pytest

from field_math import UnresolvedMath, evaluate
from grid_math import evaluate_grid
from test_field_math import lower


@pytest.mark.parametrize('expression,expected', [
    ('exp2(float3(-2,0,3))', [.25,1,8]),
    ('log10(float3(-100,.1,1))', [2,-1,0]),
    ('reflect(float3(1,-2,3),float3(0,1,0))', [1,2,3]),
    # reflect does not silently normalize the supplied normal.
    ('reflect(float3(1,-2,3),float3(0,2,0))', [1,14,3]),
    ('reflect(float3(1,-2,3),float3(0,0,0))', [1,-2,3]),
    ('float3(reflect(-2.,1.))', [2,2,2]),
])
def test_scalar_and_grid_intrinsics_match_analytic_values(expression,expected):
    model,field=lower('ret='+expression+';')
    assert model.complete,model.unknown
    np.testing.assert_allclose(evaluate(field),expected,rtol=2e-6,atol=1e-7)
    np.testing.assert_allclose(evaluate_grid(field,batch_shape=(2,3)),
                               np.broadcast_to(expected,(2,3,3)),rtol=2e-6,atol=1e-7)


def test_reflection_preserves_independent_grid_lanes():
    model,field=lower('ret=reflect(float3(uv,1),float3(0,1,0));')
    assert model.complete,model.unknown
    uv=np.array([[.25,-.5,0,0],[-.75,.1,0,0]],dtype=np.float32)
    np.testing.assert_allclose(evaluate_grid(field,batch_shape=(2,),inputs={'_uv':uv}),
                               [[.25,.5,1],[-.75,-.1,1]],atol=1e-7)


@pytest.mark.parametrize('expression', ['log10(0.)','exp2(200.)'])
def test_nonfinite_intrinsic_domains_remain_unresolved(expression):
    model,field=lower('ret=float3('+expression+');')
    assert model.complete,model.unknown
    with np.errstate(all='ignore'):
        with pytest.raises(UnresolvedMath):evaluate(field)
        with pytest.raises(UnresolvedMath):evaluate_grid(field,batch_shape=(2,))
