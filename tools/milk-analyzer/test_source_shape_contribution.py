"""Source fan integrals, including colour/alpha covariance; no raster samples."""
import pytest

from test_effect_families import read
from test_source_appearance import appearance


def shape(body='',config=''):
    source=read('fWaveAlpha=0\nshapecode_0_enabled=1\nshapecode_0_sides=4\n'
                'shapecode_0_rad=.5\n'+config+'shape_0_per_frame1='+body+'\n')
    element=next(e for e in appearance(source)['elements'] if e['id']=='shape_0')
    assert 'fill_contribution' in element,'nominal shape fill contribution is missing'
    return element['fill_contribution']


def test_opaque_constant_fill_has_area_weighted_rgb_injection():
    f=shape('r=1;g=0;b=0;a=1;r2=1;g2=0;b2=0;a2=1;')
    assert f['mean_fill_alpha']==pytest.approx(1,abs=2e-7)
    assert f['mean_source_rgb_times_alpha']==pytest.approx([1,0,0],abs=3e-7)
    assert f['nominal_alpha_area_fraction_per_aspect_y']==pytest.approx(.125)
    assert f['nominal_source_rgb_integral_per_aspect_y']==pytest.approx([.125,0,0])
    assert f['visible_screen_contribution'] is None


def test_fading_centre_keeps_colour_alpha_covariance():
    f=shape('r=1;g=0;b=0;a=1;r2=0;g2=1;b2=0;a2=0;')
    assert f['mean_fill_alpha']==pytest.approx(1/3)
    assert f['mean_source_rgb_times_alpha']==pytest.approx([1/6,1/6,0])
    assert f['nominal_source_rgb_integral_per_aspect_y']==pytest.approx([1/48,1/48,0])
    assert f['nominal_alpha_area_fraction_per_aspect_y']==pytest.approx(1/24)


def test_fan_moment_formula_matches_independent_triangle_polynomial_integral():
    f=shape('r=.2;g=.4;b=.8;a=.25;r2=.8;g2=.6;b2=.2;a2=.75;')
    material=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\n'
        'shape_0_per_frame1=r=.2;g=.4;b=.8;a=.25;r2=.8;g2=.6;b2=.2;a2=.75;\n'))['elements'][0]['material']
    centre=material['centre_vertex_rgba'];edge=material['perimeter_vertex_rgba']
    # Let t be the centre barycentric weight. Its fan-area density is 2(1-t).
    # Integrate the quadratic (edge + (centre-edge)t) RGB*alpha polynomial.
    expected=[]
    for c,p in zip(centre[:3],edge[:3]):
        a0=edge[3];da=centre[3]-a0;dc=c-p
        coefficients=[p*a0,p*da+dc*a0,dc*da]
        expected.append(sum(v*2/((n+1)*(n+2)) for n,v in enumerate(coefficients)))
    assert f['mean_source_rgb_times_alpha']==pytest.approx(expected,abs=1e-12)


def test_repeated_nominal_area_is_not_union_coverage():
    f=shape('a=1;a2=1;',config='shapecode_0_num_inst=3\n')
    assert f['summed_nominal_alpha_area_fraction_per_aspect_y']==pytest.approx(.375)
    assert f['instance_aggregation']=='sum of nominal per-instance integrals; overlaps counted repeatedly'


@pytest.mark.parametrize('config',[
    'shapecode_0_textured=1\n',
    'shapecode_0_textured=1\nshapecode_0_image=missing.png\n',
])
def test_texture_alpha_and_colour_are_not_assumed_opaque(config):
    f=shape('a=1;a2=1;',config=config)
    assert f['mean_fill_alpha'] is None
    assert f['mean_source_rgb_times_alpha']==[None]*3
    assert f['unknown_reasons']


def test_dynamic_alpha_preserves_unknown_without_default_value():
    f=shape('a=bass;a2=1;')
    assert f['mean_fill_alpha'] is None
    assert f['nominal_alpha_area_fraction_per_aspect_y'] is None


def test_dynamic_radius_keeps_known_material_moments():
    f=shape('rad=bass;a=1;a2=1;r=1;r2=1;g=0;g2=0;b=0;b2=0;')
    assert f['mean_fill_alpha']==pytest.approx(1,abs=2e-7)
    assert f['mean_source_rgb_times_alpha']==pytest.approx([1,0,0],abs=3e-7)
    assert f['nominal_source_rgb_integral_per_aspect_y']==[None]*3


def test_dynamic_one_colour_channel_does_not_hide_other_known_channels():
    f=shape('r=bass;r2=1;g=0;g2=0;b=0;b2=0;a=1;a2=1;')
    assert f['mean_source_rgb_times_alpha']==[None,0,0]


def test_transparent_fill_does_not_make_a_visible_border_disappear():
    f=shape('a=0;a2=0;border_a=1;')
    assert f['mean_fill_alpha']==0
    assert f['mean_source_rgb_times_alpha']==[0,0,0]
    assert f['border_included'] is False
    assert f['visible_screen_contribution'] is None


def test_alpha_outside_unclamped_domain_is_not_integrated_as_a_linear_gradient():
    from source_material import shape_fill_contribution
    g={'nominal_area_fraction_per_aspect_y':.1,'configured_instances':1}
    m={'texture':{'role':'untextured_vertex_gradient'},'centre_vertex_rgba':[1,0,0,1.001],
       'perimeter_vertex_rgba':[0,0,0,.5],'blend_mode':'source_alpha_over'}
    f=shape_fill_contribution(g,m)
    assert f['mean_fill_alpha'] is None
    assert f['unknown_reasons']
