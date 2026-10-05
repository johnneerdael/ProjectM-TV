import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[2]
BINARY = ROOT / 'build/milk-analyzer/native/milk-shader-random'


def run(events, seed=12345, *, valid=True, rand_policy='host-c-rand-v1'):
    assert BINARY.is_file(), 'source shader-random CPU bridge is not built'
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'request.json'
        path.write_text(json.dumps(dict(seed=seed, events=events,rand_policy=rand_policy)))
        result = subprocess.run([str(BINARY), str(path)], capture_output=True, text=True, timeout=10)
    if not valid:
        assert result.returncode != 0
        return result.stderr
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def create(name):
    return dict(kind='construct', id=name)


def load(name, time=0):
    return dict(kind='load', id=name, time=time)


def test_shared_rng_consumption_matches_independent_host_libc_sequence():
    native = run([create('warp'), create('comp'), load('warp'), load('comp')], seed=23456)
    libc = ctypes.CDLL(None)
    libc.srand.argtypes = [ctypes.c_uint]
    libc.rand.restype = ctypes.c_int
    libc.srand(23456)
    draws = [libc.rand() for _ in range(424)]
    def values(start):
        return [float(np.float32(v % 7381) / np.float32(7380)) for v in draws[start:start+4]]
    warp, comp = native['loads']
    assert native['draws_consumed'] == 424  # 2*184 constructor + 2*28 load.
    assert warp['uniforms']['rand_preset'] == values(0)
    assert comp['uniforms']['rand_preset'] == values(184)
    assert warp['uniforms']['rand_frame'] == values(368)
    assert comp['uniforms']['rand_frame'] == values(396)


def test_declared_portable_random_inputs_match_independent_mt_sequence():
    result=run([create('warp'),load('warp')],rand_policy='declared-mt19937-u31-v1')
    generator=np.random.RandomState(12345)
    values=generator.randint(0,2**32,size=212,dtype=np.uint32)&np.uint32(0x7fffffff)
    expected=lambda start:(values[start:start+4]%7381).astype(np.float32)/np.float32(7380)
    np.testing.assert_array_equal(result['loads'][0]['uniforms']['rand_preset'],expected(0))
    np.testing.assert_array_equal(result['loads'][0]['uniforms']['rand_frame'],expected(184))
    assert result['profile']['rng']=='declared-mt19937-u31-v1'


def test_random_values_have_correct_lifetime_and_repeatability():
    events = [create('warp'), load('warp'), load('warp', 12)]
    first, repeated, changed = run(events), run(events), run(events, seed=54321)
    assert first == repeated
    a, b = first['loads']
    assert a['uniforms']['rand_preset'] == b['uniforms']['rand_preset']
    assert a['uniforms']['rand_frame'] != b['uniforms']['rand_frame']
    assert a['uniforms']['rot_s1'] == b['uniforms']['rot_s1']  # First rotation speed is exactly zero.
    assert a['uniforms']['rot_rand1'] != b['uniforms']['rot_rand1']
    assert first['loads'] != changed['loads']


def test_explicit_reseed_resets_draws_but_preserves_existing_shader_state():
    events=[create('warp'),load('warp'),dict(kind='reseed',id='shared-stream',seed=54321),load('warp',12)]
    result=run(events)
    fresh=run([create('new'),load('new')],seed=54321)
    before,after=result['loads']
    assert after['uniforms']['rand_preset']==before['uniforms']['rand_preset']
    assert after['uniforms']['rot_s1']==before['uniforms']['rot_s1']
    unreseeded=run([create('warp'),load('warp'),load('warp',12)])['loads'][1]['uniforms']
    for name,value in after['uniforms'].items():
        if name!='rand_frame' and not name.startswith('rot_rand'):
            assert value==unreseeded[name]
    # Reseeding does not reconstruct an existing shader or consume its 184 draws.
    libc=ctypes.CDLL(None);libc.srand(54321);libc.rand.restype=ctypes.c_int
    expected=[float(np.float32(libc.rand()%7381)/np.float32(7380)) for _ in range(4)]
    assert after['uniforms']['rand_frame']==expected
    assert after['uniforms']['rand_frame']!=fresh['loads'][0]['uniforms']['rand_frame']
    assert result['draws_consumed']==240
    assert result['events'][2]['draws_before']==result['events'][2]['draws_after']==212
    assert result['events'][2]['seed']==54321


def test_python_reseed_validation_preserves_seed_identity():
    from shader_random import execute_ledger
    result=execute_ledger(BINARY,seed=12345,events=[create('warp'),
        dict(kind='reseed',id='shared-stream',seed=0),load('warp')])
    assert result['draws_consumed']==212
    for seed in [-1,2**32,True]:
        with pytest.raises(ValueError,match='seed'):
            execute_ledger(BINARY,seed=12345,events=[dict(kind='reseed',id='stream',seed=seed)])
        assert 'seed' in run([dict(kind='reseed',id='stream',seed=seed)],valid=False)


def test_matrix_upload_discards_translation_and_keeps_rotations_orthonormal():
    native = run([create('warp'), load('warp', 321.25)])
    matrices = {key: np.asarray(value) for key, value in native['loads'][0]['uniforms'].items()
                if key.startswith('rot_')}
    assert len(matrices) == 24
    for value in matrices.values():
        assert value.shape == (4, 3)
        np.testing.assert_array_equal(value[3], [0, 0, 0])
        np.testing.assert_allclose(value[:3].T @ value[:3], np.eye(3), atol=4e-7, rtol=0)
        np.testing.assert_allclose(np.linalg.det(value[:3]), 1, atol=4e-7, rtol=0)


def test_omitting_an_unused_stage_changes_the_next_stage_random_values():
    complete = run([create('warp'), create('unused'), load('unused'), load('warp')])
    shortened = run([create('warp'), load('warp')])
    assert complete['loads'][-1]['uniforms']['rand_preset'] == shortened['loads'][0]['uniforms']['rand_preset']
    assert complete['loads'][-1]['uniforms']['rand_frame'] != shortened['loads'][0]['uniforms']['rand_frame']


def test_invalid_lifecycle_or_seed_does_not_return_plausible_uniforms():
    assert 'unknown' in run([load('missing')], valid=False)
    assert 'duplicate' in run([create('a'), create('a')], valid=False)
    assert 'seed' in run([], seed=-1, valid=False)
    assert 'seed' in run([], seed=True, valid=False)


def test_bridge_records_source_identity_and_declares_host_profile_limitations():
    native = run([create('warp'), load('warp')])
    source = ROOT / ('build/preset-lab-production/engines/'
                    '96df3b3b13f0b358a26aeeafb4127dc8a62e51b0be76e56c33eeaea3faea705a/'
                        'src/libprojectM/MilkdropPreset/MilkdropShader.cpp')
    if os.environ.get('MILK_NATIVE_RANDOM_ENGINE_SOURCE'):
        source=Path(os.environ['MILK_NATIVE_RANDOM_ENGINE_SOURCE'])/'src/libprojectM/MilkdropPreset/MilkdropShader.cpp'
    assert native['source_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert native['rendered_frames_consumed'] is False
    assert native['target_driver_verified'] is False
    assert native['profile']['rng'] == 'host C rand'
    assert native['profile']['compiler']


def test_pipeline_uses_separate_stage_random_inputs():
    from test_pipeline_fields import trees
    from pipeline_fields import SourcePipeline
    warp, comp = trees('ret=rand_frame.xyz;', 'ret=GetPixel(uv)*rand_frame.xyz;')
    p = SourcePipeline(warp, comp, initial_feedback=np.zeros((8, 8, 4)),
                       warp_reads_blur=False, blur_levels=0, quantize=False)
    result = p.step(warp_uv=p.original_uv, uniforms={}, frame_wrap=1,
                    stage_uniforms={'warp': {'rand_frame': [.8, .6, .4, 1]},
                                    'composite': {'rand_frame': [.5, .25, .75, 1]}})
    np.testing.assert_allclose(result.feedback[...,:3], np.broadcast_to([.8, .6, .4], (8, 8, 3)), atol=1e-7)
    np.testing.assert_allclose(result.display[...,:3], np.broadcast_to([.4, .15, .3], (8, 8, 3)), atol=1e-7)


def test_random_input_binding_requires_matching_event_shader_time_and_profile():
    from shader_random import execute_ledger, bind_random_uniforms
    result = execute_ledger(BINARY, seed=12345, events=[create('warp'), load('warp', 12.25)])
    uniforms = bind_random_uniforms(result, event_index=1, shader_id='warp', time=12.25,
                                   profile=result['profile'])
    assert uniforms['rand_preset'] == result['loads'][0]['uniforms']['rand_preset']
    for changes in [dict(event_index=0), dict(shader_id='comp'), dict(time=12.5),
                    dict(profile={'rng': 'different'})]:
        args = dict(event_index=1, shader_id='warp', time=12.25, profile=result['profile'])
        args.update(changes)
        with pytest.raises(ValueError):
            bind_random_uniforms(result, **args)
    assert result['binary_sha256'] == hashlib.sha256(BINARY.read_bytes()).hexdigest()


def test_partial_or_nonfinite_uniform_bank_is_rejected():
    from shader_random import bind_random_uniforms
    result = run([create('warp'), load('warp')])
    args = dict(event_index=1, shader_id='warp', time=0, profile=result['profile'])
    result['loads'][0]['uniforms']['rand_frame'][0] = float('nan')
    with pytest.raises(ValueError, match='finite'):
        bind_random_uniforms(result, **args)
    result['loads'][0]['uniforms']['rand_frame'][0] = 0
    del result['loads'][0]['uniforms']['rot_s1']
    with pytest.raises(ValueError, match='incomplete'):
        bind_random_uniforms(result, **args)


def test_shader_matrix_field_uses_native_four_by_three_upload_layout():
    from shader_random import bind_random_uniforms
    from test_pipeline_fields import trees
    from shader_fields import ShaderFields
    from field_math import evaluate
    result = run([create('warp'), load('warp', 3.75)])
    bank = bind_random_uniforms(result, event_index=1, shader_id='warp', time=3.75, profile=result['profile'])
    _, comp = trees('ret=.5;', 'ret=mul(float4(.2,.3,.4,1),rot_s1);')
    model = ShaderFields(stage='composite', frame=0, warp_reads_blur=False)
    expression = model.lower(comp)
    assert model.complete, model.unknown
    np.testing.assert_allclose(evaluate(expression, inputs=bank),
                               np.array([.2,.3,.4,1], dtype=np.float32) @ np.array(bank['rot_s1'], dtype=np.float32),
                               atol=1e-7, rtol=0)


def test_matrix_axes_composition_and_time_dependence_match_independent_formula():
    seed, time = 34567, 7.25
    native = run([create('warp'), load('warp', time)], seed=seed)
    libc = ctypes.CDLL(None)
    libc.srand.argtypes = [ctypes.c_uint]
    libc.rand.restype = ctypes.c_int
    libc.powf.argtypes = [ctypes.c_float, ctypes.c_float]
    libc.powf.restype = ctypes.c_float
    libc.srand(seed)
    values = [np.float32(libc.rand() % 7381) / np.float32(7380) for _ in range(212)]
    def rotation(angles):
        x, y, z = [float(angle) for angle in angles]
        cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
        rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
        ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
        rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
        return ry @ rz @ rx
    bank = native['loads'][0]['uniforms']
    for index in range(24):
        if index < 20:
            offset = 4 + index * 9
            centers = np.array(values[offset+3:offset+6]) * np.float32(6.28)
            multiplier = np.float32(.9) * np.float32(libc.powf(index / 8, np.float32(3.2)))
            speed = (np.array(values[offset+6:offset+9]) * np.float32(2) - np.float32(1)) * multiplier
            angles = centers + speed * np.float32(time)
            group = ('s','d','f','vf','uf')[index // 4]
            name = f'rot_{group}{index % 4 + 1}'
        else:
            offset = 188 + (index - 20) * 6
            angles = np.array(values[offset:offset+3]) * np.float32(6.28)
            name = f'rot_rand{index - 19}'
        np.testing.assert_allclose(np.array(bank[name])[:3], rotation(angles), atol=1e-5, rtol=0,
                                   err_msg=name)


def test_source_random_matrix_drives_the_composite_grid_with_native_uvs():
    from shader_random import bind_random_uniforms
    from test_pipeline_fields import trees
    from pipeline_fields import SourcePipeline
    from composite_mesh import composite_fields
    native = run([create('comp'), load('comp', 5)])
    bank = bind_random_uniforms(native, event_index=1, shader_id='comp', time=5, profile=native['profile'])
    _, comp = trees('ret=0;', 'ret=abs(mul(float4(uv,0,1),rot_s1));')
    p = SourcePipeline(None, comp, initial_feedback=np.zeros((8, 16, 4)),
                       warp_reads_blur=False, blur_levels=0, quantize=False)
    result = p.step(warp_uv=p.original_uv, uniforms={}, frame_wrap=1, decay=1,
                    stage_uniforms={'composite': bank})
    uv = composite_fields(16, 8)['uv']
    points = np.concatenate((uv, np.zeros((8, 16, 1)), np.ones((8, 16, 1))), axis=-1)
    expected = np.clip(np.abs(points @ np.asarray(bank['rot_s1'])), 0, 1)
    np.testing.assert_allclose(result.display[...,:3], expected, atol=2e-7, rtol=0)
