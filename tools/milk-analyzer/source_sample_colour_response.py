"""Independent sampled-lane Lipschitz ceilings through supported RGB math."""


def sample_colour_response(projected,samples,domains,derived_samples):
    from effect_families import _deps
    from source_polar import _nodes
    from source_forms import known_invalid_phase_offset
    from source_control_bounds import scalar_response_envelope
    result={'policy':'source-direct-sample-colour-response-v1','samples':[],
        'includes_sampling_coordinate_response':False,'visible_response_strength':None,
        'conditions':['Each directly sampled RGBA lane independently in [0,1], all source inputs/intermediates finite',
            'Each matrix column varies one sample lane; all other sample lanes, audio/time/state and coordinates held fixed',
            'Sum column ceilings for independent simultaneous lane changes; sample locations/history remain separate',
            'Bounds concern raw stage RGB; native precision/storage, image prominence and mood remain unverified']}
    metadata=[]
    sample_names={name for name,sample in samples}
    for selected in projected:
        try:
            names=_deps(selected)
            opaque=any(n.op in {'unknown','unresolved','uninitialized','sequence'} or n.op.startswith('loop_') or
                n.op=='input' and n.detail.get('name') in sample_names for n,p in _nodes(selected))
            invalid=opaque or known_invalid_phase_offset(selected,preserve_zero_products=True)
            metadata.append((names,invalid))
        except (ValueError,RecursionError):metadata.append((set(),True))
    for name,sample in samples:
        matrix=[];reasons=[];premises=set()
        for selected,(names,invalid) in zip(projected,metadata):
            row=[]
            for lane in 'xyzw':
                scalar=name+'.'+lane
                tainted=any(scalar in derived_samples.get(n,set()) for n in names)
                if invalid or tainted:
                    row.append(None);reasons.append('known invalid, opaque or quantized sample-dependent RGB path');continue
                if scalar not in names:row.append(0.);continue
                report=scalar_response_envelope(selected,input_names={scalar},input_domains=domains)
                row.append(report['maximum_absolute_control_change_per_audio_unit'])
                reasons.extend(report['unknown_reasons']);premises.update(report['assumed_finite_input_names'])
            matrix.append(row)
        result['samples'].append({'sample_site_index':sample.detail.get('site_index'),
            'sampler':sample.detail.get('sampler'),'canonical_texture':sample.detail.get('canonical_texture'),
            'matrix_rgb_rgba_gain_upper_bounds':matrix,'rgba_column_order':['r','g','b','a'],
            'assumed_finite_input_names':sorted(premises),
            'declared_input_domains':{k:v for k,v in domains.items() if k in premises},
            'unknown_reasons':sorted(set(reasons))})
    return result
