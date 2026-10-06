import numpy as np
import pytest

from spatial import interpolate_mesh, warp_vertex_uv

PROFILE='apple-m4pro-gl41-nan-mesh-v1'


def test_portable_zero_stretch_remains_unresolved():
    with pytest.raises(ValueError,match='zero spatial divisor'):
        warp_vertex_uv(np.array([[.5,0]],dtype=np.float32),sy=0)


def test_observed_profile_retains_nan_vertex_before_interpolation():
    uv=warp_vertex_uv(np.array([[.5,0]],dtype=np.float32),sy=0,numeric_profile=PROFILE)
    assert np.isnan(uv).all()


def test_nan_vertex_affects_only_its_interpolation_support():
    values=np.full((2,2,2),.5,dtype=np.float32);values[0,0]=np.nan
    query=np.array([[.25,.25],[.75,.75]],dtype=np.float32)
    result=interpolate_mesh(values,query,numeric_profile=PROFILE)
    assert np.all(result[0]==np.finfo(np.float32).max)
    assert np.all(result[1]==.5)
    with pytest.raises(ValueError,match='nonfinite'):
        interpolate_mesh(values,query)


def test_infinity_is_not_silently_given_the_nan_rule():
    values=np.full((2,2,2),.5,dtype=np.float32);values[0,0]=np.inf
    with pytest.raises(ValueError):
        interpolate_mesh(values,np.array([[.25,.25]]),numeric_profile=PROFILE)
    with pytest.raises(ValueError):
        warp_vertex_uv(np.array([[.5,.25]],dtype=np.float32),sy=0,numeric_profile=PROFILE)


def test_unknown_runtime_profile_is_rejected():
    with pytest.raises(ValueError):
        warp_vertex_uv(np.array([[.5,0]]),numeric_profile='guess')
    with pytest.raises(ValueError):
        interpolate_mesh(np.zeros((2,2,2)),np.array([[.5,.5]]),numeric_profile='guess')


def test_apple_profile_cannot_be_applied_to_a_different_shader_backend(tmp_path):
    from forecast import forecast_source
    domain=dict(width=16,height=16,mesh_x=8,mesh_y=8,profile='gles300',
                numeric_profile=PROFILE,initial_rgba=[0,0,0,0],hue_offsets=[0]*4,
                equation_seed=1,blur_levels=0,quantize=True)
    with pytest.raises(ValueError,match='requires glsl330'):
        forecast_source({},audio={},binaries=tmp_path,domain=domain,compatibility={})


@pytest.mark.parametrize('profile',['portable',PROFILE])
@pytest.mark.parametrize('settings',[{'zoom':-.9},{'zoomexp':-1},{'zoom':0,'zoomexp':0}])
def test_undefined_nested_glsl_power_domain_is_not_numpy_integer_power(settings,profile):
    # radius1 makes the inner exponent exactly1. NumPy would accept a
    # negative base here, but GLSL pow remains undefined for any negative base.
    with pytest.raises(ValueError,match='unresolved warp power domain'):
        warp_vertex_uv(np.array([[1,0]],dtype=np.float32),numeric_profile=profile,**settings)


def test_zero_zoom_exponent_is_allowed_when_the_inner_power_domain_is_defined():
    # radius1: pow(0,1)=0, then pow(2,0)=1. Rejecting every zero base
    # would incorrectly reject this well-defined nested expression.
    uv=warp_vertex_uv(np.array([[1,0]],dtype=np.float32),zoom=2,zoomexp=0)
    np.testing.assert_array_equal(uv,[[1,.5]])
