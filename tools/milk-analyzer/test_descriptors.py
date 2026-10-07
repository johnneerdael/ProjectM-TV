import importlib
import numpy as np
import pytest


def stream(**options):
    return importlib.import_module('descriptors').DescriptorStream(**options)


def add(target, rgb, time, uv=None):
    values=np.asarray(rgb,dtype=np.float32)
    if values.shape==(3,):values=np.broadcast_to(values,(64,64,3)).copy()
    rgba=np.concatenate((values,np.ones(values.shape[:2]+(1,),dtype=np.float32)),axis=-1)
    target.add(dict(time=time,display=rgba,warp_uv=uv))


def test_visible_colour_counts_exclude_grey_and_black():
    target=stream()
    rgb=np.zeros((60,60,3),dtype=np.float32)
    rgb[:20,:,0]=1;rgb[20:40,:,1]=1;rgb[40:,:,2]=1
    add(target,rgb,0)
    result=target.report()
    assert result['colour']['mean_effective_hue_bins']==pytest.approx(3)
    assert result['colour']['mean_coloured_fraction']==1
    target=stream();add(target,[.5,.5,.5],0)
    assert target.report()['colour']['mean_effective_hue_bins']==0
    target=stream();add(target,[0,0,0],0)
    assert target.report()['colour']['mean_coloured_fraction']==0


def test_full_screen_brightness_jump_is_measured_without_invented_motion():
    target=stream()
    add(target,[0,0,0],0);add(target,[1,1,1],1/30)
    result=target.report()
    assert result['flashing']['peak_mean_luma_jump']==pytest.approx(1)
    assert result['flashing']['peak_brightness_change_area']==1
    assert result['flashing']['peak_paired_luma_area_product']==1
    assert result['flashing']['coherent_brightening_transitions']==1
    assert result['motion']['available_transition_fraction']==0
    assert result['motion']['median_speed_viewports_per_second'] is None


def test_iso_luma_colour_switch_keeps_chromatic_change_visible():
    target=stream()
    add(target,[1,0,0],0)
    add(target,[0,.2126/.7152,0],1/30)
    result=target.report()
    assert result['flashing']['peak_mean_luma_jump']<1e-6
    assert result['flashing']['peak_rgb_change_area']==1


def test_small_flash_is_measured_relative_to_visible_content_on_a_black_screen():
    target=stream()
    black=np.zeros((64,64,3),dtype=np.float32)
    pulse=black.copy();pulse[:16,:16]=1
    add(target,black,0);add(target,pulse,1/30);add(target,black,2/30)
    result=target.report()['flashing']
    assert result['peak_mean_luma_jump']==pytest.approx(1/16)
    assert result['peak_visible_brightening_fraction']==1
    assert result['peak_visible_darkening_fraction']==1
    assert result['peak_brightening_screen_area']==pytest.approx(1/16)
    assert result['peak_darkening_screen_area']==pytest.approx(1/16)


def test_opposite_local_flashes_do_not_cancel_each_other_in_the_report():
    target=stream()
    first=np.zeros((64,64,3),dtype=np.float32);first[:32]=1
    second=1-first
    add(target,first,0);add(target,second,1/30)
    result=target.report()['flashing']
    assert result['peak_mean_luma_jump']==0
    assert result['peak_visible_brightening_fraction']==.5
    assert result['peak_visible_darkening_fraction']==.5


def test_empty_visible_support_does_not_invent_a_local_flash():
    target=stream();add(target,[0,0,0],0);add(target,[0,0,0],1/30)
    result=target.report()['flashing']
    assert result['peak_visible_brightening_fraction']==0
    assert result['peak_visible_darkening_fraction']==0


def test_opposing_edge_support_does_not_invent_a_central_feature():
    target=stream()
    image=np.zeros((64,64,3),np.float32)
    image[24:40,:8]=1
    image[24:40,-8:]=1
    add(target,image,0)
    location=target.report()['structure']['spatial_support']
    row=location['frames'][0]
    assert row['centre_support_pixels']==0
    assert row['supported_pixels']==256
    assert row['grid_counts'][1][0]==128
    assert row['grid_counts'][1][2]==128
    assert row['bounds']=={'minimum':[0,24/64], 'maximum':[1,40/64]}
    assert location['grid_shape']==[3,3]
    assert location['value_floor']==.05


def test_spatial_support_retains_empty_frames_and_uses_half_open_centre():
    target=stream(warmup_frames=1)
    add(target,[1,1,1],0)
    add(target,[0,0,0],1/30)
    image=np.zeros((8,8,3),np.float32)
    # Independent stream: viewport dimensions cannot change within one stream.
    small=stream()
    image[2,2]=.05
    image[6,6]=1
    add(small,image,0)
    row=small.report()['structure']['spatial_support']['frames'][0]
    assert row['centre_support_pixels']==1
    assert sum(map(sum,row['grid_counts']))==2
    empty=target.report()['structure']['spatial_support']['frames']
    assert len(empty)==1
    assert empty[0]['bounds'] is None
    assert empty[0]['supported_pixels']==0


def test_shifted_textured_field_has_visible_speed_not_coherent_flashing():
    target=stream()
    rng=np.random.default_rng(413)
    image=np.repeat(rng.uniform(.15,.85,(64,64,1)).astype(np.float32),3,axis=-1)
    for i in range(6):add(target,np.roll(image,2*i,axis=1),i/30)
    result=target.report()
    assert result['motion']['available_transition_fraction']>.5
    assert result['motion']['median_speed_viewports_per_second']==pytest.approx(2*30/64,rel=.15)
    assert result['flashing']['coherent_brightening_transitions']==0
    assert result['flashing']['coherent_darkening_transitions']==0


def test_sparse_translation_uses_full_viewport_units_and_screen_area():
    rng=np.random.default_rng(711)
    patch=rng.uniform(.08,.3,(12,12,1)).astype(np.float32)
    target=stream()
    for i in range(6):
        image=np.zeros((128,256,3),dtype=np.float32)
        image[58:70,110+i:122+i]=patch
        assert float((image@np.array([.2126,.7152,.0722])).std()) < .02
        add(target,image,i/30)
    result=target.report()['motion']
    assert result['available_transition_fraction'] > .5
    assert result['median_speed_viewports_per_second']==pytest.approx(30/256,rel=.25)
    assert 0 < result['mean_supported_area'] < .03
    assert result['matched_brightness_change_p95'] < .04


def test_sparse_subthreshold_noise_remains_unresolved():
    rng=np.random.default_rng(713)
    first=np.zeros((128,256,3),dtype=np.float32)
    first[58:70,110:122]=rng.uniform(0,.01,(12,12,1))
    target=stream();add(target,first,0);add(target,np.roll(first,1,axis=1),1/30)
    result=target.report()['motion']
    assert result['available_transition_fraction']==0
    assert result['median_speed_viewports_per_second'] is None


def test_motion_compensated_brightness_separates_translation_from_dimming():
    rng=np.random.default_rng(517)
    image=np.repeat(rng.uniform(.25,.85,(64,64,1)).astype(np.float32),3,axis=-1)
    moving=stream()
    for i in range(6):add(moving,np.roll(image,2*i,axis=1),i/30)
    dimming=stream();add(dimming,image,0);add(dimming,image*.5,1/30)
    a=moving.report()['motion']['matched_brightness_change_p95']
    b=dimming.report()['motion']['matched_brightness_change_p95']
    assert a is not None and a < .08
    assert b is not None and b > .2


def test_untrackable_dark_fields_do_not_get_zero_matched_brightness_change():
    target=stream();add(target,[0,0,0],0);add(target,[0,0,0],1/30)
    assert target.report()['motion']['matched_brightness_change_p95'] is None


def test_tracked_dimming_reports_screen_area_and_polarity():
    rng=np.random.default_rng(517)
    image=np.repeat(rng.uniform(.25,.85,(64,64,1)).astype(np.float32),3,axis=-1)
    target=stream();add(target,image,0);add(target,image*.5,1/30)
    result=target.report()['motion']
    assert result['peak_matched_darkening_screen_area'] > .2
    assert result['peak_matched_brightening_screen_area'] == 0
    assert result['peak_matched_darkening_screen_area'] <= result['mean_supported_area']


def test_tracked_translation_does_not_create_large_brightness_area():
    rng=np.random.default_rng(517)
    image=np.repeat(rng.uniform(.25,.85,(64,64,1)).astype(np.float32),3,axis=-1)
    target=stream()
    for i in range(6):add(target,np.roll(image,2*i,axis=1),i/30)
    result=target.report()['motion']
    assert result['peak_matched_darkening_screen_area'] < .05
    assert result['peak_matched_brightening_screen_area'] < .05


def test_untrackable_fields_keep_matched_area_unknown():
    target=stream();add(target,[0,0,0],0);add(target,[0,0,0],1/30)
    result=target.report()['motion']
    assert result['peak_matched_darkening_screen_area'] is None
    assert result['peak_matched_brightening_screen_area'] is None
    assert result['peak_matched_brightness_change_p95'] is None


def test_untracked_brightness_changes_are_reported_as_unexplained_not_calm():
    target=stream();add(target,[0,0,0],0);add(target,[1,1,1],1/30)
    result=target.report()['motion']
    assert result['peak_untracked_brightness_change_screen_area'] == 1
    assert result['peak_matched_brightening_screen_area'] is None
    target=stream();add(target,[0,0,0],0);add(target,[0,0,0],1/30)
    assert target.report()['motion']['peak_untracked_brightness_change_screen_area'] == 0


def test_geometry_speed_does_not_imply_visible_motion_on_a_uniform_field():
    target=stream()
    x,y=np.meshgrid((np.arange(64)+.5)/64,(np.arange(64)+.5)/64)
    uv=np.stack((x+.2,y),axis=-1)
    add(target,[.3,.3,.3],0,uv);add(target,[.3,.3,.3],1/30,uv)
    result=target.report()
    assert result['motion']['mean_warp_query_displacement']==pytest.approx(.2)
    assert result['motion']['median_speed_viewports_per_second'] is None


def test_extreme_finite_warp_queries_do_not_overflow_descriptor_arithmetic():
    target=stream()
    uv=np.full((64,64,2),np.finfo(np.float32).max,dtype=np.float32)
    add(target,[.3,.3,.3],0,uv)
    result=target.report()['motion']
    assert np.isfinite(result['mean_warp_query_displacement'])
    assert result['mean_warp_query_displacement'] > 1e38
    assert result['median_speed_viewports_per_second'] is None


def test_known_brightness_oscillation_has_declared_sampling_limits():
    target=stream()
    for i in range(120):add(target,[.5+.3*np.sin(2*np.pi*2*i/30)]*3,i/30)
    result=target.report()
    assert result['flashing']['dominant_sampled_brightness_hz']==pytest.approx(2)
    assert result['flashing']['nyquist_hz']==pytest.approx(15)
    assert result['flashing']['frequency_resolution_hz']==pytest.approx(.25)
    assert result['appearance_accuracy_verified'] is False


def test_warmup_and_irregular_time_do_not_create_a_false_frequency_measurement():
    target=stream(warmup_frames=2)
    for time,value in [(0,0),(.01,1),(.1,.2),(.2,.2),(.5,.2)]:add(target,[value]*3,time)
    result=target.report()
    assert result['frames_measured']==3
    assert result['colour']['mean_luma']==pytest.approx(.2)
    assert result['flashing']['dominant_sampled_brightness_hz'] is None


def test_invalid_time_or_field_is_rejected_instead_of_reporting_calm():
    target=stream();add(target,[.5]*3,0)
    with pytest.raises(ValueError,match='increasing'):add(target,[.5]*3,0)
    with pytest.raises(ValueError,match='finite'):add(stream(),[np.nan]*3,0)


def test_unobserved_structure_and_causal_bass_response_remain_unknown():
    target=stream();add(target,[1,0,0],0)
    result=target.report()
    assert result['structure']['fractal'] is None
    assert result['bass_response'] is None
    assert result['mood_assignment'] is None


def test_palette_report_separates_spatial_and_temporal_entropy():
    target=stream()
    add(target,[1,0,0],0);add(target,[0,0,1],1)
    result=target.report()['colour']
    assert result['mean_hue_entropy_nats']==pytest.approx(0)
    assert result['temporal_hue_entropy_nats']==pytest.approx(np.log(2))
    assert result['warm_cool']==pytest.approx(0)
    assert result['mean_coloured_fraction']==1


def test_small_local_change_keeps_its_correlated_event_without_coherent_gate():
    target=stream()
    first=np.zeros((64,64,3),dtype=np.float32)
    second=first.copy();second[:8,:8]=1
    add(target,first,0);add(target,second,.1)
    result=target.report()['flashing']
    assert result['coherent_transitions_per_second']==0
    assert result['local_or_colour_change_transitions_per_second']==10
    event=result['events'][0]
    assert event['start_time']==0 and event['end_time']==.1
    assert event['brightening']['area']==1/64
    assert event['brightening']['mean_amplitude']==pytest.approx(1)
    assert event['coherent_up'] is False
    assert event['motion_crossing_ruled_out'] is False


def test_colour_event_is_retained_even_when_luma_does_not_change():
    target=stream()
    add(target,[1,0,0],0);add(target,[0,.2126/.7152,0],.1)
    event=target.report()['flashing']['events'][0]
    assert abs(event['signed_mean_luma_delta'])<1e-6
    assert event['rgb']['area']==1
    assert event['rgb']['mean_amplitude']==pytest.approx(1)


def test_single_measured_frame_cannot_supply_an_event_rate():
    target=stream();add(target,[1,0,0],0)
    result=target.report()['flashing']
    assert result['coherent_transitions_per_second'] is None
    assert result['local_or_colour_change_transitions_per_second'] is None
    assert result['events']==[]


def test_sparse_transition_subset_does_not_publish_confident_window_speed(monkeypatch):
    import descriptors
    calls=0
    def sample(*args):
        nonlocal calls
        calls+=1
        available=calls in [16,28]
        return dict(available=available,support=17/(256*144) if available else 0,
                    median_speed=3.1 if available else None,p95_speed=5.0 if available else None,
                    velocity=[1,0] if available else None,brightness_change_p95=.01 if available else None,
                    brightening_screen_area=0,darkening_screen_area=0,untracked_brightness_change_screen_area=0)
    monkeypatch.setattr(descriptors,'visible_motion',sample)
    target=stream(motion_window_policy='coverage-gated-window-v2')
    for i in range(30):add(target,[0,0,0],i/30)
    motion=target.report()['motion']
    assert motion['window_speed_supported'] is False
    assert motion['median_speed_viewports_per_second'] is None
    assert motion['p95_speed_viewports_per_second'] is None
    assert motion['supported_transition_count']==2
    assert motion['diagnostic_supported_subset']['median_speed_viewports_per_second']==3.1
    assert motion['available_transition_fraction']==pytest.approx(2/29)


def test_coverage_policy_rejects_unknown_names():
    with pytest.raises(ValueError,match='motion window policy'):
        stream(motion_window_policy='guess-zero-speed')
