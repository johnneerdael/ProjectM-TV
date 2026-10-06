"""Versioned source evidence records; physical features precede preference scores.

The forecast adapter is explicitly mode B. A separate geometry adapter emits
mode A evidence without requesting display fields or running a renderer.
Sampled values are never promoted into whole-domain bounds or confidence.
"""
import copy
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
import re


STRICT = 'strict-source-no-display-frames'
SIMULATED = 'source-field-simulation'
INPUT_HASHES = ('preset_sha256', 'parsed_source_sha256', 'pcm_sha256',
                'audio_sha256', 'domain_sha256', 'compatibility_sha256',
                'random_sha256', 'materials_sha256')
UNITS = {
    'colour': {
        'mean_luma': 'encoded RGB luma', 'mean_contrast': 'encoded RGB luma standard deviation',
        'mean_saturation': 'HSV saturation', 'mean_coloured_fraction': 'screen fraction',
        'mean_effective_hue_bins': 'effective hue bins', 'temporal_effective_hue_bins': 'effective hue bins',
    },
    'flashing': {
        'peak_mean_luma_jump': 'encoded RGB luma', 'peak_brightness_change_area': 'screen fraction',
        'peak_paired_luma_area_product': 'encoded RGB luma × screen fraction',
        'peak_brightening_screen_area': 'screen fraction', 'peak_darkening_screen_area': 'screen fraction',
        'peak_visible_brightening_fraction': 'visible-content fraction',
        'peak_visible_darkening_fraction': 'visible-content fraction',
        'peak_rgb_change_area': 'screen fraction', 'coherent_brightening_transitions': 'sampled transitions',
        'coherent_darkening_transitions': 'sampled transitions', 'dominant_sampled_brightness_hz': 'Hz',
        'spectral_peak_fraction': 'power fraction', 'frequency_resolution_hz': 'Hz', 'nyquist_hz': 'Hz',
    },
    'motion': {
        'available_transition_fraction': 'transition fraction', 'mean_supported_area': 'screen fraction',
        'median_speed_viewports_per_second': 'normalized viewport coordinates/s',
        'p95_speed_viewports_per_second': 'normalized viewport coordinates/s',
        'mean_acceleration_viewports_per_second_squared': 'normalized viewport coordinates/s²',
        'mean_warp_query_displacement': 'normalized viewport coordinates',
        'matched_brightness_change_p95': 'encoded RGB luma',
        'peak_matched_brightness_change_p95': 'encoded RGB luma',
        'peak_untracked_brightness_change_screen_area': 'screen fraction',
        'peak_matched_brightening_screen_area': 'screen fraction',
        'peak_matched_darkening_screen_area': 'screen fraction',
    },
}


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _hash(value, length=64):
    if not isinstance(value, str) or re.fullmatch('[0-9a-f]{'+str(length)+'}', value) is None:
        raise ValueError('exact source/context hash required')


def _context(context, *, require_wave):
    result = copy.deepcopy(context)
    inputs = result.get('input_hashes', {})
    for name in INPUT_HASHES:
        if name not in inputs:
            raise ValueError('missing feature input identity: '+name)
        if inputs[name] is None and name in {'random_sha256', 'materials_sha256'}:
            continue
        _hash(inputs[name])
    provenance = result.get('provenance', {})
    for name in ('engine_archive_sha256', 'model_sha256', 'reader_sha256'):
        _hash(provenance.get(name))
    if require_wave or 'wave_binary_sha256' in provenance:
        _hash(provenance.get('wave_binary_sha256'))
    engine = provenance.get('engine', {})
    _hash(engine.get('commit'), 40)
    _hash(engine.get('patches_sha256'))
    if not isinstance(result.get('domain'), dict) or not result['domain'].get('profile'):
        raise ValueError('declared feature domain required')
    if _digest(result['domain']) != inputs['domain_sha256']:
        raise ValueError('feature domain payload differs from its hash')
    result['feature_extractor_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def _feature(value, unit, evidence_kind, *, support, dependencies, unknown_reason):
    if value is not None:
        if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
            raise ValueError('finite numerical feature or explicit unknown required')
        value = float(value)
    return {'value': value, 'unit': unit, 'evidence_kind': evidence_kind,
            'status': 'computed' if value is not None else 'unknown',
            'interval': None, 'interval_kind': None,
            'support': copy.deepcopy(support), 'dependencies': list(dependencies),
            'unknown_reasons': [] if value is not None else [unknown_reason]}


def _geometry(geometry):
    if geometry.get('basis') != STRICT or geometry.get('uses_display_fields') is not False:
        raise ValueError('strict source geometry evidence required')
    features = {}
    for order, name in enumerate(('speed', 'acceleration', 'jerk'), 1):
        summary = geometry[name]
        unit = 'normalized viewport coordinates/s'+('' if order == 1 else '²' if order == 2 else '³')
        for statistic in ('p95', 'maximum'):
            features[f'geometry.{name}_{statistic}'] = _feature(
                summary.get(statistic), unit, 'sampled-source-geometry',
                support={'sample_count': summary['samples'], 'scope': geometry.get('geometry_scope'),
                         'method': 'consecutive-vertex divided differences; equal vertex weighting',
                         'budget_exceeded': geometry.get('budget_exceeded', False),
                         'derivative_sample_budget': geometry.get('derivative_sample_budget'),
                         'visibility_established': False},
                dependencies=['executed equation geometry', 'declared time schedule', 'component and vertex identity'],
                unknown_reason=('Geometry derivative calculation budget exceeded' if geometry.get('budget_exceeded') else
                                'Insufficient consecutive same-identity geometry samples'))
    return features


def _record(context, features, basis):
    context = _context(context, require_wave=basis == SIMULATED)
    result = {'schema_version': 1, 'feature_basis': basis, 'context': context,
              'context_sha256': _digest(context), 'features': features,
              'uses_rendered_reference': False, 'appearance_accuracy_verified': False,
              'limitations': ['Sample estimates are not whole-program bounds or calibrated confidence intervals',
                              'Dependencies identify calculation inputs, not a complete audio/material influence proof',
                              'Unknown motion/flash evidence must not be replaced with zero for collection eligibility']}
    result['record_sha256'] = _digest(result)
    return result


def geometry_feature_record(geometry, *, context):
    """Consume a strict geometry report without constructing simulated frames."""
    return _record(context, _geometry(geometry), STRICT)


def forecast_feature_record(prediction):
    """Adapt a computed source-field forecast; never accept native beta results."""
    if (prediction.get('status') != 'computed' or prediction.get('uses_rendered_reference') is not False or
            prediction.get('feature_basis') != SIMULATED):
        raise ValueError('computed explicitly labeled source-field forecast required')
    features = {}
    descriptors = prediction['descriptors']
    support = {'frames_measured': descriptors.get('frames_measured'),
               'transitions_measured': descriptors.get('transitions_measured'),
               'warmup_frames': descriptors.get('warmup_frames'),
               'settings': descriptors.get('settings'), 'scope': 'declared sampled display fields'}
    for section, fields in UNITS.items():
        for name, unit in fields.items():
            path = section+'.'+name
            frames = descriptors.get('frames_measured')
            transitions = descriptors.get('transitions_measured')
            count = frames if section == 'colour' or name == 'mean_warp_query_displacement' else transitions
            supported = type(count) is int and count > 0
            features[path] = _feature(
                descriptors.get(section, {}).get(name) if supported else None, unit, 'source-field-statistic',
                support=support, dependencies=['descriptors.'+path, 'source feedback/display simulation'],
                unknown_reason='Unavailable in the declared sample window or insufficient estimator support')
    if prediction.get('geometry_features') is not None:
        features.update(_geometry(prediction['geometry_features']))
    context = {key: prediction[key] for key in ('input_hashes', 'provenance', 'domain')}
    return _record(context, features, SIMULATED)
