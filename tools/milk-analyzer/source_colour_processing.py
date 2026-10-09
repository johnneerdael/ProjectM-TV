"""Ordered source RGB processing suffixes, without pixels or shader execution."""


def channel_processing(field):
    from source_appearance import _canonical_lane,_phase_literal,_expression
    from field_math import SWIZZLE
    from effect_families import _parts
    node=field;outer=[]
    for _ in range(64):
        node=_canonical_lane(node)
        literal=_phase_literal(node)
        if literal is not None:
            base={'kind':'constant','value':literal,'expression':_expression(node)};break
        if node.op=='cast' and node.dtype=='float' and node.args[0].dtype=='float':
            node=node.args[0];continue
        if node.op=='member' and node.detail.get('swizzle') and len(node.detail.get('field',''))==1:
            parent=node.args[0]
            if parent.op=='domain_checked':
                outer.append({'operation':'domain_guard','function':parent.detail.get('function'),
                              'domain_condition':parent.detail.get('domain')})
                node=_parts(parent.args[0])[SWIZZLE[node.detail['field']]];continue
            if parent.op=='sample':
                base={'kind':'sample_channel','sample_channel':SWIZZLE[node.detail['field']],
                      'sampler':parent.detail.get('sampler'),'canonical_texture':parent.detail.get('canonical_texture'),
                      'sample_site_index':parent.detail.get('site_index'),
                      'coordinate_expression':_expression(parent.args[0]),'expression':_expression(node)};break
        step=None;child=None
        if node.op=='domain_checked':
            step={'operation':'domain_guard','function':node.detail.get('function'),
                  'domain_condition':node.detail.get('domain')};child=node.args[0]
        elif node.op=='pow' and len(node.args)==2:
            exponent=_phase_literal(node.args[1])
            if exponent is not None:
                step={'operation':'power','value':exponent,
                      'domain_condition':'source power input/exponent must be valid; usual bright/dark interpretation requires encoded input0..1'}
                child=node.args[0]
        elif node.op in {'saturate','abs'}:
            step={'operation':node.op};child=node.args[0]
        elif node.op=='clamp' and len(node.args)==3:
            low=_phase_literal(node.args[1]);high=_phase_literal(node.args[2])
            if low is not None and high is not None and low<=high:
                step={'operation':'clamp','lower':low,'upper':high};child=node.args[0]
        elif node.op in {'add','subtract','multiply','divide'} and len(node.args)==2:
            a=_phase_literal(node.args[0]);b=_phase_literal(node.args[1])
            if node.op=='subtract' and a==1:
                step={'operation':'one_minus'};child=node.args[1]
            elif node.op=='subtract' and a is not None:
                step={'operation':'constant_minus','value':a};child=node.args[1]
            elif node.op=='add' and (a is not None or b is not None):
                step={'operation':'add_constant','value':a if a is not None else b}
                child=node.args[1] if a is not None else node.args[0]
            elif node.op=='subtract' and b is not None:
                step={'operation':'add_constant','value':-b};child=node.args[0]
            elif node.op=='multiply' and (a is not None or b is not None):
                step={'operation':'multiply_constant','value':a if a is not None else b}
                child=node.args[1] if a is not None else node.args[0]
            elif node.op=='divide' and b not in {None,0}:
                step={'operation':'divide_constant','value':b};child=node.args[0]
        if step is None:
            base={'kind':'source_expression','expression':_expression(node)};break
        outer.append(step);node=child
    else:
        base={'kind':'source_expression','expression':None,'unknown_reason':'colour suffix depth budget exceeded'}
    return {'base':base,'steps_from_base':list(reversed(outer)),
            'complete_scene_colour_model':False,'actual_palette':None}


def colour_processing(analysis):
    from effect_families import _parts
    from source_appearance import _data_return
    stages={}
    for stage in ('warp','composite'):
        field=analysis.outputs.get(stage)
        if field is None:
            stages[stage]={'stage_kind':analysis.stages[stage]['kind'],'channels':None,
                'unknown_reasons':['no custom RGB field; native legacy/default processing is not represented as an authored shader chain'],
                'final_palette_verified':False}
        else:
            stages[stage]={'stage_kind':analysis.stages[stage]['kind'],
                'channels':[channel_processing(node) for node in _parts(_data_return(field))[:3]],
                'unknown_reasons':[],'final_palette_verified':False}
    return {'policy':'source-ordered-colour-processing-v1','colour_space':'source encoded RGB',
        'stages':stages,'final_palette_verified':False,
        'conditions':['Processing order is an authored source suffix, conditional on stage selection and valid domains',
                      'Base textures, source generation, masks, branches and storage may remain unresolved',
                      'RGB tone parameters do not prove palette diversity, warmth/coldness or visible contrast'],
        'uses_rendered_images':False,'uses_equation_execution':False,'uses_shader_execution':False}
