"""Pointwise nonlinear sampled-colour offsets, not image-gradient dynamics."""


def sample_value_offset_envelope(field,*,input_scenario=None):
    from effect_families import _parts,_deps
    from source_advection import substitute_sample_values
    from source_periodic_sampling import uniform_affine_scalar
    from source_ripple_envelopes import coefficient_envelope
    from source_appearance import _phase_literal,_expression
    from source_polar import _nodes
    from source_forms import known_invalid_phase_offset
    result={'policy':'source-nonlinear-sample-offset-envelope-v1','source_model':'unknown',
        'offset_range_uv':None,'offset_value_envelopes':None,'base_coefficient_programs':None,
        'offset_programs':None,'sample_textures':[],'sample_sites':[],
        'coordinate_sample_dependency':None,'full_coordinate_sensitivity':None,
        'actual_feedback_persistence':None,'visible_motion_intensity':None,'unknown_reasons':[],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False,
        'conditions':['Each directly sampled RGBA lane independently lies in [0,1]; this image-input premise is not observed or certified',
                      'Sample values are local independent parameters for pointwise source algebra, not spatially uniform images',
                      'Spatial coefficients must not depend on sampled values; only the residual offset is bounded',
                      'Ranges include non-image uniform offsets and require their finite/domain premises; baseline mapping is excluded',
                      'Sampling gradients, coordinates/history, filtering/decoding, texture bindings and native precision remain separate',
                      'No global motion, whole-feedback stability, displayed structure, flashing or mood certificate follows']}
    scenario_result=None
    if input_scenario is not None:
        scenario_result={'source_model':'unknown','offset_range_uv':None,'offset_value_envelopes':None,
            'input_scenario_sha256':input_scenario['record_sha256'],'unknown_reasons':[],
            'observed_runtime_inputs':False,'runtime_binding_verified':False}
        result['scenario_offset_envelope']=scenario_result
    try:
        replaced,samples=substitute_sample_values(field)
        if not samples:raise ValueError('lookup has no direct sampled-value coordinate inputs')
        parts=_parts(replaced)
        if len(parts)!=2:raise ValueError('sampled-value offset is not two-dimensional')
        names={name for name,s in samples};domains={name+'.'+lane:[0.,1.] for name in names for lane in 'xyzw'}
        pairs=[uniform_affine_scalar(v) for v in parts]
        if any(_deps(v)&names for coefficients,offset in pairs for v in coefficients):
            raise ValueError('spatial coefficients depend on sampled values; offset-only model withheld')
        if not any(_deps(offset)&names for coefficients,offset in pairs):raise ValueError('sampled values do not reach residual offsets')
        offsets=[offset for coefficients,offset in pairs]
        coefficients=[[_expression(v) for v in row] for row,offset in pairs]
        programs=[_expression(v) for v in offsets]
        if any(p is None for row in coefficients for p in row) or any(p is None for p in programs):raise ValueError('sample-offset program export budget exceeded')
        if known_invalid_phase_offset(field,preserve_zero_products=True):raise ValueError('sample-offset source has a known invalid original domain')
        reports=[coefficient_envelope(v,input_domains=domains) for v in offsets]
        spans=[r['nominal_value_range'] for r in reports]
        if scenario_result is not None:
            scenario_domains=dict(input_scenario['scalar_input_domains'])
            scenario_domains.update(domains)
            extra=[coefficient_envelope(v,input_domains=scenario_domains) for v in offsets]
            ranges=[r['nominal_value_range'] for r in extra]
            scenario_result.update(source_model='sample_value_offset_bounds' if all(v is not None for v in ranges) else
                'partial_sample_value_offset_bounds' if any(v is not None for v in ranges) else 'unknown',
                offset_range_uv=ranges,offset_value_envelopes=extra,
                unknown_reasons=[reason for r in extra for reason in r['unknown_reasons']])
        dependency=False;sites=[]
        for name,s in samples:
            nodes=list(_nodes(s.args[0]))
            if any(n.op=='sample' for n,p in nodes):dependency=True
            elif dependency is not True and any(n.op in {'unknown','uninitialized'} or n.op.startswith('loop_') for n,p in nodes):dependency=None
            sites.append({'local_input_name':name,'sample_site_index':s.detail.get('site_index'),
                'canonical_texture':s.detail.get('canonical_texture'),'sampler':s.detail.get('sampler'),
                'coordinate_expression':_expression(s.args[0]),'sampling_policy':s.detail.get('sampling_policy')})
        result.update(source_model='sample_value_offset_bounds' if all(v is not None for v in spans) else
            'partial_sample_value_offset_bounds' if any(v is not None for v in spans) else 'unknown',
            offset_range_uv=spans,offset_value_envelopes=reports,offset_programs=programs,
            base_coefficient_programs=coefficients,sample_sites=sites,
            sample_textures=sorted({s.detail.get('canonical_texture') for name,s in samples},key=str),
            coordinate_sample_dependency=dependency,unknown_reasons=[reason for r in reports for reason in r['unknown_reasons']])
    except (ValueError,RecursionError,OverflowError,IndexError) as error:
        result['unknown_reasons']=[str(error)]
        if scenario_result is not None:scenario_result['unknown_reasons']=[str(error)]
    return result
