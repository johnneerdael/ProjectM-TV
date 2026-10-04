"""Pinned TextureManager settings and main-sampler binding order from source."""
import math


def texture_settings(sampler_name:str)->dict:
    name=sampler_name.removeprefix('sampler_')
    prefix=name[:3].lower()
    settings={'texture':name,'wrap':True,'linear':True,'mipmapped':False,'base_level':0}
    if len(name)>3 and name[2]=='_':
        settings['texture']=name[3:]
        if prefix in {'fc_','cf_'}:settings.update(wrap=False,linear=True)
        elif prefix in {'pc_','cp_'}:settings.update(wrap=False,linear=False)
        elif prefix in {'pw_','wp_'}:settings.update(wrap=True,linear=False)
        # fw/wf and unknown two-letter qualifiers keep native defaults.
    return settings


def main_sampler_bindings(references,*,stage:str,frame_wrap:float|None)->dict:
    if stage not in {'warp','composite'}:raise ValueError('warp/composite stage required')
    if frame_wrap is not None and not math.isfinite(frame_wrap):raise ValueError('finite frame wrap required')
    names=sorted({name for name in references if texture_settings(name)['texture'].lower()=='main'}|{'sampler_main'})
    bindings={}
    for unit,name in enumerate(names):
        policy={**texture_settings(name),'unit':unit}
        if stage=='warp' and unit==0:
            # MilkdropShader binds descriptors first; PerPixelMesh then replaces
            # sampler0 with its own linear sampler and frame-controlled wrap.
            policy.update(linear=True,wrap=None if frame_wrap is None else frame_wrap>.0001)
            if frame_wrap is None:policy['wrap_condition']='frame_wrap > 0.0001'
        bindings[name]=policy
    return bindings
