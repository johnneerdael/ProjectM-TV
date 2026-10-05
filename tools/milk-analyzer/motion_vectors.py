"""Source motion-vector geometry and canonical drawing for pinned projectM.

Follow MotionVectors.cpp and PresetMotionVectorsVertexShaderGlsl330.vert,
including fractional grids, previous UV sampling, minimum trails and projection.
Input UV surfaces are top-row-first. GPU precision and line smoothing remain
profile limitations; canonical unsmoothed lines are not driver-exact coverage.
"""
import numpy as np
from line_points import draw_lines
from scene_equations import MAIN
from spatial import sample2d


def _value(state, name, *, single=False):
    value = float(state.get(name, MAIN[name][1]))
    if not np.isfinite(value):
        raise ValueError('nonfinite motion-vector value: ' + name)
    if single:
        with np.errstate(over='ignore'):
            value = np.float32(value)
        if not np.isfinite(value):
            raise ValueError('motion-vector value exceeds float32: ' + name)
    return value


def motion_active(state):
    if _value(state, 'mv_a') < float(np.float32(.0001)):
        return False
    counts = []
    for name in ('mv_x', 'mv_y'):
        value = _value(state, name)
        if not -(2**31) <= value < 2**31:
            raise ValueError('motion-vector count outside native int32 cast domain')
        counts.append(int(value))
    return min(counts) > 0


def motion_uv_surface(uv):
    values = np.asarray(uv, dtype=np.float32)
    if values.ndim != 3 or values.shape[-1] != 2 or not np.all(np.isfinite(values)):
        raise ValueError('finite two-channel motion UV surface required')
    with np.errstate(over='ignore'):
        stored = values.astype(np.float16).astype(np.float32)
    if not np.all(np.isfinite(stored)):
        raise ValueError('motion UV exceeds finite native half-precision storage')
    return stored


def motion_geometry(state, *, previous_uv, width, height):
    if any(type(n) is not int or not 0 < n < 2**31 for n in (width, height)):
        raise ValueError('positive int32 motion viewport required')
    result = dict(positions=np.empty((0, 2, 2), dtype=np.float32), counts=[0, 0],
                  minimum_length=0., active=motion_active(state))
    if not result['active']:
        return result
    coordinates = []
    counts = []
    for name, maximum, offset_name, sign in [('mv_x', 64, 'mv_dx', 1), ('mv_y', 48, 'mv_dy', -1)]:
        value = _value(state, name)
        count = int(value)
        divert = np.float32(value) - np.float32(count)
        if count > maximum:
            count, divert = maximum, np.float32(0)
        divert = np.clip(divert, np.float32(0), np.float32(1))
        denominator = np.float32(count) + divert + np.float32(.25) - np.float32(1)
        pos = (np.arange(count, dtype=np.float32) + np.float32(.25)) / denominator
        pos += np.float32(sign) * _value(state, offset_name, single=True)
        coordinates.append(pos[(pos > np.float32(.0001)) & (pos < np.float32(.9999))])
        counts.append(count)
    result['counts'] = counts
    if not all(len(axis) for axis in coordinates):
        return result
    if previous_uv is None:
        raise ValueError('previous motion UV surface is not initialized')
    previous = np.asarray(previous_uv, dtype=np.float32)
    if previous.shape != (height, width, 2) or not np.all(np.isfinite(previous)):
        raise ValueError('previous motion UV must match finite viewport dimensions')
    x, y = np.meshgrid(*coordinates)
    starts = np.stack((x, y), axis=-1).reshape(-1, 2)
    lookup = starts.copy()
    lookup[:, 1] = np.float32(1) - lookup[:, 1]
    old_uv = sample2d(previous, lookup, wrap=False, linear=True, origin='bottom')
    delta = (old_uv - starts) * _value(state, 'mv_l', single=True)
    inverse_width = np.float32(1.25) / np.float32(width)
    inverse_height = np.float32(1.25) / np.float32(height)
    minimum = np.sqrt(inverse_width * inverse_width + inverse_height * inverse_height)
    length = np.sqrt(np.sum(delta * delta, axis=-1))
    short = (length <= minimum) & (length > np.float32(.00000001))
    delta[short] *= (minimum / length[short])[:, None]
    zero = length <= np.float32(.00000001)
    delta[zero] = minimum  # Native fallback deliberately sets both components.
    ends = starts + delta
    positions = np.stack((starts, ends), axis=1)
    positions[..., 1] = np.float32(1) - positions[..., 1]
    if not np.all(np.isfinite(positions)):
        raise ValueError('nonfinite motion-vector endpoint')
    result.update(positions=positions, minimum_length=float(minimum))
    return result


def draw_motion_vectors(destination, state, *, previous_uv, quantize=True):
    target = np.asarray(destination, dtype=np.float32).copy()
    if target.ndim != 3 or target.shape[-1] != 4:
        raise ValueError('RGBA motion-vector framebuffer required')
    height, width = target.shape[:2]
    geometry = motion_geometry(state, previous_uv=previous_uv, width=width, height=height)
    if not len(geometry['positions']):
        return target
    colour = [_value(state, 'mv_' + channel, single=True) for channel in 'rgba']
    for segment in geometry['positions']:
        # Native GL_LINES, not a connected line strip across the grid.
        target = draw_lines(target, segment, colour, additive=False, quantize=quantize)
    return target
