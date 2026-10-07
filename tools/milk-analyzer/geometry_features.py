"""Sample source geometry trajectories without constructing display fields.

These are changes in normalized geometry coordinates, not visible motion.
Divided differences estimate derivatives on consecutive same-identity vertices;
they are not bounds between samples or across arbitrary future inputs.
"""
from math import factorial

import numpy as np

from primitives import shape_fan


def _summary(values, unit):
    magnitudes = np.concatenate(values) if values else np.array([])
    return {'p95': float(np.percentile(magnitudes, 95)) if magnitudes.size else None,
            'maximum': float(magnitudes.max()) if magnitudes.size else None,
            'samples': int(magnitudes.size), 'unit': unit}


def trajectory_summary(rows, *, max_derivative_samples=1_000_000):
    """Track explicit component IDs; reset on disappearance or changed topology.

    Each component supplies corresponding N×2 vertices, not raster features.
    A vertex-index identity is supplied by the producer, not inferred here.
    """
    if type(max_derivative_samples) is not int or max_derivative_samples <= 0:
        raise ValueError('positive integer geometry derivative budget required')
    histories = {}
    seen = set()
    values = {order: [] for order in (1, 2, 3)}
    translations = {}
    bounds = {}
    previous_time = None
    births = deaths = topology = 0
    sample_count = 0
    budget_exceeded = False
    frames_sampled = 0
    frames_received = len(rows) if hasattr(rows, '__len__') else None
    for row in rows:
        if isinstance(row['time'], bool):
            raise ValueError('finite strictly increasing geometry time required')
        time = float(row['time'])
        if not np.isfinite(time) or (previous_time is not None and time <= previous_time):
            raise ValueError('finite strictly increasing geometry time required')
        components = row['components']
        if not isinstance(components, dict):
            raise ValueError('explicit geometry component identities required')
        if previous_time is not None:
            births += len(components.keys() - histories.keys())
            deaths += len(histories.keys() - components.keys())
        for key in list(histories.keys() - components.keys()):
            del histories[key]
        for key, data in components.items():
            if not isinstance(key, str) or not key:
                raise ValueError('nonempty geometry component identity required')
            points = np.asarray(data, dtype=np.float64)
            if points.ndim != 2 or points.shape[1] != 2 or len(points) == 0 or not np.all(np.isfinite(points)):
                raise ValueError('finite nonempty N by 2 geometry required')
            seen.add(key)
            history = histories.setdefault(key, [])
            if history and history[-1][1].shape != points.shape:
                topology += 1
                history.clear()
            history.append((time, points.copy()))
            del history[:-4]
            required = len(points)*min(3, len(history)-1)
            if sample_count+required > max_derivative_samples:
                budget_exceeded = True
                break
            extent={'minimum':points.min(axis=0).tolist(),'maximum':points.max(axis=0).tolist()}
            location=bounds.setdefault(key,{'first':extent,'last':extent,
                                           'window':extent,'frames':0})
            location['last']=extent
            location['window']={
                'minimum':np.minimum(location['window']['minimum'],extent['minimum']).tolist(),
                'maximum':np.maximum(location['window']['maximum'],extent['maximum']).tolist(),
            }
            location['frames']+=1
            if len(history) >= 2:
                displacement = np.mean(history[-1][1]-history[-2][1], axis=0)
                if not np.all(np.isfinite(displacement)):
                    raise ValueError('geometry translation numeric domain unresolved')
                translation = translations.setdefault(key, {'displacement': np.zeros(2),
                                                              'matched_intervals': 0})
                translation['displacement'] += displacement
                if not np.all(np.isfinite(translation['displacement'])):
                    raise ValueError('geometry translation numeric domain unresolved')
                translation['matched_intervals'] += 1
            for order in range(1, min(3, len(history)-1)+1):
                window = history[-order-1:]
                times = np.array([sample[0] for sample in window])
                differences = np.stack([sample[1] for sample in window])
                with np.errstate(all='ignore'):
                    for degree in range(1, order+1):
                        differences = np.diff(differences, axis=0) / (times[degree:]-times[:-degree])[:, None, None]
                    derivative = differences[0] * factorial(order)
                    magnitudes = np.hypot(derivative[:, 0], derivative[:, 1])
                if not np.all(np.isfinite(magnitudes)):
                    raise ValueError('geometry derivative numeric domain unresolved')
                values[order].append(magnitudes)
                sample_count += len(magnitudes)
        if budget_exceeded:
            # A prefix percentile is not a percentile of the declared window.
            # Withhold every derivative rather than silently truncating support.
            values = {order: [] for order in (1, 2, 3)}
            translations = {}
            bounds = {}
            break
        frames_sampled += 1
        previous_time = time
    signed_translation = {}
    for key, translation in translations.items():
        dx, dy = translation['displacement']
        signed_translation[key] = {
            'displacement': [float(dx), float(dy)],
            'horizontal': 'right' if dx > 0 else 'left' if dx < 0 else 'unchanged',
            'vertical': 'down' if dy > 0 else 'up' if dy < 0 else 'unchanged',
            'matched_intervals': translation['matched_intervals'],
        }
    return {'schema_version': 1, 'basis': 'strict-source-no-display-frames',
            'uses_display_fields': False, 'frames_sampled': frames_sampled,
            'frames_received': frames_received, 'budget_exceeded': budget_exceeded,
            'derivative_sample_budget': max_derivative_samples,
            'components_seen': len(seen), 'component_births': births,
            'component_deaths': deaths, 'topology_changes': topology,
            'component_translation': signed_translation,
            'component_bounds': bounds,
            'bounds_basis': 'Per-component source vertex extents in normalized top-origin coordinates, before visibility or viewport clipping',
            'translation_basis': 'Sum of equal-vertex centroid displacements over matched intervals; top-origin normalized screen coordinates',
            'speed': _summary(values[1], 'normalized viewport coordinates/s'),
            'acceleration': _summary(values[2], 'normalized viewport coordinates/s²'),
            'jerk': _summary(values[3], 'normalized viewport coordinates/s³'),
            'interval_kind': 'sampled finite-difference estimates',
            'visible_motion': None, 'preset_activity': None,
            'unknown_reasons': (['Geometry derivative calculation budget exceeded; partial derivatives withheld'] if budget_exceeded else [])+
                               ['Visibility, occlusion, feedback transport and waveform motion are not established by shape trajectories'],
            'limitations': ['Equal vertex weighting, not screen-area weighting',
                            'Component identity and vertex correspondence must be supplied by the producer',
                            'Finite differences do not prove smoothness between samples or classify teleports',
                            'Signed translation excludes identity/topology gaps; nonzero direction has no perceptual threshold and does not imply monotonic movement',
                            'Normalized x/y use fractions of viewport width/height, not physical distance']}


def scene_geometry_features(scene):
    """Reuse evaluated custom-shape fan geometry; no scene rasterization.

    Shape index and physical draw ordinal identify components. EEL can overwrite
    its instance variable, so that variable is not an identity. Correspondence is
    used only while the clamped side count is unchanged. Initializers/equations
    have already run; this function does not evaluate them again.
    """
    width, height = scene['viewport']
    if width <= 0 or height <= 0:
        raise ValueError('positive geometry viewport required')
    def rows():
        for frame in scene['frames']:
            components = {}
            ordinals = {}
            for shape in frame['shapes']:
                attributes = shape['values']
                index = shape['index']
                ordinal = ordinals.get(index, 0)
                ordinals[index] = ordinal+1
                key = f'shape:{index}:{ordinal}'
                # The last fan vertex repeats the first perimeter vertex; omit it
                # from statistics to avoid counting that vertex twice.
                components[key] = shape_fan(attributes, aspect_y=min(1, height/width))['positions'][:-1]
            yield {'time': frame['render_inputs']['time'], 'components': components}
    result = trajectory_summary(rows())
    result['frames_received'] = len(scene['frames'])
    result['geometry_scope'] = 'custom shape fan vertices'
    return result
