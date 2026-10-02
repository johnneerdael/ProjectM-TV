"""Select a requested number of Dance presets from cached screen measurements."""

from dataclasses import asdict
import math
from pathlib import Path
import shutil
import tempfile

from .cache import write_atomic
from .export import verify_bundle
from .identity import canonical_json, digest, file_digest, load_json
from .models import PresetRecord


def select_dance(measurements: list[dict], inventory: list[PresetRecord], count: int = 500) -> list[dict]:
    if type(count) is not int or count < 1:
        raise ValueError('Dance collection size must be positive')
    known = {r.path: r for r in inventory}
    candidates = {}
    for row in measurements:
        record = row.get('preset', {})
        name = record.get('path')
        if name not in known or record != asdict(known[name]):
            continue
        score = row.get('score')
        if (row.get('status') != 'success' or type(score) not in (int, float)
                or not math.isfinite(score) or not 0 <= score <= 1 or row.get('reasons')):
            continue
        levels = row.get('levels', {})
        if (row.get('control_repeat_identical') is not True
                or set(levels) != {'bass-0.05','bass-0.15','bass-0.30'}
                or row.get('protocol', {}).get('version') != 'bass-screen-v1'):
            continue
        peaks = [v.get('peak_magnitude') for v in levels.values()]
        if any(type(v) not in (int,float) or not math.isfinite(v) or not 0 <= v <= 1 for v in peaks):
            continue
        if not math.isclose(score, sum(peaks)/3, abs_tol=1e-8):
            continue
        if name in candidates:
            raise ValueError(f'duplicate Dance measurement: {name}')
        candidates[name] = row
    if len(candidates) < count:
        raise ValueError(f'requested {count} Dance presets, only {len(candidates)} eligible measurements available')
    return sorted(candidates.values(), key=lambda r: (-r['score'], r['preset']['path']))[:count]


def export_dance_selection(measurements: list[dict], inventory: list[PresetRecord],
                           base_bundle: Path, destination: Path, evidence: dict,
                           count: int = 500) -> Path:
    """Update Dance only; preserve the other existing category memberships."""
    selected = select_dance(measurements, inventory, count)
    manifest = verify_bundle(base_bundle, inventory)
    prior_evidence = manifest['evidence']
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        staged = Path(temporary) / 'bundle'
        shutil.copytree(base_bundle, staged)
        index = staged / 'genres/dance.idx'
        index.write_text(''.join(f"{r['preset']['path']}\t{r['preset']['weight_mb']}\n"
                                 for r in sorted(selected, key=lambda r:r['preset']['path'].encode())), encoding='utf-8')
        prior_rows = [load_json_line(line) for line in (staged/'presets.jsonl').read_text().splitlines() if line]
        rows = [r for r in prior_rows if r['genre_id'] != 'dance']
        rows.extend({'preset': r['preset'], 'genre_id': 'dance', 'included': True,
                     'evidence_state': 'bass-screen-tested', 'rank': rank, 'score': r['score'],
                     'screen_response': r['levels'], 'protocol': r['protocol']}
                    for rank, r in enumerate(selected, 1))
        (staged/'presets.jsonl').write_text(''.join(canonical_json(r)+'\n' for r in
                                          sorted(rows, key=lambda r:(r['preset']['path'].encode(),r['genre_id']))), encoding='utf-8')
        used = {r['preset']['path']:r['preset'] for r in rows}
        manifest['presets'] = [used[name] for name in sorted(used, key=lambda n:n.encode())]
        for genre in manifest['genres']:
            if genre['id'] == 'dance':
                genre['count'] = count
        category_evidence = prior_evidence.get('categories', {g['id']:prior_evidence for g in manifest['genres']})
        category_evidence = dict(category_evidence, dance=dict(evidence,
                                  selection_count=count, cutoff_score=selected[-1]['score'],
                                  selection_rule='highest measured whole-screen bass response; no fixed strength cutoff',
                                  subjective_suitability='provisional'))
        manifest['evidence'] = {k:v for k,v in prior_evidence.items() if k in
                                ('texture_sha256','app_patches_sha256','engine_identity')}
        manifest['evidence']['categories'] = category_evidence
        manifest['evidence_level'] = 'category-specific measured suggestions; Dance selected by bass-caused screen change'
        manifest['checksums'] = {name:file_digest(staged/name) for name in manifest['checksums']}
        manifest.pop('generation_identity', None)
        manifest['generation_identity'] = digest(manifest)
        write_atomic(staged/'manifest.json', manifest)
        verify_bundle(staged, inventory)
        backup = destination.with_name(destination.name + '.previous')
        if backup.exists():
            raise ValueError('unfinished previous Dance export')
        if destination.exists():
            destination.rename(backup)
        try:
            staged.rename(destination)
        except BaseException:
            if backup.exists():
                backup.rename(destination)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    return destination


def load_json_line(line: str) -> dict:
    import json
    return json.loads(line)
