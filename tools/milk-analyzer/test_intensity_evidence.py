import importlib
import importlib.util

import pytest


def evidence():
    assert importlib.util.find_spec('intensity_evidence') is not None, 'Intensity evidence is not implemented'
    return importlib.import_module('intensity_evidence')


def test_low_motion_does_not_dilute_an_independent_flash_contribution():
    assert evidence().combine_activity(10, coherent_flash=80) == 80
    assert evidence().combine_activity(90, coherent_flash=80) == 90


def test_unmeasured_contribution_is_not_fabricated_as_zero():
    assert evidence().combine_activity(None, coherent_flash=None, component_burst=None) is None
    assert evidence().combine_activity(None, coherent_flash=80) == 80


def test_coherent_flash_proxy_requires_opposite_changes_and_weights_extent():
    report=dict(frames_measured=360,flashing=dict(peak_mean_luma_jump=.6,
        peak_brightness_change_area=1,coherent_brightening_transitions=24,
        coherent_darkening_transitions=24,peak_paired_luma_area_product=.6))
    assert evidence().coherent_flash_proxy(report, fps=30) == pytest.approx(100*.6**.5)
    report['flashing']['coherent_darkening_transitions']=0
    assert evidence().coherent_flash_proxy(report, fps=30) == 0


def test_unrelated_contrast_and_area_peaks_cannot_inflate_the_flash_proxy():
    report=dict(frames_measured=360,flashing=dict(peak_mean_luma_jump=.9,
        peak_brightness_change_area=.9,coherent_brightening_transitions=24,
        coherent_darkening_transitions=24,peak_paired_luma_area_product=.04))
    assert evidence().coherent_flash_proxy(report, fps=30) == pytest.approx(20)


def test_legacy_report_without_paired_evidence_stays_unmeasured():
    report=dict(frames_measured=360,flashing=dict(peak_mean_luma_jump=.9,
        peak_brightness_change_area=.9,coherent_brightening_transitions=24,
        coherent_darkening_transitions=24))
    assert evidence().coherent_flash_proxy(report, fps=30) is None


@pytest.mark.parametrize('score', [-1, 101, float('nan')])
def test_invalid_contributions_are_rejected(score):
    with pytest.raises(ValueError):
        evidence().combine_activity(score, coherent_flash=None)
