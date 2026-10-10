"""Nonlinear raw-warp colour difference bounds; no stored feedback simulation."""
from fractions import Fraction


def feedback_colour_sensitivity(description,*,warp_contains_clip=False):
    from source_sampling_motion import _finite_round
    model=description['nonlinear_texture_colour_bounds']['stages']['warp']
    maps={(r['sample_site_index'],r['sampler']):r for r in
          description['sampling_geometry']['stages']['warp'] or []}
    def summarize(model,scenario=False):
        result={'policy':'source-nonlinear-feedback-colour-sensitivity-v1','source_model':'unknown',
            'maximum_fixed_coordinate_feedback_sample_gain':None,
            'feedback_sample_row_gain_upper_bounds_rgb':[None,None,None],
            'maximum_previous_image_colour_gain':None,
            'sufficient_raw_warp_colour_contraction':None,'sample_contributions':[],
            'whole_feedback_contraction_verified':False,'actual_feedback_stability':None,
            'actual_feedback_persistence':None,'unknown_reasons':[],
            'conditions':['Authored custom warp is selected under the declared source/target compatibility context',
                'Nominal raw warp RGB infinity-norm differences, with sampled RGBA values in [0,1]',
                'All non-image inputs and external texture contents held identical in compared states',
                'Independent sample-channel derivative ceilings are summed across feedback sites; correlations can tighten them',
                'Previous-image gain additionally requires valid image-independent lookup coordinates and nonexpansive main sampling',
                'Blur inputs need a separate previous-image transfer proof; unknown or image-driven coordinates withhold operator credit',
                'Raw warp output alpha is fixed by the declared native wrapper; all four sampled RGBA columns are retained',
                'Later drawing, storage/rounding, blur updates, trails, composition and time-varying input sequences remain separate',
                'A failed sufficient contraction bound does not prove amplification, instability, visible flashing or a mood']}
        samples=model['direct_sample_colour_response']['samples']
        feedback=[s for s in samples if s['canonical_texture'] in {'main','blur1','blur2','blur3'}]
        if not feedback:
            result['unknown_reasons']=['no direct feedback-sample response; native/fixed or unsupported paths retain their existing models']
            return result
        totals=[]
        for axis in range(3):
            gains=[v for s in feedback for v in s['matrix_rgb_rgba_gain_upper_bounds'][axis]]
            totals.append(None if any(v is None for v in gains) else _finite_round(sum(map(Fraction,gains)),upper=True))
        result['feedback_sample_row_gain_upper_bounds_rgb']=totals
        result['sample_contributions']=[{'sample_site_index':s['sample_site_index'],'sampler':s['sampler'],
            'canonical_texture':s['canonical_texture'],'matrix_rgb_rgba_gain_upper_bounds':s['matrix_rgb_rgba_gain_upper_bounds']} for s in feedback]
        if any(v is not None for v in totals):result['source_model']='partial_feedback_sample_colour_response'
        if any(v is None for v in totals):
            result['unknown_reasons']=['one or more feedback RGB rows lack a complete finite sample-response bound']
            return result
        gain=max(totals);result.update(source_model='bounded_feedback_sample_colour_response',
            maximum_fixed_coordinate_feedback_sample_gain=gain)
        active=lambda s:any(v is None or v>0 for row in s['matrix_rgb_rgba_gain_upper_bounds'] for v in row)
        reasons=[]
        if any(s['canonical_texture']!='main' and active(s) for s in feedback):
            reasons.append('active blur sample-to-previous-image transfer is not established')
        for sample in samples:
            if not active(sample):continue
            lookup=maps.get((sample['sample_site_index'],sample['sampler']))
            if lookup is None:
                reasons.append('active colour sample lacks its coordinate/sampler descriptor');continue
            uv=lookup['mesh_uv_response']
            if scenario:uv=uv.get('scenario_mesh_uv_response',uv)
            if lookup['sampled_coordinate_response']['direct_sample_count']!=0 or not uv['global_lipschitz_domain_verified']:
                reasons.append('active colour sample coordinates lack a valid image-independent domain proof')
            if sample['canonical_texture']=='main':
                p=lookup['sampling_policy'] or {}
                # The native frame-wrap selector chooses repeat or clamp. Both
                # are nonexpansive for identical coordinates in compared states.
                addressing=type(p.get('wrap')) is bool or p.get('wrap_condition')=='frame_wrap > 0.0001'
                if type(p.get('linear')) is not bool or not addressing or p.get('mipmapped') is not False or p.get('base_level')!=0:
                    reasons.append('main sampling nonexpansive base-level policy is unresolved')
        # Discard can retain prior storage rather than write the modeled colour.
        if warp_contains_clip:
            reasons.append('warp clip/discard leaves incomplete writes outside this colour operator')
        result['unknown_reasons']=sorted(set(reasons))
        if not reasons:
            result['maximum_previous_image_colour_gain']=gain
            result['sufficient_raw_warp_colour_contraction']=gain<1
        return result
    result=summarize(model)
    if 'scenario_colour_envelope' in model:
        extra=model['scenario_colour_envelope']
        result['scenario_feedback_colour_sensitivity']={**summarize(extra,True),
            'input_scenario_sha256':extra['input_scenario_sha256'],
            'observed_runtime_inputs':False,'runtime_binding_verified':False}
    return result
