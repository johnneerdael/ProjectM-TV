"""Source motion-vector geometry and canonical drawing for pinned projectM.

Follow MotionVectors.cpp and PresetMotionVectorsVertexShaderGlsl330.vert,
including fractional grids, previous UV sampling, minimum trails and projection.
Input UV surfaces are top-row-first. GPU precision and line smoothing remain
profile limitations; canonical unsmoothed lines are not driver-exact coverage.
"""
import numpy as np
from line_points import draw_lines
from primitives import _finite
from quad_lines import PROFILE,quad_line_vertices,_draw_quad_segments,line_scale
from scene_equations import MAIN
from spatial import sample2d

PORTABLE_STORAGE='portable-half-nearest-v1'
APPLE_RTZ_STORAGE='apple-m4pro-gles-rg16f-rtz-normal-v1'
APPLE_FINITE_STORAGE='apple-m4pro-gles-rg16f-rtz-finite-v1'
PORTABLE_SAMPLING='portable-half-bilinear-v1'
MEASURED_SAMPLING='measured-gles300-vertex-half-v1'


def validate_motion_sampler(profile, sampler):
    if profile not in (PORTABLE_SAMPLING, MEASURED_SAMPLING):
        raise ValueError('unknown motion UV sampling profile')
    if (profile == MEASURED_SAMPLING and not callable(sampler)) or (profile == PORTABLE_SAMPLING and sampler is not None):
        raise ValueError('motion UV sampler requires explicit measured profile and callback')


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


def motion_uv_surface(uv, *, storage_profile=PORTABLE_STORAGE):
    if storage_profile not in (PORTABLE_STORAGE,APPLE_RTZ_STORAGE,APPLE_FINITE_STORAGE):
        raise ValueError('unknown motion UV storage profile')
    values = np.asarray(uv, dtype=np.float32)
    if values.ndim != 3 or values.shape[-1] != 2 or not np.all(np.isfinite(values)):
        raise ValueError('finite two-channel motion UV surface required')
    if storage_profile!=PORTABLE_STORAGE:
        magnitude=np.abs(values)
        if np.any(magnitude>np.finfo(np.float16).max):
            raise ValueError('half-storage profile requires finite half range')
        if storage_profile==APPLE_RTZ_STORAGE and np.any((magnitude!=0)&(magnitude<np.finfo(np.float16).tiny)):
            raise ValueError('half-storage profile requires zero or finite normal half range')
    with np.errstate(over='ignore'):
        half=values.astype(np.float16)
        if storage_profile!=PORTABLE_STORAGE:
            overshoot=np.abs(half.astype(np.float32))>np.abs(values)
            half=np.where(overshoot,np.nextafter(half,np.float16(0)),half)
        stored=half.astype(np.float32)
    if not np.all(np.isfinite(stored)):
        raise ValueError('motion UV exceeds finite native half-precision storage')
    return stored


def motion_geometry(state, *, previous_uv, width, height, sampling_profile=PORTABLE_SAMPLING, sampler=None,
                    reference_size=None,diffusion_active=False):
    """Sample the UV texture at its own extent; enforce target-sized trails.

    Only explicit diffusion activation scales minimum trails by the reference
    ratio. Authored targets pass reference_size=(0,0); defaults remain unscaled.
    """
    validate_motion_sampler(sampling_profile, sampler)
    if any(type(n) is not int or not 0 < n < 2**31 for n in (width, height)):
        raise ValueError('positive int32 motion viewport required')
    scale=line_scale(width,height,reference_size)
    if type(diffusion_active) is not bool:raise ValueError('boolean diffusion activation required')
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
    if (previous.ndim!=3 or previous.shape[-1]!=2 or min(previous.shape[:2])<=0 or
            not np.all(np.isfinite(previous))):
        raise ValueError('previous motion UV requires finite nonempty two-channel texture dimensions')
    x, y = np.meshgrid(*coordinates)
    starts = np.stack((x, y), axis=-1).reshape(-1, 2)
    lookup = starts.copy()
    lookup[:, 1] = np.float32(1) - lookup[:, 1]
    if sampling_profile == MEASURED_SAMPLING:
        old_uv = np.asarray(sampler(previous.copy(), lookup.copy(),
            wrap=False, linear=True, origin='bottom'), dtype=np.float32)
        if old_uv.shape != lookup.shape or not np.all(np.isfinite(old_uv)):
            raise ValueError('measured motion UV samples must be finite and match query shape')
    else:
        old_uv = sample2d(previous, lookup, wrap=False, linear=True, origin='bottom')
    delta = (old_uv - starts) * _value(state, 'mv_l', single=True)
    inverse_width = np.float32(1.25) / np.float32(width)
    inverse_height = np.float32(1.25) / np.float32(height)
    minimum = np.sqrt(inverse_width * inverse_width + inverse_height * inverse_height)
    if diffusion_active:minimum*=max(np.float32(1),scale)
    length = np.sqrt(np.sum(delta * delta, axis=-1))
    short = (length <= minimum) & (length > np.float32(.00000001))
    delta[short] *= (minimum / length[short])[:, None]
    zero = length <= np.float32(.00000001)
    delta[zero] = minimum  # Native fallback deliberately sets both components.
    ends = starts + delta
    positions = np.stack((starts, ends), axis=1)
    clip_positions=positions*np.float32(2)-np.float32(1)
    positions[..., 1] = np.float32(1) - positions[..., 1]
    if not np.all(np.isfinite(positions)):
        raise ValueError('nonfinite motion-vector endpoint')
    result.update(positions=positions,clip_positions=clip_positions, minimum_length=float(minimum))
    return result


def draw_motion_vectors(destination, state, *, previous_uv, quantize=True,
                        line_rendering_profile='canonical-gl-lines-v1',raster_subpixel_bits=None,
                        sampling_profile=PORTABLE_SAMPLING,sampler=None,reference_size=None,diffusion_active=False):
    if line_rendering_profile not in ('canonical-gl-lines-v1',PROFILE):
        raise ValueError('unknown motion-vector line profile')
    if raster_subpixel_bits is not None and (type(raster_subpixel_bits) is not int or not 4<=raster_subpixel_bits<=16):
        raise ValueError('motion raster subpixel bits must be an integer within4..16')
    target = np.asarray(destination, dtype=np.float32).copy()
    if target.ndim != 3 or target.shape[-1] != 4:
        raise ValueError('RGBA motion-vector framebuffer required')
    height, width = target.shape[:2]
    scale=line_scale(width,height,reference_size)
    quad=line_rendering_profile==PROFILE and scale>0
    if quad and reference_size is None and width*height>1024*768:
        raise ValueError('motion quad profile requires viewport within reference area')
    geometry = motion_geometry(state, previous_uv=previous_uv, width=width, height=height,
                               sampling_profile=sampling_profile, sampler=sampler,
                               reference_size=reference_size,diffusion_active=diffusion_active)
    if not len(geometry['positions']):
        return target
    colour = [_value(state, 'mv_' + channel, single=True) for channel in 'rgba']
    if quad:
        # The old per-vector draw validated even a skipped/degenerate quad.
        _finite(target,'framebuffer')
        segments=[]
        for index,segment in enumerate(geometry['positions']):
            # Keep vectors independent: connecting the grid would create joins
            # and different coverage. Only the already-generated quads are batched.
            segments.extend(quad_line_vertices(segment,colour,width=width,height=height,
                clip_positions=geometry['clip_positions'][index],reference_size=reference_size))
        return _draw_quad_segments(target,segments,additive=False,quantize=quantize,
                                   raster_subpixel_bits=raster_subpixel_bits)
    for segment in geometry['positions']:
        target=draw_lines(target,segment,colour,additive=False,quantize=quantize)
    return target
