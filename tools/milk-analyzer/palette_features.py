"""Colour summaries from numerical RGB queries, without image classification.

Callers declare whether queries come from strict source evaluation or optional
display-field simulation. Query weights are explicit, not inferred screen area.
Warm/cool sectors are a versioned vocabulary assumption, not preference evidence.
"""
import cv2
import numpy as np


WARM_COOL_POLICY = 'warm-cool-sectors-v1'


def _relative_mass(mass):
    with np.errstate(under='ignore'):
        scaled = mass/mass.max()
    if np.any((mass > 0) & (scaled == 0)):
        raise ValueError('positive colour weight underflow; numeric domain unresolved')
    return scaled


def _hsv(rgb, *, value_floor, saturation_floor):
    points = np.asarray(rgb, dtype=np.float32)
    if (points.ndim != 2 or points.shape[1] != 3 or len(points) == 0 or
            not np.all(np.isfinite(points)) or np.any((points < 0) | (points > 1))):
        raise ValueError('finite nonempty normalized N by 3 RGB queries required')
    for threshold in (value_floor, saturation_floor):
        if isinstance(threshold, bool) or not np.isfinite(threshold) or threshold <= 0:
            raise ValueError('positive finite chromatic thresholds required')
    hsv = cv2.cvtColor(points.reshape(1, len(points), 3), cv2.COLOR_RGB2HSV).reshape(-1, 3)
    coloured = (hsv[:, 1] >= saturation_floor) & (hsv[:, 2] >= value_floor)
    return hsv, coloured


def hue_entropy(histogram):
    mass = np.asarray(histogram, dtype=np.float64)
    if mass.ndim != 1 or not np.all(np.isfinite(mass)) or np.any(mass < 0):
        raise ValueError('finite nonnegative hue histogram required')
    if mass.size == 0 or not np.any(mass > 0):
        return None
    mass = _relative_mass(mass)
    total = float(mass.sum())
    probabilities = mass[mass > 0]/total
    if np.any(probabilities == 0):
        raise ValueError('positive hue probability underflow; numeric domain unresolved')
    return float(-np.sum(probabilities*np.log(probabilities)))


def palette_summary(rgb, *, hue_bins=12, value_floor=.05, saturation_floor=.15, weights=None):
    """Use fixed circular bins and a chromatically supported warm/cool mean.

    Warm plateau: −30…90 degrees; cool plateau: 150…270 degrees.
    Cosine tapers join the plateaus; green120/purple300 are neutral. Equal
    weights describe query frequency unless the producer supplies area weights.
    """
    if type(hue_bins) is not int or hue_bins <= 0:
        raise ValueError('positive integer hue bin count required')
    hsv, coloured = _hsv(rgb, value_floor=value_floor, saturation_floor=saturation_floor)
    weights = np.ones(len(hsv), dtype=np.float64) if weights is None else np.asarray(weights, dtype=np.float64)
    if weights.shape != (len(hsv),) or not np.all(np.isfinite(weights)) or np.any(weights < 0) or not np.any(weights > 0):
        raise ValueError('matching finite nonnegative weights with positive total required')
    # Normalize first so large finite weights cannot overflow histogram mass.
    weights = _relative_mass(weights)
    total = float(weights.sum())
    chromatic_mass = float(weights[coloured].sum())
    bins = np.floor(hsv[:, 0]/360*hue_bins).astype(int) % hue_bins
    histogram = np.bincount(bins[coloured], weights=weights[coloured], minlength=hue_bins)
    entropy = hue_entropy(histogram)
    distance = np.abs((hsv[:, 0].astype(np.float64)-30+180) % 360-180)
    warmth = np.cos(np.pi*np.clip((distance-60)/60, 0, 1))
    if chromatic_mass:
        # Warmth is conditional on chromatic queries. Normalize that subset
        # independently so a tiny supported area cannot erase its colour mean.
        chromatic_weights = _relative_mass(weights[coloured])
        warm_cool = float(np.sum(warmth[coloured]*chromatic_weights)/chromatic_weights.sum())
    else:
        warm_cool = None
    return {'policy': WARM_COOL_POLICY, 'query_count': len(hsv),
            'warm_cool': warm_cool, 'chromatic_support': chromatic_mass/total,
            'chromatic_weight': chromatic_mass, 'total_weight': total,
            'hue_histogram': histogram.tolist(), 'hue_entropy_nats': entropy,
            'effective_hue_bins': float(np.exp(entropy)) if entropy is not None else None,
            'weighting': 'equal query frequency' if np.all(weights == 1) else 'explicit relative query weights',
            'limitations': ['Hue is undefined for achromatic or below-threshold queries',
                            'Query statistics do not establish visibility or complete spatial coverage']}


def hue_change_summary(before, after, *, dt, value_floor=.05, saturation_floor=.15):
    """Shortest circular hue change at matching query locations, not optical flow."""
    if isinstance(dt, bool) or not np.isfinite(dt) or dt <= 0:
        raise ValueError('positive finite hue query time interval required')
    old, a = _hsv(before, value_floor=value_floor, saturation_floor=saturation_floor)
    new, b = _hsv(after, value_floor=value_floor, saturation_floor=saturation_floor)
    if old.shape != new.shape:
        raise ValueError('matching hue query identities required')
    support = a & b
    cycles = np.abs((new[:, 0].astype(np.float64)-old[:, 0]+180) % 360-180)/360
    rate = cycles[support]/dt
    if not np.all(np.isfinite(rate)):
        raise ValueError('hue derivative numeric domain unresolved')
    return {'p95_cycles_per_second': float(np.percentile(rate, 95)) if rate.size else None,
            'maximum_cycles_per_second': float(rate.max()) if rate.size else None,
            'matched_chromatic_fraction': float(support.mean()),
            'matched_query_count': int(support.sum()),
            'limitations': ['Same-location change can include motion crossings or changed materials',
                            'Shortest circular differences can alias faster hue evolution']}
