"""Nominal periodic coordinate preimages; not rendered feature/copy counts."""
import math
import numpy as np


def copy_lattice(mapping):
    policy=mapping.get('sampling_policy') or {};wrap=policy.get('wrap')
    result={'policy':'source-affine-repeat-preimages-v1','status':'unknown',
        'coordinate_basis':mapping.get('basis'),
        'native_mesh_transform_precedes_basis':mapping.get('native_mesh_transform_precedes_basis'),
        'wrap_enabled':wrap,'wrap_condition':policy.get('wrap_condition'),
        'lattice_basis_uv':None,'origin_for_source_feature_zero_uv':None,
        'origin_from_offset_matrix':None,'fundamental_cell_area_uv2':None,
        'nominal_lattice_points_per_unit_uv_area':None,'orientation_reversed':None,
        'origin_velocity_uv_per_source_second':None,
        'origin_speed_uv_per_source_second_upper_bound':None,'origin_speed_estimate_kind':'unknown',
        'actual_visible_copy_count':None,'visible_screen_motion':None,'unknown_reasons':[],
        'conditions':['For repeat sampling and a fixed source feature s, candidate positions are inverse(M)*(s+integer_shift-offset)',
                      'Generator columns and density describe coordinate preimages in the declared basis, not actual visible copies or screen coverage',
                      'Unknown wrap requires its declared context; clamped sampling has no periodic point lattice',
                      'Warp shader basis already includes native mesh motion; inverse coordinates are not automatically physical screen coordinates',
                      'Offsets may depend on audio/time/state; velocity holds matrix/source feature/integer index fixed',
                      'Colour weights, clipping, source content, filter/LOD, masks, shader rounding and feedback history can suppress/change visible features']}
    if wrap is False:result['status']='not_periodic';return result
    inverse=mapping.get('inverse_matrix');det=mapping.get('determinant')
    if inverse is None or det is None or det==0:
        result['unknown_reasons']=['no finite invertible single-basis affine sampling map'];return result
    m=np.array(inverse,dtype=float);area=abs(1/det);density=abs(det)
    if m.shape!=(2,2) or not np.all(np.isfinite(m)) or not math.isfinite(area) or not math.isfinite(density):
        result['unknown_reasons']=['lattice geometry is nonfinite'];return result
    result.update(status='conditional_periodic_preimages' if wrap is True else 'conditional_on_repeat_wrap',
        lattice_basis_uv=m.tolist(),origin_from_offset_matrix=(-m).tolist(),
        origin_for_source_feature_zero_uv=mapping.get('inverse_offset_uv'),
        fundamental_cell_area_uv2=area,nominal_lattice_points_per_unit_uv_area=density,
        orientation_reversed=det<0)
    def transformed(rates,*,absolute=False):
        weights=np.abs(m) if absolute else -m
        with np.errstate(over='ignore',invalid='ignore'):terms=weights*np.array(rates)[None,:]
        if np.any((weights!=0)&(np.array(rates)[None,:]!=0)&(terms==0)):
            result['unknown_reasons'].append('origin-rate product underflow');return None
        with np.errstate(over='ignore',invalid='ignore'):return terms.sum(axis=1)
    curves=mapping.get('offset_controls',[])
    if len(curves)!=2:return result
    if all(c['curve_kind'] in {'constant','linear_time'} for c in curves):
        rates=np.array([0. if c['curve_kind']=='constant' else c['signed_linear_rate_per_second'] for c in curves])
        velocity=transformed(rates)
        if velocity is None:return result
        speed=math.hypot(*velocity)
        if np.all(np.isfinite(velocity)) and math.isfinite(speed):
            result.update(origin_velocity_uv_per_source_second=velocity.tolist(),
                origin_speed_uv_per_source_second_upper_bound=speed,origin_speed_estimate_kind='exact_nominal')
    else:
        rates=[c['maximum_absolute_control_rate_per_second'] for c in curves]
        if all(r is not None for r in rates):
            components=transformed(rates,absolute=True)
            if components is None:return result
            speed=math.hypot(*components)
            if math.isfinite(speed):result.update(origin_speed_uv_per_source_second_upper_bound=speed,origin_speed_estimate_kind='upper_bound')
    return result
