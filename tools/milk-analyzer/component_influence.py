"""Measure conditional component influence in source-predicted luma fields.

Callers must establish matched prior state and unchanged actual output. These
measurements do not certify flashing or assign an audience score.
"""
import numpy as np

from effect_bursts import measure_bursts


def summarize_component_influence(times, actual, control, *, contrast_threshold, area_threshold):
    actual=np.asarray(actual,dtype=np.float32)
    control=np.asarray(control,dtype=np.float32)
    times=np.asarray(times,dtype=float)
    if actual.ndim!=3 or actual.shape!=control.shape or min(actual.shape)<1:
        raise ValueError('Matching frame-by-height-by-width luma fields required')
    if times.shape!=(len(actual),):
        raise ValueError('One time per field required')
    if not all(np.all(np.isfinite(field)) and np.all((field>=0)&(field<=1)) for field in (actual,control)):
        raise ValueError('Finite normalized luma fields required')
    if isinstance(contrast_threshold,bool) or not np.isfinite(contrast_threshold) or not 0<contrast_threshold<=1:
        raise ValueError('Contrast threshold must be positive and at most one')
    influence=actual-control
    areas=(np.abs(influence)>=contrast_threshold).mean(axis=(1,2))
    bursts=measure_bursts(times,areas,area_threshold=area_threshold)
    changing=(np.abs(np.diff(influence,axis=0))>=contrast_threshold).mean(axis=(1,2))
    return dict(
        contrast_threshold=float(contrast_threshold),
        mean_influenced_screen_area=float(areas.mean()),
        peak_influenced_screen_area=float(areas.max()),
        mean_changing_influence_screen_area=float(changing.mean()),
        peak_changing_influence_screen_area=float(changing.max()),
        mean_absolute_luma_influence=float(np.abs(influence).mean()),
        bursts=bursts,audience_score=None,
        interpretation='Conditional component influence, not a certified flash rate or perceptual score',
    )
