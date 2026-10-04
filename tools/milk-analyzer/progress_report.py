#!/usr/bin/env python3
"""Save structural support snapshots and compare gains, gaps and regressions."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


METRIC_DEFINITION = 'original-code-tokens-and-shader-whole-section-lowering-v1'
LABELS = {
    'code_tokens': 'Original code tokens',
    'parsed_code_tokens': 'Parsed code tokens',
    'parsed_code_percent': 'Parsed code (%)',
    'shader_tokens': 'Original shader tokens',
    'shader_lowered_tokens': 'Completely lowered shader tokens',
    'shader_lowering_percent': 'Shader lowering (%)',
    'presets_with_known_gaps': 'Presets with known gaps',
    'presets_without_known_gaps': 'Passing current structural checks',
}


def percent(numerator: int, denominator: int) -> float | None:
    return 100 * numerator / denominator if denominator else None


def make_snapshot(audit: dict, priority: dict) -> dict:
    if audit['schema_version'] != 1 or priority['schema_version'] != 1:
        raise ValueError('unsupported audit or gap schema')
    if (audit['corpus_sha256'] != priority['corpus_sha256'] or
            audit['presets'] != priority['presets']):
        raise ValueError('audit and gap report corpus mismatch')
    names = {row['preset'] for row in audit['rows']}
    if len(names) != audit['presets']:
        raise ValueError('audit preset rows are missing or duplicated')
    gaps = {}
    for gap in priority['gaps']:
        affected = sorted({use['preset'] for use in gap['uses']})
        if not set(affected).issubset(names) or len(affected) != gap['affected_presets']:
            raise ValueError('gap affected presets do not match the corpus/count')
        gaps[gap['gap']] = dict(affected_presets=affected,
                               affected_units=gap['affected_units'],
                               affected_source_tokens=gap['affected_source_tokens'])
    affected = set().union(*(set(g['affected_presets']) for g in gaps.values()))
    if len(affected) != priority['presets_with_known_gaps']:
        raise ValueError('gap preset total mismatch')
    shader_stages = [audit['stages'].get(stage, {}) for stage in ('warp', 'composite')]
    shader_tokens = sum(stage.get('source_tokens', 0) for stage in shader_stages)
    lowered = sum(stage.get('lowering_complete_tokens', 0) for stage in shader_stages)
    return dict(
        schema_version=1, metric_definition=METRIC_DEFINITION,
        corpus_sha256=audit['corpus_sha256'], presets=audit['presets'],
        provenance={key: audit.get(key) for key in
                    ('reader_sha256', 'audit_sha256', 'lowering_inputs')},
        metrics=dict(code_tokens=audit['code_tokens'],
                     parsed_code_tokens=audit['parsed_code_tokens'],
                     parsed_code_percent=percent(audit['parsed_code_tokens'], audit['code_tokens']),
                     shader_tokens=shader_tokens, shader_lowered_tokens=lowered,
                     shader_lowering_percent=percent(lowered, shader_tokens),
                     presets_with_known_gaps=len(affected),
                     presets_without_known_gaps=len(names - affected)),
        presets_without_known_gaps=sorted(names - affected), gaps=dict(sorted(gaps.items())),
        verified_behavior_percent=None, prediction_readiness='unassessed',
        scope='Structural support only; not certified behavior or prediction accuracy.')


def compare_snapshots(before: dict, after: dict) -> dict:
    reasons = []
    for label, value in [('before', before), ('after', after)]:
        if value.get('schema_version') != 1:
            reasons.append(f'{label} schema unsupported')
        if value.get('metric_definition') != METRIC_DEFINITION:
            reasons.append(f'{label} metric definition unsupported')
    for key in ('corpus_sha256', 'presets', 'metric_definition'):
        if before.get(key) != after.get(key):
            reasons.append(key + ' differs')
    if not reasons:
        for key in ('code_tokens', 'shader_tokens'):
            if before['metrics'][key] != after['metrics'][key]:
                reasons.append(key + ' denominator differs')
    result = dict(schema_version=1, comparable=not reasons, reasons=reasons,
                  verified_behavior_percent=None, prediction_readiness='unassessed',
                  scope='Structural support changes; not prediction accuracy.')
    if reasons:
        return result
    result['changed_provenance'] = sorted(key for key in
        set(before['provenance']) | set(after['provenance'])
        if before['provenance'].get(key) != after['provenance'].get(key))
    metrics = {}
    for key in LABELS:
        old, new = before['metrics'][key], after['metrics'][key]
        metrics[key] = dict(before=old, after=new,
                            delta=new - old if old is not None and new is not None else None)
    result['metrics'] = metrics
    old_clear, new_clear = (set(snapshot['presets_without_known_gaps'])
                            for snapshot in (before, after))
    result['newly_without_known_gaps'] = sorted(new_clear - old_clear)
    result['newly_with_known_gaps'] = sorted(old_clear - new_clear)
    changes = []
    for reason in sorted(set(before['gaps']) | set(after['gaps'])):
        old, new = before['gaps'].get(reason, {}), after['gaps'].get(reason, {})
        old_names, new_names = set(old.get('affected_presets', [])), set(new.get('affected_presets', []))
        changes.append(dict(
            gap=reason, before_presets=len(old_names), after_presets=len(new_names),
            delta_presets=len(new_names) - len(old_names),
            resolved_presets=sorted(old_names - new_names),
            introduced_presets=sorted(new_names - old_names),
            delta_units=new.get('affected_units', 0) - old.get('affected_units', 0),
            delta_source_tokens=new.get('affected_source_tokens', 0) - old.get('affected_source_tokens', 0)))
    result['gaps'] = sorted(changes, key=lambda gap: (-gap['after_presets'], gap['gap']))
    return result


def render_report(result: dict) -> str:
    lines = ['# Interpreter support progress', '', result['scope'], '',
             '**Prediction readiness: unassessed for the entire corpus.**',
             'Passing current structural checks only means no parsing/lowering gap was recorded. '
             'Runtime inputs, full effect-chain integration and appearance predictions are not assessed by this report.', '']
    if not result['comparable']:
        return '\n'.join(lines + ['Snapshots are not comparable: ' + '; '.join(result['reasons']), ''])
    lines += ['Percentage deltas are percentage points.', '',
              '| Measure | Before | After | Change |', '|---|---:|---:|---:|']
    for key, label in LABELS.items():
        row = result['metrics'][key]
        def display(value, *, signed=False):
            if value is None:
                return 'unmeasured'
            return format(value, '+.4f' if signed else '.4f') if isinstance(value, float) else format(value, '+d' if signed else 'd')
        lines.append(f"| {label} | {display(row['before'])} | {display(row['after'])} | {display(row['delta'], signed=True)} |")
    lines += ['', f"Presets newly without recorded gaps: {len(result['newly_without_known_gaps'])}.",
              f"Presets newly acquiring recorded gaps: {len(result['newly_with_known_gaps'])}.", '',
              'No recorded structural gaps does not establish correct behavior.', '',
              '## Missing semantics, ranked by current affected presets', '',
              '| Gap | Before | After | Removed from presets | Added to presets |',
              '|---|---:|---:|---:|---:|']
    for gap in result['gaps']:
        name = gap['gap'].replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {name} | {gap['before_presets']} | {gap['after_presets']} | {len(gap['resolved_presets'])} | {len(gap['introduced_presets'])} |")
    lines += ['', 'Changed analyzer provenance: ' + (', '.join(result['changed_provenance']) or 'none') + '.',
              'The companion JSON preserves the individual preset names for gains and regressions.', '']
    return '\n'.join(lines)


def read_input(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    save = commands.add_parser('snapshot')
    save.add_argument('--audit', type=Path, required=True)
    save.add_argument('--gaps', type=Path, required=True)
    save.add_argument('--output', type=Path, required=True)
    diff = commands.add_parser('compare')
    diff.add_argument('--before', type=Path, required=True)
    diff.add_argument('--after', type=Path, required=True)
    diff.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'snapshot':
        audit, audit_sha = read_input(args.audit)
        gaps, gaps_sha = read_input(args.gaps)
        result = make_snapshot(audit, gaps)
        result['input_sha256'] = dict(audit=audit_sha, gaps=gaps_sha)
        result['created_utc'] = datetime.now(timezone.utc).isoformat()
        result['reporter_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as output:
            output.write(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result['metrics'], indent=2))
    else:
        before, before_sha = read_input(args.before)
        after, after_sha = read_input(args.after)
        result = compare_snapshots(before, after)
        result['input_sha256'] = dict(before=before_sha, after=after_sha)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
        args.output.with_suffix('.md').write_text(render_report(result))
        print(render_report(result))


if __name__ == '__main__':
    main()
