"""Logical source composition/dataflow, with render-context branches unresolved."""


def composition_from_analysis(analysis,elements):
    from effect_families import _walk
    from source_appearance import _phase_literal,_expression,_digest
    from scene_equations import _scalar
    configured=[]
    for i in range(4):
        prefix=f'shapecode_{i}_'
        if _scalar(analysis.values,prefix+'enabled',0,'bool') and _scalar(analysis.values,prefix+'num_inst',1,'int')>0:
            configured.append('shape_'+str(i))
    for i in range(4):
        if _scalar(analysis.values,f'wavecode_{i}_enabled',0,'bool'):configured.append('wave_'+str(i))
    alpha=getattr(analysis,'main',{}).get('wave_a')
    if alpha is None or _phase_literal(alpha)!=0:configured.append('builtin_wave')
    reads={};status={}
    for stage in ('warp','composite'):
        field=analysis.outputs.get(stage);selection=analysis.stages[stage]
        if field is None:
            if selection['kind'] in {'fixed_warp','legacy_composite','default_composite'}:
                reads[stage]=[{'sampler':'native_main','canonical_texture':'main',
                    'source_role':'previous_main' if stage=='warp' else 'current_warp_with_draws',
                    'coordinate_expression':None,'frame_age':None,'basis':'selected native fixed/legacy stage'}]
                status[stage]='native stage under declared engine contract'
            else:
                reads[stage]=None;status[stage]='unresolved stage source/selection'
            continue
        items=[];seen=set()
        for node,path in _walk(field):
            if node.op!='sample':continue
            texture=node.detail.get('canonical_texture')
            role=('previous_main' if stage=='warp' else 'current_warp_with_draws') if texture=='main' else \
                 'blur_history' if texture in {'blur1','blur2','blur3'} else 'procedural_or_external_texture'
            item={'sampler':node.detail.get('sampler'),'canonical_texture':texture,
                  'source_role':role,'coordinate_expression':_expression(node.args[0]),
                  'extra_argument_expressions':[_expression(arg) for arg in node.args[1:]],
                  'sample_site_index':node.detail.get('site_index'),'source_graph_path':path,
                  'intrinsic':node.detail.get('intrinsic'),'lod_effect':node.detail.get('lod_effect'),
                  'sampling_policy':node.detail.get('sampling_policy'),
                  'frame_age':None,'basis':'source sample dependency, conditional on source interpretation and custom-stage selection'}
            key=_digest(item)
            if key not in seen:items.append(item);seen.add(key)
        reads[stage]=items;status[stage]='conditional custom source'
    warp=analysis.stages['warp']
    discard='possible_or_unresolved' if warp.get('source_contains_clip') or warp['kind']=='unknown' else 'not_independently_certified'
    return {'policy':'source-logical-composition-v1','render_context_resolved':False,
        'normal_feedback_flow':['previous_main','warp','drawing_and_filters','retained_main'],
        'normal_display_flow':['retained_main','flip_or_diffusion_exact_copy','composite','display'],
        'configured_drawing_order':configured,
        'display_elements':[name for name in configured if name in elements],
        'shader_sample_reads':reads,'stage_read_status':status,
        'pre_warp_operations':['motion_vectors_on_previous_main_if_not_first_frame',
                               'main_orientation_or_diffusion_preparation',
                               'blur_update_before_or_after_warp_depending_on_blur_reads'],
        'post_drawing_operations':['darken_center_if_enabled','borders'],
        'feedback_detail_path':'conditional_on_render_context',
        'warp_discard_or_incomplete_write':discard,
        'composite_feedback_influence':'normally_display_only_but_stale_pixels_may_feed_back',
        'conditions':['Normal logical flow assumes full-frame writes and usable source input domains',
                      'Configured drawing candidates need opacity/audio/termination/projection to contribute',
                      'Native authored/detail/diffusion paths, motion vectors, blur timing and warp discard alter state/edges',
                      'Custom samples are source dependencies, not certified actual texture-unit bindings'],
        'unknown_reasons':['Render size, trails/detail/diffusion configuration and initial/history textures are not supplied',
                           'No complete material/blend graph, screen dominance or recurrence solution is established'],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False}
