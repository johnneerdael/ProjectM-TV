"""Native per-frame input names and file-value conversion needed by source proofs.

Names mirror PerFrameContext::RegisterBuiltinVariables in the pinned engine.
The Q registers reload their post-init snapshot separately in equation_domains.
"""
import ctypes
import errno
import numpy as np


FRAME_INPUTS = frozenset('''
zoom zoomexp rot warp cx cy dx dy sx sy time fps bass mid treb bass_att
mid_att treb_att frame decay wave_a wave_r wave_g wave_b wave_x wave_y
wave_mystery wave_mode progress ob_size ob_r ob_g ob_b ob_a ib_size ib_r
ib_g ib_b ib_a mv_x mv_y mv_dx mv_dy mv_l mv_r mv_g mv_b mv_a echo_zoom
echo_alpha echo_orient wave_usedots wave_thick wave_additive wave_brighten
darken_center gamma wrap invert brighten darken solarize meshx meshy
pixelsx pixelsy aspectx aspecty blur1_min blur2_min blur3_min blur1_max
blur2_max blur3_max blur1_edge_darken
'''.split())

_LIBC = ctypes.CDLL(None, use_errno=True)
_LIBC.strtof.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
_LIBC.strtof.restype = ctypes.c_float
_LIBC.strtol.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p), ctypes.c_int]
_LIBC.strtol.restype = ctypes.c_long


def scalar(values, key, default, kind):
    """Look up native lowercase file keys and match stof/stoi conversion."""
    text = ctypes.create_string_buffer(str(values.get(key.lower(), default)).encode('utf-8'))
    end = ctypes.c_void_p()
    ctypes.set_errno(0)
    if kind in {'int', 'bool'}:
        value = _LIBC.strtol(text, ctypes.byref(end), 10)
        if end.value == ctypes.addressof(text) or ctypes.get_errno() == errno.ERANGE or not -(2**31) <= value < 2**31:
            value = int(default)
        return int(value > 0) if kind == 'bool' else value
    value = _LIBC.strtof(text, ctypes.byref(end))
    if end.value == ctypes.addressof(text) or ctypes.get_errno() == errno.ERANGE:
        value = float(np.float32(default))
    if not np.isfinite(value):
        raise ValueError('nonfinite source default: ' + key)
    return value
