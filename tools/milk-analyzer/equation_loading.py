"""Explicit equation loading policies; compiler status is not visual accuracy."""

POLICIES={'strict-raw-v1','projectmtv-core-2.2.6-v1'}


def select_equation(section,prefix,*,policy):
    if policy not in POLICIES:raise ValueError('explicit supported equation loader policy required')
    if section is None:
        return {'compile_status':'accepted','assembly':'absent','code':'0;',
                'tree_status':'parsed','tree':None,'policy':policy}
    raw=section.get('projectm_native_compile_status')
    if raw=='accepted':
        return {'compile_status':'accepted','assembly':'raw','code':section['source'],
                'tree_status':section.get('projectm_native_status','unknown') if 'projectm_raw_tree' in section else 'unknown',
                'tree':section.get('projectm_raw_tree'),'policy':policy}
    if (raw=='rejected' and policy=='projectmtv-core-2.2.6-v1' and prefix=='per_frame_' and
            section.get('compile_status')=='accepted'):
        return {'compile_status':'accepted','assembly':'legacy-retry','code':section['assembled_source'],
                'tree_status':section.get('status','unknown'),'tree':section.get('tree'),'policy':policy}
    return {'compile_status':raw if raw=='rejected' else 'unknown','assembly':'unresolved',
            'code':None,'tree_status':'unknown','tree':None,'policy':policy}


def constant_q_banks(source,*,policy):
    """Prove untouched main Q banks zero; referenced banks stay unconstrained."""
    names=set()
    for prefix,section in source.get('sections',{}).items():
        if prefix not in {'warp_','comp_'} and select_equation(section,prefix,policy=policy)['compile_status']!='accepted':return {}
    def visit(node):
        if isinstance(node,list):
            for child in node:visit(child)
        elif isinstance(node,dict):
            if node.get('kind')=='variable':names.add(node['name'].lower())
            for child in node.values():visit(child)
    for prefix in ['per_frame_init_','per_frame_','per_pixel_']:
        selected=select_equation(source.get('sections',{}).get(prefix),prefix,policy=policy)
        if selected['compile_status']!='accepted' or selected['tree_status']!='parsed':return {}
        visit(selected['tree'])
    return {'_q'+chr(ord('a')+bank):[0,0,0,0] for bank in range(8)
            if not {f'q{bank*4+component+1}' for component in range(4)}&names}
