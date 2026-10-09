"""Release31 legacy-only warp contracts, with historical/custom controls."""
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest

from engine_profiles import CORE_2331_ENGINE, CORE_2331_LEGACY_WARP
from scene_equations import execute_scene
from spatial import mesh_inputs, interpolate_mesh, warp_vertex_uv

ROOT = Path(__file__).resolve().parents[2]
BINARIES = Path(os.environ.get('MILK_TEST_2331_BINARIES', ROOT/'build/preset-corpus/source31/adapters'))


def test_legacy_diagonal_has_distinct_interpolation_and_keeps_custom_default():
    values = np.array([[0, 0], [0, 1]], np.float32)
    query = [[.75, .25], [.25, .75]]
    np.testing.assert_array_equal(interpolate_mesh(values, query, diagonal='ad'), [.25, .25])
    np.testing.assert_array_equal(interpolate_mesh(values, query), [0, 0])
    with pytest.raises(ValueError, match='diagonal'):
        interpolate_mesh(values, query, diagonal='invented')


def test_legacy_left_axis_retains_cached_signed_angle_only_on_axis():
    old = mesh_inputs(8, 8, aspect_x=1, aspect_y=.5)
    legacy = mesh_inputs(8, 8, aspect_x=1, aspect_y=.5, legacy_angle_seam=True)
    np.testing.assert_array_equal(legacy['equation_ang'][4, :4], legacy['angle'][4, :4])
    assert old['equation_ang'][4, 0] < 0 < legacy['equation_ang'][4, 0]
    np.testing.assert_array_equal(legacy['equation_ang'][:4], old['equation_ang'][:4])
    np.testing.assert_array_equal(legacy['equation_ang'][5:], old['equation_ang'][5:])
    np.testing.assert_array_equal(legacy['position'], old['position'])


def test_legacy_oscillator_reverses_only_deformation_y():
    p = np.array([[.25, .5], [-.6, -.25]], np.float32)
    args = dict(time=.7, warp=.8, warp_scale=1.2, warp_anim_speed=.9)
    old = warp_vertex_uv(p, **args)
    reflected = p*np.array([1, -1], np.float32)
    # Identity UV is restored from original coordinates; only oscillators use -Y.
    expected = warp_vertex_uv(reflected, **args) + np.stack((np.zeros(2), p[:, 1]), axis=-1)
    new = warp_vertex_uv(p, legacy_warp_policy=CORE_2331_LEGACY_WARP, **args)
    np.testing.assert_allclose(new, expected, atol=1e-7)
    assert not np.allclose(new, old)
    np.testing.assert_array_equal(warp_vertex_uv(p, warp=0),
        warp_vertex_uv(p, warp=0, legacy_warp_policy=CORE_2331_LEGACY_WARP))


def read_source(tmp_path, body):
    reader = BINARIES/'milk-native-reader'
    if not reader.is_file():
        pytest.skip('prepared source31 reader required')
    path = tmp_path/'case.milk'
    path.write_text('[preset00]\n'+body)
    result = subprocess.run([str(reader), str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    source = json.loads(result.stdout)
    assert source['parser_inputs']['engine'] == CORE_2331_ENGINE
    source['parser_inputs']['setting_lookup_policy']='native-case-insensitive-v1'
    return source, reader


def inputs():
    return [{'time':1, 'frame':1, 'fps':15, 'progress':0,
             'bass':1, 'mid':1, 'treb':1, 'bass_att':1, 'mid_att':1, 'treb_att':1}]


def test_legacy_traversal_executes_reverse_rows_but_stores_at_original_vertex(tmp_path):
    source, reader = read_source(tmp_path, 'per_pixel_1=q1=q1+1;zoom=q1;dx=ang;dy=aspecty;\n')
    legacy = execute_scene(source, inputs(), reader=reader, width=16, height=8,
        mesh_x=8, mesh_y=8, legacy_warp_policy=CORE_2331_LEGACY_WARP)
    custom = execute_scene(source, inputs(), reader=reader, width=16, height=8,
        mesh_x=8, mesh_y=8)
    old_rows, new_rows = custom['frames'][0]['mesh'], legacy['frames'][0]['mesh']
    assert [row['zoom'] for row in old_rows] == list(range(1,82))
    assert [row['zoom'] for row in new_rows[:9]] == list(range(73,82))
    assert [row['zoom'] for row in new_rows[-9:]] == list(range(1,10))
    assert new_rows[36]['dx'] > 0 > old_rows[36]['dx']
    # The new inverse-aspect context applies to custom as well as legacy.
    assert all(row['dy'] == 2 for row in new_rows+old_rows)


def test_wave_point_builtins_are_loaded_fresh_before_point_code(tmp_path):
    source, reader = read_source(tmp_path,
        'wavecode_0_enabled=1\nwavecode_0_samples=1\nwavecode_0_bUseDots=1\n'
        'per_frame_1=time=40;\nwave_0_per_frame1=time=50;q1=8;\n'
        'wave_0_per_point1=x=time;y=q1;\n')
    frames = inputs()
    for key in ('waveform_left', 'waveform_right', 'spectrum_left', 'spectrum_right'):
        frames[0][key] = [0]*(480 if key.startswith('waveform') else 512)
    scene = execute_scene(source, frames, reader=reader, width=16, height=8, mesh_x=8, mesh_y=8)
    point = scene['frames'][0]['waves'][0]['points'][0]
    assert point['x'] == 1
    assert point['y'] == 8


def test_legacy_policy_rejects_unqualified_engine(tmp_path):
    source, reader = read_source(tmp_path, 'per_pixel_1=zoom=1;\n')
    source['parser_inputs']['engine'] = {}
    with pytest.raises(ValueError, match='legacy warp.*identity'):
        execute_scene(source, inputs(), reader=reader, mesh_x=8, mesh_y=8,
                      legacy_warp_policy=CORE_2331_LEGACY_WARP)


def test_scene_rasterization_inherits_resolved_legacy_policy(tmp_path):
    from scene_warp import warp_fields
    source, reader = read_source(tmp_path, 'warp=.8\nper_pixel_1=dx=x*y*.2;\n')
    scene=execute_scene(source, inputs(), reader=reader, width=16, height=8,
                        mesh_x=8, mesh_y=8,legacy_warp_policy=CORE_2331_LEGACY_WARP)
    result=warp_fields(source,scene,0,query_uv=[[.18,.31],[.63,.78]])
    assert result['legacy_warp_policy']==CORE_2331_LEGACY_WARP
    assert result['mesh_diagonal']=='ad'
    expected=interpolate_mesh(result['vertex_uv'],[[.18,.31],[.63,.78]],diagonal='ad')
    np.testing.assert_array_equal(result['uv'],expected)
    source['parser_inputs']['engine']={}
    with pytest.raises(ValueError,match='legacy warp.*identity'):
        warp_fields(source,scene,0)
