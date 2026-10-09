"""Nominal affine RGB mixtures of texture samples, not final scene appearance."""
import math
import numpy as np


def texture_colour_transfer(analysis,warp_vertex):
    from source_advection import substitute_sample_values
    from source_sampling import _affine_basis_map
    from source_appearance import _data_return,_phase_literal,_expression
    from source_polar import _nodes
    stages={}
    for stage in ('warp','composite'):
        result={'source_model':'unknown','base_uv_matrix_rgb':None,'constant_offset_rgb':None,
                'offset_expressions':None,'sample_contributions':[],'direct_colour_gain_norm':None,
                'source_mixture_kind':None,'coordinate_sample_dependency':None,
                'full_colour_sensitivity':None,'actual_sharpness':None,'actual_feedback_persistence':None,
                'final_palette_verified':False,'unknown_reasons':[]}
        field=analysis.outputs.get(stage)
        if field is None:
            result['unknown_reasons']=['native or unresolved stage has no authored RGB transfer'];stages[stage]=result;continue
        try:
            replaced,samples=substitute_sample_values(_data_return(field),known_vertex=warp_vertex if stage=='warp' else None)
            matrix,offsets=_affine_basis_map(replaced,('_uv',)+tuple(name for name,sample in samples),output_width=3)
            weights=[];textures=set();dependency=False
            for i,(name,sample) in enumerate(samples):
                m=matrix[:,4+4*i:8+4*i]
                if not np.any(m!=0):continue
                texture=sample.detail.get('canonical_texture');textures.add(texture);weights.append(m)
                nodes=list(_nodes(sample.args[0]))
                if any(n.op=='sample' for n,p in nodes):dependency=True
                elif dependency is not True and any(n.op in {'unknown','uninitialized'} or n.op.startswith('loop_') for n,p in nodes):dependency=None
                result['sample_contributions'].append({'sample_site_index':sample.detail['site_index'],
                    'sampler':sample.detail.get('sampler'),'canonical_texture':texture,'matrix_rgb_rgba':m.tolist(),
                    'coordinate_expression':_expression(sample.args[0]),'sampling_policy':sample.detail.get('sampling_policy')})
            norm=max((sum(abs(m[row,column]) for m in weights for column in range(4)) for row in range(3)),default=0.)
            if not math.isfinite(norm):raise ValueError('RGB sample norm is nonfinite')
            has_blur=bool(textures&{'blur1','blur2','blur3'})
            mixture='signed_main_blur_mix' if 'main' in textures and has_blur and any(np.any(m<0) for m in weights) else                     'nonnegative_main_blur_mix' if 'main' in textures and has_blur else 'other_affine_source_mix'
            result.update(source_model='affine_sample_colour',base_uv_matrix_rgb=matrix[:,:4].tolist(),
                constant_offset_rgb=[_phase_literal(o) for o in offsets],offset_expressions=[_expression(o) for o in offsets],
                direct_colour_gain_norm=float(norm),source_mixture_kind=mixture,coordinate_sample_dependency=dependency)
        except (ValueError,RecursionError) as error:
            result['sample_contributions']=[];result['unknown_reasons']=[str(error)]
        stages[stage]=result
    return {'policy':'source-affine-texture-colour-transfer-v1','stages':stages,
        'scope':'raw selected-stage RGB before storage and later drawing/composition',
        'observed_runtime_bindings':False,'uses_rendered_images':False,
        'uses_equation_execution':False,'uses_shader_execution':False,
        'conditions':['Source coefficients hold sample locations fixed and describe nominal real-valued arithmetic, not GPU rounding',
                      'Main/blur mixture signs do not prove spatial sharpening or softness without matching kernels, history and coordinates',
                      'Different sample sites remain independent; cancellation across different locations is not an absence proof',
                      'Storage, clipping, masks, feedback, image-driven coordinates and native detail can change the final scene',
                      'No complete palette, whole-loop gain, perceived brightness, flashing or mood confidence is certified']}
