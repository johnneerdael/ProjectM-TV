"""Nominal affine texture lookup maps, preserving mesh/original coordinate bases."""
import math
import numpy as np


def affine_uv_map(field,*,basis_name='_uv'):
    """Split two coordinates into constant _uv coefficients and uniform offsets.

    This is algebra on the source graph, not floating-point shader execution.
    Reject image/spatial-dependent offsets, dynamic scale and quantized spatial
    inputs rather than exporting an incorrect global transform.
    """
    from shader_fields import Field
    from field_math import SWIZZLE
    from effect_families import _parts,_walk
    from source_appearance import _canonical_lane,_phase_literal
    zero=Field('constant',dtype='float',detail={'value':0.})
    memo={};active=set()

    def uniform(node):
        for child,path in _walk(node):
            if child.op in {'sample','unknown','uninitialized'} or child.op.startswith('loop_'):return False
            if child.op=='input' and child.detail.get('name') in {basis_name,'_uv','_uv_orig','_rad_ang','_vDiffuse','x','y','rad','ang'}:return False
        return True

    def scale(pair,k):
        weights,offset=pair
        return weights*k,Field('multiply',(offset,Field('constant',dtype='float',detail={'value':k})),'float')

    def visit(node,depth=0):
        if depth>64 or len(memo)+len(active)>=4096:raise ValueError('coordinate graph budget exceeded')
        key=id(node)
        if key in memo:return memo[key]
        if key in active:raise ValueError('coordinate graph cycle unresolved')
        active.add(key)
        try:result=calculate(_canonical_lane(node),depth)
        finally:active.remove(key)
        if not np.all(np.isfinite(result[0])):raise ValueError('coordinate coefficients are nonfinite')
        memo[key]=result;return result

    def calculate(node,depth):
        if node.op=='member' and node.dtype=='float' and node.detail.get('swizzle') and len(node.detail.get('field',''))==1:
            parent=node.args[0]
            if parent.op=='input' and parent.dtype in {'float2','float4'} and parent.detail.get('name')==basis_name:
                weights=np.zeros(4);weights[SWIZZLE[node.detail['field']]]=1.
                return weights,zero
            if parent.op!='input':
                lane=SWIZZLE[node.detail['field']];parts=_parts(parent)
                if lane<len(parts):
                    projected=parts[lane]
                    if not (projected.op=='member' and projected.args and projected.args[0] is parent):
                        return visit(projected,depth+1)
        if uniform(node):return np.zeros(4),node
        if node.dtype!='float':raise ValueError('spatial coordinate conversion is not continuous float arithmetic')
        if node.op in {'cast','narrow','construct','components'} and len(node.args)==1:
            if node.args[0].dtype!='float':raise ValueError('spatial numeric conversion is unresolved')
            return visit(node.args[0],depth+1)
        if node.op=='negate' or node.op=='unary' and node.detail.get('operator')==0:
            return scale(visit(node.args[0],depth+1),-1.)
        if node.op=='unary' and node.detail.get('operator')==1:return visit(node.args[0],depth+1)
        if node.op in {'add','subtract'}:
            a=visit(node.args[0],depth+1);b=visit(node.args[1],depth+1)
            sign=1. if node.op=='add' else -1.
            return a[0]+sign*b[0],Field(node.op,(a[1],b[1]),'float')
        if node.op in {'multiply','divide'}:
            a,b=node.args;ka=_phase_literal(a);kb=_phase_literal(b)
            if node.op=='multiply':
                if ka is not None:return scale(visit(b,depth+1),ka)
                if kb is not None:return scale(visit(a,depth+1),kb)
            elif kb is not None and kb!=0:return scale(visit(a,depth+1),1./kb)
        raise ValueError('coordinate is not supported constant-affine UV plus uniform offset')

    parts=_parts(field)
    if len(parts)!=2:raise ValueError('texture coordinates are not two-dimensional')
    values=[visit(part) for part in parts]
    return np.array([v[0] for v in values]),[v[1] for v in values]


def sampling_geometry(analysis):
    from effect_families import _walk
    from source_appearance import _phase_literal,_expression,_routes
    from source_motion import motion_control
    from source_polar import polar_projection
    stages={};statuses={}
    for stage in ('warp','composite'):
        field=analysis.outputs.get(stage)
        if field is None:
            stages[stage]=None;statuses[stage]='native or unresolved stage; shader map not extracted';continue
        maps=[];seen=set()
        for node,path in _walk(field):
            if node.op!='sample' or id(node) in seen:continue
            seen.add(id(node))
            result={'sample_site_index':node.detail.get('site_index'),
                'sampler':node.detail.get('sampler'),'canonical_texture':node.detail.get('canonical_texture'),
                'sampling_policy':node.detail.get('sampling_policy'),
                'source_graph_path':path,'coordinate_expression':_expression(node.args[0]),
                'matrix_uv4':None,'offset_uv':None,'offset_expressions':None,'offset_controls':[],
                'audio_routes':[],'basis':None,'native_mesh_transform_precedes_basis':None,
                'determinant':None,'orientation_reversed':None,'inverse_matrix':None,
                'inverse_offset_uv':None,'nominal_feature_area_ratio':None,
                'visible_screen_motion':None,'unknown_reasons':[],
                'polar_projection':polar_projection(node.args[0],analysis)}
            try:
                matrix,offsets=affine_uv_map(node.args[0])
                result['matrix_uv4']=matrix.tolist()
                result['offset_uv']=[_phase_literal(v) for v in offsets]
                result['offset_expressions']=[_expression(v) for v in offsets]
                for axis,v in zip('xy',offsets):
                    result['offset_controls'].append(motion_control(v,'sample_offset_'+axis,'source texture UV',application='texture sampling offset'))
                    result['audio_routes']+=_routes('sample_offset_'+axis,'source texture UV',v,analysis)
                xy=bool(np.any(matrix[:,:2]!=0));zw=bool(np.any(matrix[:,2:]!=0))
                result['basis']='mixed_uv' if xy and zw else 'shader_uv' if xy else 'original_uv' if zw else 'uniform_lookup'
                if result['basis'] in {'shader_uv','original_uv'}:
                    result['native_mesh_transform_precedes_basis']=stage=='warp' and xy
                    m=matrix[:,:2] if xy else matrix[:,2:]
                    determinant=float(np.linalg.det(m))
                    if not math.isfinite(determinant):raise ValueError('coordinate determinant is nonfinite')
                    result['determinant']=determinant
                    result['orientation_reversed']=determinant<0 if determinant!=0 else None
                    if determinant!=0:
                        inverse=np.linalg.inv(m);area=abs(1./determinant)
                        if np.all(np.isfinite(inverse)) and math.isfinite(area):
                            result['inverse_matrix']=inverse.tolist();result['nominal_feature_area_ratio']=area
                            if all(v is not None for v in result['offset_uv']):
                                translation=-inverse@np.array(result['offset_uv'])
                                if np.all(np.isfinite(translation)):result['inverse_offset_uv']=translation.tolist()
                elif result['basis']=='mixed_uv':result['unknown_reasons'].append('mixed mesh/original coordinates have no single-basis inverse')
            except (ValueError,RecursionError,np.linalg.LinAlgError) as error:
                result['unknown_reasons'].append(str(error))
            maps.append(result)
        stages[stage]=maps;statuses[stage]='conditional custom source'
    return {'policy':'source-affine-sampling-geometry-v1','stages':stages,'stage_status':statuses,
        'input_column_order':['_uv.x','_uv.y','_uv.z','_uv.w'],
        'coordinate_unit':'source texture UV','uses_rendered_images':False,
        'uses_equation_execution':False,'uses_shader_execution':False,
        'conditions':['Matrices describe authored nominal real-valued arithmetic, not GPU interpolation/rounding',
            'Sampling maps pull source content into output; the inverse locates an isolated texture feature',
            'Area ratio is local in the declared coordinate basis, not screen coverage or projected pixel area',
            'Warp shader UV already includes the native mesh; original UV bypasses it; composite aliases both to xy',
            'Texture wrap/filter, clipping, masks, colour weights, seed/history and later stages determine actual copies',
            'No texture content, final geometry trajectory, repeated-layer count or visible motion is certified']}
