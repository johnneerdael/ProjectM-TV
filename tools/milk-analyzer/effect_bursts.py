"""Measure temporal bursts in source-predicted component influence traces.

Influence onsets are not automatically brightness flashes. Thresholds are
explicit research settings, not calibrated Chill/Normal/Party boundaries.
"""
import numpy as np


def measure_bursts(times, affected_areas, *, area_threshold):
    times = np.asarray(times, dtype=float)
    areas = np.asarray(affected_areas, dtype=float)
    if times.ndim != 1 or len(times) < 2 or areas.shape != times.shape:
        raise ValueError('Matching one-dimensional traces with at least two samples required')
    if not np.all(np.isfinite(times)) or not np.all(np.isfinite(areas)) or np.any((areas < 0) | (areas > 1)):
        raise ValueError('Finite times and affected areas from zero to one required')
    intervals = np.diff(times)
    if np.any(intervals <= 0) or not np.allclose(intervals, intervals[0], rtol=1e-6, atol=1e-9):
        raise ValueError('Increasing uniformly sampled times required')
    if not np.isfinite(area_threshold) or not 0 < area_threshold <= 1:
        raise ValueError('Area threshold must be positive and at most one')
    dt = float(intervals[0])
    active = areas >= area_threshold
    starts = np.flatnonzero(active & ~np.r_[False, active[:-1]])
    stops = np.flatnonzero(active & ~np.r_[active[1:], False])
    bursts = []
    for start, stop in zip(starts, stops):
        bursts.append(dict(start_seconds=float(times[start]),
                           duration_seconds=float((stop - start + 1) * dt),
                           peak_affected_area=float(areas[start:stop + 1].max()),
                           left_censored=bool(start == 0), right_censored=bool(stop == len(times) - 1)))
    onsets = sum(not event['left_censored'] for event in bursts)
    duration = len(times) * dt
    return dict(area_threshold=float(area_threshold), sample_interval_seconds=dt,
                observation_seconds=duration, burst_count=len(bursts),
                uncensored_onsets=onsets, onset_rate_hz=onsets / duration,
                duty_fraction=float(active.mean()), bursts=bursts,
                interpretation='Component influence events; not a certified flashing rate or audience score')
