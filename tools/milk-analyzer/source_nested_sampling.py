"""Nested lookup chain ceilings as dimension polynomials, without images."""
from fractions import Fraction


def coordinate_sample_response(field,prior,*,input_scenario=None):
    from source_advection import substitute_sample_values
    from effect_families import _parts
    from source_ripple_envelopes import coefficient_envelope
    from source_forms import known_invalid_phase_offset
    result={'policy':'source-nonlinear-coordinate-sample-response-v1','samples':[],
        'includes_inner_sampling_coordinate_response':False,'unknown_reasons':[],
        'native_aspect_domain_premise':{'_c0.x':[0,1],'_c0.y':[0,1]},
        'conditions':['Independent sampled RGBA lanes in [0,1]; finite relevant inputs/intermediates',
            'Native aspectX/aspectY are ratios or one under positive finite viewport dimensions',
            'One inner sample lane varies; other lanes, coordinates, audio/time/state and native uploads fixed',
            'Direct UV gain does not include the inner sample coordinate/history; nested edges compose it separately']}
    if prior['direct_sample_count']==0:return result
    if prior['direct_sample_count'] is None:
        result['unknown_reasons']=['direct coordinate sample inventory unavailable'];return result
    try:
        if known_invalid_phase_offset(field,preserve_zero_products=True):raise ValueError('known invalid nested coordinate arithmetic')
        replaced,samples=substitute_sample_values(field);parts=_parts(replaced)
        if len(parts)!=2:raise ValueError('nested lookup coordinate is not two-dimensional')
        def reports(domains):
            rows=[]
            for name,sample in samples:
                matrix=[];reasons=[];premises=set()
                for part in parts:
                    values=[]
                    for lane in 'xyzw':
                        r=coefficient_envelope(part,input_domains=domains,response_inputs={name+'.'+lane})
                        values.append(r['maximum_absolute_control_change_per_audio_unit'])
                        reasons.extend(r['unknown_reasons']);premises.update(r['assumed_finite_input_names'])
                    matrix.append(values)
                rows.append({'sample_site_index':sample.detail.get('site_index'),'sampler':sample.detail.get('sampler'),
                    'canonical_texture':sample.detail.get('canonical_texture'),'matrix_uv_rgba_gain_upper_bounds':matrix,
                    'assumed_finite_input_names':sorted(premises),'unknown_reasons':sorted(set(reasons))})
            return rows
        domains={'_c0.x':[0,1],'_c0.y':[0,1]}
        domains.update({name+'.'+lane:[0,1] for name,sample in samples for lane in 'xyzw'})
        result['samples']=reports(domains)
        if input_scenario is not None:
            extra=dict(input_scenario['scalar_input_domains']);extra.update(domains)
            result['scenario_coordinate_response']={'samples':reports(extra),'input_scenario_sha256':input_scenario['record_sha256']}
    except (ValueError,RecursionError,OverflowError,IndexError) as error:result['unknown_reasons']=[str(error)]
    return result


def nested_texture_motion(description):
    from source_sampling_motion import _finite_round
    result={'policy':'source-nested-texture-motion-v1','chains':[],'unknown_reasons':[],
        'visible_rgb_rate_per_second':None,'paths_are_exhaustive':False,'full_sampling_motion_bound_verified':False,
        'conditions':['Finite nominal lookup DAG; each sampled RGBA texel independently in [0,1]',
            'Selected authored shader path reaches these lookups under the declared native profile',
            'All traversed filters use linear nonmipmapped base-level sampling and standard repeat/clamp addressing',
            'Supply actual uploaded W/H for every factor; sum terms/paths only for the modeled contributions, not a complete output ceiling',
            'Fixed texture contents/history, spatial/native mesh inputs, audio/state/frame/FPS and all non-time inputs',
            'Source clock/lookup motion and coordinate/color response premises must hold over the interval',
            'No typical response, changing texture history, direct colour variation, full feedback or visible flash/mood claim']}
    count=0
    def key(record):return record['sample_site_index'],record['sampler']
    def linear(record):
        p=record['sampling_policy'] or {}
        return p.get('linear') is True and p.get('mipmapped') is False and p.get('base_level')==0
    def row_gain(row):return None if any(v is None for v in row) else sum(map(Fraction,row))
    def dimension(stage,record,axis):return {'stage':stage,'sample_site_index':record['sample_site_index'],
        'sampler':record['sampler'],'canonical_texture':record['canonical_texture'],'axis':axis}
    for stage,maps in description['sampling_geometry']['stages'].items():
        if maps is None:continue
        by_key={key(r):r for r in maps};colour=description['nonlinear_texture_colour_bounds']['stages'][stage]
        for scenario in (False,True):
            if scenario and 'scenario_colour_envelope' not in colour:continue
            source=colour['scenario_colour_envelope'] if scenario else colour
            sinks={key(r):r for r in source['direct_sample_colour_response']['samples']}
            adjacency={}
            for outer in maps:
                response=outer['coordinate_sample_response']
                edges=response.get('scenario_coordinate_response',response)['samples'] if scenario else response['samples']
                for edge in edges:adjacency.setdefault(key(edge),[]).append((outer,edge))
            for root in maps:
                movement=root['sampling_motion'].get('scenario_sampling_motion') if scenario else root['sampling_motion']
                if movement is None or not linear(root):continue
                rates=movement['maximum_lookup_axis_speed_uv_per_second']
                if any(v is None for v in rates) or not any(v>0 for v in rates):continue
                terms=[(Fraction(v),[dimension(stage,root,axis)]) for v,axis in zip(rates,('width','height')) if v>0]
                pending=[(root,terms,[key(root)])]
                while pending:
                    current,polynomial,path=pending.pop()
                    if len(path)>64:
                        result['unknown_reasons'].append('nested lookup path exceeds64sites');continue
                    if len(path)>1 and key(current) in sinks:
                        matrix=sinks[key(current)]['matrix_rgb_rgba_gain_upper_bounds'];rgb=[]
                        for row in matrix:
                            gain=row_gain(row);converted=[]
                            if gain is None:rgb.append(None);continue
                            for coefficient,factors in polynomial:
                                value=_finite_round(coefficient*gain,upper=True)
                                if value is None:converted=None;break
                                if value>0:converted.append({'coefficient':value,'dimension_factors':factors})
                            rgb.append(converted)
                        if any(row for row in rgb):
                            result['chains'].append({'stage':stage,'path_sample_site_indices':[k[0] for k in path],
                                'path_samplers':[k[1] for k in path],
                                'input_scenario_sha256':source['input_scenario_sha256'] if scenario else None,
                                'rgb_rate_polynomial':rgb,'visible_rgb_rate_per_second':None,
                                'scope':'modeled lookup-motion path; direct time changes in coefficients/colour and texture history remain separate'})
                    for outer,edge in adjacency.get(key(current),[]):
                        if key(outer) in path or not linear(outer):continue
                        gains=[row_gain(row) for row in edge['matrix_uv_rgba_gain_upper_bounds']]
                        if any(v is None for v in gains):continue
                        next_terms=[(c*g,f+[dimension(stage,outer,axis)]) for c,f in polynomial
                                    for g,axis in zip(gains,('width','height')) if g>0]
                        count+=len(next_terms)
                        if count>4096:
                            result['unknown_reasons'].append('nested lookup polynomial exceeds4096terms');return result
                        if next_terms:pending.append((outer,next_terms,path+[key(outer)]))
    return result
