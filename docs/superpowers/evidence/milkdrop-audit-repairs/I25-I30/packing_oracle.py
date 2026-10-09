"""Independent bounded source-byte oracle; no renderer or framebuffer model.

Geometry inputs are double equation channels. Display inputs are already
produced float diffuse values. Out-of-range/nonfinite behavior is excluded.
"""
import math
import struct


def float32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def check_unit(value):
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Oracle admits finite [0,1] producer values only")


def geometry_byte(value, alpha_mult=1):
    check_unit(value)
    check_unit(alpha_mult)
    return math.trunc(value * 255.0 * float32(alpha_mult)) & 255


def display_byte(diffuse):
    check_unit(diffuse)
    return math.trunc(float32(float32(diffuse) * 255.0)) & 255


def normalized(byte):
    if not isinstance(byte, int) or not 0 <= byte <= 255:
        raise ValueError("Not a byte")
    return byte / 255.0
