"""Global nominal mesh-UV response for source lookup maps, without images."""
from fractions import Fraction


def mesh_uv_response(field,lookup,*,input_scenario=None):
    from effect_families import _parts
    from source_ripple_envelopes import coefficient_envelope
    from source_forms import known_invalid_phase_offset
    result={'policy':'source-global-mesh-uv-response-v1','matrix_uv_output_input_gain_upper_bounds':None,
        'global_lipschitz_domain_verified':False,'includes_sample_coordinate_chain':False,
        'unknown_reasons':[],
        'conditions':['Finite nominal source UV/intermediates; shader uniforms, original UV and other inputs held fixed',
            'Mesh UV x/y vary independently over their finite domains; no [0,1] mesh bound is invented',
            'Global Lipschitz ceilings apply between warped and original UV only when both outputs and the connecting path share valid domains',
            'Image-driven coordinates require nested texture gradients and are excluded from this global direct UV certificate',
            'Native rounding, fold seam precision, filtering/history and actual visible motion remain separate']}
    prior=lookup['sampled_coordinate_response']
    if prior['direct_sample_count']!=0:
        result['unknown_reasons']=['image-driven or unresolved lookup requires a complete sample-coordinate chain'];return result
    if lookup['matrix_uv4'] is not None:
        if lookup['sampling_motion']['unknown_reasons']:
            result['unknown_reasons']=['affine coordinate domain is unresolved or invalid'];return result
        result.update(matrix_uv_output_input_gain_upper_bounds=[[abs(v) for v in row[:2]] for row in lookup['matrix_uv4']],
            global_lipschitz_domain_verified=True)
        return result
    folded=lookup['folded_coordinate_map']
    if folded['source_model']=='planar_periodic_folds' and all(a['continuous_nominal'] and a['phase_coefficients_uv4'] is not None for a in folded['axes']):
        from source_sampling_motion import _finite_round
        matrix=[[_finite_round(2*abs(Fraction(a['output_scale']))*abs(Fraction(v)),upper=True)
                 for v in a['phase_coefficients_uv4'][:2]] for a in folded['axes']]
        if all(v is not None for row in matrix for v in row):
            result.update(matrix_uv_output_input_gain_upper_bounds=matrix,global_lipschitz_domain_verified=True)
        return result
    try:
        parts=_parts(field)
        if len(parts)!=2:raise ValueError('lookup is not two-dimensional')
        def bounds(domains):
            matrix=[];reasons=[];assumptions=set()
            for part in parts:
                row=[]
                for name in ('_uv.x','_uv.y'):
                    r=coefficient_envelope(part,input_domains=domains,response_inputs={name})
                    row.append(r['maximum_absolute_control_change_per_audio_unit'])
                    reasons.extend(r['unknown_reasons']);assumptions.update(r['assumed_finite_input_names'])
                matrix.append(row)
            return {'matrix_uv_output_input_gain_upper_bounds':matrix,
                'global_lipschitz_domain_verified':all(v is not None for row in matrix for v in row),
                'assumed_finite_input_names':sorted(assumptions),'unknown_reasons':sorted(set(reasons))}
        result.update(bounds(None))
        if input_scenario is not None:
            result['scenario_mesh_uv_response']={**bounds(input_scenario['scalar_input_domains']),
                'input_scenario_sha256':input_scenario['record_sha256'],'observed_runtime_inputs':False,'runtime_binding_verified':False}
        candidate=result['global_lipschitz_domain_verified'] or result.get('scenario_mesh_uv_response',{}).get('global_lipschitz_domain_verified')
        if candidate and known_invalid_phase_offset(field,preserve_zero_products=True):
            raise ValueError('known invalid original lookup domain')
    except (ValueError,RecursionError,OverflowError,IndexError) as error:
        result['global_lipschitz_domain_verified']=False
        if 'scenario_mesh_uv_response' in result:result['scenario_mesh_uv_response']['global_lipschitz_domain_verified']=False
        result['unknown_reasons']=[str(error)]
    return result
