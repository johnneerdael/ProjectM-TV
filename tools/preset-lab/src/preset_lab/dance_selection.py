"""Select a requested number of Dance presets from cached screen measurements."""

from dataclasses import asdict
import math
from pathlib import Path
import shutil
import tempfile
import json

from .cache import write_atomic
from .export import verify_bundle, _library_identity
from .identity import canonical_json, digest, file_digest, load_json
from .models import PresetRecord, RunConfig

EXPERIMENT_KEYS = ('version','code','worker','engine','textures_sha256','audio','config')


def matches_experiment(row: dict, experiment: dict) -> bool:
    return all(key in experiment and row.get('protocol', {}).get(key) == experiment[key]
               for key in EXPERIMENT_KEYS)


def current_experiment(repo: Path, measurements: Path, state: dict, worker: Path | None = None) -> dict:
    from .bass_screen import VERSION, bass_signals
    from .build_worker import prepare_engine
    from .inventory import inventory
    config = RunConfig()
    _, identity = prepare_engine(repo, measurements.parent.parent)
    if worker is None:
        ranked = state.get('ranking', [])
        if not ranked:
            raise ValueError('no current experiment available; run bass-screen first')
        expected_worker = ranked[0].get('protocol', {}).get('worker')
        candidates = []
        for root in (measurements.parent/'engine', measurements.parent, measurements.parent.parent):
            candidates.extend(root.glob('native-build/*/preset-lab-worker'))
        worker = next((p for p in candidates if file_digest(p) == expected_worker), None)
        if worker is None:
            raise ValueError('native worker unavailable; provide --worker')
    if load_json(worker.parent/'build-identity.json') != asdict(identity):
        raise ValueError('native worker differs from current engine/patches/instrumentation; rebuild and analyze')
    textures = repo/'core/src/main/assets/textures'
    texture_files = sorted(p for p in textures.rglob('*') if p.is_file() and p.name != '.DS_Store')
    _, assets = inventory(repo/'core/src/main/assets/presets', repo/'core/src/main/assets/presets.idx', textures)
    with tempfile.TemporaryDirectory(prefix='bass-selection-probes-') as directory:
        signals = bass_signals(config, Path(directory))
        audio = {name:file_digest(path) for name,path in signals.items()}
    return dict(version=VERSION, code=file_digest(Path(__file__).with_name('bass_screen.py')),
                worker=file_digest(worker), engine=asdict(identity), config=asdict(config), audio=audio,
                textures_sha256=digest([(p.relative_to(textures).as_posix(),file_digest(p)) for p in texture_files]),
                texture_bundle_sha256=assets['texture_sha256'])


def select_dance(measurements: list[dict], inventory: list[PresetRecord], count: int = 500,
                 *, experiment: dict) -> list[dict]:
    if type(count) is not int or count < 1:
        raise ValueError('Dance collection size must be positive')
    known = {r.path: r for r in inventory}
    candidates = {}
    for row in measurements:
        if not matches_experiment(row, experiment):
            continue
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
                           count: int = 500, *, experiment: dict) -> Path:
    """Update Dance only; preserve the other existing category memberships."""
    selected = select_dance(measurements, inventory, count, experiment=experiment)
    stored = load_json(base_bundle/'manifest.json')
    manifest = verify_bundle(base_bundle, [PresetRecord(**r) for r in stored['presets']],
                             check_library_identity=False)
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
        current = {r.path:asdict(r) for r in inventory}
        if any(r['preset'] != current.get(r['preset']['path']) for r in rows):
            raise ValueError('stale retained category members; refresh their evidence before preserving them')
        rows.extend({'preset': r['preset'], 'genre_id': 'dance', 'included': True,
                     'evidence_state': 'bass-screen-tested', 'rank': rank, 'score': r['score'],
                     'screen_response': r['levels'], 'protocol': r['protocol']}
                    for rank, r in enumerate(selected, 1))
        (staged/'presets.jsonl').write_text(''.join(canonical_json(r)+'\n' for r in
                                          sorted(rows, key=lambda r:(r['preset']['path'].encode(),r['genre_id']))), encoding='utf-8')
        used = {r['preset']['path']:r['preset'] for r in rows}
        manifest['presets'] = [used[name] for name in sorted(used, key=lambda n:n.encode())]
        manifest['library_sha256'] = _library_identity(inventory)
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
        manifest['evidence']['engine_identity'] = experiment['engine']
        manifest['evidence']['app_patches_sha256'] = experiment['engine']['patches_sha256']
        manifest['evidence']['texture_sha256'] = experiment['texture_bundle_sha256']
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
    return json.loads(line)
