"""Analytic procedural form generators from contributing typed shader graphs."""
import math
from fractions import Fraction
from shader_fields import Field


def constant_colour_clip_children(node):
    """Prune only proved complete nominal clipping; retain ordinary unknowns."""
    from source_appearance import _phase_literal,_phase_terms
    if node.dtype!='float' or node.op not in {'saturate','clamp','min','max'}:return None
    def span(field):
        low=high=Fraction(0)
        try:
            for coefficient,term in _phase_terms(field):
                c=Fraction.from_float(coefficient);literal=_phase_literal(term)
                if literal is not None:
                    low+=c*Fraction.from_float(literal);high+=c*Fraction.from_float(literal)
                elif term.dtype=='float' and term.op in {'sin','cos'}:
                    low-=abs(c);high+=abs(c)
                elif term.dtype=='float' and term.op=='saturate':
                    low+=min(c,0);high+=max(c,0)
                else:return None
        except (ValueError,RecursionError,OverflowError):return None
        return low,high
    if node.op in {'saturate','clamp'}:
        limits=(0.,1.) if node.op=='saturate' else tuple(_phase_literal(v) for v in node.args[1:])
        if len(limits)!=2 or any(v is None for v in limits) or limits[0]>limits[1]:return None
        if limits[0]==limits[1]:return ()
        values=span(node.args[0])
        if values is not None and (values[1]<=Fraction.from_float(limits[0]) or values[0]>=Fraction.from_float(limits[1])):return ()
    elif len(node.args)==2:
        a,b=map(span,node.args)
        if a is not None and b is not None:
            if a[1]<=b[0]:return (node.args[0] if node.op=='min' else node.args[1],)
            if b[1]<=a[0]:return (node.args[1] if node.op=='min' else node.args[0],)
    return None


def known_invalid_phase_offset(field):
    """Reject known singular/overflow domains; unknown finite inputs stay conditional."""
    from effect_families import _walk
    from source_appearance import _phase_literal
    from source_control_bounds import scalar_value_envelope
    from source_native_warp import _f32
    for count,(node,path) in enumerate(_walk(field)):
        if count>=512:raise ValueError('spatial-band offset domain budget exceeded')
        if node.op=='divide' and len(node.args)==2 and _phase_literal(node.args[1])==0:return True
        if node.op in {'pow','sqrt','log','log2','log10','rsqrt'} and node.args:
            span=scalar_value_envelope(node.args[0])['nominal_value_range']
            if span is None:continue
            if node.op in {'log','log2','log10','rsqrt'} and span[1]<=0:return True
            if node.op=='sqrt' and span[1]<0:return True
            exponent=_phase_literal(node.args[1]) if node.op=='pow' and len(node.args)==2 else None
            if exponent is not None and span==[0.,0.] and exponent<=0:return True
        if node.op=='narrow' and node.detail.get('numeric_domain')=='shader-float32':
            span=scalar_value_envelope(node.args[0])['nominal_value_range']
            if span is not None:
                try:
                    for value in span:_f32(value)
                except ValueError:return True
    return False


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


def spatial_oscillatory_band(node,analysis):
    """Recognize a constant-affine spatial phase, not its final screen effect."""
    from source_sampling import _affine_basis_map
    from source_appearance import _expression,_digest,_routes
    from source_motion import motion_control
    from effect_families import _deps
    if node.op not in {'sin','cos'} or node.dtype!='float' or len(node.args)!=1:return None
    phase=node.args[0];basis=None;coefficients=None;offset=None;normal=None
    dependencies=_deps(phase)
    for name in ('_uv','_rad_ang'):
        if name not in dependencies:continue
        try:matrix,offsets=_affine_basis_map(phase,(name,),output_width=1)
        except (ValueError,RecursionError):continue
        c=matrix[0].tolist()
        if name=='_uv':
            xy=any(v!=0 for v in c[:2]);zw=any(v!=0 for v in c[2:])
            if xy==zw:continue # Uniform or mixed bases have no single UV spacing.
            k=c[:2] if xy else c[2:];norm=math.hypot(*k)
            if not math.isfinite(norm) or norm==0:continue
            basis='shader_uv' if xy else 'original_uv';normal=[v/norm for v in k]
            construction='planar_oscillatory_bands'
        else:
            if c[0]==0 or any(v!=0 for v in c[1:]):continue
            norm=abs(c[0]);basis='native_radial_varying'
            construction='native_radius_oscillatory_bands'
        period=math.tau/norm
        if not math.isfinite(period) or period<=0:continue
        coefficients=c;offset=offsets[0];break
    if basis is None or known_invalid_phase_offset(offset):return None
    program=_expression(node);phase_program=_expression(phase)
    if program is None or phase_program is None:return None
    return {'policy':'source-spatial-oscillatory-bands-v1','id':'band_'+_digest(program),
        'form_code':10,'record_semantics':'canonical contributing generator formula within parent element; not usage or layer count',
        'construction':construction,'generator':node.op+'(spatial_phase+uniform_phase)',
        'generator_expression':program,'phase_expression':phase_program,'basis':basis,
        'phase_coefficients':coefficients,'phase_coefficient_unit':'radians/declared basis unit',
        'phase_normal_uv':normal,'nominal_period_in_basis_units':period,
        'period_unit':'source texture UV along phase normal' if normal is not None else 'native radial varying unit',
        'phase_motion_control':motion_control(offset,'band_phase','radian',application='raw spatial-band phase offset'),
        'audio_routes':_routes('band_phase','radian',offset,analysis),
        'actual_screen_coverage':None,'visible_motion_speed':None,'appearance_guaranteed':False,
        'conditions':['Source sine/cosine generator reaches live RGB; usage/mask/colour transfer and dominance are separate',
                      'Spacing and orientation use nominal constant-affine source phase, before GPU precision and interpolation',
                      'UV phase normal is in the declared basis, not a physical screen normal after mesh/aspect/projection',
                      'Native radius is the supplied radial varying; triangulation and target projection do not prove exact circles',
                      'Uniform phase inputs and source domains must be usable; time wraps, native narrowing and audio timing remain separate',
                      'Masks, thresholding, inversion, products and feedback can alter or suppress the raw bands; no ring count or mood label is established']}
