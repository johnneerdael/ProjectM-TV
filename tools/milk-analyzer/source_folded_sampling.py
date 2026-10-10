"""Explicit planar periodic coordinate folds; no rendered tile-count claims."""
import math
import numpy as np
from shader_fields import Field


def folded_coordinate_map(field,analysis):
    from effect_families import _parts
    from source_appearance import _canonical_lane,_phase_literal,_expression,_routes
    from source_periodic_sampling import uniform_affine_scalar
    from source_polar import _nodes,_atom_affine
    from source_forms import known_invalid_phase_offset
    result={'policy':'source-planar-periodic-folds-v1','source_model':'unknown','axes':[None,None],
        'phase_matrix_uv4':None,'phase_coefficient_programs':None,'basis':None,
        'repeat_lattice_basis_uv':None,'fundamental_cell_area_uv2':None,
        'actual_visible_copy_count':None,'visible_motion_speed':None,'unknown_reasons':[],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False,
        'conditions':['Nominal real-valued explicit frac/triangular source coordinate maps, under finite valid source domains',
                      'Uniform phase inputs held fixed; dynamic scales can collapse and have no constant inverse lattice',
                      'A repeat cell describes coordinate preimages, not displayed copies, kaleidoscopic appearance or mood',
                      'Mesh/original coordinates, clipping, texture content/filtering, colour and later feedback remain separate',
                      'Frac is phase-floor(phase), including negative phases; native rounding and seam coverage remain unqualified']}
    memo={};active=set()
    def scalar(original,depth=0):
        key=id(original)
        if key in memo:return memo[key][1]
        if depth>64 or len(memo)+len(active)>=512 or key in active:raise ValueError('fold scalar projection budget exceeded')
        active.add(key)
        try:
            node=_canonical_lane(original)
            if node.op=='member' and node.dtype=='float' and node.detail.get('swizzle') and len(node.detail.get('field',''))==1 and node.args[0].op!='input':
                from field_math import SWIZZLE
                parent=node.args[0];lane=SWIZZLE[node.detail['field']];parts=_parts(parent)
                if lane<len(parts) and not (parts[lane].op=='member' and parts[lane].args and parts[lane].args[0] is parent):
                    value=scalar(parts[lane],depth+1)
                else:value=Field(node.op,tuple(scalar(v,depth+1) for v in node.args),node.dtype,node.detail)
            else:value=Field(node.op,tuple(scalar(v,depth+1) for v in node.args),node.dtype,node.detail)
        finally:active.remove(key)
        memo[key]=(original,value);return value
    def axis(lane,index):
        pending=list(_nodes(lane));candidates=[]
        for node,path in pending:
            if node.op!='abs' or node.dtype!='float':continue
            for wrapped,p in _nodes(node.args[0]):
                if wrapped.op!='frac' or wrapped.dtype!='float':continue
                try:
                    k,b=_atom_affine(node.args[0],wrapped)
                    if abs(k)!=2 or _phase_literal(b) is None or k*_phase_literal(b)!=-2:continue
                    scale,offset=_atom_affine(lane,node)
                    candidates.append((wrapped,'triangular_frac',scale,offset))
                except (ValueError,RecursionError):continue
        for node,path in pending:
            if node.op=='frac' and node.dtype=='float':
                try:
                    scale,offset=_atom_affine(lane,node);candidates.append((node,'frac',scale,offset))
                except (ValueError,RecursionError):continue
        for wrapped,function,scale,offset in candidates:
            if scale==0:continue
            try:
                coefficients,phase_offset=uniform_affine_scalar(wrapped.args[0])
                if any(_phase_literal(v)!=0 for v in coefficients[4:]):continue
                constants=[_phase_literal(v) for v in coefficients[:4]]
                if all(v==0 for v in constants):continue
                programs=[_expression(v) for v in coefficients[:4]]
                phase=_expression(phase_offset);output=_expression(offset)
                if any(v is None for v in programs+[phase,output]):continue
            except (ValueError,RecursionError):continue
            return {'function':function,'phase_coefficients_uv4':constants if all(v is not None for v in constants) else None,
                'phase_coefficient_programs':programs,'phase_offset_value':_phase_literal(phase_offset),'phase_offset_expression':phase,
                'output_scale':scale,'output_offset_value':_phase_literal(offset),'output_offset_expression':output,
                'fold_output_range':[0,1],'fold_output_upper_endpoint_included':function=='triangular_frac',
                'derivative_wrt_phase_away_from_seams':[-2,2] if function=='triangular_frac' else [1,1],
                'continuous_nominal':function=='triangular_frac',
                'audio_routes':_routes('fold_phase_offset_'+str(index),'phase cycles',phase_offset,analysis)+
                    _routes('fold_output_offset_'+str(index),'source texture UV',offset,analysis)+
                    [route for j,c in enumerate(coefficients[:4]) for route in _routes('fold_phase_coefficient_'+str(index)+'_'+str(j),'phase cycles/source UV',c,analysis)]}
        return None
    try:
        if not any(n.op=='frac' for n,path in _nodes(field)):raise ValueError('no explicit frac coordinate kernel')
        parts=_parts(field)
        if len(parts)!=2:raise ValueError('folded lookup is not two-dimensional')
        axes=[axis(scalar(v),i) for i,v in enumerate(parts)]
        if not any(axes):raise ValueError('no supported explicit planar periodic fold')
        if known_invalid_phase_offset(field,preserve_zero_products=True):raise ValueError('folded source has a known invalid original domain')
        result.update(axes=axes,source_model='planar_periodic_folds' if all(axes) else 'partial_planar_periodic_folds',
            phase_coefficient_programs=[a['phase_coefficient_programs'] if a else None for a in axes])
        if not all(axes):return result
        rows=[a['phase_coefficients_uv4'] for a in axes]
        if any(row is None for row in rows):return result
        matrix=np.array(rows);xy=bool(np.any(matrix[:,:2]!=0));zw=bool(np.any(matrix[:,2:]!=0))
        basis='mixed_uv' if xy and zw else 'shader_uv' if xy else 'original_uv'
        result.update(phase_matrix_uv4=rows,basis=basis)
        if basis=='mixed_uv':return result
        m=matrix[:,:2] if xy else matrix[:,2:];det=float(np.linalg.det(m))
        if det==0 or not math.isfinite(det):return result
        inverse=np.linalg.inv(m);area=abs(1/det)
        if np.all(np.isfinite(inverse)) and math.isfinite(area):result.update(repeat_lattice_basis_uv=inverse.tolist(),fundamental_cell_area_uv2=area)
    except (ValueError,RecursionError,OverflowError,IndexError,np.linalg.LinAlgError) as error:result['unknown_reasons']=[str(error)]
    return result
