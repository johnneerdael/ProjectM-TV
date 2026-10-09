"""Direct sampled-colour coordinate coefficients, holding sample locations fixed."""
import math
import numpy as np
from shader_fields import Field


def sampled_coordinate_response(field):
    from source_sampling import _affine_basis_map
    from source_appearance import _expression,_phase_literal
    from source_polar import _nodes
    result={'policy':'source-direct-sampled-coordinate-response-v1','source_model':'unknown',
        'base_matrix_uv4':None,'offset_uv':None,'offset_expressions':None,
        'sample_contributions':[],'direct_sample_gain_norm':None,
        'conditional_sample_offset_range_uv':None,
        'range_premise':'each directly sampled RGBA component independently lies in [0,1]; not certified by source',
        'coordinate_sample_dependency':None,'full_coordinate_sensitivity':None,
        'visible_motion_speed':None,'observed_runtime_bindings':False,'unknown_reasons':[],
        'conditions':['Nominal source coefficients hold each sampled location fixed; no GPU interpolation/rounding is modeled',
                      'Sampling input bounds are an explicit premise, not an assertion about blur decoding or external textures',
                      'Image-dependent sample locations can add nonlinear response; their Jacobians remain unresolved',
                      'UV response is a sampling-map change, not a measured screen trajectory, speed, bass response or mood score'],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False}
    try:
        replaced,samples=substitute_sample_values(field)
        matrix,offsets=_affine_basis_map(replaced,('_uv',)+tuple(name for name,sample in samples))
        contributions=[];weights=[];dependency=False
        for index,(name,sample) in enumerate(samples):
            m=matrix[:,4+4*index:8+4*index]
            if not np.any(m!=0):continue
            nodes=list(_nodes(sample.args[0]))
            if any(n.op=='sample' for n,p in nodes):dependency=True
            elif dependency is not True and any(n.op in {'unknown','uninitialized'} or n.op.startswith('loop_') for n,p in nodes):dependency=None
            weights.append(m)
            contributions.append({'sample_site_index':sample.detail['site_index'],
                'sampler':sample.detail.get('sampler'),'canonical_texture':sample.detail.get('canonical_texture'),
                'matrix_uv_rgba':m.tolist(),'coordinate_expression':_expression(sample.args[0]),
                'sampling_policy':sample.detail.get('sampling_policy')})
        norm=max((sum(abs(m[row,column]) for m in weights for column in range(4)) for row in range(2)),default=0.)
        if not math.isfinite(norm):raise ValueError('coordinate response norm is nonfinite')
        # Bounds exclude base UV and uniform offsets; independent sample values
        # can be correlated in reality, which can tighten this conditional box.
        bounds=[[sum(min(0.,float(c)) for m in weights for c in m[row]),
                 sum(max(0.,float(c)) for m in weights for c in m[row])] for row in range(2)]
        if not all(math.isfinite(v) for row in bounds for v in row):raise ValueError('conditional sample bounds are nonfinite')
        result.update(source_model='affine_uv_and_sample_values',base_matrix_uv4=matrix[:,:4].tolist(),
            offset_uv=[_phase_literal(v) for v in offsets],offset_expressions=[_expression(v) for v in offsets],
            sample_contributions=contributions,direct_sample_gain_norm=float(norm),
            conditional_sample_offset_range_uv=bounds,coordinate_sample_dependency=dependency)
    except (ValueError,RecursionError) as error:result['unknown_reasons']=[str(error)]
    return result


def substitute_sample_values(field,*,known_vertex=None):
    """Share typed sample inputs without inventing texture values or bindings."""
    samples=[];memo={}
    def substitute(node,depth=0):
        if depth>64 or len(memo)>=4096:raise ValueError('coordinate sample substitution budget exceeded')
        if id(node) in memo:return memo[id(node)]
        if known_vertex is not None and node.op=='input' and node.dtype=='float4' and node.detail.get('name')=='_vDiffuse':
            components=[]
            for i,value in enumerate(known_vertex):
                components.append(Field('constant',dtype='float',detail={'value':value}) if value is not None else
                    Field('member',(node,),'float',{'field':'xyzw'[i],'swizzle':True}))
            value=Field('components',tuple(components),'float4')
        elif node.op=='sample':
            if node.dtype!='float4' or node.detail.get('site_index') is None:raise ValueError('sample value type/site identity is unresolved')
            if len(samples)>=64:raise ValueError('direct coordinate sample count exceeds 64-input budget')
            name=':coordinate-sample-'+str(len(samples));samples.append((name,node))
            value=Field('input',dtype='float4',detail={'name':name})
        else:
            value=Field(node.op,tuple(substitute(arg,depth+1) for arg in node.args),node.dtype,node.detail)
            if known_vertex is not None and value.op=='member' and value.detail.get('swizzle') and value.args[0].op=='components':
                from field_math import SWIZZLE
                chosen=tuple(value.args[0].args[SWIZZLE[c]] for c in value.detail['field'])
                value=chosen[0] if len(chosen)==1 else Field('components',chosen,value.dtype)
        memo[id(node)]=value;return value
    return substitute(field),samples
