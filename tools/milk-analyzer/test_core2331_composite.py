"""Release31 VideoEcho discriminators; no native rendering or device claims."""
import numpy as np
import pytest

from engine_profiles import (CORE_2329_ENGINE, CORE_2331_ENGINE,
                             CORE_2315_DISPLAY, CORE_2331_DISPLAY, LEGACY_DISPLAY)
from field_math import UnresolvedMath
from legacy_composite import gamma_weights, legacy_display, source_tint_amount


def controls(**changes):
    return {'gamma': 1, 'echo_alpha': 0, 'echo_zoom': 1, 'echo_orient': 0,
            'brighten': 0, 'darken': 0, 'solarize': 0, 'invert': 0, **changes}


@pytest.mark.parametrize('gamma,count', [
    (np.float32(1.0005), 1),
    (np.nextafter(np.float32(1.001), np.float32(-np.inf)), 1),
    (np.float32(1.001), 2),
    (np.nextafter(np.float32(1.001), np.float32(np.inf)), 2),
    (np.nextafter(np.float32(2.001), np.float32(-np.inf)), 2),
    (np.float32(2.001), 2),
    (np.nextafter(np.float32(2.001), np.float32(np.inf)), 3),
])
def test_gamma_only_uses_float32_milkdrop_epsilon_at_pass_boundaries(gamma, count):
    weights = gamma_weights(gamma, echo=False, control_policy=CORE_2331_DISPLAY)
    assert len(weights) == count
    assert weights[:-1] == [1] * (count - 1)
    assert weights[-1] == float(np.float32(gamma - np.float32(count - 1)))


@pytest.mark.parametrize('gamma,count', [(1.0005, 2), (2.001, 3)])
def test_echo_retains_old_epsilon_and_final_diffuse_weight(gamma, count):
    weights = gamma_weights(gamma, echo=True, control_policy=CORE_2331_DISPLAY)
    assert len(weights) == count
    assert weights[:-1] == [1] * (count - 1)
    assert weights[-1] == float(np.float32(np.float32(gamma) - np.float32(count - 1)))


@pytest.mark.parametrize('policy', [LEGACY_DISPLAY, CORE_2315_DISPLAY])
def test_historical_gamma_only_keeps_old_pass_count(policy):
    assert len(gamma_weights(1.0005, echo=False, control_policy=policy)) == 2
    assert len(gamma_weights(2.001, echo=False, control_policy=policy)) == 3
    assert gamma_weights(1.0005, echo=False) == gamma_weights(1.0005, echo=False, control_policy=policy)


def asymmetric_field():
    field = np.zeros((8, 8, 4), np.float32)
    field[..., 0] = np.linspace(.02, .2, 8)[None, :]
    field[..., 1] = np.linspace(.01, .1, 8)[:, None]
    field[..., 3] = 1
    return field


def display(orientation, policy=CORE_2331_DISPLAY, **changes):
    return legacy_display(asymmetric_field(), values={'nVideoEchoOrientation': str(orientation),
        'fVideoEchoAlpha': '1', 'fVideoEchoZoom': '1', 'fGammaAdj': '1'},
        main=controls(echo_alpha=1, echo_orient=orientation, **changes), control_policy=policy,
        time=0, hue_offsets=[0]*4, shader_amount=0, quantize=False)


@pytest.mark.parametrize('orientation,flip_x,flip_y', [
    (-1, True, False), (-3, True, False), (-5, True, False),
    (-2, False, False), (-4, False, False), (-1.9, True, False),
    (-.9, False, False), (1, True, False), (2, False, True), (3, True, True),
])
def test_echo_signed_remainder_flips_negative_odd_u_only(orientation, flip_x, flip_y):
    expected = display(0)
    if flip_x:
        expected = expected[:, ::-1]
    if flip_y:
        expected = expected[::-1]
    np.testing.assert_allclose(display(orientation), expected, atol=2e-8, rtol=0)


@pytest.mark.parametrize('policy', [LEGACY_DISPLAY, CORE_2315_DISPLAY])
@pytest.mark.parametrize('orientation', [-1, -3, -5])
def test_historical_negative_odd_echo_stays_unflipped(policy, orientation):
    np.testing.assert_array_equal(display(orientation, policy), display(0, policy))


@pytest.mark.parametrize('orientation', [float('nan'), float('inf'), 2**31, -2**31-1])
def test_invalid_orientation_still_omits_echo_and_preserves_gamma(orientation):
    actual = display(orientation, gamma=1.0005)
    expected = legacy_display(asymmetric_field(), values={},
        main=controls(gamma=1.0005), control_policy=CORE_2331_DISPLAY,
        time=0, hue_offsets=[0]*4, shader_amount=0, quantize=False)
    np.testing.assert_array_equal(actual, expected)


def test_source31_keeps_live_gamma_and_nonzero_filters_over_file_values():
    field = np.full((8, 8, 4), .1, np.float32); field[..., 3] = 1
    actual = legacy_display(field, values={'fGammaAdj': '2', 'bInvert': '0'},
        main=controls(invert=-1), control_policy=CORE_2331_DISPLAY,
        time=0, hue_offsets=[0]*4, shader_amount=0, quantize=False)
    np.testing.assert_array_equal(actual[..., :3], np.full((8, 8, 3), .9, np.float32))


@pytest.mark.parametrize('policy,echo_alpha,stored_byte', [
    (CORE_2331_DISPLAY, 0, 26),
    (CORE_2315_DISPLAY, 0, 25),
    (CORE_2331_DISPLAY, 1, 25),
])
def test_display_selects_gamma_count_before_each_quantized_blend(policy, echo_alpha, stored_byte):
    # 0.09999*255 is below25.5; weighting once by1.0005 crosses it.
    # The old two-pass path rounds to25 first, then adds less than half a byte.
    field = np.full((8, 8, 4), .09999, np.float32); field[..., 3] = 1
    actual = legacy_display(field, values={},
        main=controls(gamma=1.0005, echo_alpha=echo_alpha), control_policy=policy,
        time=0, hue_offsets=[0]*4, shader_amount=0, quantize=True)
    np.testing.assert_array_equal(actual[..., :3],
        np.full((8, 8, 3), np.float32(stored_byte)/np.float32(255), np.float32))


@pytest.mark.parametrize('gamma,reason', [
    (float('nan'), 'nonfinite'), (float('inf'), 'nonfinite'),
    (2**31, 'integer domain'), (-1, 'unwritten'), (4097, 'budget'),
])
def test_source31_preserves_gamma_domain_guards(gamma, reason):
    with pytest.raises(UnresolvedMath, match=reason):
        gamma_weights(gamma, echo=False, control_policy=CORE_2331_DISPLAY)


def test_source31_static_tint_requires_exact_identity_and_retains_historical_admission():
    source = {'values': {'fShader': '.25'}, 'parser_inputs': {'engine': CORE_2331_ENGINE}}
    assert source_tint_amount(source) == .25
    source['parser_inputs']['engine'] = CORE_2329_ENGINE
    assert source_tint_amount(source) == .25
    source['parser_inputs']['engine'] = {**CORE_2331_ENGINE, 'patches_sha256': '0'*64}
    assert source_tint_amount(source) is None


def test_source31_static_tint_respects_declared_native_lowercase_lookup():
    source = {'values': {'fshader': '.25'}, 'parser_inputs': {
        'engine': CORE_2331_ENGINE, 'setting_lookup_policy': 'native-case-insensitive-v1'}}
    assert source_tint_amount(source) == .25


def test_unknown_display_policy_is_not_silently_admitted():
    with pytest.raises(ValueError, match='policy'):
        gamma_weights(1, echo=False, control_policy='unknown')
