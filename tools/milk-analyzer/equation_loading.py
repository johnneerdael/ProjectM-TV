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
                'tree_status':section.get('projectm_native_status','unknown'),
                'tree':section.get('projectm_raw_tree'),'policy':policy}
    if (raw=='rejected' and policy=='projectmtv-core-2.2.6-v1' and prefix=='per_frame_' and
            section.get('compile_status')=='accepted'):
        return {'compile_status':'accepted','assembly':'legacy-retry','code':section['assembled_source'],
                'tree_status':section.get('status','unknown'),'tree':section.get('tree'),'policy':policy}
    return {'compile_status':raw if raw=='rejected' else 'unknown','assembly':'unresolved',
            'code':None,'tree_status':'unknown','tree':None,'policy':policy}
