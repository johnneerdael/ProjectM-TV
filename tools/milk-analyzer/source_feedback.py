"""Nominal warp colour transfer, not full feedback/stored-image dynamics."""
import math
import numpy as np


def feedback_transfer(analysis):
    from effect_families import _parts,_walk
    from source_appearance import _phase_literal,_canonical_lane,_data_return,_expression
    from field_math import SWIZZLE
    result={'policy':'source-warp-colour-transfer-v1',
        'scope':'selected warp RGB before storage/drawing/detail, holding sample coordinates fixed',
        'source_model':'unknown','matrix_rgb':None,'constant_offset_rgb':None,
        'direct_colour_gain_norm':None,'uniform_diagonal_gain':None,
        'nominal_half_life_warp_evaluations':None,'source_sample_sites':None,
        'coordinate_feedback_dependency':None,'sample_contributions':[],
        'actual_feedback_persistence':None,'unknown_reasons':[],
        'conditions':['Custom source must remain selected and execute in valid input/sample domains',
                      'Colour weights hold sampling coordinates fixed; image-driven coordinates can add nonlinear response',
                      'Nominal half life excludes UNORM storage/rounding, clipping, source injection, blur, motion vectors and authored/native detail',
                      'Composite/display gain is not included; stale/discard feedback remains unresolved'],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False}
    selection=analysis.stages['warp'];field=analysis.outputs.get('warp')
    if selection['kind']=='fixed_warp':
        decay=getattr(analysis,'main',{}).get('decay');value=None if decay is None else _phase_literal(decay)
        if value is None:
            result['unknown_reasons']=['fixed warp decay is not a supported constant'];return result
        with np.errstate(over='ignore',invalid='ignore'):gain=float(np.float32(value))
        if not math.isfinite(gain):
            result['unknown_reasons']=['nonfinite native decay conversion'];return result
        gain=min(gain,1.);matrix=np.eye(3)*gain;bias=np.zeros(3);norm=abs(gain)
        sites=1;dependent=False;result['source_model']='fixed_main_decay'
    elif field is not None:
        samples={};memo={};active=set()
        def visit(node):
            key=id(node)
            if key in memo:return memo[key]
            if key in active or len(memo)+len(active)>=4096:raise ValueError('warp transfer graph budget/cycle unresolved')
            active.add(key)
            try:value=calculate(node)
            finally:active.remove(key)
            if not math.isfinite(value[0]) or any(not math.isfinite(c) for c in value[1].values()):
                raise ValueError('warp transfer coefficients are nonfinite')
            memo[key]=value;return value
        def calculate(node):
            node=_canonical_lane(node);literal=_phase_literal(node)
            if literal is not None:return literal,{}
            if node.op=='member' and node.dtype=='float' and node.detail.get('swizzle') and len(node.detail.get('field',''))==1:
                parent=node.args[0];lane=SWIZZLE[node.detail['field']]
                if parent.op=='sample' and parent.detail.get('canonical_texture')=='main' and lane<3:
                    site=parent.detail.get('site_index')
                    if site is None:raise ValueError('main sample site identity unresolved')
                    samples[site]=parent;return 0.,{(site,lane):1.}
            if node.op=='cast' and node.dtype=='float' and node.args[0].dtype=='float':return visit(node.args[0])
            if node.op not in {'add','subtract','multiply','divide'} or node.dtype!='float':
                raise ValueError('warp RGB is not supported affine previous-main sample colour')
            a,at=visit(node.args[0]);b,bt=visit(node.args[1])
            if node.op in {'add','subtract'}:
                sign=1 if node.op=='add' else -1;terms=dict(at)
                for key,c in bt.items():terms[key]=terms.get(key,0)+sign*c
                return a+sign*b,terms
            if node.op=='divide':
                if bt or b==0:raise ValueError('warp transfer divisor is not a finite nonzero constant')
                return a/b,{key:c/b for key,c in at.items()}
            if at and bt:raise ValueError('nonlinear product of previous-main colour')
            return a*b,{**{key:c*b for key,c in at.items()},**{key:c*a for key,c in bt.items()}}
        try:
            lanes=[visit(node) for node in _parts(_data_return(field))[:3]]
            if len(lanes)!=3:raise ValueError('warp RGB lanes unresolved')
            matrices={site:np.zeros((3,3)) for site in samples}
            for row,(offset,terms) in enumerate(lanes):
                for (site,column),coefficient in terms.items():matrices[site][row,column]=coefficient
            matrices={site:m for site,m in matrices.items() if np.any(m!=0)}
            matrix=sum(matrices.values(),np.zeros((3,3)));bias=np.array([v[0] for v in lanes])
            norm=max((sum(abs(m[row,col]) for m in matrices.values() for col in range(3)) for row in range(3)),default=0.)
            sites=len(matrices);dependent=False
            for site,m in matrices.items():
                sample=samples[site]
                nodes=list(_walk(sample.args[0]))
                if any(n.op=='sample' and n.detail.get('canonical_texture') in {'main','blur1','blur2','blur3'} for n,p in nodes):dependent=True
                elif dependent is not True and any(n.op in {'unknown','uninitialized'} or n.op.startswith('loop_') for n,p in nodes):dependent=None
                result['sample_contributions'].append({'sample_site_index':site,'matrix_rgb':m.tolist(),
                    'coordinate_expression':_expression(sample.args[0]),'sampling_policy':sample.detail.get('sampling_policy')})
            result['source_model']='affine_previous_main_samples'
        except (ValueError,RecursionError) as error:
            result['unknown_reasons']=[str(error)];return result
        gain=float(matrix[0,0]) if sites<=1 and np.array_equal(matrix,np.eye(3)*matrix[0,0]) else None
    else:
        result['unknown_reasons']=['warp source/selection is unresolved'];return result
    if not np.all(np.isfinite(matrix)) or not np.all(np.isfinite(bias)) or not math.isfinite(norm):
        result['unknown_reasons']=['aggregate transfer is nonfinite'];return result
    result.update(matrix_rgb=matrix.tolist(),constant_offset_rgb=bias.tolist(),direct_colour_gain_norm=float(norm),
        uniform_diagonal_gain=gain,source_sample_sites=sites,coordinate_feedback_dependency=dependent)
    if gain is not None and 0<gain<1 and dependent is False:
        result['nominal_half_life_warp_evaluations']=math.log(.5)/math.log(gain)
    return result
