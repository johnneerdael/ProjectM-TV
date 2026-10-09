"""Uniform colour/flash reduction against the existing full descriptor formula."""
import importlib.util
import numpy as np
import pytest
from descriptors import DescriptorStream


@pytest.fixture(autouse=True)
def qualified_hsv_backend(request):
    if request.node.name=='test_unqualified_colour_backend_abstains':return
    from uniform_descriptors import _qualified_hsv_backend
    try:_qualified_hsv_backend()
    except ValueError:pytest.skip('uniform numerical parity fixture requires OpenCV 5.0.0 optimized NEON')


def uniform_stream(size,**kwargs):
    assert importlib.util.find_spec('uniform_descriptors'), 'uniform descriptor reducer missing'
    from uniform_descriptors import UniformDescriptorStream
    return UniformDescriptorStream(viewport=size,**kwargs)


def compare(old,new):
    # Preserve nulls, event flags/areas and timings exactly. Only floating
    # reduction roundoff gets a small absolute tolerance, not category slack.
    if isinstance(old,dict):
        assert old.keys()==new.keys()
        for k in old:compare(old[k],new[k])
    elif isinstance(old,list):
        assert len(old)==len(new)
        for a,b in zip(old,new):compare(a,b)
    elif old is None or isinstance(old,(bool,str,int)):assert new==old
    else:assert new==pytest.approx(old,rel=2e-6,abs=2e-7)


@pytest.mark.parametrize('size',[(32,18),(128,72),(854,480)])
@pytest.mark.parametrize('warmup',[0,2])
def test_uniform_windows_preserve_colour_flash_and_motion_unknowns(size,warmup):
    old=DescriptorStream(warmup_frames=warmup)
    new=uniform_stream(size,warmup_frames=warmup)
    colors=[[0,0,0],[.1,.1,.1],[.2,.4,.6],[1,0,0],[0,1,0],[0,0,1],[.049,.01,.02],
            [.8,.8,.8],[.95,.2,.7],[.95,.2,.7]]*2
    for i,rgb in enumerate(colors):
        rgba=np.array([*rgb,1],np.float32);time=(i+1)/15
        old.add({'time':time,'display':np.broadcast_to(rgba,(size[1],size[0],4)).copy()})
        new.add_uniform(time=time,rgba=rgba)
    a,b=old.report(),new.report()
    for group in ['colour','flashing','motion']:compare(a[group],b[group])
    compare(a['structure'],b['structure'])
    assert b['motion']['median_speed_viewports_per_second'] is None
    assert new.previous.shape==(3,) # retained state contains no RGB viewport
    assert b['uniform_reduction']['display_fields_constructed'] is False


def test_constant_output_keeps_undefined_fft_and_achromatic_hue_null():
    stream=uniform_stream((854,480))
    for i in range(20):stream.add_uniform(time=(i+1)/15,rgba=[.2,.2,.2,1])
    report=stream.report()
    assert report['flashing']['dominant_sampled_brightness_hz'] is None
    assert report['flashing']['spectral_peak_fraction'] is None
    assert report['colour']['warm_cool'] is None
    assert report['colour']['mean_effective_hue_bins']==0
    assert report['flashing']['peak_rgb_change_area']==0


def test_irregular_schedule_and_short_windows_keep_support_rules():
    stream=uniform_stream((5,7))
    stream.add_uniform(time=.1,rgba=[1,0,0,1])
    assert stream.report()['flashing']['peak_rgb_change_area'] is None
    for time in [.2,.31]:stream.add_uniform(time=time,rgba=[0,1,0,1])
    assert stream.report()['flashing']['nyquist_hz'] is None
    assert stream.report()['flashing']['frequency_resolution_hz'] is None


def test_invalid_vector_time_and_viewport_are_rejected():
    import uniform_descriptors
    with pytest.raises(ValueError):uniform_descriptors.UniformDescriptorStream(viewport=(0,8))
    stream=uniform_stream((8,8))
    for rgba in [[1,0,0],[[1,0,0,1]],[-.1,0,0,1],[np.nan,0,0,1]]:
        with pytest.raises(ValueError):stream.add_uniform(time=.1,rgba=rgba)
    stream.add_uniform(time=.1,rgba=[1,0,0,1])
    with pytest.raises(ValueError):stream.add_uniform(time=.1,rgba=[0,1,0,1])


@pytest.mark.parametrize('size',[(3,7),(5,7),(32,18),(854,480)])
def test_simd_hue_boundary_and_tail_preserve_histograms_and_query_counts(size):
    old=DescriptorStream();new=uniform_stream(size)
    colors=[[.7107577323913574,.41735729575157166,.5640576481819153,1],
            [.36622685194015503,.03363323211669922,.30749213695526123,1]]
    for i,rgba in enumerate(colors):
        time=(i+1)/15
        old.add({'time':time,'display':np.broadcast_to(np.array(rgba,np.float32),(size[1],size[0],4)).copy()})
        new.add_uniform(time=time,rgba=rgba)
        compare(old.report()['colour'],new.report()['colour'])
    compare(old.transitions[0]['hue_change'],new.transitions[0]['hue_change'])


def test_random_and_dim_supported_colours_match_full_reductions():
    rng=np.random.default_rng(743)
    for size in [(1,1),(3,7),(5,7),(17,19),(32,18)]:
        old=DescriptorStream();new=uniform_stream(size)
        colors=np.vstack(([.1,0,0,1],[0,.1,0,1],rng.uniform(0,1,(40,4)))).astype(np.float32)
        for i,rgba in enumerate(colors):
            time=(i+1)/15
            old.add({'time':time,'display':np.broadcast_to(rgba,(size[1],size[0],4)).copy()})
            new.add_uniform(time=time,rgba=rgba)
        for group in ['colour','flashing','motion','structure']:compare(old.report()[group],new.report()[group])
        for before,after in zip(old.transitions,new.transitions):compare(before['hue_change'],after['hue_change'])


def test_unqualified_colour_backend_abstains(monkeypatch):
    import uniform_descriptors
    monkeypatch.setattr(uniform_descriptors.cv2,'__version__','unqualified')
    with pytest.raises(ValueError,match='qualified OpenCV'):
        uniform_descriptors.UniformDescriptorStream(viewport=(32,18))


def test_unrepresentable_hue_rate_retains_original_failure():
    old=DescriptorStream();new=uniform_stream((32,18))
    old.add({'time':0,'display':np.broadcast_to([1,0,0,1],(18,32,4)).copy()})
    new.add_uniform(time=0,rgba=[1,0,0,1])
    with np.errstate(over='ignore',invalid='ignore'):
        with pytest.raises(ValueError,match='hue derivative numeric domain unresolved'):
            old.add({'time':1e-320,'display':np.broadcast_to([0,1,0,1],(18,32,4)).copy()})
        with pytest.raises(ValueError,match='hue derivative numeric domain unresolved'):
            new.add_uniform(time=1e-320,rgba=[0,1,0,1])


@pytest.mark.parametrize('setting',['value_floor','saturation_floor'])
def test_boolean_chromatic_thresholds_retain_original_failure(setting):
    for stream in [DescriptorStream(settings={setting:True}),uniform_stream((32,18),settings={setting:True})]:
        with pytest.raises(ValueError,match='positive finite chromatic thresholds'):
            if isinstance(stream,DescriptorStream) and type(stream) is DescriptorStream:
                stream.add({'time':0,'display':np.broadcast_to([1,0,0,1],(18,32,4)).copy()})
            else:stream.add_uniform(time=0,rgba=[1,0,0,1])


def test_overflowing_dt_retains_original_failure():
    old=DescriptorStream();new=uniform_stream((32,18))
    old.add({'time':-1e308,'display':np.broadcast_to([1,0,0,1],(18,32,4)).copy()})
    new.add_uniform(time=-1e308,rgba=[1,0,0,1])
    with pytest.raises(ValueError,match='positive finite hue query time interval'):
        old.add({'time':1e308,'display':np.broadcast_to([0,1,0,1],(18,32,4)).copy()})
    with pytest.raises(ValueError,match='positive finite hue query time interval'):
        new.add_uniform(time=1e308,rgba=[0,1,0,1])
