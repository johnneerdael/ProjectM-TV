"""Source flashing mechanisms and actual feedback-step movement components."""
import math


def blackout_colour_channels(field):
    """Project colour factors without rebuilding sample-coordinate programs.

    Sample objects remain intact: callers validate original lookup domains
    separately. Numeric conversions remain typed source operations.
    """
    from effect_families import _parts
    from shader_fields import Field
    from source_appearance import _canonical_lane,_data_return
    from field_math import SWIZZLE
    memo={}
    def scalar(node,depth=0):
        key=id(node)
        if key in memo and memo[key][0] is node:return memo[key][1]
        if depth>64 or len(memo)>=512:raise ValueError('activity scalar projection budget exceeded')
        n=_canonical_lane(node)
        if n.op in {'sample','input'}:result=n
        elif n.op=='member' and n.dtype in {'float','int','bool'} and n.detail.get('swizzle') and len(n.detail.get('field',''))==1:
            parent=n.args[0];i=SWIZZLE[n.detail['field']]
            if parent.op in {'input','sample'}:result=n
            else:
                parts=_parts(parent)
                if i<len(parts) and not (parts[i].op=='member' and parts[i].args and parts[i].args[0] is parent):
                    result=scalar(parts[i],depth+1)
                else:result=Field(n.op,tuple(scalar(a,depth+1) for a in n.args),n.dtype,n.detail)
        else:result=Field(n.op,tuple(scalar(a,depth+1) for a in n.args),n.dtype,n.detail)
        memo[key]=(node,result);return result
    return [scalar(p) for p in _parts(_data_return(field))[:3]]


def _known_invalid_feedback_domain(analysis):
    """Check every known control, even when recipe loading stopped earlier."""
    from source_appearance import _phase_literal
    from source_native_warp import _f32
    from scene_equations import _scalar
    controls=getattr(analysis,'mesh_controls',{})
    try:
        for name,value in controls.items():
            literal=_phase_literal(value)
            if literal is None:continue
            native=_f32(literal)
            if name in {'zoom','sx','sy'}:
                if native==0 or _f32(1/native)==0:return True
        scale=_scalar(analysis.values,'fWarpScale',1,'float')
        if scale==0 or _f32(1/scale)==0:return True
    except (ValueError,OverflowError,ZeroDivisionError):return True
    return False


def source_activity(analysis,description):
    from effect_families import SPATIAL
    from source_appearance import _colour_product,_typed_control_identity,_data_return
    from source_polar import _nodes
    from source_time_switches import time_switch_events
    from source_forms import known_invalid_phase_offset
    flashing={'value':None,'status':'unknown','hazards':[],'material_change_bounds':[],'material_jump_bounds':[],'shader_change_bounds':[],
        'conditions':['Full-stage blackout is an authored raw-RGB mechanism under finite inputs and selected custom shader',
                      'All contributing RGB intermediates and multiplicative factors must be finite; finite inputs alone do not prove this',
                      'Nonblack retained content and later storage/composition/trails determine visible flashes',
                      'Source clocks, sampling cadence and native precision must retain the schedule; no flash-safe absence proof']}
    motion={'value':None,'status':'unknown','feedback_step_components':[],'geometry_speed_bounds':[],
        'conditions':['Warp parameters act every feedback step; constant parameter time derivatives are not image speeds',
                      'Components are separated from combined transport, wrapping, texel shifts and later custom shaders',
                      'Multiply per-step rates by actual feedback FPS only under steady controls/cadence',
                      'Geometry speeds precede clipping, source coverage, later shaders and feedback; no whole-screen intensity score']}
    from source_sampling_motion import texture_motion_bounds
    motion['texture_motion_bounds']=texture_motion_bounds(description)
    from source_nested_sampling import nested_texture_motion
    motion['nested_texture_motion']=nested_texture_motion(description)
    from source_nearest_activity import nearest_sampling_hazards
    flashing['hazards'].extend(nearest_sampling_hazards(description))
    from source_native_lookup_transport import native_lookup_transport,native_nearest_hazards
    motion['native_lookup_transport']=native_lookup_transport(description)
    flashing['hazards'].extend(native_nearest_hazards(description,motion['native_lookup_transport']))
    for stage,model in description['nonlinear_texture_colour_bounds']['stages'].items():
        for report,scenario in ((model,None),(model.get('scenario_colour_envelope'),True)):
            if report is None:continue
            response=report['direct_colour_time_response']
            flashing['hazards'].extend({**h,'stage':stage,'input_scenario_sha256':report['input_scenario_sha256'] if scenario else None}
                for h in report['channel_threshold_resets'])
            if response['channels']:
                flashing['shader_change_bounds'].append({**response,'stage':stage,
                    'input_scenario_sha256':report['input_scenario_sha256'] if scenario else None})
    composite=analysis.outputs.get('composite')
    if composite is not None:
        try:
            channels=blackout_colour_channels(composite)
            candidates={};active=[]
            for c in channels:
                coefficient,factors=_colour_product(c)
                if coefficient==0:continue
                ids=set()
                for f in factors:
                    gate=f
                    while gate.op=='cast' and gate.dtype=='float' and len(gate.args)==1 and gate.args[0].dtype=='bool':gate=gate.args[0]
                    if gate.op not in {'greater','greater_equal','less','less_equal'}:continue
                    if any(n.op in {'sample','unknown','uninitialized','sequence'} or n.op.startswith('loop_') or n.op=='input' and n.detail.get('name') in SPATIAL for n,path in _nodes(gate)):continue
                    if known_invalid_phase_offset(gate,preserve_zero_products=True):continue
                    identity=_typed_control_identity(gate)
                    if identity is None:continue
                    events=[e for e in time_switch_events(gate) if e['whole_control_levels_known'] and e.get('control_true_value')==1 and e.get('control_false_value')==0]
                    if not events:continue
                    ids.add(identity);candidates[identity]=(gate,events)
                active.append(ids)
            common=set.intersection(*active) if active and len(channels)==3 else set()
            if common and known_invalid_phase_offset(_data_return(composite),preserve_zero_products=True):
                raise ValueError('Known invalid contributing RGB domain prevents blackout certification')
            for identity in sorted(common):
                gate,events=candidates[identity]
                for e in events:
                    flashing['hazards'].append({'kind':'full_stage_blackout_gate','stage':'composite','off_rgb':[0,0,0],
                        'switch_event_rate_hz':e['nominal_event_rate_hz'],'blackout_cycles_hz':1/e['period_seconds'],
                        'period_seconds':e['period_seconds'],'off_fraction':1-e['predicate_true_fraction'],
                        'clock_kind':e['clock_kind'],'visible_flashing_verified':False,'source_event':e})
        except (ValueError,RecursionError,IndexError,OverflowError) as error:flashing['unknown_reasons']=[str(error)]
    recipe=description['native_warp_recipe'];p=recipe['native_float32_controls']
    invalid=_known_invalid_feedback_domain(analysis)
    if recipe['contribution']=='consumed' and not invalid:
        if p.get('rot') not in (None,0):
            amount=abs(math.atan2(math.sin(p['rot']),math.cos(p['rot'])))
            motion['feedback_step_components'].append({'kind':'rotation',
                'authored_native_radians_per_feedback_step':p['rot'],
                'absolute_radians_per_feedback_step':amount,'degrees_per_second_per_feedback_fps':amount*180/math.pi,
                'parameter_time_rate_is_motion_speed':False,'net_screen_speed_verified':False})
        if p.get('zoomexp')==1 and p.get('zoom',0)>0 and p['zoom']!=1:
            motion['feedback_step_components'].append({'kind':'zoom','scale_per_feedback_step':p['zoom'],
                'log_scale_per_second_per_feedback_fps':math.log(p['zoom']),
                'parameter_time_rate_is_motion_speed':False,'net_screen_speed_verified':False})
    for element in description['elements']:
        if 'material_temporal' in element and 'material' in element:
            from source_shape_activity import shape_activity
            records,hazards=shape_activity(element)
            flashing['material_change_bounds'].extend(records)
            flashing['hazards'].extend(hazards)
            from source_shape_jump_bounds import shape_material_jump_bounds
            flashing['material_jump_bounds'].extend(shape_material_jump_bounds(element))
        v=element.get('vertex_motion',{});speed=v.get('maximum_vertex_speed_ndc_per_second_upper_bound')
        if speed is not None:motion['geometry_speed_bounds'].append({'element_id':element['id'],
            'kind':'polygon_perimeter_vertex_speed','maximum_ndc_per_second':speed,
            'estimate_kind':v['estimate_kind'],'visible_screen_speed_verified':False})
    if flashing['hazards']:flashing['status']='source flash mechanisms; visibility unresolved'
    if motion['feedback_step_components'] or motion['geometry_speed_bounds'] or any(
            v is not None and v>0 for r in motion['texture_motion_bounds'] for v in r['maximum_lookup_axis_speed_uv_per_second']):
        motion['status']='source movement quantified for listed components'
    return {'flashing':flashing,'motion_intensity':motion}
