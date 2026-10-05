import importlib

import numpy as np
import pytest
from test_motion_vectors import state
from test_pipeline_fields import trees


def pipeline(warp=None, comp=None):
    return importlib.import_module('pipeline_fields').SourcePipeline(
        warp, comp, initial_feedback=np.zeros((32, 32, 4), dtype=np.float32),
        warp_reads_blur=False, blur_levels=0, quantize=False)


def step(p, values, uv=None):
    return p.step(warp_uv=p.original_uv if uv is None else uv,
                  uniforms={}, frame_wrap=1, decay=1, motion_state=values)


def test_first_frame_only_writes_map_second_frame_draws_before_warp():
    p = pipeline()
    first = step(p, state())
    assert np.count_nonzero(first.feedback[..., 0]) == 0
    assert first.history['motion_vector_source_frame'] is None
    second = step(p, state())
    assert np.count_nonzero(second.feedback[..., 0]) > 0
    assert second.history['motion_vector_source_frame'] == 0


def test_inactive_frames_preserve_the_last_written_map_for_reactivation():
    p = pipeline()
    step(p, state())
    original = p.motion_uv.copy()
    hidden = state()
    hidden['mv_a'] = 0
    step(p, hidden, p.original_uv + [.125, 0])
    np.testing.assert_array_equal(p.motion_uv, original)
    assert p.motion_uv_frame == 0
    result = step(p, state(), p.original_uv + [.25, 0])
    assert result.history['motion_vector_source_frame'] == 0
    assert p.motion_uv_frame == 2


def test_first_activation_after_unwritten_frames_requires_known_starting_map():
    p = pipeline()
    step(p, {'mv_a': 0})
    with pytest.raises(ValueError, match='previous motion UV'):
        step(p, state())
    assert p.frame == 1
    assert p.motion_uv is None


def test_composite_failure_does_not_commit_the_motion_map():
    warp, comp = trees('ret=.5;', 'ret=tex2D(sampler_missing_resource,uv).xyz;')
    p = pipeline(warp, comp)
    with pytest.raises(ValueError, match='texture'):
        step(p, state())
    assert p.frame == 0
    assert p.motion_uv is None


def test_custom_warp_motion_output_is_captured_before_ordinary_uv_rewrites():
    warp, comp = trees('uv += float2(.125,0);ret=.5;', 'ret=.5;')
    p = pipeline(warp, comp)
    step(p, state())
    np.testing.assert_array_equal(p.motion_uv, p.original_uv.astype(np.float16).astype(np.float32))
    # Preset code can explicitly override the generated motion output.
    warp, comp = trees('_mv_tex_coords.xy=float2(.25,.75);ret=.5;', 'ret=.5;')
    p = pipeline(warp, comp)
    step(p, state())
    np.testing.assert_array_equal(p.motion_uv, np.broadcast_to([.25, .75], (32, 32, 2)))


def test_scene_draw_requires_explicit_prewarp_motion_integration():
    module = importlib.import_module('scene_draw')
    frame = {'main': state(), 'shapes': []}
    target = np.zeros((32, 32, 4))
    with pytest.raises(ValueError, match='before warp'):
        module.draw_source_scene(target, {'values': {}}, frame, None, [])
    result = module.draw_source_scene(target, {'values': {}}, frame, None, [], motion_vectors_prewarped=True)
    np.testing.assert_array_equal(result, target)


def test_unwritten_entry_output_components_are_not_external_inputs():
    from shader_fields import ShaderFields
    warp, _ = trees('ret=float3(_mv_tex_coords.z);', 'ret=.5;')
    model = ShaderFields(stage='warp', frame=0, warp_reads_blur=False)
    model.lower(warp)
    assert not model.complete
    assert 'uninitialized shader value reaches a read' in model.unknown
