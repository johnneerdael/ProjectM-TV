"""Source-derived sampler inheritance for the pinned native shape draw path."""
import math
import re
from sampling_policy import texture_settings
from source_inventory import mask_comments

LEGACY='legacy-repeat-linear-v1'
CORE_238='projectmtv-core-2.3.8-shape-state-v1'


def native_blur_level(source:dict,stages:dict)->int:
    """Mirror successful custom shaders' native blur resource requests.

    GetReferencedSamplers strips comments, then scans sampler/texsize names and
    GetBlur substrings. A rejected stage never commits its blur request.
    """
    level=0
    for stage,prefix in [('warp','warp_'),('composite','comp_')]:
        if not stages[stage]['kind'].startswith('custom_'):continue
        text=mask_comments(source.get('sections',{}).get(prefix,{}).get('source',''),shader=True)
        for candidate in (1,2,3):
            if f'GetBlur{candidate}' in text:level=max(level,candidate)
        for match in re.finditer(r'(?:sampler_|texsize_)([A-Za-z0-9_]+)',text):
            name=texture_settings('sampler_'+match[1])['texture'].lower()
            if name in {'blur1','blur2','blur3'}:level=max(level,int(name[-1]))
    return level


def shape_sampling_modes(shapes:list,*,image_names:dict,policy:str,
                         warp_reads_blur:bool,blur_level:int,frame_wrap:float)->dict:
    """Return a mode for each textured draw, retaining instance order.

    In the verified old core, a texture-only bind preserves sampler0. The first
    main-textured draw inherits linear warp/blur sampling; each textured draw
    then clears sampler0. Later main draws use the attachment's repeat/nearest
    settings. Named images explicitly bind their own descriptor samplers.
    """
    if policy not in {LEGACY,CORE_238}:raise ValueError('unsupported shape sampler policy')
    if type(blur_level) is not int or not 0<=blur_level<=3:raise ValueError('native blur level0..3 required')
    if type(warp_reads_blur) is not bool or not math.isfinite(frame_wrap):raise ValueError('finite shape sampler context required')
    inherited=True
    first_wrap=False if warp_reads_blur and blur_level else frame_wrap>.0001
    modes={}
    for ordinal,shape in enumerate(shapes):
        if not int(shape['values'].get('textured',0)):continue
        image=image_names.get(shape['index'],'')
        if image:
            settings=texture_settings(image)
            mode={'wrap':settings['wrap'],'linear':settings['linear']}
        elif policy==LEGACY:mode={'wrap':True,'linear':True}
        elif inherited:mode={'wrap':first_wrap,'linear':True}
        else:mode={'wrap':True,'linear':False}
        modes[ordinal]=mode
        inherited=False
    return modes
