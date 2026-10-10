"""Partial source-time lookup motion and conditional texture-gradient rates."""
import math
from fractions import Fraction


def _finite_round(value,*,upper=False):
    try:result=float(value)
    except OverflowError:return None
    if not math.isfinite(result):return None
    if upper and Fraction(result)<value:result=math.nextafter(result,math.inf)
    if not math.isfinite(result) or value!=0 and result==0:return None
    return result


def _report(record,rates,velocities):
    result={'maximum_lookup_axis_speed_uv_per_second':rates,
        'signed_feature_velocity_basis_uv_per_second':None,
        'maximum_feature_speed_basis_uv_per_second':None,
        'total_lookup_speed_uv_per_second':None}
    matrix=record['matrix_uv4'];basis=record['basis']
    if matrix is None or basis not in {'shader_uv','original_uv'} or any(v is None for v in rates):return result
    index=0 if basis=='shader_uv' else 2
    a,b=map(Fraction,matrix[0][index:index+2]);c,d=map(Fraction,matrix[1][index:index+2])
    determinant=a*d-b*c
    if determinant==0:return result
    inverse=((d/determinant,-b/determinant),(-c/determinant,a/determinant))
    ceilings=[sum(abs(k)*Fraction(v) for k,v in zip(row,rates)) for row in inverse]
    values=[_finite_round(v,upper=True) for v in ceilings]
    if all(v is not None for v in values):
        length=math.hypot(*values)
        if math.isfinite(length):
            upper=math.nextafter(length,math.inf) if length else 0.
            if math.isfinite(upper):result['maximum_feature_speed_basis_uv_per_second']=upper
    if all(v is not None for v in velocities):
        signed=[_finite_round(-sum(k*Fraction(v) for k,v in zip(row,velocities))) for row in inverse]
        if all(v is not None for v in signed):result['signed_feature_velocity_basis_uv_per_second']=signed
    return result


def sampling_motion(record,field,*,input_scenario=None):
    from source_forms import known_invalid_phase_offset
    result={'policy':'source-affine-sampling-time-motion-v1',**_report(record,[None,None],[None,None]),
        'feature_basis':record['basis'],'native_mesh_input_is_held_fixed':True,
        'visible_screen_speed':None,'unknown_reasons':[],
        'conditions':['Nominal constant-affine lookup with uniform offsets; spatial/mesh inputs held fixed',
            'Source-clock continuity and finite supported arithmetic required; native quantization/cadence excluded',
            'Inverse feature motion assumes an isolated fixed texture feature and fixed affine coefficients',
            'Texture history/content, filtering/wrapping, clipping, later transforms/feedback and visibility remain separate',
            'Scenario quantities are partial time response with audio/state/frame/FPS and all other inputs fixed']}
    curves=record['offset_controls']
    try:
        if record['matrix_uv4'] is None:
            return _nonlinear_sampling_motion(result,record,field,input_scenario=input_scenario)
        if len(curves)!=2:raise ValueError('constant-affine coordinate offsets unavailable')
        if known_invalid_phase_offset(field,preserve_zero_products=True):raise ValueError('known invalid coordinate arithmetic')
        rates=[c['maximum_absolute_control_rate_per_second'] for c in curves]
        velocities=[0. if c['curve_kind']=='constant' else c['signed_linear_rate_per_second'] for c in curves]
        result.update(_report(record,rates,velocities))
        if input_scenario is not None:
            extra=[c['scenario_time_component']['maximum_absolute_control_rate_per_source_second'] for c in curves]
            result['scenario_sampling_motion']={**_report(record,extra,[None,None]),
                'input_scenario_sha256':input_scenario['record_sha256'],
                'observed_runtime_inputs':False,'runtime_binding_verified':False}
    except (ValueError,RecursionError,OverflowError) as error:result['unknown_reasons']=[str(error)]
    return result


def _nonlinear_sampling_motion(result,record,field,*,input_scenario=None):
    """Nominal partial derivative ceilings; no inverse-feature velocity inferred."""
    from effect_families import _parts
    from source_ripple_envelopes import coefficient_envelope
    from source_forms import known_invalid_phase_offset
    result.update(policy='source-nonlinear-sampling-time-motion-v1',
        conditions=['Nominal partial lookup response while source-time aliases advance together',
            'Native mesh/original coordinates, audio/state/frame/FPS and all other inputs held fixed and finite',
            'No [0,1] bound is invented for warped UV; unbounded spatial gains remain unresolved',
            'Image-driven coordinates require texture-history and gradient chains and remain separate',
            'These axis ceilings are not inverse feature velocity, total lookup speed or screen movement',
            'Native quantization/cadence, clock wraps/resets, filtering/history and later passes remain unqualified'])
    try:
        if record['sampled_coordinate_response']['direct_sample_count']!=0:
            raise ValueError('image-driven coordinates require a complete sample-coordinate time chain')
        parts=_parts(field)
        if len(parts)!=2:raise ValueError('lookup is not two-dimensional')
        def bounds(domains):
            reports=[coefficient_envelope(p,input_domains=domains,
                response_inputs={'time',':native-render-time-f32','_c2.x'}) for p in parts]
            rates=[r['maximum_absolute_control_change_per_audio_unit'] for r in reports]
            return {**_report(record,rates,[None,None]),
                'assumed_finite_input_names':sorted({n for r in reports for n in r['assumed_finite_input_names']}),
                'unknown_reasons':sorted({s for r in reports for s in r['unknown_reasons']})}
        result.update(bounds(None))
        if input_scenario is not None:
            result['scenario_sampling_motion']={**bounds(input_scenario['scalar_input_domains']),
                'input_scenario_sha256':input_scenario['record_sha256'],
                'observed_runtime_inputs':False,'runtime_binding_verified':False}
        # Keep original arithmetic, including zero products, in the validity gate.
        candidates=[result,result.get('scenario_sampling_motion')]
        if any(r is not None and any(v is not None for v in r['maximum_lookup_axis_speed_uv_per_second']) for r in candidates):
            if known_invalid_phase_offset(field,preserve_zero_products=True):
                raise ValueError('known invalid original coordinate arithmetic')
    except (ValueError,RecursionError,OverflowError,IndexError) as error:
        result.update(_report(record,[None,None],[None,None]),unknown_reasons=[str(error)])
        if 'scenario_sampling_motion' in result:
            result['scenario_sampling_motion'].update(_report(record,[None,None],[None,None]),unknown_reasons=[str(error)])
    return result


def texture_motion_bounds(description):
    """Weighted bilinear worst-case coefficients; texture dimensions are inputs."""
    rows=[]
    for stage,maps in description['sampling_geometry']['stages'].items():
        if maps is None:continue
        transfer=description['texture_colour_transfer']['stages'][stage]
        weights={(r['sample_site_index'],r['sampler']):r for r in transfer['sample_contributions']}
        nonlinear=description['nonlinear_texture_colour_bounds']['stages'][stage]
        for record in maps:
            movement=record['sampling_motion'];weight=weights.get((record['sample_site_index'],record['sampler']))
            for part,scenario in ((movement,None),(movement.get('scenario_sampling_motion'),True)):
                if part is None:continue
                coefficients=[[None,None] for _ in range(3)]
                response_model=None
                policy=record['sampling_policy'] or {}
                linear=policy.get('linear') is True and policy.get('mipmapped') is False and policy.get('base_level')==0
                if weight is not None and linear:
                    response_model='affine_sample_colour'
                    for i,row in enumerate(weight['matrix_rgb_rgba']):
                        gain=sum(abs(Fraction(v)) for v in row)
                        for axis,speed in enumerate(part['maximum_lookup_axis_speed_uv_per_second']):
                            if speed is not None:coefficients[i][axis]=_finite_round(gain*Fraction(speed),upper=True)
                elif linear:
                    report=nonlinear.get('scenario_colour_envelope',nonlinear) if scenario else nonlinear
                    candidate=next((r for r in report['direct_sample_colour_response']['samples'] if
                        (r['sample_site_index'],r['sampler'])==(record['sample_site_index'],record['sampler'])),None)
                    if candidate is not None:
                        response_model='nonlinear_sample_lipschitz'
                        for i,row in enumerate(candidate['matrix_rgb_rgba_gain_upper_bounds']):
                            if any(v is None for v in row):continue
                            gain=sum(Fraction(v) for v in row)
                            for axis,speed in enumerate(part['maximum_lookup_axis_speed_uv_per_second']):
                                if speed is not None:coefficients[i][axis]=_finite_round(gain*Fraction(speed),upper=True)
                rows.append({'stage':stage,'sample_site_index':record['sample_site_index'],
                    'sampler':record['sampler'],'canonical_texture':record['canonical_texture'],
                    'input_scenario_sha256':part['input_scenario_sha256'] if scenario else None,
                    'maximum_lookup_axis_speed_uv_per_second':part['maximum_lookup_axis_speed_uv_per_second'],
                    'linear_texture_rgb_rate_coefficients_per_dimension':coefficients,
                    'colour_response_model':response_model,
                    'texture_dimensions_verified':False,'visible_rgb_rate_per_second':None,
                    'scope':'sampling-motion contribution with fixed texture contents and supported RGB response',
                    'conditions':['Each sampled RGBA texel in [0,1], linear base-level filtering with standard repeat or clamp addressing',
                        'Supply actual uploaded width W and height H: each RGB rate <= coefficient_x*W + coefficient_y*H',
                        'Coefficients bound worst-case adjacent-texel contrast; constant images can have zero actual variation',
                        'Different sites must be summed; changing texture contents/history, direct colour changes and other passes remain separate',
                        'No typical/average activity, actual flash frequency, displayed speed or mood certification']})
    return rows
