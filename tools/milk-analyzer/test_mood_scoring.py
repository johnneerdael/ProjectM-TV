"""Chosen scoring transforms have analytic oracles; none use preset images."""
import copy
import hashlib
import importlib
import json

import pytest


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def record(values, *, basis='strict-source-no-display-frames', bounded=()):
    from source_features import geometry_feature_record
    from test_source_features import prediction
    data = prediction()
    result = geometry_feature_record(data['geometry_features'], context={
        key: data[key] for key in ['input_hashes','provenance','domain']})
    result['feature_basis'] = basis
    result['features'] = {}
    for name, value in values.items():
        result['features'][name] = {'value': value, 'status': 'computed',
            'evidence_kind': 'source-domain-bound' if name in bounded else 'source-point-query',
            'interval': [value,value] if name in bounded else None,
            'interval_kind': 'conservative-domain-bound' if name in bounded else None,
            'support': {'scope': 'preset-output', 'domain_sha256': result['context']['input_hashes']['domain_sha256']}}
    result['record_sha256'] = digest({key:value for key,value in result.items() if key!='record_sha256'})
    return result


def complete(**updates):
    return {'motion.speed_p95_vp_s': 0, 'motion.acceleration_p95_vp_s2': 0,
            'motion.jerk_p95_vp_s3': 0, 'motion.discontinuities_hz': 0,
            'flash.coherent_transitions_hz': 0, 'flash.coherent_delta_peak': 0,
            'brightness.jump_p95': 0, 'audio.bass_peak_rgb_effect': 0,
            'palette.warm_cool': .8, 'palette.coloured_support': 1,
            'palette.effective_hue_bins': 1, 'palette.hue_rate_p95_cycles_s': 0,
            'structure.nonlinear_warp': 0, 'structure.symmetry': 0,
            'feedback.complexity': 0, **updates}


def score(data, **options):
    return importlib.import_module('mood_scoring').score_source_features(data, **options)


def test_stationary_supported_values_do_not_imply_chill_without_bounds():
    result = score(record(complete()))
    assert result['scores']['intensity']['value'] == 1
    assert result['scores']['smoothness']['value'] == 100
    assert result['scores']['warm']['value'] == 90
    assert result['scores']['cold']['value'] == pytest.approx(10)
    assert 'Chill' not in result['bands']
    assert result['chill_constraints']['unknown'] > 0


def test_missing_inputs_widen_scores_instead_of_renormalizing():
    values = complete()
    del values['audio.bass_peak_rgb_effect']
    result = score(record(values))['scores']['intensity']
    assert result['value'] is None
    assert result['interval'] == pytest.approx([1, 8.92])


def test_fast_steady_motion_can_be_smooth_and_normal():
    result = score(record(complete(**{'motion.speed_p95_vp_s': .75})))
    assert result['scores']['intensity']['value'] == pytest.approx(28.72)
    assert result['scores']['smoothness']['value'] == 100
    assert result['bands'] == ['Normal']


def test_coherent_flash_floor_prevents_a_calm_label():
    result = score(record(complete(**{'flash.coherent_transitions_hz': 4,
                                     'flash.coherent_delta_peak': .3})))
    assert result['scores']['intensity']['value'] == 100
    assert result['bands'] == ['Intense']


def test_unknown_palette_support_cannot_produce_warm_tag():
    values = complete(); del values['palette.coloured_support']
    result = score(record(values))
    assert result['scores']['warm']['value'] is None
    assert 'Warm' not in result['tags']


def test_partial_shape_motion_is_not_substituted_for_whole_preset_motion():
    result = score(record({'geometry.speed_p95': .01}))
    assert result['scores']['intensity']['interval'] == [1,100]


def test_simulated_evidence_requires_explicit_opt_in():
    data = record(complete(), basis='source-field-simulation')
    with pytest.raises(ValueError, match='opt-in'):
        score(data)
    assert score(data, allow_simulated=True)['feature_basis'] == 'source-field-simulation'


def test_stale_record_hash_and_unknown_basis_are_rejected():
    data = record(complete());data['features']['motion.speed_p95_vp_s']['value']=1
    with pytest.raises(ValueError, match='hash'):
        score(data)
    with pytest.raises(ValueError, match='basis'):
        score(record(complete(), basis='native-frame-analysis'))


def test_profile_changes_only_rescore_cached_features():
    module = importlib.import_module('mood_scoring')
    data = record(complete())
    original = copy.deepcopy(data)
    profile = {'id': 'warm-v1', 'preferences': [
        {'feature': 'score.warm', 'target': [80,100], 'scale': 20, 'weight': 1}], 'constraints': []}
    warm = module.score_source_features(data, profile=profile)
    profile['preferences'][0]['target'] = [0,20]
    cold = module.score_source_features(data, profile=profile)
    assert warm['profile']['suitability']['value'] == 100
    assert cold['profile']['suitability']['value'] < 1
    assert warm['profile_sha256'] != cold['profile_sha256']
    assert data == original


def test_unknown_preference_keeps_its_weight_and_reduces_coverage():
    profile = {'id': 'two-v1', 'preferences': [
        {'feature': 'score.warm','target':[80,100],'scale':20,'weight':1},
        {'feature': 'feedback.half_life_s','target':[.3,1.5],'scale':1,'weight':1}], 'constraints': []}
    result = score(record(complete()), profile=profile)['profile']
    assert result['suitability']['value'] is None
    assert result['suitability']['interval'] == [50,100]
    assert result['supported_preference_weight_fraction'] == .5
    assert result['eligible'] is False


def test_no_flash_chill_eligibility_requires_declared_matching_domain_bounds():
    values = complete()
    bounds = {'motion.speed_upper_bound_vp_s': .1, 'motion.acceleration_upper_bound_vp_s2': .2,
              'motion.jerk_upper_bound_vp_s3': .5, 'flash.local_or_colour_pulses_hz': 0}
    values.update(bounds)
    bounded = list(bounds)+['flash.coherent_transitions_hz']
    result = score(record(values,bounded=bounded))
    assert result['bands'] == ['Chill']
    assert result['chill_constraints']['supported_passed'] == 5
    data = record(values,bounded=bounded)
    entry = data['features']['flash.local_or_colour_pulses_hz']
    entry['support']['domain_sha256'] = '0'*64
    data['record_sha256'] = digest({key:value for key,value in data.items() if key!='record_sha256'})
    assert 'Chill' not in score(data)['bands']


def test_native_feature_cannot_hide_inside_a_strict_record():
    data = record(complete())
    data['features']['palette.warm_cool']['evidence_kind']='native-frame-statistic'
    data['record_sha256']=digest({key:value for key,value in data.items() if key!='record_sha256'})
    with pytest.raises(ValueError,match='evidence'):
        score(data)


def test_genre_defaults_remain_independent_of_age_and_explicit_preferences():
    module=importlib.import_module('mood_profiles')
    profile=module.get_profile('melodic-techno-v1')
    assert sum(item['weight'] for item in profile['preferences'])==pytest.approx(.9)
    assert not any(item['feature']=='score.warm' for item in profile['preferences'])
    assert module.get_profile(age_band='18–34')==module.get_profile(age_band='55–69')
    gentle=module.get_profile(age_band='70+')
    assert gentle['id']=='gentle-home-tv-v1'
    explicit=module.get_profile('psychedelic-v1',age_band='70+')
    assert explicit['id']=='psychedelic-v1'
    assert module.get_profile('neutral-v1',age_band='70+')['id']=='neutral-v1'
    assert all(rule.get('require_bound') for rule in gentle['constraints'])


def test_psychedelic_tag_requires_structural_support_not_rainbow_alone():
    rich=complete(**{'structure.nonlinear_warp':1,'structure.symmetry':1,'feedback.complexity':1,
                     'palette.effective_hue_bins':8,'palette.hue_rate_p95_cycles_s':.5})
    assert 'Psychedelic' in score(record(rich))['tags']
    rainbow=complete(**{'palette.effective_hue_bins':8,'palette.hue_rate_p95_cycles_s':.5})
    assert 'Psychedelic' not in score(record(rainbow))['tags']


def test_supported_palette_interval_is_evidence_even_when_score_is_not_a_point():
    data=record(complete())
    data['features']['palette.warm_cool']['interval']=[.75,.85]
    data['record_sha256']=digest({key:value for key,value in data.items() if key!='record_sha256'})
    profile={'id':'warm-range','constraints':[],'preferences':[
        {'feature':'score.warm','target':[80,100],'scale':20,'weight':1}]}
    result=score(data,profile=profile)['profile']
    assert result['suitability']['value']==100
    assert result['supported_preference_weight_fraction']==1
    assert result['eligible'] is True


def test_large_finite_preference_weights_preserve_their_ratio():
    profile={'id':'huge','constraints':[],'preferences':[
        {'feature':'score.warm','target':[80,100],'scale':20,'weight':1e308},
        {'feature':'score.smoothness','target':[80,100],'scale':20,'weight':1e308}]}
    result=score(record(complete()),profile=profile)['profile']
    assert result['suitability']['value']==100
    assert result['supported_preference_weight_fraction']==1


def test_negative_physical_bounds_cannot_qualify_chill():
    values=complete()
    bounds={'motion.speed_upper_bound_vp_s':-100,'motion.acceleration_upper_bound_vp_s2':-100,
            'motion.jerk_upper_bound_vp_s3':-100,'flash.local_or_colour_pulses_hz':-1}
    values.update(bounds)
    with pytest.raises(ValueError,match='nonnegative'):
        score(record(values,bounded=list(bounds)+['flash.coherent_transitions_hz']))


def test_edited_domain_payload_cannot_borrow_old_bound_identity():
    data=record(complete())
    data['context']['domain']['profile']='glsl330'
    data['context_sha256']=digest(data['context'])
    data['record_sha256']=digest({key:value for key,value in data.items() if key!='record_sha256'})
    with pytest.raises(ValueError,match='domain'):
        score(data)


def test_direct_cold_preference_consumes_actual_producer_field_name():
    from source_features import forecast_feature_record
    from test_source_features import prediction
    data=prediction()
    data['descriptors']['colour'].update(warm_cool=-.8,mean_coloured_fraction=1)
    cached=forecast_feature_record(data)
    profile={'id':'cold-direct','constraints':[],'preferences':[
        {'feature':'colour.warm_cool','target':[-1,-.4],'scale':.2,'weight':1}]}
    result=score(cached,profile=profile,allow_simulated=True)
    assert result['profile']['suitability']['value']==100
    assert result['profile']['eligible'] is True
    assert result['scores']['cold']['value']==90
