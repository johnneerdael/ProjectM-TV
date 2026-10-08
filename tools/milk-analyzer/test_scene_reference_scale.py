import numpy as np
from scene_draw import _wave
from quad_lines import PROFILE


def dot(*,builtin=False):
    value={'positions':[[.5,.5]],'colours':[1,0,0,1],'rgba':[1,0,0,1],
           'draw_mode':'points','point_size':1,'thick':False,
           'additive':True,'copy_offsets':[[0,0]]}
    if builtin:value['positions']=[value['positions']]
    return value


def test_native_custom_dot_area_scales_but_author_keeps_its_single_pixel():
    low=_wave(np.zeros((16,16,4),np.float32),dot(),quantize=False,
              line_rendering_profile=PROFILE,reference_size=(0,0))
    high=_wave(np.zeros((32,32,4),np.float32),dot(),quantize=False,
               line_rendering_profile=PROFILE,reference_size=(16,16))
    assert low[...,0].sum()==1
    assert high[...,0].sum()==4


def test_noninteger_dot_scale_preserves_area_through_alpha_fade():
    high=_wave(np.zeros((24,24,4),np.float32),dot(),quantize=False,
               line_rendering_profile=PROFILE,reference_size=(16,16))
    np.testing.assert_allclose(high[...,0].sum(),2.25,atol=1e-7)


def test_main_native_dots_have_double_base_width():
    high=_wave(np.zeros((32,32,4),np.float32),dot(builtin=True),builtin=True,
               quantize=False,line_rendering_profile=PROFILE,reference_size=(16,16))
    assert high[...,0].sum()==16


def test_authored_main_dots_replace_native_prepared_point_style():
    value=dot(builtin=True)
    value.update(point_size=2,thick=True,positions=[[[.51,.51]]])
    authored=_wave(np.zeros((16,16,4),np.float32),value,builtin=True,
                   quantize=False,line_rendering_profile='canonical-gl-lines-v1',reference_size=(0,0))
    # Authored GL path uses four independently offset one-pixel point passes.
    assert np.count_nonzero(authored[...,0])==4
    assert authored[...,0].sum()==4
    np.testing.assert_array_equal(np.argwhere(authored[...,0]),[[7,8],[7,9],[8,8],[8,9]])


def test_custom_dot_alpha_is_not_amplified_above_one_by_style_epsilon():
    value=dot()
    value['colours']=[1,0,0,.5]
    target=_wave(np.zeros((2,20001,4),np.float32),value,quantize=False,
                 line_rendering_profile=PROFILE,reference_size=(20000,2))
    assert target[...,0].sum()==.5
