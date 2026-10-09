"""Published31 corpus identity, separate static metadata and bounded worker checks."""
import json
import shutil
from pathlib import Path

import pytest

import corpus_worker
import preset_corpus
from corpus_store import atomic_json, file_hash
from engine_profiles import CORE_2329_ENGINE, CORE_2331_ENGINE
from forecast import CORE_2329_EQUATION_RNG_POLICY, CORE_2331_EQUATION_RNG_POLICY, model_file_hashes

ROOT = Path(__file__).resolve().parents[2]


def test_cli_defaults_bind_latest32_bytes_without_reusing_historical_output():
    args = preset_corpus.parse_args([])
    assert args.binaries == ROOT / 'build/preset-corpus/source31/adapters'
    assert args.aar == ROOT / 'build/preset-corpus/published32/projectM-TV-core-2.3.32.aar'
    assert args.engine_profile == ROOT / 'tools/milk-analyzer/profiles/published-core-v2.3.32.json'
    assert args.output.name.endswith('-core2332')
    assert args.target == 'core2331'
    explicit = preset_corpus.parse_args(['--aar', '/tmp/one.aar', '--engine-profile', '/tmp/profile.json'])
    assert explicit.aar == Path('/tmp/one.aar') and explicit.engine_profile == Path('/tmp/profile.json')


def test_latest32_publication_has_identical_full_bytes_and_qualified_source_engine():
    args=preset_corpus.parse_args([])
    profile=json.loads(args.engine_profile.read_text())
    old=ROOT/'build/preset-corpus/published31/projectM-TV-core-2.3.31.aar'
    assert profile['release']=='v2.3.32'
    assert args.aar.read_bytes()==old.read_bytes()
    assert profile['byte_equivalence']['equivalent_release']=='v2.3.31'
    assert profile['source_engine']==CORE_2331_ENGINE
    identity=preset_corpus.target_identity(args,args.binaries)
    assert identity['published_aar']==str(args.aar.resolve())
    assert identity['source_engine_archive_sha256']==preset_corpus.CORE_2331_SOURCE_ARCHIVE_SHA256


def test_explicit_historical31_publication_is_not_relabelled_latest32():
    args=preset_corpus.parse_args(['--aar',str(ROOT/'build/preset-corpus/published31/projectM-TV-core-2.3.31.aar'),
        '--engine-profile',str(ROOT/'tools/milk-analyzer/profiles/published-core-v2.3.31.json')])
    identity=preset_corpus.target_identity(args,args.binaries)
    assert json.loads(Path(identity['engine_profile']).read_text())['release']=='v2.3.31'


def test_historical_direct_config_keeps29_without_relabeling():
    engine, rng = corpus_worker.target_policies({})
    assert engine == CORE_2329_ENGINE and rng == CORE_2329_EQUATION_RNG_POLICY
    engine, rng = corpus_worker.target_policies({'source_engine': CORE_2331_ENGINE})
    assert engine == CORE_2331_ENGINE and rng == CORE_2331_EQUATION_RNG_POLICY
    with pytest.raises(ValueError, match='unsupported.*engine'):
        corpus_worker.target_policies({'source_engine': {'commit': 'unknown'}})


def test_controller_freezes_full_publication_separately_from_source_archive():
    args = preset_corpus.parse_args([])
    target = preset_corpus.target_identity(args, args.binaries)
    assert target['source_engine'] == CORE_2331_ENGINE
    assert target['published_aar_sha256'] == '13290b486d08569f229f1f684e57aba849a31a2506270a4d305777322d8d7377'
    assert target['engine_profile_sha256'] == file_hash(args.engine_profile)
    assert target['source_engine_archive_sha256'] == '997c082aabf9d0702c58da57efdd4c05e6faa99b9abd46ba1041d1fbb4b9cca8'
    migration = json.loads((ROOT / 'tools/milk-analyzer/fixtures/core2331-source-migration-2026-10-09.json').read_text())
    assert preset_corpus.CORE_2331_SOURCE_ARCHIVE_SHA256 == migration['source_adapter_archive_sha256']
    assert target['source_engine_archive_sha256'] != target['published_aar_sha256']
    assert target['source_engine_archive_sha256'] not in migration['published']['native_libraries'].values()


def test_controller_rejects_wellformed_unqualified_source_archive():
    args = preset_corpus.parse_args([])
    target = preset_corpus.target_identity(args, args.binaries)
    target['source_engine_archive_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='source.*archive'):
        preset_corpus.verify_target(target)


def test_target_probe_cannot_admit_self_reported_unqualified_archive(monkeypatch):
    import forecast
    monkeypatch.setattr(forecast, 'read_source', lambda *args, **kwargs:
        {'parser_inputs': {'engine': CORE_2331_ENGINE, 'engine_archive_sha256': '0' * 64}})
    args = preset_corpus.parse_args([])
    with pytest.raises(ValueError, match='source.*archive'):
        preset_corpus.target_identity(args, args.binaries)


def test_frozen_and_worker_admission_reject_unqualified_archive_before_parse(tmp_path, monkeypatch):
    args = preset_corpus.parse_args([])
    target = preset_corpus.target_identity(args, args.binaries)
    inputs = tmp_path / 'inputs'
    atomic_json(inputs / 'manifest.json', {'files': {}, 'textures': {}})
    preset = tmp_path / 'one.milk'; preset.write_text('[preset00]\n')
    config = {**target, 'source_engine_archive_sha256': '0' * 64,
        'model_modules': model_file_hashes(), 'binaries': str(args.binaries), 'binary_sha256': {},
        'validator': str(args.engine_profile), 'validator_sha256': file_hash(args.engine_profile),
        'inputs': str(inputs), 'prepared_inputs_sha256': file_hash(inputs / 'manifest.json'),
        'simulation': {'frames': 1, 'fps': 15, 'width': 32, 'height': 18}}
    with pytest.raises(ValueError, match='source.*archive'):
        preset_corpus.verify_frozen(config)
    parsed = []
    def unexpected_parse(*args, **kwargs):
        parsed.append(True)
        raise AssertionError('unqualified archive reached source parsing')
    monkeypatch.setattr(corpus_worker, 'read_source', unexpected_parse)
    result = corpus_worker.run({'configuration': config,
        'case': {'path': str(preset), 'sha256': file_hash(preset)}})
    assert result['stage'] == 'identity' and result['status'] == 'unsupported', result
    assert 'source' in result['error'] and 'archive' in result['error']
    assert result['feature_record'] is None and not parsed


def test_controller_rejects_wrong_aar_profile_or_source_adapter(tmp_path):
    args = preset_corpus.parse_args([])
    bad = tmp_path / 'wrong.aar'; bad.write_bytes(b'not published core')
    args.aar = bad
    with pytest.raises(ValueError, match='AAR'):
        preset_corpus.target_identity(args, args.binaries)
    args = preset_corpus.parse_args([])
    profile = json.loads(args.engine_profile.read_text())
    profile['source_engine'] = CORE_2329_ENGINE
    args.engine_profile = tmp_path / 'wrong-profile.json'; atomic_json(args.engine_profile, profile)
    with pytest.raises(ValueError, match='profile.*engine'):
        preset_corpus.target_identity(args, args.binaries)
    args = preset_corpus.parse_args([])
    with pytest.raises(ValueError, match='source.*engine'):
        preset_corpus.target_identity(args, ROOT / 'build/preset-corpus/source29/adapters')


def test_effect_metadata_cache_uses_actual_compatibility_and_retains_unknowns(tmp_path, monkeypatch):
    calls = []
    def analyze(source, **kwargs):
        calls.append(kwargs)
        return {'families': [], 'unknowns': [{'reason': 'unsupported typed form'}], 'appearance_prediction_complete': False}
    monkeypatch.setattr(corpus_worker, 'analyze_families', analyze)
    source = {'values': {}, 'sections': {}, 'parser_inputs': {'engine': CORE_2331_ENGINE}}
    compatibility = {'warp': {'offline_accepted': False}}
    one, hit = corpus_worker.effect_metadata(source, compatibility, cache=tmp_path)
    assert not hit and one['unknowns']
    two, hit = corpus_worker.effect_metadata(source, compatibility, cache=tmp_path)
    assert hit and two == one and len(calls) == 1
    corpus_worker.effect_metadata(source, {'warp': {'offline_accepted': True}}, cache=tmp_path)
    assert len(calls) == 2 and calls[0] == {'profile': 'gles300', 'compatibility': compatibility}


@pytest.fixture
def bounded_job(tmp_path):
    """Prepare one frame, empty materials and one synthetic preset; no corpus."""
    from corpus_inputs import prepare_inputs
    args = preset_corpus.parse_args([])
    validator = shutil.which('glslangValidator')
    assert validator, 'prepared shader validator required'
    inputs = tmp_path / 'inputs'; textures = tmp_path / 'textures'; textures.mkdir()
    preset = tmp_path / 'one.milk'
    preset.write_text('[preset00]\nPSVERSION_WARP=0\nPSVERSION_COMP=0\nfDecay=1\nfWaveAlpha=0\n')
    target = preset_corpus.target_identity(args, args.binaries)
    prepare_inputs(inputs, binaries=args.binaries, textures=textures, frames=1, fps=15, seed=12345)
    config = {**target, 'model_modules': model_file_hashes(), 'binaries': str(args.binaries),
        'binary_sha256': {name: file_hash(args.binaries / name) for name in preset_corpus.ADAPTERS},
        'validator': validator, 'validator_sha256': file_hash(validator), 'inputs': str(inputs),
        'prepared_inputs_sha256': file_hash(inputs / 'manifest.json'), 'seed': 12345,
        'simulation': {'frames': 1, 'fps': 15, 'width': 32, 'height': 18}, 'equation_timeout': 30,
        'effect_cache': str(tmp_path / 'effect-cache')}
    return {'configuration': config, 'case': {'path': str(preset), 'sha256': file_hash(preset)}}


def test_actual_small_worker_keeps47_fields_and_separate_static_metadata(bounded_job):
    result = corpus_worker.run(bounded_job)
    assert result['status'] == 'computed', result
    assert len(result['feature_record']['features']) == 47
    assert result['effect_analysis']['uses_shader_execution'] is False
    assert result['effect_analysis']['uses_equation_execution'] is False
    assert not result['effect_analysis_cache_hit']
    cached = corpus_worker.run(bounded_job)
    assert cached['status'] == 'computed' and cached['effect_analysis_cache_hit']
    assert cached['effect_analysis'] == result['effect_analysis']
    provenance = result['feature_record']['context']['provenance']
    assert provenance['engine'] == CORE_2331_ENGINE
    assert provenance['motion_uv_backend'] == 'conditional'
    assert result['feature_record']['context']['domain']['motion_uv_storage_profile'] == 'portable-half-nearest-v1'


@pytest.mark.parametrize('changed', ['published_aar_sha256', 'engine_profile_sha256', 'source_engine', 'source_engine_archive_sha256'])
def test_worker_rejects_publication_profile_source_drift(bounded_job, changed):
    config = bounded_job['configuration']
    config[changed] = CORE_2329_ENGINE if changed == 'source_engine' else 'wrong'
    result = corpus_worker.run(bounded_job)
    assert result['status'] != 'computed' and result['stage'] == 'identity', result


def test_static_metadata_survives_later_resource_failure(bounded_job, monkeypatch):
    def missing(*args, **kwargs): raise ValueError('missing texture witness')
    monkeypatch.setattr(corpus_worker, 'material_inputs', missing)
    result = corpus_worker.run(bounded_job)
    assert result['status'] == 'unsupported' and result['stage'] == 'resources'
    assert result['effect_analysis']['families'] == []
    assert result['feature_record'] is None


def test_analysis_model_bug_is_explicit_and_does_not_fake_complete_metadata(bounded_job, monkeypatch):
    def broken(*args, **kwargs): raise RuntimeError('model bug witness')
    monkeypatch.setattr(corpus_worker, 'analyze_families', broken)
    result = corpus_worker.run(bounded_job)
    assert result['status'] == 'computed', result
    assert result['effect_analysis']['status'] == 'error'
    assert result['effect_analysis']['appearance_prediction_complete'] is False
    assert result['effect_analysis']['error_type'] == 'RuntimeError'


def test_typed_unknown_effect_metadata_does_not_abort_numeric_report(bounded_job, monkeypatch):
    monkeypatch.setattr(corpus_worker, 'analyze_families', lambda *args, **kwargs:
        {'families': [], 'unknowns': [{'reason': 'unsupported typed construction'}],
         'appearance_prediction_complete': False})
    result = corpus_worker.run(bounded_job)
    assert result['status'] == 'computed', result
    assert len(result['feature_record']['features']) == 47
    assert result['effect_analysis']['unknowns'][0]['reason'] == 'unsupported typed construction'


def test_actual_source_cannot_be_relabelled_by_configuration(bounded_job, monkeypatch):
    actual = corpus_worker.read_source
    def historical(*args, **kwargs):
        source = actual(*args, **kwargs)
        source['parser_inputs']['engine'] = CORE_2329_ENGINE
        return source
    monkeypatch.setattr(corpus_worker, 'read_source', historical)
    result = corpus_worker.run(bounded_job)
    assert result['stage'] == 'identity' and result['status'] != 'computed'


def test_cached_metadata_corruption_fails_explicitly(tmp_path, monkeypatch):
    monkeypatch.setattr(corpus_worker, 'analyze_families', lambda *args, **kwargs:
        {'families': [], 'unknowns': []})
    source = {'values': {}, 'sections': {}}
    corpus_worker.effect_metadata(source, {}, cache=tmp_path)
    path = next(tmp_path.glob('*.json'))
    cached = json.loads(path.read_text()); cached['analysis']['families'] = ['tampered']
    atomic_json(path, cached)
    with pytest.raises(ValueError, match='cache identity'):
        corpus_worker.effect_metadata(source, {}, cache=tmp_path)


def test_explicit29_diagnostic_selects_old_adapters_without_publication_claim():
    args = preset_corpus.parse_args(['--target', 'core2329-diagnostic'])
    assert args.binaries == ROOT / 'build/preset-corpus/source29/adapters'
    assert args.aar is None and args.engine_profile is None
    identity = preset_corpus.target_identity(args, args.binaries)
    assert identity['source_engine'] == CORE_2329_ENGINE
    assert 'published_aar_sha256' not in identity


def test_malformed_analysis_output_is_explicit_metadata_error(tmp_path, monkeypatch):
    monkeypatch.setattr(corpus_worker, 'analyze_families', lambda *args, **kwargs: None)
    metadata, hit = corpus_worker.effect_metadata({'values': {}, 'sections': {}}, {}, cache=tmp_path)
    assert metadata['status'] == 'error' and metadata['error_type'] == 'TypeError'
    assert not hit and not list(tmp_path.glob('*.json'))


def test_model_change_during_analysis_cannot_populate_cache(tmp_path, monkeypatch):
    models = {'model.py': 'before'}
    monkeypatch.setattr(corpus_worker, '_MODEL_IMPORT_HASHES', dict(models))
    monkeypatch.setattr(corpus_worker, '_FAMILY_IMPORT_HASHES', dict(models))
    monkeypatch.setattr(corpus_worker, 'model_file_hashes', lambda: dict(models))
    def changing(*args, **kwargs):
        models['model.py'] = 'after'
        return {'families': [], 'unknowns': []}
    monkeypatch.setattr(corpus_worker, 'analyze_families', changing)
    with pytest.raises(ValueError, match='model changed'):
        corpus_worker.effect_metadata({'values': {}, 'sections': {}}, {}, cache=tmp_path)
    assert not list(tmp_path.glob('*.json'))


def test_parser_elapsed_time_does_not_change_static_metadata_cache(tmp_path, monkeypatch):
    calls = []
    def analyze(source, **kwargs):
        calls.append(source)
        return {'families': [], 'unknowns': []}
    monkeypatch.setattr(corpus_worker, 'analyze_families', analyze)
    source = {'values': {}, 'sections': {}, 'elapsed_ms': 1}
    corpus_worker.effect_metadata(source, {}, cache=tmp_path)
    _, hit = corpus_worker.effect_metadata({**source, 'elapsed_ms': 100}, {}, cache=tmp_path)
    assert hit and len(calls) == 1


def test_imported_model_baselines_cannot_be_restamped_as_new_disk_code(monkeypatch):
    monkeypatch.setattr(corpus_worker, 'model_file_hashes', lambda: {'fresh-on-disk.py': 'new'})
    with pytest.raises(ValueError, match='changed since import'):
        corpus_worker.effect_metadata({'values': {}, 'sections': {}}, {})


def test_complete_actual_compatibility_remains_bound_even_when_diagnostics_change(tmp_path, monkeypatch):
    calls = []
    def analyze(source, **kwargs):
        calls.append(kwargs['compatibility'])
        return {'families': [], 'unknowns': []}
    monkeypatch.setattr(corpus_worker, 'analyze_families', analyze)
    source = {'values': {}, 'sections': {}}
    old = {'warp': {'offline_accepted': False, 'request': {'code': 'bad shader', 'stage': 'warp', 'profile': 'gles300'},
        'translation': {'status': 'translated', 'glsl': 'bad'}, 'compiler_diagnostics': '/tmp/first/shader.frag ERROR'}}
    corpus_worker.effect_metadata(source, old, cache=tmp_path)
    new = {'warp': {**old['warp'], 'compiler_diagnostics': '/tmp/second/shader.frag ERROR'}}
    _, hit = corpus_worker.effect_metadata(source, new, cache=tmp_path)
    assert not hit and len(calls) == 2
    # The complete actual binding reaches analysis on the first computation.
    assert calls[0] == old
    _, hit = corpus_worker.effect_metadata(source, {'warp': {**new['warp'], 'offline_accepted': True}}, cache=tmp_path)
    assert not hit and len(calls) == 3
