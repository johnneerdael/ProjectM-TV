"""Research calibration from source activity measurements to audience intervals.

Fits nonnegative feature weights to interval-valued labels. Training agreement
does not establish generalization or native appearance accuracy.
"""
import numpy as np
from scipy.optimize import LinearConstraint, minimize

from audience_policy import BANDS


def _features(values):
    x = np.asarray(values, dtype=float)
    if x.ndim != 2 or not len(x) or not x.shape[1] or not np.all(np.isfinite(x)) or np.any(x < 0):
        raise ValueError('Nonempty finite nonnegative source feature rows required')
    return np.column_stack((np.ones(len(x)), np.log1p(x)))


def predict_intensity(model, values):
    x = _features(values)
    scale = np.asarray(model.get('feature_scale', [1] * (x.shape[1] - 1)), dtype=float)
    if scale.shape != (x.shape[1] - 1,) or not np.all(np.isfinite(scale)) or np.any(scale <= 0):
        raise ValueError('Finite positive stored training feature scales required')
    x[:, 1:] /= scale
    theta = np.asarray([model['intercept'], *model['weights']], dtype=float)
    if theta.shape != (x.shape[1],) or not np.all(np.isfinite(theta)) or np.any(theta < 0):
        raise ValueError('Finite nonnegative weights matching the source features required')
    return np.round(np.clip(x @ theta, 0, 100), 8)


def fit_intervals(values, judgments):
    x = _features(values)
    scale = np.sqrt(np.mean(x[:, 1:] ** 2, axis=0))
    scale = np.where(scale > 0, scale, 1)
    x[:, 1:] /= scale
    bands = {name: (low, high) for name, low, high in BANDS}
    if len(judgments) != len(x) or any(name not in bands for name in judgments):
        raise ValueError('One valid audience judgment per source feature row required')
    lower = np.array([bands[name][0] for name in judgments], dtype=float)
    upper = np.array([np.inf if name == 'Party' else bands[name][1] for name in judgments])
    result = minimize(lambda theta: .5 * np.dot(theta, theta), np.zeros(x.shape[1]),
                      jac=lambda theta: theta, method='SLSQP',
                      bounds=[(0, 100)] + [(0, None)] * (x.shape[1] - 1),
                      constraints=[LinearConstraint(x, lower, upper)],
                      options={'ftol': 1e-10, 'maxiter': 1000})
    if not result.success or np.any(x @ result.x < lower - 1e-6) or np.any(x @ result.x > upper + 1e-6):
        raise ValueError('Audience intervals incompatible with these source features; no feasible calibration')
    return dict(intercept=float(result.x[0]), weights=result.x[1:].tolist(),
                feature_scale=scale.tolist(),
                transform='log1p', method='nonnegative minimum-norm interval fit',
                training_rows=len(x), appearance_accuracy_verified=False)
