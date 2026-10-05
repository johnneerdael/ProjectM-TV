"""Map a known intensity to the user's overlapping audience bands.

Intensity is an ordinal visual-activity score, not prediction confidence or a
measured accuracy percentage. This mapping does not estimate intensity itself.
"""
import math
from numbers import Real


BANDS = (('Chill', 0, 30), ('Normal', 25, 75), ('Party', 70, 100))


def labels_for_intensity(score: float | None) -> list[str]:
    if score is None:
        return []
    if isinstance(score, bool) or not isinstance(score, Real) or not math.isfinite(score) or not 0 <= score <= 100:
        raise ValueError('Intensity must be a finite number from 0 to 100, or unresolved (None)')
    return [label for label, lower, upper in BANDS if lower <= score <= upper]


def score_band_error(score: float | None, judgment: str) -> float | None:
    bands = {label: (lower, upper) for label, lower, upper in BANDS}
    if judgment not in bands:
        raise ValueError('Judgment must be Chill, Normal or Party')
    labels_for_intensity(score)
    if score is None:
        return None
    lower, upper = bands[judgment]
    return max(lower - score, score - upper, 0)


def score_matches_judgment(score: float | None, judgment: str, *, tolerance: float = 0) -> bool | None:
    if isinstance(tolerance, bool) or not isinstance(tolerance, Real) or not math.isfinite(tolerance) or not 0 <= tolerance <= 100:
        raise ValueError('Tolerance must be a finite nonnegative number of percentage points, at most 100')
    error = score_band_error(score, judgment)
    return None if error is None else error <= tolerance
