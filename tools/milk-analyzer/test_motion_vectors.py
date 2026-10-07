import importlib

import numpy as np
import pytest


def identity(width=32, height=32):
    x, y = np.meshgrid((np.arange(width, dtype=np.float32) + .5) / width,
                       (np.arange(height, dtype=np.float32) + .5) / height)
    return np.stack((x, y), axis=-1)


def state(**changes):
    # Exactly representable first grid position (.25,.25).
    return dict(mv_a=1, mv_x=2, mv_y=2, mv_dx=.05, mv_dy=-.05,
                mv_l=1, mv_r=1, mv_g=0, mv_b=0, **changes)


def geometry(values, uv=None):
    return importlib.import_module('motion_vectors').motion_geometry(
        values, previous_uv=uv, width=32, height=32)


def test_identity_has_native_diagonal_minimum_trail_and_projection_flip():
    result = geometry(state(), identity())
    assert result['positions'].shape == (1, 2, 2)
    np.testing.assert_allclose(result['positions'][0, 0], [.25, .75], atol=1e-7)
    minimum = np.sqrt(np.float32(2) * np.float32(1.25 / 32) ** 2)
    np.testing.assert_allclose(result['positions'][0, 1], [.25 + minimum, .75 - minimum], atol=1e-7)
    # Native zero-length fallback sets both components, not a unit diagonal.
    np.testing.assert_allclose(np.linalg.norm(np.diff(result['positions'][0], axis=0)), minimum * np.sqrt(2), atol=1e-7)


def test_previous_warp_displacement_is_scaled_and_y_direction_is_preserved():
    values = state()
    values['mv_l'] = 2
    result = geometry(values, identity() + [.125, .0625])
    np.testing.assert_allclose(result['positions'][0], [[.25, .75], [.5, .625]], atol=1e-7)


def test_short_nonzero_trail_is_lengthened_without_changing_its_direction():
    result = geometry(state(), identity() + [.001, 0])
    delta = result['positions'][0, 1] - result['positions'][0, 0]
    np.testing.assert_allclose(delta, [result['minimum_length'], 0], atol=2e-6)


def test_fractional_grid_counts_and_offsets_control_placement():
    values = state()
    values.update(mv_x=2.5, mv_y=2.25, mv_dx=0, mv_dy=0)
    result = geometry(values, identity())
    assert len(result['positions']) == 4
    np.testing.assert_allclose(result['positions'][:, 0],
                               [[1/7, 5/6], [5/7, 5/6], [1/7, 1/6], [5/7, 1/6]], atol=1e-7)


def test_native_count_caps_and_hidden_vectors_require_no_previous_map():
    values = state()
    values.update(mv_x=100, mv_y=100, mv_dx=0, mv_dy=0)
    result = geometry(values, identity())
    assert result['counts'] == [64, 48]
    assert len(result['positions']) == 63 * 47
    values['mv_a'] = 0
    assert len(geometry(values)['positions']) == 0


def test_missing_previous_map_and_undefined_int_cast_stay_unresolved():
    with pytest.raises(ValueError, match='previous motion UV'):
        geometry(state())
    values = state()
    values['mv_x'] = 2**31
    with pytest.raises(ValueError, match='int32'):
        geometry(values, identity())


def test_motion_map_uses_half_precision_and_rejects_overflow():
    module = importlib.import_module('motion_vectors')
    uv = identity() + [.000123, 0]
    stored = module.motion_uv_surface(uv)
    np.testing.assert_array_equal(stored, uv.astype(np.float16).astype(np.float32))
    with pytest.raises(ValueError, match='half'):
        module.motion_uv_surface(uv * 1e8)


def test_drawing_uses_independent_segments_and_alpha_colour():
    module = importlib.import_module('motion_vectors')
    values = state()
    values['mv_a'] = .5
    target = np.zeros((32, 32, 4), dtype=np.float32)
    result = module.draw_motion_vectors(target, values, previous_uv=identity() + [.125, 0], quantize=False)
    assert np.count_nonzero(result[..., 0]) > 0
    assert np.max(result[..., 0]) == .5
    assert np.count_nonzero(result[..., 1:3]) == 0


def test_declared_quad_profile_uses_native_flat_ended_band_coverage():
    from motion_vectors import draw_motion_vectors,motion_geometry
    from quad_lines import PROFILE,draw_quad_lines
    target=np.zeros((32,32,4),np.float32)
    values=state();uv=identity()+[.125,0]
    segment=motion_geometry(values,previous_uv=uv,width=32,height=32)['positions'][0]
    expected=draw_quad_lines(target,segment,[1,0,0,1],additive=False,
        clip_positions=segment*np.array([2,-2],np.float32)+np.array([-1,1],np.float32),
        raster_subpixel_bits=8)
    actual=draw_motion_vectors(target,values,previous_uv=uv,
        line_rendering_profile=PROFILE,raster_subpixel_bits=8)
    np.testing.assert_array_equal(actual,expected)
    assert not np.array_equal(actual,draw_motion_vectors(target,values,previous_uv=uv))


def test_motion_line_profile_rejects_unknown_coverage_rules():
    from motion_vectors import draw_motion_vectors
    with pytest.raises(ValueError,match='motion.*line profile'):
        draw_motion_vectors(np.zeros((32,32,4),np.float32),state(),previous_uv=identity(),
                            line_rendering_profile='unknown')


def test_motion_grid_and_viewport_guards_do_not_depend_on_visible_vectors():
    from motion_vectors import draw_motion_vectors
    from quad_lines import PROFILE
    hidden=state();hidden['mv_a']=0
    for bits in [True,3,17]:
        with pytest.raises(ValueError,match='subpixel'):
            draw_motion_vectors(np.zeros((32,32,4)),hidden,previous_uv=None,
                                raster_subpixel_bits=bits)
    with pytest.raises(ValueError,match='reference area'):
        draw_motion_vectors(np.zeros((900,900,4)),hidden,previous_uv=None,
                            line_rendering_profile=PROFILE)
