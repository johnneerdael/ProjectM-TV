import numpy as np
import pytest

from component_influence import summarize_component_influence


def fields():
    return np.zeros((6, 4, 4), dtype=np.float32)


def test_steady_influence_does_not_become_repeated_bursts():
    actual=fields()+.4
    result=summarize_component_influence(np.arange(6)/30,actual,fields(),contrast_threshold=.1,area_threshold=.2)
    assert result['mean_influenced_screen_area']==1
    assert result['peak_changing_influence_screen_area']==0
    assert result['bursts']['uncensored_onsets']==0


def test_short_local_pulse_retains_its_peak_and_duration():
    actual=fields();actual[2,:2,:2]=.5
    result=summarize_component_influence(np.arange(6)/30,actual,fields(),contrast_threshold=.1,area_threshold=.2)
    assert result['peak_influenced_screen_area']==.25
    assert result['mean_influenced_screen_area']==pytest.approx(.25/6)
    assert result['peak_changing_influence_screen_area']==.25
    assert result['bursts']['burst_count']==1
    assert result['bursts']['bursts'][0]['duration_seconds']==pytest.approx(1/30)
    assert result['audience_score'] is None


def test_equal_fields_have_no_conditional_influence():
    actual=fields()+.5
    result=summarize_component_influence(np.arange(6)/30,actual,actual,contrast_threshold=.1,area_threshold=.2)
    assert result['peak_influenced_screen_area']==0
    assert result['bursts']['burst_count']==0


@pytest.mark.parametrize('failure',['shape','nan','range','threshold','time'])
def test_invalid_fields_or_measurement_domain_are_rejected(failure):
    actual=fields();control=fields();times=np.arange(6)/30;threshold=.1
    if failure=='shape':control=control[:5]
    if failure=='nan':actual[0,0,0]=np.nan
    if failure=='range':actual[0,0,0]=2
    if failure=='threshold':threshold=0
    if failure=='time':times[3]=times[2]
    with pytest.raises(ValueError):
        summarize_component_influence(times,actual,control,contrast_threshold=threshold,area_threshold=.2)
