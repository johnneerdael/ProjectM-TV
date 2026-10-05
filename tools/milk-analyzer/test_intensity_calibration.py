import importlib
import importlib.util

import numpy as np
import pytest


def calibration():
    assert importlib.util.find_spec('intensity_calibration') is not None, 'Intensity calibration is not implemented'
    return importlib.import_module('intensity_calibration')


def test_fit_learns_intervals_instead_of_copying_midpoint_labels():
    module = calibration()
    x = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0]], dtype=float)
    model = module.fit_intervals(x, ['Chill', 'Normal', 'Party'])
    scores = module.predict_intensity(model, x)
    assert 0 <= scores[0] <= 30
    assert 25 <= scores[1] <= 75
    assert 70 <= scores[2] <= 100
    assert model['appearance_accuracy_verified'] is False


def test_increasing_a_measured_activity_feature_cannot_lower_the_score():
    module = calibration()
    x = np.array([[0, 0, 0], [1, 1, 1], [3, 3, 3]], dtype=float)
    model = module.fit_intervals(x, ['Chill', 'Normal', 'Party'])
    base = np.array([[1, 1, 1]], dtype=float)
    original = module.predict_intensity(model, base)[0]
    for feature in range(3):
        increased = base.copy(); increased[0, feature] += 1
        assert module.predict_intensity(model, increased)[0] >= original


def test_contradictory_training_rows_are_reported_not_claimed_as_a_perfect_fit():
    with pytest.raises(ValueError, match='incompatible|feasible'):
        calibration().fit_intervals(np.zeros((2, 3)), ['Chill', 'Party'])


@pytest.mark.parametrize('x', [np.array([[np.nan, 0, 0]]), np.array([[-1, 0, 0]])])
def test_missing_or_invalid_source_features_do_not_become_calm(x):
    with pytest.raises(ValueError, match='finite|nonnegative'):
        calibration().fit_intervals(x, ['Chill'])


def test_training_feature_scale_is_saved_and_not_reestimated_from_prediction_batch():
    module=calibration()
    x=np.array([[0,0,0],[1,.01,0],[2,.02,0]],dtype=float)
    model=module.fit_intervals(x,['Chill','Normal','Party'])
    assert len(model['feature_scale']) == 3
    assert all(np.isfinite(v) and v>0 for v in model['feature_scale'])
    assert model['feature_scale'][2] == 1
    point=np.array([[1,.01,0]],dtype=float)
    alone=module.predict_intensity(model,point)[0]
    batch=module.predict_intensity(model,np.vstack([point,[1000,1000,1000]]))[0]
    assert alone == batch
