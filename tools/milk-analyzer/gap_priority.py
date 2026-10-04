#!/usr/bin/env python3
"""Rank known source-audit gaps by distinct presets needing each calculation."""
import argparse
from collections import Counter, defaultdict
from collections.abc import Iterable
import hashlib
import json
from pathlib import Path


def rank_gaps(rows: Iterable[dict]) -> dict:
    """Count section uses once, preserving overlapping preset dependencies.

    This inventory describes known parsing/lowering gaps only. A preset with no
    such gaps is not necessarily behaviorally verified or visually predictable.
    Identical-content files count separately as corpus presets, not independent
    evidence of correctness.
    """
    identities = {}
    preset_gaps = defaultdict(set)
    uses = defaultdict(list)
    for row in rows:
        name = row['preset']
        if name in identities:
            raise ValueError(f'duplicate preset row: {name}')
        identities[name] = row['preset_sha256']
        for unit in row['units']:
            if unit['stage'] == 'configuration' or not unit['source_tokens']:
                continue
            if not unit['loader_numbering_reachable']:
                reasons = set() if unit.get('loader_ignored_confirmed') is True else {'source outside supported numbered loader'}
            elif not unit['target_parsed']:
                reasons = {'target parse unavailable'}
            else:
                reasons = set(unit['lowering_unknowns'])
                if unit['lowering_complete'] is False and not reasons:
                    reasons = {'incomplete lowering without recorded reason'}
            preset_gaps[name].update(reasons)
            witness = {key: unit[key] for key in
                       ('section', 'stage', 'lines', 'source_sha256', 'source_tokens')}
            witness.update(preset=name, preset_sha256=row['preset_sha256'])
            for reason in sorted(reasons):
                uses[reason].append(witness)

    gaps = []
    for reason, witnesses in uses.items():
        affected = {use['preset'] for use in witnesses}
        overlap = Counter(other for name in affected
                          for other in preset_gaps[name] - {reason})
        gaps.append(dict(
            gap=reason, affected_presets=len(affected),
            affected_units=len(witnesses),
            affected_source_tokens=sum(use['source_tokens'] for use in witnesses),
            sole_known_gap_presets=sum(preset_gaps[name] == {reason} for name in affected),
            overlap_presets=dict(sorted(overlap.items())),
            uses=sorted(witnesses, key=lambda use:
                        (use['preset'], use['section'], use['lines']))))
    gaps.sort(key=lambda gap: (-gap['affected_presets'], -gap['affected_units'],
                              -gap['affected_source_tokens'], gap['gap']))
    corpus = sorted(identities.items())
    return dict(
        schema_version=1, presets=len(identities),
        corpus_sha256=hashlib.sha256(json.dumps(corpus).encode()).hexdigest(),
        priority_order=['affected_presets descending', 'affected_units descending',
                        'affected_source_tokens descending', 'gap name ascending'],
        scope='Known source-audit parsing/lowering gaps; native-confirmed ignored source remains in the inventory '
              'without an execution gap. Behavioral obligations are not yet enumerated.',
        use_count_definition='One section partition needing a gap; repeated expressions/frames do not add uses.',
        sole_known_gap_definition='Removing this gap would leave no recorded structural gaps for these presets. '
                                  'This does not establish verified behavior or successful prediction.',
        overlap_definition='Counts share presets and must not be added as independent gains.',
        presets_with_known_gaps=sum(bool(reasons) for reasons in preset_gaps.values()),
        verified_behavior_percent=None, gaps=gaps)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--details', type=Path, required=True,
                        help='coverage_audit.py per-preset JSONL')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Hash and consume the same bytes so provenance describes the actual input.
    digest = hashlib.sha256()
    def rows():
        with args.details.open('rb') as source:
            for line in source:
                digest.update(line)
                if line.strip():
                    yield json.loads(line)
    result = rank_gaps(rows())
    result['details_sha256'] = digest.hexdigest()
    result['implementation_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'gaps'}, indent=2))
    for gap in result['gaps'][:10]:
        print(f"{gap['affected_presets']:4} presets / {gap['affected_units']:4} sections: {gap['gap']}")


if __name__ == '__main__':
    main()
