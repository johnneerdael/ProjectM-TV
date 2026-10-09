"""Release31 source motion recurrence and conditional packed-half contracts."""
import numpy as np
import pytest

from engine_profiles import CORE_2329_ENGINE, CORE_2331_ENGINE, CORE_2331_MOTION, CORE_2331_DISPLAY
from pipeline_fields import SourcePipeline
from test_motion_vectors import state
from test_pipeline_fields import trees


OLD_MOTION = 'legacy-visible-motion-v1'


def pipeline(warp=None, comp=None, size=16, **kwargs):
    return SourcePipeline(warp, comp, initial_feedback=np.zeros((size, size, 4), np.float32),
        warp_reads_blur=False, blur_levels=0, quantize=False,
        motion_map_policy=CORE_2331_MOTION, source_engine=CORE_2331_ENGINE, **kwargs)


def step(p, visible=False, uv=None, **kwargs):
    return p.step(warp_uv=p.original_uv if uv is None else uv, uniforms={}, frame_wrap=1,
        decay=1, motion_state=state() if visible else {'mv_a': 0}, **kwargs)


def test_exact31_source_defaults_to_continuous_with_explicit_old_diagnostic():
    source = {'values': {}, 'sections': {}, 'parser_inputs': {'engine': CORE_2331_ENGINE}}
    args = dict(profile='gles300', compatibility={}, initial_feedback=np.zeros((16, 16, 4)),
                warp_reads_blur=False, blur_levels=0)
    current = SourcePipeline.from_source(source, **args)
    assert current.motion_map_policy == CORE_2331_MOTION
    old = SourcePipeline.from_source(source, **args, motion_map_policy=OLD_MOTION)
    assert old.motion_map_policy == OLD_MOTION
    source['parser_inputs']['engine'] = CORE_2329_ENGINE
    assert SourcePipeline.from_source(source, **args).motion_map_policy == OLD_MOTION
    with pytest.raises(ValueError, match='engine identity'):
        SourcePipeline.from_source(source, **args, motion_map_policy=CORE_2331_MOTION)


def test_direct_constructor_requires_exact_engine_for_new_policy():
    args = dict(initial_feedback=np.zeros((16, 16, 4)), warp_reads_blur=False, blur_levels=0)
    assert SourcePipeline(None, None, **args).motion_map_policy == OLD_MOTION
    for engine in (None, CORE_2329_ENGINE, {**CORE_2331_ENGINE, 'patches_sha256': 'wrong'}):
        with pytest.raises(ValueError, match='engine identity'):
            SourcePipeline(None, None, **args, motion_map_policy=CORE_2331_MOTION,
                           source_engine=engine)
    assert pipeline(legacy_control_policy=CORE_2331_DISPLAY).legacy_control_policy == CORE_2331_DISPLAY


@pytest.mark.parametrize('hidden', [{'mv_a': 0}, {'mv_a': 1, 'mv_x': 0}, None])
def test_hidden_frames_publish_and_reactivation_consumes_immediate_previous(hidden):
    p = pipeline()
    step(p, True)
    for offset in (.125, .25):
        p.step(warp_uv=p.original_uv + [offset, 0], uniforms={}, frame_wrap=1, decay=1,
               motion_state=hidden)
    np.testing.assert_array_equal(p.motion_uv,
        (p.original_uv + [.25, 0]).astype(np.float16).astype(np.float32))
    assert p.motion_uv_frame == 2
    assert step(p, True).history['motion_vector_source_frame'] == 2


def test_initially_hidden_frame_writes_known_map_without_drawing():
    p = pipeline()
    first = step(p)
    assert np.count_nonzero(first.feedback[..., :3]) == 0
    assert p.motion_uv_frame == 0
    assert step(p, True).history['motion_vector_source_frame'] == 0


def test_custom_final_motion_write_runs_hidden_and_tracks_input_dependencies():
    warp, comp = trees('uv += .125; _mv_tex_coords.xy=uv; ret=.5;', 'ret=.5;')
    p = pipeline(warp, comp)
    assert p.requires_warp_uv(frame_wrap=1, motion_state={'mv_a': 0})
    step(p)
    np.testing.assert_array_equal(p.motion_uv,
        (p.original_uv + .125).astype(np.float16).astype(np.float32))
    warp, comp = trees('_mv_tex_coords.xy=float2(-.25,1.75);ret=.5;', 'ret=.5;')
    p = pipeline(warp, comp)
    assert not p.requires_warp_uv(frame_wrap=1, motion_state=state())
    step(p)
    np.testing.assert_array_equal(p.motion_uv, np.broadcast_to([-.25, 1.75], (16, 16, 2)))


def test_default_custom_motion_output_keeps_original_uv_before_authored_uv_rewrite():
    warp, comp = trees('uv += .125;ret=.5;', 'ret=.5;')
    p = pipeline(warp, comp)
    assert p.requires_warp_uv(frame_wrap=1, motion_state={'mv_a': 0})
    step(p)
    np.testing.assert_array_equal(p.motion_uv, p.original_uv.astype(np.float16).astype(np.float32))


def test_composite_failure_and_replay_do_not_publish_pending_motion():
    p = pipeline()
    step(p)
    before = p.motion_uv.copy()
    _, p.composite_tree = trees('ret=.5;', 'ret=tex2D(sampler_missing,uv).xyz;')
    with pytest.raises(ValueError):
        step(p, uv=p.original_uv + [.125, 0])
    assert p.frame == 1 and p.motion_uv_frame == 0
    np.testing.assert_array_equal(p.motion_uv, before)
    p.composite_tree = None
    step(p, uv=p.original_uv + [.25, 0], write_motion_uv=False)
    assert p.motion_uv_frame == 0
    np.testing.assert_array_equal(p.motion_uv, before)


@pytest.mark.parametrize('alpha', [0, .5])
def test_detail_consumers_share_previous_authored_map_without_native_producer(alpha):
    from detail_pipeline import DetailPipeline
    low = pipeline(size=16)
    high = pipeline(size=32, shader_canvas_size=(16, 16))
    p = DetailPipeline(low, high, alpha=alpha)
    for index, visible in enumerate((False, False, True)):
        result = p.step(authored_warp_uv=low.original_uv + [index / 8, 0],
            native_warp_uv=high.original_uv + [.5, 0], uniforms={}, frame_wrap=1,
            decay=1, motion_state=state() if visible else {'mv_a': 0})
    assert result.history['motion_vector_source_frame'] == 1
    assert result.history['motion_uv_written'] is False
    assert result.history['authored_motion_uv_written'] is True
    assert result.history['authored_motion_uv_frame'] == 2
    assert result.history['authored_motion_uv_contract']['native_driver_verified'] is False
    assert low.motion_uv_frame == 2 and high.motion_uv_frame == 1
    assert high.motion_uv.shape == (16, 16, 2)
    np.testing.assert_array_equal(high.motion_uv,
        (low.original_uv + [.125, 0]).astype(np.float16).astype(np.float32))


@pytest.mark.parametrize('alpha',[0,.125])
def test_detail_failure_rolls_back_authored_publication(alpha):
    from detail_pipeline import DetailPipeline
    low=pipeline(size=16)
    high=pipeline(size=32,shader_canvas_size=(16,16))
    p=DetailPipeline(low,high,alpha=alpha)
    args=dict(authored_warp_uv=low.original_uv,native_warp_uv=high.original_uv,
              uniforms={},frame_wrap=1,decay=1,motion_state={'mv_a':0})
    p.step(**args)
    before=low.motion_uv.copy()
    _,high.composite_tree=trees('ret=.5;','ret=tex2D(sampler_missing,uv).xyz;')
    with pytest.raises(ValueError):p.step(**args)
    assert low.frame==high.frame==1 and low.motion_uv_frame==0
    np.testing.assert_array_equal(low.motion_uv,before)


def test_packed_half_words_preserve_sign_range_and_decode_before_bilinear():
    from pipeline_fields import pack_motion_uv, decode_motion_uv, sample_packed_motion_uv
    uv = np.array([[[-0., 0.], [-.25, 1.75]],
                   [[2**-24, 2**-14], [2.5, -.75]]], np.float32)
    words = pack_motion_uv(uv)
    assert words.dtype == np.uint16 and words[0, 0, 0] == 0x8000
    decoded = decode_motion_uv(words)
    np.testing.assert_array_equal(decoded, uv)
    assert np.signbit(decoded[0, 0, 0])
    np.testing.assert_array_equal(decode_motion_uv(np.zeros((2, 2, 2), np.uint16)), 0)
    query = np.array([[.375, .625]], np.float32)
    # Bottom-origin query has local weights (.25,.25) in this top-row-first map.
    expected = (uv[0, 0] * .75 + uv[0, 1] * .25) * .75 + (uv[1, 0] * .75 + uv[1, 1] * .25) * .25
    np.testing.assert_array_equal(sample_packed_motion_uv(words, query), expected[None])
    assert not np.array_equal(sample_packed_motion_uv(words, query), decoded[0, 0][None])


def test_packed_profiles_do_not_inherit_measured_float_path_evidence():
    from motion_vectors import APPLE_RTZ_STORAGE, MEASURED_SAMPLING
    for kwargs in ({'motion_uv_storage_profile': APPLE_RTZ_STORAGE},
                   {'motion_uv_sampling_profile': MEASURED_SAMPLING, 'motion_uv_sampler': lambda *a, **k: None}):
        with pytest.raises(ValueError, match='packed.*portable'):
            pipeline(motion_uv_backend='rg16ui-half-words', **kwargs)
    p = pipeline(motion_uv_backend='rg16ui-half-words')
    result = step(p)
    provenance = result.history['motion_uv_contract']
    assert provenance['storage'] == 'rg16ui-half-words'
    assert provenance['consumer'] == 'decode-half-before-manual-bilinear'
    assert provenance['native_driver_verified'] is False
    assert provenance['packing_rounding'] == 'host-numpy-half-nearest; GLES ties unverified'


def test_default_continuous_storage_is_conditional_and_wrapper_compile_unverified():
    result = step(pipeline())
    provenance = result.history['motion_uv_contract']
    assert provenance['storage'] == 'conditional'
    assert provenance['capability_selection_verified'] is False
    assert provenance['final_wrapper_compile_verified'] is False
    assert result.history['motion_map_policy'] == CORE_2331_MOTION
    assert result.history['motion_uv_written'] is True


def test_supplied_color_surface_cannot_substitute_for_actual_motion_producer():
    p = pipeline()
    with pytest.raises(ValueError, match='actual.*motion'):
        step(p, supplied_warp=np.zeros((16, 16, 4), np.float32))
    assert p.frame == 0 and p.motion_uv is None
    step(p, supplied_warp=np.zeros((16, 16, 4), np.float32), write_motion_uv=False)
    assert p.frame == 1 and p.motion_uv is None


def test_new_instance_and_resized_target_have_separate_first_frame_ownership():
    old = pipeline()
    step(old, True, uv=old.original_uv + [.25, 0])
    for size in (16, 32):
        fresh = pipeline(size=size)
        assert fresh.motion_uv is None and fresh.first_frame
        result = step(fresh, True)
        assert result.history['motion_vector_source_frame'] is None
        assert np.count_nonzero(result.feedback[..., :3]) == 0
        assert fresh.motion_uv_frame == 0 and fresh.motion_uv.shape == (size, size, 2)


@pytest.mark.parametrize('backend', ['conditional', 'rg16ui-half-words'])
def test_packed_or_conditional_contract_preserves_final_out_of_range_custom_output(backend):
    warp, comp = trees('_mv_tex_coords.xy=float2(-.25,1.75);ret=.5;', 'ret=.5;')
    p = pipeline(warp, comp, motion_uv_backend=backend)
    step(p)
    np.testing.assert_array_equal(p.motion_uv, np.broadcast_to([-.25, 1.75], (16, 16, 2)))


def test_source_engine_override_cannot_relabel_historical_parser():
    source = {'values': {}, 'sections': {}, 'parser_inputs': {'engine': CORE_2329_ENGINE}}
    with pytest.raises(ValueError, match='engine identity'):
        SourcePipeline.from_source(source, profile='gles300', compatibility={},
            source_engine=CORE_2331_ENGINE, motion_map_policy=CORE_2331_MOTION)
