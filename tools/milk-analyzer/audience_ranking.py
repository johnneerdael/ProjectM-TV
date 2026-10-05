"""Relative collection ranks for finite, nonnegative activity measurements."""
import math
from collections import Counter
from numbers import Real


def relative_activity_ranks(scores):
    """Return 1–100 ranks with equal scores tied and unknown scores unranked.

    Average ordinal positions are rescaled to give the lowest and highest
    observed score groups ranks 1 and 100. A collection with no measured spread
    receives midpoint ranks. Ranks depend on collection membership, not only on
    the preset. Raw activity is deliberately unclipped: its units are not the
    final 1–100 collection score.
    """
    scores=list(scores)
    known=[value for value in scores if value is not None]
    if any(isinstance(value,bool) or not isinstance(value,Real) or not math.isfinite(value) or value<0 for value in known):
        raise ValueError('Measured activity must be finite and nonnegative')
    counts=Counter(known)
    positions={}
    before=0
    for value in sorted(counts):
        positions[value]=before+(counts[value]-1)/2
        before+=counts[value]
    if len(positions)>1:
        low=min(positions.values());span=max(positions.values())-low
        ranks={value:1+99*(position-low)/span for value,position in positions.items()}
    else:
        ranks={value:50.5 for value in positions}
    return [ranks[value] if value is not None else None for value in scores]
