"""Nominal shape-centre response to audio units, never a temporal speed."""
import math
from fractions import Fraction


def shape_audio_center_response(controls,*,input_scenario=None):
    from source_appearance import EEL_AUDIO,_expression
    from source_control_bounds import scalar_response_envelope,scalar_value_envelope
    from source_sampling_motion import _finite_round
    bands=list(EEL_AUDIO)
    def ndc_norm(values):
        if any(v is None for v in values):return None
        value=2*math.hypot(*values)
        if not math.isfinite(value):return None
        rounded=math.nextafter(value,math.inf) if value else 0.
        return rounded if math.isfinite(rounded) else None
    def bound(domains):
        reports=[[scalar_response_envelope(controls[axis],input_names={band},input_domains=domains)
            for band in bands] for axis in ('x','y')]
        matrix=[[r['maximum_absolute_control_change_per_audio_unit'] for r in row] for row in reports]
        ndc=[]
        for column in zip(*matrix):
            ndc.append(ndc_norm(column))
        return {'matrix_center_xy_per_audio_unit_upper_bounds':matrix,
            'maximum_center_ndc_distance_per_audio_unit_upper_bounds':ndc,
            'axis_band_reports':reports,'unknown_reasons':sorted({reason for row in reports for r in row for reason in r['unknown_reasons']})}
    result={'policy':'source-shape-center-audio-response-v1','audio_input_codes':list(EEL_AUDIO.values()),
        'audio_input_names':bands,'axis_order':['x','y'],**bound(None),
        'center_source_expressions':[_expression(controls[axis]) for axis in ('x','y')],
        'maximum_center_speed_ndc_per_second':None,'visible_screen_movement':None,
        'native_numeric_certified':False,'uses_equation_execution':False,'uses_rendered_images':False,
        'conditions':['Nominal source control response while one current audio band varies and time/state/instance/all other inputs remain fixed',
            'Finite supported continuous arithmetic and valid connecting input domain required; unknown/discontinuous paths abstain',
            'NDC centre mapping is (2*x-1,1-2*y); Euclidean NDC distance is not physical-pixel or screen-aspect distance',
            'Inputs describe current engine bands; init snapshots and persistent locals are distinct held-fixed values',
            'No audio change rate or trajectory across frames is supplied; native float32 projection, changing other controls, clipping/visibility and feedback remain separate']}
    if input_scenario is not None:
        domains=input_scenario['scalar_input_domains'];value=bound(domains)
        envelopes=[scalar_value_envelope(controls[axis],input_domains=domains) for axis in ('x','y')]
        spans=[r['nominal_value_range'] for r in envelopes];distance=None
        if all(s is not None for s in spans):
            widths=[_finite_round(Fraction(s[1])-Fraction(s[0]),upper=True) for s in spans]
            distance=ndc_norm(widths)
        value.update(input_scenario_sha256=input_scenario['record_sha256'],
            center_source_xy_value_envelopes=envelopes,
            maximum_two_state_center_ndc_distance_upper_bound=distance,
            observed_runtime_inputs=False,runtime_binding_verified=False,
            two_state_scope='independent enclosure over declared inputs; simultaneous reachability and temporal trajectory unverified')
        result['scenario_center_response']=value
    return result
