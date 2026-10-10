"""Source polar texture projections; geometry parameters are conditional facts."""
import math
import numpy as np
from shader_fields import Field


def _nodes(field):
    """Bound this descriptor independently rather than consuming family visits."""
    from effect_families import _children
    pending=[(field,'coordinate')];seen=set()
    while pending:
        node,path=pending.pop()
        if id(node) in seen:continue
        if len(seen)>=4096:raise ValueError('polar coordinate traversal budget exceeded')
        seen.add(id(node));yield node,path
        pending.extend((child,path+'/'+node.op) for child in _children(node))


def _plane_program(plane):
    from effect_families import _parts
    from source_appearance import _canonical_lane,_expression
    from field_math import SWIZZLE
    memo={}
    def canonical(node,depth=0):
        if depth>64 or len(memo)>=4096:raise ValueError('polar plane normalization budget exceeded')
        if id(node) in memo:return memo[id(node)]
        n=_canonical_lane(node)
        if n.op=='member' and n.detail.get('swizzle') and len(n.detail.get('field',''))==1:
            parent=n.args[0]
            if parent.op!='input':
                lane=SWIZZLE[n.detail['field']];parts=_parts(parent)
                if lane<len(parts):
                    candidate=parts[lane]
                    if not (candidate.op=='member' and candidate.args and candidate.args[0] is parent):
                        result=canonical(candidate,depth+1);memo[id(node)]=result;return result
        result=Field(n.op,tuple(canonical(a,depth+1) for a in n.args),n.dtype,n.detail)
        memo[id(node)]=result;return result
    parts=_parts(plane)
    if len(parts)!=2:return None
    expression=_expression(Field('components',tuple(canonical(p) for p in parts),'float2'))
    return expression if expression is not None and expression['complete'] else None


def _atoms_affine(field,atoms):
    from source_appearance import _canonical_lane,_typed_control_identity
    from source_sampling import affine_uv_map
    identities=[_typed_control_identity(atom,required=True) for atom in atoms];memo={}
    markers=[Field('member',(Field('input',dtype='float4',detail={'name':':polar-atoms'}),),
                   'float',{'field':'xyzw'[i],'swizzle':True}) for i in range(len(atoms))]
    def replace(node,depth=0):
        if depth>64 or len(memo)>=4096:raise ValueError('polar substitution budget exceeded')
        if id(node) in memo:return memo[id(node)]
        canonical=_canonical_lane(node)
        for atom,identity,marker in zip(atoms,identities,markers):
            if node is atom or canonical.op==atom.op and canonical.dtype==atom.dtype and _typed_control_identity(canonical)==identity:
                memo[id(node)]=marker;return marker
        result=Field(node.op,tuple(replace(a,depth+1) for a in node.args),node.dtype,node.detail)
        memo[id(node)]=result;return result
    matrix,offsets=affine_uv_map(replace(field),basis_name=':polar-atoms')
    if np.any(matrix[:,len(atoms):]!=0):raise ValueError('polar expression includes another spatial basis')
    return matrix[:,:len(atoms)],offsets


def _atom_affine(field,atom):
    zero=Field('constant',dtype='float',detail={'value':0.})
    matrix,offsets=_atoms_affine(Field('components',(field,zero),'float2'),(atom,))
    if np.any(matrix[1]!=0):raise ValueError('polar scalar projection is unresolved')
    return float(matrix[0,0]),offsets[0]


def _plane_radius_key(program):
    """Axis permutation preserves length; retain angle's ordered plane separately."""
    from source_appearance import _digest
    memo={}
    def key(index,depth=0):
        if depth>64:raise ValueError('polar plane identity budget exceeded')
        if index in memo:return memo[index]
        node=program['nodes'][index]
        result=_digest({'op':node['op'],'dtype':node['dtype'],'detail':node['detail'],
                        'args':[key(i,depth+1) for i in node['args']]})
        memo[index]=result;return result
    root=program['nodes'][program['root']]
    return _digest({'radius_axes':sorted(key(i) for i in root['args'])})


def _anchor(node):
    from source_appearance import _canonical_lane,_expression,_phase_literal,_digest
    from source_sampling import affine_uv_map
    node=_canonical_lane(node)
    if node.op=='member' and node.detail.get('swizzle') and node.dtype=='float':
        parent=node.args[0]
        if parent.op=='input' and parent.dtype=='float2' and parent.detail.get('name')=='_rad_ang':
            lane=node.detail.get('field')
            if lane in {'x','r','y','g'}:
                return ('radius' if lane in {'x','r'} else 'angle','native_rad_ang',
                        {'kind':'native_rad_ang','centre_in_basis_uv':None,
                         'conditions':['Native original-position radius/angle includes target aspect/projection and interpolation; no direct shader-UV metric is supplied']})
    if node.op=='atan2':
        plane=Field('components',(node.args[1],node.args[0]),'float2');kind='angle'
    elif node.op=='length':plane=node.args[0];kind='radius'
    elif node.op=='distance':plane=Field('subtract',node.args,node.args[0].dtype);kind='radius'
    else:return None
    program=_plane_program(plane)
    if program is None:return None
    try:matrix,offsets=affine_uv_map(plane)
    except (ValueError,RecursionError):
        from effect_families import SPATIAL
        if not any(n.op=='input' and n.detail.get('name') in SPATIAL for n,p in _nodes(plane)):return None
        return kind,_plane_radius_key(program),{'kind':'authored_plane_program',
            'plane_expression':program,'matrix_uv4':None,'offset_uv':None,'basis':None,
            'centre_in_basis_uv':None,'conditions':['The angle and radius share this exact source plane program; its nonlinear/dynamic metric and centre remain unresolved']}

    if not np.any(matrix!=0):return None
    constants=[_phase_literal(o) for o in offsets]
    programs=[_expression(o) for o in offsets]
    # Unexportable offsets cannot establish equivalent spatial anchors.
    if any(o is None for o in programs):return None
    identity=_digest({'radius_axes':sorted(_digest({'matrix_row':row.tolist(),'offset':v if v is not None else p}) for row,v,p in zip(matrix,constants,programs))})
    xy=bool(np.any(matrix[:,:2]!=0));zw=bool(np.any(matrix[:,2:]!=0))
    basis='mixed_uv' if xy and zw else 'shader_uv' if xy else 'original_uv'
    result={'kind':'authored_affine_plane','plane_expression':program,'matrix_uv4':matrix.tolist(),
            'offset_uv':constants,'offset_expressions':programs,'basis':basis,
            'centre_in_basis_uv':None,'conditions':['Length and atan2 use this authored plane; anisotropic/sheared matrices alter the radius metric and angle geometry']}
    if basis!='mixed_uv' and all(v is not None for v in constants):
        m=matrix[:,:2] if xy else matrix[:,2:]
        try:centre=-np.linalg.solve(m,np.array(constants))
        except np.linalg.LinAlgError:pass
        else:
            if np.all(np.isfinite(centre)):result['centre_in_basis_uv']=centre.tolist()
    return kind,identity,result


def _offset(field,name,analysis,unit):
    from source_appearance import _phase_literal,_expression,_routes
    from source_motion import motion_control
    return {'offset_value':_phase_literal(field),'offset_expression':_expression(field),
            'offset_control':motion_control(field,name,unit,application='polar texture lookup control',input_scenario=getattr(analysis,'input_scenario',None)),
            'audio_routes':_routes(name,unit,field,analysis)}


def _angle_profile(field,atom,analysis):
    from effect_families import _walk
    from source_appearance import _phase_literal
    # Prefer explicit folded/wrapped kernels over affine-only phase formulas.
    for node,path in _nodes(field):
        if node.op!='abs':continue
        for wrapped,p in _nodes(node.args[0]):
            if wrapped.op!='frac':continue
            try:
                scale,bias=_atom_affine(node.args[0],wrapped)
                coefficient,phase=_atom_affine(wrapped.args[0],atom)
                out_scale,out_offset=_atom_affine(field,node)
            except ValueError:continue
            if abs(scale)!=2 or abs(_phase_literal(bias) or 0)!=1 or coefficient==0 or out_scale==0:continue
            # abs(2*frac-1) and abs(1-2*frac) are the supported triangular fold.
            if scale*_phase_literal(bias)!=-2:continue
            result={'function':'triangular_frac','input_scale':coefficient,'output_scale':out_scale,
                    'output_offset':_offset(out_offset,'angle_output_offset',analysis,'source texture UV'),
                    'angular_period_rad':abs(1./coefficient),'cycles_per_turn_nominal':abs(coefficient)*math.tau,
                    'exact_closed_turn_symmetry':None,'turn_span_uv':None,
                    'conditions':['Period is nominal source formula; shader precision and atan2 seam can prevent exact closed-turn symmetry']}
            result.update(_offset(phase,'angular_phase_offset',analysis,'wrap cycles'));return result
    for node,path in _nodes(field):
        if node.op!='frac':continue
        try:
            coefficient,phase=_atom_affine(node.args[0],atom)
            out_scale,out_offset=_atom_affine(field,node)
        except ValueError:continue
        if coefficient==0 or out_scale==0:continue
        result={'function':'frac','input_scale':coefficient,'output_scale':out_scale,
                'output_offset':_offset(out_offset,'angle_output_offset',analysis,'source texture UV'),
                'angular_period_rad':abs(1./coefficient),'cycles_per_turn_nominal':abs(coefficient)*math.tau,
                'exact_closed_turn_symmetry':None,'turn_span_uv':None,
                'conditions':['Wrapped angular formula can introduce a seam; final sampling and contents control appearance']}
        result.update(_offset(phase,'angular_phase_offset',analysis,'wrap cycles'));return result
    coefficient,offset=_atom_affine(field,atom)
    if coefficient==0:raise ValueError('angle cancels from projection')
    result={'function':'affine','input_scale':coefficient,'output_scale':1.,
            'turn_span_uv':abs(coefficient)*math.tau,'angular_period_rad':None,
            'cycles_per_turn_nominal':None,'exact_closed_turn_symmetry':None}
    result.update(_offset(offset,'angle_output_offset',analysis,'source texture UV'));return result


def _depth_profile(field,atom,analysis):
    from effect_families import _walk
    from source_appearance import _phase_literal
    for node,path in _nodes(field):
        kernel=node;guarded=False;absolute=False
        if node.op=='domain_checked' and node.args[0].op in {'log','log2','log10'}:
            kernel=node;node=node.args[0];guarded=True
        if node.op=='divide':
            numerator=_phase_literal(node.args[0])
            if numerator is None or numerator==0:continue
            argument=node.args[1];function='reciprocal'
        elif node.op in {'log','log2','log10'}:
            argument=node.args[0];numerator=1.;function=node.op
            if argument.op=='abs':argument=argument.args[0];absolute=True
        else:continue
        try:
            scale,bias=_atom_affine(argument,atom)
            output_scale,offset=_atom_affine(field,kernel)
        except ValueError:continue
        bias_value=_phase_literal(bias)
        if scale==0 or bias_value is None or output_scale==0:continue
        output_scale*=numerator
        result={'function':function,'radius_scale':scale,'radius_bias':bias_value,'output_scale':output_scale,
                'input_absolute':absolute,'domain_guard_retained':guarded,
                'domain_condition':'radius_scale*r+radius_bias != 0' if function=='reciprocal' else
                                   'abs(radius_scale*r+radius_bias) > 0' if absolute else 'radius_scale*r+radius_bias > 0'}
        coefficient=-output_scale*scale if function=='reciprocal' else output_scale*scale/(math.log(2) if function=='log2' else math.log(10) if function=='log10' else 1.)
        result['radial_derivative']={'coefficient':coefficient,'radius_scale':scale,'radius_bias':bias_value,
            'denominator_power':2 if function=='reciprocal' else 1,
            'unit':'source texture UV/authored radius unit','scope':'nominal derivative in valid source domains; not screen-space velocity'}
        result.update(_offset(offset,'depth_output_offset',analysis,'source texture UV'));return result
    scale,offset=_atom_affine(field,atom)
    if scale==0:raise ValueError('radius cancels from projection')
    result={'function':'affine_radius','radius_scale':1.,'radius_bias':0.,'output_scale':scale,'input_absolute':False,'domain_guard_retained':False,'domain_condition':'finite radius'}
    result['radial_derivative']={'coefficient':scale,'radius_scale':1.,'radius_bias':0.,'denominator_power':0,
        'unit':'source texture UV/authored radius unit','scope':'nominal derivative in valid source domains; not screen-space velocity'}
    result.update(_offset(offset,'depth_output_offset',analysis,'source texture UV'));return result


def _mixed_projection(field,angle,radius,analysis):
    from source_motion import motion_control
    from source_appearance import _expression,_phase_literal,_routes
    kernels=[n for n,path in _nodes(field) if n.op=='divide' or
             n.op=='domain_checked' and n.args[0].op in {'log','log2','log10'}]+[radius]
    for kernel in kernels:
        try:
            depth=_depth_profile(kernel,radius,analysis)
            matrix,offsets=_atoms_affine(field,(angle,kernel))
            if not np.any(matrix[:,0]!=0) or not np.any(matrix[:,1]!=0):continue
            if not math.isfinite(depth['radial_derivative']['coefficient']):continue
            angular=_angle_profile(angle,angle,analysis)
        except (ValueError,RecursionError):continue
        routes=[]
        for axis,offset in zip('xy',offsets):routes+=_routes('polar_sample_offset_'+axis,'source texture UV',offset,analysis)
        return {'kind':'mixed_angle_depth','coordinate_lanes':None,'angle':angular,'depth':depth,
                'polar_to_sample_matrix':matrix.tolist(),'sample_offset_uv':[_phase_literal(o) for o in offsets],
                'sample_offset_expressions':[_expression(o) for o in offsets],
                'sample_offset_controls':[motion_control(o,'polar_sample_offset_'+axis,'source texture UV',
                    application='mixed polar texture sampling offset',input_scenario=getattr(analysis,'input_scenario',None)) for axis,o in zip('xy',offsets)],
                'sample_offset_audio_routes':routes}
    return None


def _polar_projection(field,analysis):
    from effect_families import _parts
    result={'policy':'source-separable-polar-projection-v1','kind':'not_recognized',
            'coordinate_lanes':None,'shared_anchor':None,'angle':None,'depth':None,
            'polar_to_sample_matrix':None,'sample_offset_uv':None,'sample_offset_expressions':None,
            'sample_offset_controls':[],'sample_offset_audio_routes':[],
            'appearance_guaranteed':False,'unknown_reasons':[],
            'conditions':['Source projection needs selected RGB contribution, valid domains and appropriate sampling; authored atan2 excludes an undefined zero vector',
                          'No dominant tunnel, spiral, visible symmetry or feedback-layer count is certified']}
    parts=_parts(field)
    if len(parts)!=2:return result
    nodes=[list(_nodes(part)) for part in parts]
    def primitive(node,kind):
        if node.op in ({'atan2'} if kind=='angle' else {'length','distance'}):return True
        return (node.op=='member' and node.detail.get('swizzle') and node.args[0].op=='input' and
            node.args[0].detail.get('name')=='_rad_ang' and node.detail.get('field') in ({'y','g'} if kind=='angle' else {'x','r'}))
    angle_flags=[any(primitive(n,'angle') for n,p in row) for row in nodes]
    radius_flags=[any(primitive(n,'radius') for n,p in row) for row in nodes]
    candidate=(angle_flags[0] and radius_flags[1]) or (angle_flags[1] and radius_flags[0])
    if not candidate:return result
    result['kind']='unresolved'
    for angle_index in (0,1):
        depth_index=1-angle_index
        if not angle_flags[angle_index] or not radius_flags[depth_index]:continue
        angles=[];radii=[]
        for node,path in nodes[angle_index]:
            anchor=_anchor(node)
            if anchor is not None and anchor[0]=='angle':angles.append((node,anchor))
        for node,path in nodes[depth_index]:
            anchor=_anchor(node)
            if anchor is not None and anchor[0]=='radius':radii.append((node,anchor))
        for angle,a in angles:
            for radius,r in radii:
                if a[1]!=r[1]:continue
                try:
                    angular=_angle_profile(parts[angle_index],angle,analysis)
                    depth=_depth_profile(parts[depth_index],radius,analysis)
                    # Guard derived values against overflow before exporting JSON.
                    values=[angular['input_scale'],depth['output_scale'],depth['radius_scale'],depth['radius_bias'],depth['radial_derivative']['coefficient']]
                    values+=[angular[k] for k in ('angular_period_rad','cycles_per_turn_nominal','turn_span_uv') if angular[k] is not None]
                    if not all(math.isfinite(v) for v in values):raise ValueError('polar coefficients are nonfinite')
                except (ValueError,RecursionError):
                    mixed=_mixed_projection(field,angle,radius,analysis)
                    if mixed is not None:
                        result.update(mixed);result['shared_anchor']=a[2];return result
                    continue
                result.update(kind='separable_angle_depth',coordinate_lanes=['angle','depth'] if angle_index==0 else ['depth','angle'],
                              shared_anchor=a[2],angle=angular,depth=depth)
                return result
    result['unknown_reasons']=['no supported angle/depth formulas with the same proved spatial anchor']
    return result


def polar_projection(field,analysis):
    try:return _polar_projection(field,analysis)
    except (ValueError,RecursionError) as error:
        return {'policy':'source-separable-polar-projection-v1','kind':'unresolved',
                'coordinate_lanes':None,'shared_anchor':None,'angle':None,'depth':None,
            'polar_to_sample_matrix':None,'sample_offset_uv':None,'sample_offset_expressions':None,
            'sample_offset_controls':[],'sample_offset_audio_routes':[],
                'appearance_guaranteed':False,'unknown_reasons':[str(error)],
                'conditions':['Polar descriptor budget/input uncertainty does not establish a visible effect']}
