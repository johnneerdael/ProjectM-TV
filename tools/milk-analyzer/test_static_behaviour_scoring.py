"""Source-model activity decisions retain extent and missing contributors."""
import pytest


def evidence(*, speed=0., contrast=0., frequency=0., extent=1., complete=True):
    return {'policy':'source-static-behaviour-v1', 'context':{'viewport':[1920,1080],'feedback_fps':30},
            'output_model_complete':complete,
            'flashing':{'records':[{'component_id':'shader_composite','kind':'shader_brightness_change',
                'periodic_contrast_range':[contrast,contrast], 'brightness_delta_range':[0.,contrast],
                'cycle_rate_hz':frequency, 'event_rate_hz':0., 'event_schedules':[],
                'nominal_continuity':'smooth_nominal','total_brightness_rate_known':True,
                'maximum_brightness_change_per_second':contrast*frequency*3.141592653589793,
                'unknown_reasons':[]}], 'source_hazards':[], 'unknown_reasons':[]},
            'motion':{'contributions':[{'component_id':'shader_composite','kind':'geometry_trajectory',
                'rate_kind':'source_time_partial','speed_interval_vp_per_second':[speed,speed],
                'unknown_reasons':[]}]},
            'prominence':{'by_component':{'shader_composite':{
                'displayed_support_fraction_interval':[extent,extent],
                'displayed_contribution_interval':[extent,extent],
                'final_transfer':{'difference_gain_interval':[1.,1.]},
                'known_invalid_native_domain':False,'unknown_reasons':[]}}}}


def test_calm_source_model_is_chill():
    from static_behaviour_scoring import score_static_behaviour
    result=score_static_behaviour(evidence(speed=.01,contrast=.1,frequency=.05))
    assert 'Chill' in result['eligible_bands']
    assert result['intensity']['interval'][1]<=30


def test_uniform_fast_brightness_modulation_is_intense():
    from static_behaviour_scoring import score_static_behaviour
    result=score_static_behaviour(evidence(contrast=.8,frequency=4))
    assert 'Intense' in result['eligible_bands']
    assert 'Chill' not in result['eligible_bands']


@pytest.mark.parametrize('extent',[0.,.0001])
def test_invisible_or_tiny_fast_effect_does_not_drive_intense(extent):
    from static_behaviour_scoring import score_static_behaviour
    result=score_static_behaviour(evidence(speed=10.,contrast=1.,frequency=30.,extent=extent))
    assert 'Intense' not in result['predicted_bands']
    assert result['intensity']['interval'][1]<30


def test_unknown_prominent_motion_stays_unknown():
    from static_behaviour_scoring import score_static_behaviour
    model=evidence()
    model['motion']['contributions'][0]['speed_interval_vp_per_second']=[0.,None]
    result=score_static_behaviour(model)
    assert 'Chill' not in result['eligible_bands']
    assert result['unknown_contributors']


def test_no_records_cannot_prove_calm_when_output_model_incomplete():
    from static_behaviour_scoring import score_static_behaviour
    model=evidence(complete=False);model['flashing']['records']=[];model['motion']['contributions']=[]
    result=score_static_behaviour(model)
    assert result['eligible_bands']==[]
    assert result['intensity']['interval']==[1.,100.]


def test_nonfinite_domain_never_resolves_an_opacity_zero_effect():
    from static_behaviour_scoring import score_static_behaviour
    model=evidence(extent=0.)
    model['prominence']['by_component']['shader_composite']['known_invalid_native_domain']=True
    result=score_static_behaviour(model)
    assert result['eligible_bands']==[]
    assert result['unknown_contributors']


def test_exported_preferences_cannot_mutate_future_scores():
    from static_behaviour_scoring import score_static_behaviour
    first=score_static_behaviour(evidence())
    first['preference_rules']['motion_reference_vp_s']=999
    assert score_static_behaviour(evidence())['preference_rules']['motion_reference_vp_s']==.75


def test_partial_calm_components_cannot_nominate_chill_when_activity_is_unknown():
    from static_behaviour_scoring import score_static_behaviour
    model=evidence(speed=.01,complete=False)
    result=score_static_behaviour(model)
    assert 'Chill' not in result['predicted_bands']
    assert result['eligible_bands']==[]


def test_zero_known_components_with_missing_activity_do_not_supply_a_calm_index():
    from static_behaviour_scoring import score_static_behaviour
    result=score_static_behaviour(evidence(complete=False))
    assert result['intensity']['value'] is None
    assert result['predicted_bands']==[]


def test_nonperiodic_low_contrast_does_not_become_intense_from_rate_alone():
    from static_behaviour_scoring import score_static_behaviour
    model=evidence()
    record=model['flashing']['records'][0]
    record.update(periodic_contrast_range=None,cycle_rate_hz=None,
                  brightness_delta_range=[0.,.01],maximum_brightness_change_per_second=100.)
    result=score_static_behaviour(model)
    assert 'Intense' not in result['predicted_bands']
    assert result['intensity']['interval'][1]<30


def textured_partial_model(extent=1.):
    model=evidence(complete=False,extent=extent)
    record=model['flashing']['records'][0]
    record.update(periodic_contrast_range=None,brightness_delta_range=None,
                  maximum_brightness_change_per_second=None,cycle_rate_hz=None,total_brightness_rate_known=False)
    record['fixed_unit_texture_material_partial']={
        'policy':'source-fixed-unit-texture-material-modulation-v1',
        'maximum_brightness_change_per_second':3.,'brightness_delta_range':[0.,1.],
        'nominal_continuity':'smooth_nominal','total_brightness_rate_known':False,
        'sampling_coordinate_response_included':False,'texture_history_change_rate':None,
        'premises':['Sample RGBA and destination fixed in[0,1]']}
    return model


def test_quantified_texture_material_can_inform_potential_without_certifying_total():
    from static_behaviour_scoring import score_static_behaviour
    result=score_static_behaviour(textured_partial_model())
    assert result['intensity']['value']==100
    assert 'Intense' in result['predicted_bands']
    assert result['eligible_bands']==[]
    assert result['unknown_contributors']
    assert result['partial_contributions'][0]['scope']=='fixed_texture_material_partial'


@pytest.mark.parametrize('extent',[0.,.0001])
def test_tiny_or_disconnected_texture_partial_does_not_become_intense(extent):
    from static_behaviour_scoring import score_static_behaviour
    result=score_static_behaviour(textured_partial_model(extent))
    assert 'Intense' not in result['predicted_bands']
    assert 'Chill' not in result['predicted_bands']


def test_unknown_texture_partial_transfer_does_not_invent_strength():
    from static_behaviour_scoring import score_static_behaviour
    model=textured_partial_model();model['prominence']['by_component']['shader_composite']['final_transfer']['difference_gain_interval']=[0.,None]
    result=score_static_behaviour(model)
    assert result['intensity']['value'] is None
    assert result['partial_contributions'][0]['strength_interval'][1] is None


def test_editable_preference_reference_changes_mapping_not_mathematical_evidence():
    from static_behaviour_scoring import score_static_behaviour
    model=evidence(speed=.6);before=repr(model)
    default=score_static_behaviour(model)
    adjusted=score_static_behaviour(model,preferences={'motion_reference_vp_s':1.5})
    assert default['intensity']['value']>adjusted['intensity']['value']
    assert adjusted['intensity']['value']==pytest.approx(40.6)
    assert repr(model)==before


@pytest.mark.parametrize('preferences',[{'motion_reference_vp_s':0},{'unknown':1},{'flash_cycle_reference_hz':float('nan')}])
def test_invalid_preferences_are_rejected(preferences):
    from static_behaviour_scoring import score_static_behaviour
    with pytest.raises(ValueError):score_static_behaviour(evidence(),preferences=preferences)


def test_actual_producer_piecewise_material_partial_can_inform_potential():
    from static_behaviour_scoring import score_static_behaviour
    model=textured_partial_model()
    partial=model['flashing']['records'][0]['fixed_unit_texture_material_partial']
    partial['nominal_continuity']='piecewise_lipschitz'
    result=score_static_behaviour(model)
    assert result['partial_contributions'][0]['strength_interval'][1]==1.
    assert result['intensity']['value']==100
    assert result['eligible_bands']==[]


def test_source_producer_textured_fill_is_consumed_without_changing_total_scope():
    from test_source_flash_behaviour import textured_fill
    from static_behaviour_scoring import score_static_behaviour
    row=textured_fill('r=.5+.4*sin(60*time);r2=r;g=0;g2=0;b=0;b2=0;a=.5;a2=.5;border_a=0;additive=1;')
    model=textured_partial_model()
    identity=row['component_id']
    model['flashing']['records']=[row]
    model['prominence']['by_component'][identity]=model['prominence']['by_component'].pop('shader_composite')
    model['motion']['contributions']=[]
    result=score_static_behaviour(model)
    assert result['partial_contributions'][0]['strength_interval'][1]>0
    assert result['intensity']['value'] is not None
    assert result['eligible_bands']==[]
    assert row['total_brightness_rate_known'] is False
