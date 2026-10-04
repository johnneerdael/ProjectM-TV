import importlib

import pytest


def unit(*reasons, section='warp_', tokens=10, parsed=True, reachable=True):
    return dict(section=section, stage='warp', lines=[1], source_sha256='unit',
                source_tokens=tokens, target_parsed=parsed,
                loader_numbering_reachable=reachable,
                lowering_complete=not reasons, lowering_unknowns=list(reasons))


def preset(name, *units):
    return dict(preset=name, preset_sha256=name, units=list(units))


def report(*rows):
    return importlib.import_module('gap_priority').rank_gaps(rows)


def test_distinct_presets_outrank_repeated_sections_and_source_volume():
    result = report(preset('a', unit('rare', tokens=10000),
                           unit('rare', section='comp_', tokens=10000)),
                    preset('b', unit('common')), preset('c', unit('common')))
    common, rare = result['gaps']
    assert common['gap'] == 'common'
    assert common['affected_presets'] == 2
    assert rare['affected_presets'] == 1
    assert rare['affected_units'] == 2


def test_overlap_is_reported_without_claiming_a_preset_is_fully_verified():
    result = report(preset('a', unit('x', 'y')), preset('b', unit('x')),
                    preset('c', unit('y'), unit('z', section='comp_')))
    gaps = {g['gap']: g for g in result['gaps']}
    assert gaps['x']['sole_known_gap_presets'] == 1
    assert gaps['y']['sole_known_gap_presets'] == 0
    assert gaps['x']['overlap_presets'] == {'y': 1}
    assert gaps['y']['overlap_presets'] == {'x': 1, 'z': 1}
    assert result['presets_with_known_gaps'] == 3
    assert result['verified_behavior_percent'] is None


def test_duplicate_reasons_count_one_section_use_and_keep_source_witness():
    gap = report(preset('a', unit('x', 'x')))['gaps'][0]
    assert gap['affected_presets'] == gap['affected_units'] == 1
    assert gap['affected_source_tokens'] == 10
    assert gap['uses'][0]['lines'] == [1]
    assert gap['uses'][0]['preset_sha256'] == 'a'


def test_missing_parses_and_omitted_source_are_visible_configuration_is_separate():
    config = unit(section='configuration', parsed=False, reachable=False)
    config['stage'] = 'configuration'
    result = report(preset('a', unit(parsed=False), config),
                    preset('b', unit(parsed=False, reachable=False)))
    gaps = {g['gap']: g for g in result['gaps']}
    assert set(gaps) == {'target parse unavailable', 'source outside supported numbered loader'}
    assert gaps['target parse unavailable']['affected_presets'] == 1
    assert gaps['source outside supported numbered loader']['affected_presets'] == 1


def test_duplicate_preset_rows_are_rejected_instead_of_inflating_counts():
    with pytest.raises(ValueError, match='duplicate preset'):
        report(preset('a', unit('x')), preset('a', unit('x')))


def test_order_is_deterministic_and_identical_content_files_remain_distinct_presets():
    a, b = preset('a', unit('x')), preset('b', unit('x'))
    b['preset_sha256'] = a['preset_sha256']
    assert report(a, b) == report(b, a)
    assert report(a, b)['gaps'][0]['affected_presets'] == 2
