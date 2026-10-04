import importlib
import numpy as np
import pytest
import test_forecast


def module():return importlib.import_module('source_bass')


def test_band_intervention_preserves_waveform_time_and_recomputes_derived_volume():
    baseline=test_forecast.audio()
    schedule=[{}, {'bass':2,'bass_att':1.5}, {}]
    variant=module().band_variant(baseline,schedule,warmup_frames=1)
    assert baseline['frames'][1]['bass']!=variant['frames'][1]['bass']
    for a,b in zip(baseline['frames'],variant['frames']):
        for key in ['time','frame','fps','mid','treb','mid_att','treb_att',
                    'waveform_left','waveform_right','spectrum_left','spectrum_right']:
            assert a[key]==b[key]
    assert variant['frames'][1]['vol']==float(np.float32(4)*np.float32(.333))
    assert variant['frames'][1]['vol_att']==float(np.float32(3.5)*np.float32(.333))


def test_invalid_intervention_does_not_claim_bass_causality():
    baseline=test_forecast.audio()
    for schedule in [[{'mid':2},{},{}], [{'bass':2},{},{}], [{},{'bass':float('nan')},{}], [{},{}]]:
        with pytest.raises(ValueError):module().band_variant(baseline,schedule,warmup_frames=1)


def test_response_magnitude_rewards_broad_effect_over_tiny_bright_patch():
    control=np.zeros((20,20,4),dtype=np.float32)
    broad=control.copy();broad[...,:3]=.1
    small=control.copy();small[:2,:2,:3]=1
    a=module().pixel_response(broad,control)
    b=module().pixel_response(small,control)
    assert a['magnitude']==pytest.approx(.1)
    assert a['affected_area']==1
    assert b['magnitude']==pytest.approx(.01)
    assert a['magnitude']>b['magnitude']


def predict(body,schedule):
    source=test_forecast.native(test_forecast.BASE+body)
    return module().predict_bass_response(source,audio=test_forecast.audio(),
        binaries=test_forecast.BINARIES,domain=test_forecast.domain(),
        compatibility=test_forecast.compatibility(source),warmup_frames=1,
        interventions={'pulse':schedule})


def test_full_screen_bass_response_has_exact_area_strength_and_repeat_control():
    result=predict('comp_1=`shader_body {ret=(bass-1)*.2;}\n',[{}, {'bass':2}, {}])
    level=result['levels']['pulse']
    assert result['status']=='computed'
    assert result['control_repeat_identical'] is True
    assert level['trajectory'][0]['magnitude']==pytest.approx(.2,abs=1e-6)
    assert level['trajectory'][0]['affected_area']==1
    assert level['summary']['first_response_seconds']==0
    assert result['appearance_accuracy_verified'] is False


def test_audio_independent_shader_has_zero_causal_response_even_while_time_changes():
    result=predict('comp_1=`shader_body {ret=time*.1;}\n',[{}, {'bass':2,'bass_att':2}, {}])
    assert result['levels']['pulse']['summary']['peak_magnitude']==0
    assert result['levels']['pulse']['summary']['first_response_seconds'] is None


def test_feedback_keeps_response_after_the_bass_override_ends():
    result=predict('warp_1=`shader_body {ret=GetPixel(uv)*.5+(bass-1)*.2;}\n'
                   'comp_1=`shader_body {ret=GetPixel(uv);}\n',[{}, {'bass':2}, {}])
    trajectory=result['levels']['pulse']['trajectory']
    assert trajectory[0]['magnitude']==pytest.approx(.2,abs=1e-6)
    assert trajectory[1]['magnitude']==pytest.approx(.1,abs=1e-6)
    assert trajectory[1]['input_changed'] is False


def test_unchanged_schedule_is_not_called_a_zero_reactivity_measurement():
    with pytest.raises(ValueError,match='changes no'):
        predict('comp_1=`shader_body {ret=0;}\n',[{},{},{}])


def test_short_strong_response_is_preserved_alongside_the_robust_percentile():
    trajectory=[dict(time=i/30,magnitude=.8 if i==1 else 0,affected_area=1 if i==1 else 0,
                     local_intensity=.8 if i==1 else 0) for i in range(60)]
    result=module().summarize(trajectory,1/30)
    assert result['peak_magnitude']==0
    assert result['maximum_magnitude']==pytest.approx(.8)
    assert result['maximum_affected_area']==1


def test_first_response_delay_is_relative_to_actual_intervention_onset():
    trajectory=[dict(time=t,magnitude=m,affected_area=1,local_intensity=m)
                for t,m in [(5.0,0),(5.1,0),(5.2,.4)]]
    assert module().summarize(trajectory,5.1)['first_response_seconds']==pytest.approx(.1)
