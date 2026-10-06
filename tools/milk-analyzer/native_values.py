"""Decode equation-reader values only at a modeled native consumer boundary.

IEEE tags are not finite constants or a generic zero/default policy. Consumers
must opt in when their target operation defines nonfinite behavior explicitly.
"""
from numbers import Real
import math


def native_scalar(value, *, allow_ieee=False):
    if isinstance(value, Real):
        result=float(value)
    elif allow_ieee and isinstance(value, dict) and set(value)=={'ieee'}:
        tags={'nan':math.nan,'positive_infinity':math.inf,'negative_infinity':-math.inf}
        if value['ieee'] not in tags:raise ValueError('unknown native IEEE value')
        result=tags[value['ieee']]
    else:
        raise ValueError('unresolved native scalar value')
    if not allow_ieee and not math.isfinite(result):raise ValueError('finite native scalar required')
    return result


def live_wave_mode(value):
    """Patch0048 truncation, checked conversion and signed remainder."""
    value=native_scalar(value,allow_ieee=True)
    if not math.isfinite(value):return None
    truncated=math.trunc(value)
    if not -(2**31)<=truncated<=2**31-1:return None
    mode=truncated%16 if truncated>=0 else -(abs(truncated)%16)
    return mode if mode>=0 else None
