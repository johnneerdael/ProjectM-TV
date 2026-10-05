import copy
import importlib

import pytest


def snapshot(gaps):
    module = importlib.import_module('progress_report')
    ranking = importlib.import_module('gap_priority').rank_gaps
    rows = []
    for name, reasons in gaps.items():
        rows.append(dict(preset=name, preset_sha256=name, units=[dict(
            stage='warp', section='warp_', lines=[1], source_sha256=name,
            source_tokens=10, loader_numbering_reachable=True,
            target_parsed=True, lowering_complete=not reasons,
            lowering_unknowns=reasons)]))
    priority = ranking(rows)
    audit = dict(schema_version=1, corpus_sha256=priority['corpus_sha256'],
                 presets=len(rows), rows=rows, code_tokens=10 * len(rows),
                 parsed_code_tokens=10 * len(rows), reader_sha256='reader',
                 audit_sha256='audit', lowering_inputs={'shader_fields.py': 'model'},
                 stages={'warp': dict(source_tokens=10 * len(rows),
                                      lowering_complete_tokens=10 * sum(not r for r in gaps.values()))})
    return module.make_snapshot(audit, priority)


def compare(before, after):
    return importlib.import_module('progress_report').compare_snapshots(before, after)


def test_equal_totals_do_not_hide_improvements_and_regressions():
    before = snapshot({'a': ['x'], 'b': []})
    after = snapshot({'a': [], 'b': ['y']})
    result = compare(before, after)
    assert result['comparable'] is True
    assert result['metrics']['presets_with_known_gaps']['delta'] == 0
    assert result['newly_without_known_gaps'] == ['a']
    assert result['newly_with_known_gaps'] == ['b']
    gaps = {g['gap']: g for g in result['gaps']}
    assert gaps['x']['resolved_presets'] == ['a']
    assert gaps['y']['introduced_presets'] == ['b']
    assert result['verified_behavior_percent'] is None


def test_resolving_one_overlapping_gap_does_not_clear_the_whole_preset():
    result = compare(snapshot({'a': ['x', 'y']}), snapshot({'a': ['y']}))
    assert result['newly_without_known_gaps'] == []
    assert result['metrics']['presets_with_known_gaps']['delta'] == 0
    assert next(g for g in result['gaps'] if g['gap'] == 'x')['resolved_presets'] == ['a']


def test_percentage_points_and_token_changes_are_both_reported():
    result = compare(snapshot({'a': ['x'], 'b': []}), snapshot({'a': [], 'b': []}))
    assert result['metrics']['shader_lowered_tokens']['delta'] == 10
    assert result['metrics']['shader_lowering_percent']['delta'] == 50


def test_corpus_or_definition_changes_do_not_produce_comparable_gains():
    before = snapshot({'a': ['x']})
    for field in ['corpus_sha256', 'metric_definition']:
        after = copy.deepcopy(before)
        after[field] = 'changed'
        result = compare(before, after)
        assert result['comparable'] is False
        assert 'metrics' not in result


def test_reader_changes_are_visible_without_invalidating_source_support_comparison():
    before = snapshot({'a': ['x']})
    after = snapshot({'a': []})
    after['provenance']['reader_sha256'] = 'new reader'
    result = compare(before, after)
    assert result['comparable'] is True
    assert result['changed_provenance'] == ['reader_sha256']


def test_mismatched_audit_and_gap_corpus_is_rejected():
    module = importlib.import_module('progress_report')
    with pytest.raises(ValueError, match='corpus'):
        module.make_snapshot(dict(schema_version=1, corpus_sha256='a', presets=1),
                             dict(schema_version=1, corpus_sha256='b', presets=1))


def test_identical_snapshots_have_zero_changes_and_readable_report():
    module = importlib.import_module('progress_report')
    before = snapshot({'a': ['x']})
    result = compare(before, before)
    assert all(row['delta'] == 0 for row in result['metrics'].values())
    assert result['newly_without_known_gaps'] == result['newly_with_known_gaps'] == []
    text = module.render_report(result)
    assert '| Presets with known gaps | 1 | 1 | +0 |' in text
    assert 'not prediction accuracy' in text
    assert 'Prediction readiness: unassessed for the entire corpus' in text
    assert 'Passing current structural checks' in text


def test_changed_token_denominators_are_not_reported_as_support_gains():
    before = snapshot({'a': ['x']})
    after = copy.deepcopy(before)
    after['metrics']['shader_tokens'] += 1
    assert compare(before, after)['comparable'] is False


def test_snapshot_cli_preserves_an_existing_baseline(tmp_path, monkeypatch):
    module = importlib.import_module('progress_report')
    output = tmp_path / 'baseline.json'
    output.write_text('existing baseline')
    monkeypatch.setattr(module, 'read_input', lambda path: ({}, 'hash'))
    monkeypatch.setattr(module, 'make_snapshot', lambda audit, gaps: {'metrics': {}})
    monkeypatch.setattr('sys.argv', ['progress_report.py', 'snapshot', '--audit', 'a',
                                    '--gaps', 'g', '--output', str(output)])
    with pytest.raises(FileExistsError):
        module.main()
    assert output.read_text() == 'existing baseline'
