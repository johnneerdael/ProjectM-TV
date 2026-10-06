"""Pinned shape sampler inheritance and blur resource requests."""
import pytest
import shape_sampling as module


def shapes(*textured):
    return [{'index':i,'values':{'textured':int(value)}} for i,value in enumerate(textured)]


def test_first_main_shape_inherits_delayed_blur_clamp_linear():
    modes=module.shape_sampling_modes(shapes(True,True),image_names={},policy=module.CORE_238,
                                     warp_reads_blur=True,blur_level=3,frame_wrap=1)
    assert modes[0]=={'wrap':False,'linear':True}
    assert modes[1]=={'wrap':True,'linear':False}


@pytest.mark.parametrize('frame_wrap,expected',[(0,False),(1,True)])
def test_no_delayed_blur_inherits_warp_sampler(frame_wrap,expected):
    for reads,level in [(False,3),(True,0)]:
        modes=module.shape_sampling_modes(shapes(False,True),image_names={},policy=module.CORE_238,
                                         warp_reads_blur=reads,blur_level=level,frame_wrap=frame_wrap)
        assert modes[1]=={'wrap':expected,'linear':True}


def test_named_image_owns_sampler_and_clears_prior_inheritance():
    modes=module.shape_sampling_modes(shapes(True,True),image_names={0:'pc_image'},policy=module.CORE_238,
                                     warp_reads_blur=True,blur_level=1,frame_wrap=0)
    assert modes[0]=={'wrap':False,'linear':False}
    assert modes[1]=={'wrap':True,'linear':False}


def test_instances_are_distinct_draws_even_with_same_shape_index():
    entries=[{'index':3,'values':{'textured':1}} for _ in range(2)]
    modes=module.shape_sampling_modes(entries,image_names={},policy=module.CORE_238,
                                     warp_reads_blur=True,blur_level=1,frame_wrap=1)
    assert modes[0]['wrap'] is False and modes[0]['linear'] is True
    assert modes[1]['wrap'] is True and modes[1]['linear'] is False


def test_historical_shape_policy_retains_repeat_linear():
    assert module.shape_sampling_modes(shapes(True),image_names={},policy=module.LEGACY,
                                       warp_reads_blur=True,blur_level=3,frame_wrap=0)[0]=={'wrap':True,'linear':True}


def test_native_blur_requests_follow_comments_aliases_and_active_stages():
    source={'sections':{'warp_':{'source':'// GetBlur3(uv)\nfloat4 texsize_fc_blur2;'},
                        'comp_':{'source':'GetBlur1(uv)'}}}
    active={'warp':{'kind':'custom_warp'},'composite':{'kind':'custom_composite'}}
    assert module.native_blur_level(source,active)==2
    active['warp']['kind']='fixed_warp'
    assert module.native_blur_level(source,active)==1
    active['composite']['kind']='default_composite'
    assert module.native_blur_level(source,active)==0


@pytest.mark.parametrize('update',[{'policy':'latest'},{'blur_level':4},{'frame_wrap':float('nan')}])
def test_invalid_context_is_not_silently_coerced(update):
    options=dict(image_names={},policy=module.CORE_238,warp_reads_blur=True,blur_level=1,frame_wrap=1)
    options.update(update)
    with pytest.raises(ValueError):module.shape_sampling_modes(shapes(True),**options)
