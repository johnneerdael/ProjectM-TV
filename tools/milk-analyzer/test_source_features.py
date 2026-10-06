"""Contract consumers must distinguish geometry from simulated visual evidence."""
import copy
import hashlib
import importlib
import json

import pytest


def prediction():
    result = {'status': 'computed', 'uses_rendered_reference': False,
            'feature_basis': 'source-field-simulation',
            'input_hashes': {key: '1'*64 for key in [
                'preset_sha256', 'parsed_source_sha256', 'pcm_sha256', 'audio_sha256',
                'domain_sha256', 'compatibility_sha256', 'random_sha256', 'materials_sha256']},
            'provenance': {'engine': {'commit': '2'*40, 'patches_sha256': '3'*64},
                           'engine_archive_sha256': '4'*64, 'model_sha256': '5'*64,
                           'reader_sha256': '6'*64, 'wave_binary_sha256': '7'*64},
            'domain': {'profile': 'gles300'},
            'descriptors': {'frames_measured': 2, 'transitions_measured': 1,
                            'colour': {'mean_luma': 0, 'mean_coloured_fraction': 0},
                            'motion': {'p95_speed_viewports_per_second': None}},
            'geometry_features': {'basis': 'strict-source-no-display-frames',
                                  'uses_display_fields': False,
                                  'speed': {'p95': .1, 'samples': 12},
                                  'acceleration': {'p95': 0, 'samples': 6},
                                  'jerk': {'p95': None, 'samples': 0},
                                  'geometry_scope': 'custom shape fan vertices',
                                  'visible_motion': None}}
    result['input_hashes']['domain_sha256'] = hashlib.sha256(
        json.dumps(result['domain'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return result


def build(data):
    return importlib.import_module('source_features').forecast_feature_record(data)


def test_zero_luma_is_computed_but_untrackable_motion_is_unknown():
    result = build(prediction())
    assert result['features']['colour.mean_luma']['status'] == 'computed'
    assert result['features']['colour.mean_luma']['value'] == 0
    missing = result['features']['motion.p95_speed_viewports_per_second']
    assert missing['status'] == 'unknown'
    assert missing['value'] is None
    assert missing['unknown_reasons']


def test_geometry_and_simulated_display_features_have_distinct_evidence():
    result = build(prediction())
    assert result['feature_basis'] == 'source-field-simulation'
    geometry = result['features']['geometry.speed_p95']
    display = result['features']['colour.mean_luma']
    assert geometry['evidence_kind'] == 'sampled-source-geometry'
    assert geometry['support']['sample_count'] == 12
    assert display['evidence_kind'] == 'source-field-statistic'
    assert result['appearance_accuracy_verified'] is False
    assert geometry['interval'] is None


@pytest.mark.parametrize('changes', [
    {'uses_rendered_reference': True},
    {'feature_basis': 'native-frame-analysis'},
    {'feature_basis': 'strict-source-no-display-frames'},
    {'status': 'failed'},
])
def test_forecast_adapter_cannot_relabel_other_evidence(changes):
    data = prediction()
    data.update(changes)
    with pytest.raises(ValueError):
        build(data)


def test_missing_engine_or_stale_context_is_rejected():
    data = prediction()
    del data['provenance']['engine']
    with pytest.raises(ValueError):
        build(data)
    data = prediction()
    data['input_hashes']['pcm_sha256'] = 'missing'
    with pytest.raises(ValueError):
        build(data)


def test_cache_identity_changes_with_source_engine_inputs_or_feature_values():
    data = prediction()
    original = build(data)
    for section, key, value in [('input_hashes', 'audio_sha256', '9'*64),
                                ('provenance', 'engine_archive_sha256', 'a'*64)]:
        changed = copy.deepcopy(data)
        changed[section][key] = value
        assert build(changed)['context_sha256'] != original['context_sha256']
    changed = copy.deepcopy(data)
    changed['geometry_features']['speed']['p95'] = .2
    updated = build(changed)
    assert updated['context_sha256'] == original['context_sha256']
    assert updated['record_sha256'] != original['record_sha256']


def test_nonfinite_feature_values_are_rejected():
    data = prediction()
    data['descriptors']['colour']['mean_luma'] = float('nan')
    with pytest.raises(ValueError):
        build(data)


def test_contract_is_detached_from_mutable_prediction_inputs():
    data = prediction()
    result = build(data)
    data['provenance']['engine']['commit'] = '9'*40
    data['input_hashes']['audio_sha256'] = '9'*64
    assert result['context']['provenance']['engine']['commit'] == '2'*40
    assert result['context']['input_hashes']['audio_sha256'] == '1'*64


def test_domain_payload_cannot_borrow_another_context_hash():
    data = prediction()
    data['domain']['profile'] = 'glsl330'
    with pytest.raises(ValueError, match='domain'):
        build(data)


def test_strict_geometry_record_does_not_require_a_wave_or_display_execution():
    module = importlib.import_module('source_features')
    data = prediction()
    del data['provenance']['wave_binary_sha256']
    result = module.geometry_feature_record(data['geometry_features'], context={
        key: data[key] for key in ['input_hashes', 'provenance', 'domain']})
    assert result['feature_basis'] == 'strict-source-no-display-frames'
    assert all(name.startswith('geometry.') for name in result['features'])


def test_empty_measurement_window_cannot_claim_zero_flash_or_motion():
    data = prediction()
    data['descriptors'].update(frames_measured=0, transitions_measured=0)
    data['descriptors']['flashing'] = {'coherent_brightening_transitions': 0}
    data['descriptors']['motion']['available_transition_fraction'] = 0
    data['descriptors']['colour']['temporal_effective_hue_bins'] = 0
    features = build(data)['features']
    for key in ['flashing.coherent_brightening_transitions',
                'motion.available_transition_fraction', 'colour.temporal_effective_hue_bins']:
        assert features[key]['value'] is None
        assert features[key]['status'] == 'unknown'


def test_one_frame_has_palette_support_but_no_temporal_events():
    data = prediction()
    data['descriptors'].update(frames_measured=1, transitions_measured=0)
    data['descriptors']['flashing'] = {'coherent_darkening_transitions': 0}
    features = build(data)['features']
    assert features['colour.mean_luma']['value'] == 0
    assert features['flashing.coherent_darkening_transitions']['value'] is None


def test_new_palette_and_event_evidence_keeps_units_and_timing_in_record_hash():
    data = prediction()
    data['descriptors']['colour'].update(warm_cool=.8, mean_hue_entropy_nats=.3,
                                         hue_rate_p95_cycles_s=.1)
    event = {'start_time': 0, 'end_time': 1, 'dt': 1,
             'signed_mean_luma_delta': .2,
             'brightening': {'area': .25, 'mean_amplitude': .8, 'maximum_amplitude': .8},
             'darkening': {'area': 0, 'mean_amplitude': None, 'maximum_amplitude': None},
             'rgb': {'area': .25, 'mean_amplitude': .8, 'maximum_amplitude': .8},
             'coherent_up': True, 'coherent_down': False, 'motion_crossing_ruled_out': False}
    data['descriptors']['flashing'] = {'events': [event]}
    first = build(data)
    assert first['features']['colour.warm_cool']['value'] == .8
    assert first['features']['colour.mean_hue_entropy_nats']['unit'] == 'nats'
    assert first['features']['flashing.events']['value'][0]['brightening']['area'] == .25
    changed = copy.deepcopy(data)
    changed['descriptors']['flashing']['events'][0].update(start_time=1, end_time=2)
    assert build(changed)['record_sha256'] != first['record_sha256']
    assert first['features']['flashing.events']['value'][0]['start_time'] == 0


def test_event_evidence_is_unknown_with_no_transitions_and_rejects_missing_rows():
    data = prediction()
    data['descriptors']['transitions_measured'] = 0
    data['descriptors']['flashing'] = {'events': []}
    assert build(data)['features']['flashing.events']['status'] == 'unknown'
    data['descriptors']['transitions_measured'] = 1
    with pytest.raises(ValueError, match='event'):
        build(data)


def test_hue_rate_needs_temporal_support_even_when_palette_has_one_frame():
    data = prediction()
    data['descriptors'].update(frames_measured=1, transitions_measured=0)
    data['descriptors']['colour']['hue_rate_p95_cycles_s'] = 0
    assert build(data)['features']['colour.hue_rate_p95_cycles_s']['value'] is None


def test_nonconsecutive_event_intervals_cannot_be_cached_as_a_complete_window():
    data = prediction()
    data['descriptors']['flashing'] = {'events': [{'start_time': 0, 'end_time': 1,
                                                'dt': .5, 'signed_mean_luma_delta': .2}]}
    with pytest.raises(ValueError, match='interval'):
        build(data)


def test_negative_duration_cannot_pass_an_absolute_tolerance_check():
    data = prediction()
    empty = {'area': 0, 'mean_amplitude': None, 'maximum_amplitude': None}
    data['descriptors']['flashing'] = {'events': [{'start_time': 0, 'end_time': 1e-13,
        'dt': -1e-13, 'signed_mean_luma_delta': 0, 'brightening': empty,
        'darkening': empty, 'rgb': empty, 'coherent_up': False,
        'coherent_down': False, 'motion_crossing_ruled_out': False}]}
    with pytest.raises(ValueError, match='interval'):
        build(data)


def test_encoded_luma_event_delta_cannot_exceed_normalized_rgb_range():
    data = prediction()
    empty = {'area': 0, 'mean_amplitude': None, 'maximum_amplitude': None}
    data['descriptors']['flashing'] = {'events': [{'start_time': 0, 'end_time': 1,
        'dt': 1, 'signed_mean_luma_delta': 2, 'brightening': empty,
        'darkening': empty, 'rgb': empty, 'coherent_up': False,
        'coherent_down': False, 'motion_crossing_ruled_out': False}]}
    with pytest.raises(ValueError, match='luma'):
        build(data)
