"""Analytic procedural form generators from contributing typed shader graphs."""
import math
from fractions import Fraction
from shader_fields import Field


def _periodic_axis(value):
    from source_appearance import _canonical_lane,_phase_literal
    value=_canonical_lane(value)
    if value.op=='abs':value=_canonical_lane(value.args[0])
    if value.dtype!='float' or value.op not in {'subtract','add'}:return None
    a,b=value.args;centre=None;wrapped=None
    if a.op=='frac':
        shift=_phase_literal(b)
        if shift is not None:wrapped=a;centre=shift if value.op=='subtract' else -shift
    elif b.op=='frac':
        shift=_phase_literal(a)
        if shift is not None:wrapped=b;centre=shift if value.op=='subtract' else -shift
    if wrapped is None or wrapped.dtype!='float' or not 0<centre<1:return None
    return wrapped.args[0],centre


def periodic_radial_glow(node,analysis):
    from effect_families import _parts
    from source_polar import _nodes
    from source_sampling import affine_uv_map
    from source_appearance import _phase_literal,_expression,_digest,_routes
    from source_motion import motion_control
    if node.op!='saturate' or node.dtype!='float':return None
    divide=node.args[0]
    if divide.op!='divide' or divide.dtype!='float':return None
    gain=_phase_literal(divide.args[0]);distance=divide.args[1]
    if gain is None or gain<=0 or distance.op!='length':return None
    parts=_parts(distance.args[0])
    if len(parts)!=2:return None
    axes=[_periodic_axis(part) for part in parts]
    if any(axis is None for axis in axes):return None
    phases=[axis[0] for axis in axes];centre=[axis[1] for axis in axes]
    coordinate=Field('components',tuple(phases),'float2')
    # x/y/rad/ang are EEL coordinates, but may be ordinary shader uniforms.
    # Require the typed native shader varying bases, never a name-only EEL set.
    if not any(n.op=='input' and (n.detail.get('name')=='_uv' and n.dtype in {'float2','float4'} or
                                 n.detail.get('name')=='_rad_ang' and n.dtype=='float2')
               for n,p in _nodes(coordinate)):return None
    # A gain at least the furthest cell radius saturates the whole valid cell.
    furthest=math.hypot(*(max(c,1-c) for c in centre))
    if gain>=furthest:return None
    matrix=None;offsets=None;rank=None;conditions=[]
    try:
        m,offsets=affine_uv_map(coordinate)
        # Exact rank of the exported nominal binary64 coefficients. Do not use
        # an SVD tolerance as proof that a thin but invertible mapping is rank1.
        rows=[[Fraction.from_float(float(c)) for c in row] for row in m]
        rank=2 if any(rows[0][i]*rows[1][j]!=rows[0][j]*rows[1][i]
                      for i in range(4) for j in range(i+1,4)) else 1 if any(c for row in rows for c in row) else 0
        if rank<2:return None
        matrix=m.tolist()
    except (ValueError,RecursionError):conditions.append('Grid mapping is not a supported constant-affine UV map; final dimensionality remains unresolved')
    program=_expression(node);mapping=_expression(coordinate)
    if program is None or mapping is None:return None
    clipped=gain>min(*(min(c,1-c) for c in centre))
    routes=[]
    for axis,phase in zip('xy',phases):routes+=_routes('grid_phase_'+axis,'grid cell coordinate',phase,analysis)
    # Native sin/cos/etc phase controls remain source programs where time-only
    # curve extraction cannot separate the spatial terms from their offsets.
    motion=[]
    for axis,phase,offset in zip('xy',phases,offsets if offsets is not None else phases):
        motion.append(motion_control(offset,'grid_phase_'+axis,'grid cell coordinate',application='procedural field mapping offset'))
    return {'policy':'source-periodic-radial-glow-v1','id':'grid_'+_digest(program),
        'form_code':9,'record_semantics':'canonical contributing generator formula within parent element; not usage or layer count',
        'generator':'saturate(gain / length(frac(mapping)-cell_centre))',
        'generator_expression':program,'mapping_expression':mapping,'cell_centre':centre,
        'radial_gain':gain,'core_radius_cell_units':gain,'core_clipped_by_cell':clipped,
        'core_disk_area_per_cell':None if clipped else math.pi*gain*gain,
        'mapping_matrix_uv4':matrix,'mapping_rank_uv4':rank,
        'mapping_rank_basis':'exact rank of exported nominal coefficient matrix; GPU precision/projection not certified',
        'phase_motion_controls':motion,'audio_routes':routes,
        'actual_screen_coverage':None,'visible_motion_speed':None,'appearance_guaranteed':False,
        'conditions':['Generator facts describe the raw scalar before masks, tint, inversion, clipping and composition',
                      'Nominal generator-plane formulas omit GPU rounding, interpolation and subnormal handling',
                      'Cell-area formula is in the generator plane, not a fraction of visible screen pixels',
                      'Finite mapping inputs and usable reciprocal domains are required; the exact zero-distance sample is not certified',
                      'No independent particles, final spot count, brightness, flashing or mood label is established']+conditions}
