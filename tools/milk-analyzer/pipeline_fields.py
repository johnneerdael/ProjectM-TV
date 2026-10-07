"""Compose supported source shader fields with explicit spatial feedback state.

This is a numeric integration of declared inputs, not a finished preset loader or
appearance predictor. Warp coordinates, equation uniforms, source drawing and
external/procedural texture functions must be supplied faithfully. No native
rendered frames are consumed. Discard/unsupported language remains unresolved.
"""
from dataclasses import dataclass
import numpy as np
from shader_fields import ShaderFields,Field,uses_input_components
from grid_math import evaluate_grid
from field_math import UnresolvedMath
from field_math import GLES_HIGHP_INFINITY
from spatial import sample2d
from blur import blur_bank,native_ranges,pass_dimensions
from feedback_field import unorm8
from engine_profiles import LEGACY_BLUR,CORE_2315_BLUR,LEGACY_DISPLAY,CORE_2315_DISPLAY


@dataclass(frozen=True)
class PipelineResult:
    frame:int
    warped:np.ndarray
    feedback:np.ndarray
    display:np.ndarray
    history:dict


class SourcePipeline:
    def _lower_stage(self,tree,name,frame_wrap):
        model=ShaderFields(stage=name,frame=self.frame,warp_reads_blur=self.warp_reads_blur,frame_wrap=frame_wrap,
                           main_binding_policy=self.main_binding_policy,known_uniforms=self.known_uniforms,known_uniform_components=self.known_uniform_components,
                           known_uniform_component_domains=self.known_uniform_component_domains,
                           global_input_policy=self.global_input_policies.get(name,'strict-v1'),
                           array_initializer_policy=self.array_initializer_policies.get(name,'legacy-layout-v1'))
        expression=model.lower(tree,language_extensions=self.language_extensions.get(name,[]),
                               native_samplers=self.native_samplers.get(name,{}))
        if not model.complete:raise UnresolvedMath('unsupported source shader: '+'; '.join(model.unknown))
        return model,expression

    def requires_warp_uv(self,*,frame_wrap,motion_state):
        from motion_vectors import motion_active
        if self.warp_tree is None or motion_active(motion_state):return True
        _,expression=self._lower_stage(self.warp_tree,'warp',frame_wrap)
        return uses_input_components(expression,'_uv',{0,1})

    def __init__(self,warp_tree,composite_tree,*,initial_feedback,warp_reads_blur:bool,
                 blur_levels:int,quantize:bool=True,composite_kind=None,source_values=None,coordinate_profile='strict',language_extensions=None,native_samplers=None,composite_subpixel_bits=None,main_sampling_profile='portable',main_binding_policy='legacy-sorted-v1',blur_range_policy=LEGACY_BLUR,legacy_control_policy=LEGACY_DISPLAY,shader_numeric_policy='strict',texture_sampling_profile='portable',line_rendering_profile='canonical-gl-lines-v1',motion_raster_subpixel_bits=None,motion_uv_storage_profile='portable-half-nearest-v1'):
        from quad_lines import PROFILE as quad_profile
        if line_rendering_profile not in ('canonical-gl-lines-v1',quad_profile):
            raise ValueError('unknown motion-vector line profile')
        if motion_raster_subpixel_bits is not None and (type(motion_raster_subpixel_bits) is not int or not 4<=motion_raster_subpixel_bits<=16):
            raise ValueError('motion raster subpixel bits must be an integer within4..16')
        from motion_vectors import PORTABLE_STORAGE,APPLE_RTZ_STORAGE,APPLE_FINITE_STORAGE
        if motion_uv_storage_profile not in (PORTABLE_STORAGE,APPLE_RTZ_STORAGE,APPLE_FINITE_STORAGE):
            raise ValueError('unknown motion UV storage profile')
        self.motion_uv_storage_profile=motion_uv_storage_profile
        self.line_rendering_profile=line_rendering_profile
        self.motion_raster_subpixel_bits=motion_raster_subpixel_bits
        if shader_numeric_policy not in {'strict',GLES_HIGHP_INFINITY}:raise ValueError('unsupported shader numeric policy')
        if shader_numeric_policy==GLES_HIGHP_INFINITY and coordinate_profile!='strict':raise ValueError('unsupported mixed shader numeric/coordinate policies')
        self.shader_numeric_policy=shader_numeric_policy
        if coordinate_profile not in ('strict','apple-m4pro-gl41-nan-sampler-v1'):
            raise ValueError('unsupported shader coordinate profile')
        field=np.asarray(initial_feedback,dtype=np.float32)
        if field.ndim!=3 or field.shape[2]!=4 or min(field.shape[:2])<=0 or not np.all(np.isfinite(field)):
            raise ValueError('explicit finite RGBA initial feedback required')
        if line_rendering_profile==quad_profile and field.shape[0]*field.shape[1]>1024*768:
            raise ValueError('motion quad profile requires viewport within reference area')
        if type(blur_levels) is not int or not 0<=blur_levels<=3:raise ValueError('blur level0..3 required')
        self.warp_tree=warp_tree;self.composite_tree=composite_tree
        self.language_extensions=language_extensions or {}
        self.native_samplers=native_samplers or {}
        self.composite_kind=composite_kind or ('custom_composite' if composite_tree is not None else 'default_composite')
        self.source_values=source_values or {};self.stage_resolution=None
        self.known_uniforms={}
        self.known_uniform_components={}
        self.known_uniform_component_domains={}
        self.array_initializer_policies={}
        self.global_input_policies={}
        self.coordinate_profile=coordinate_profile
        self.feedback=field.copy();self.frame=0;self.warp_reads_blur=warp_reads_blur
        self.motion_uv=None;self.motion_uv_frame=None
        self.blur_levels=blur_levels;self.quantize=quantize
        from unorm_sampler import PROFILE,sampler_2d
        if main_sampling_profile not in ('portable',PROFILE) or (main_sampling_profile==PROFILE and not quantize):
            raise ValueError('supported main sampling profile with actual unorm storage required')
        self.main_sampling_profile=main_sampling_profile
        self.sample_2d=sampler_2d(texture_sampling_profile)
        if texture_sampling_profile!='portable' and (not quantize or main_sampling_profile!='portable'):
            raise ValueError('texture profile requires unorm storage and no conflicting main profile')
        self.texture_sampling_profile=texture_sampling_profile
        if texture_sampling_profile!='portable':self.main_sampling_profile=texture_sampling_profile
        from sampling_policy import main_sampler_bindings
        main_sampler_bindings([],stage='warp',frame_wrap=None,policy=main_binding_policy)
        self.main_binding_policy=main_binding_policy
        if blur_range_policy not in {LEGACY_BLUR,CORE_2315_BLUR}:raise ValueError('unsupported blur range policy')
        if legacy_control_policy not in {LEGACY_DISPLAY,CORE_2315_DISPLAY}:raise ValueError('unsupported legacy control policy')
        self.blur_range_policy=blur_range_policy;self.legacy_control_policy=legacy_control_policy
        self.height,self.width=field.shape[:2]
        x,y=np.meshgrid((np.arange(self.width,dtype=np.float32)+.5)/self.width,
                        (np.arange(self.height,dtype=np.float32)+.5)/self.height)
        self.original_uv=np.stack((x,y),axis=-1)
        sizes=pass_dimensions(self.width,self.height)
        # Explicit cold-start model: incomplete native blur textures return
        # black RGB. No texsize_blur uniform is fabricated from this assumption.
        self.blur={level:np.zeros((sizes[level*2-1][1],sizes[level*2-1][0],3),dtype=np.float32)
                   for level in range(1,blur_levels+1)}
        self.blur_source_frame=-2
        from composite_mesh import make_mesh
        self.composite_mesh=make_mesh(self.width,self.height,raster_subpixel_bits=composite_subpixel_bits)

    @classmethod
    def from_source(cls,source,*,profile,compatibility,equation_loader_policy='strict-raw-v1',**kwargs):
        from quad_lines import PROFILE as quad_profile
        from motion_vectors import PORTABLE_STORAGE
        if kwargs.get('motion_uv_storage_profile',PORTABLE_STORAGE)!=PORTABLE_STORAGE and profile!='gles300':
            raise ValueError('motion half storage profile requires declared GLES300 context')
        if kwargs.get('line_rendering_profile','canonical-gl-lines-v1')==quad_profile and profile!='gles300':
            raise ValueError('motion quad profile requires declared GLES300 context')
        if kwargs.get('texture_sampling_profile','portable')!='portable' and profile!='gles300':
            raise ValueError('observed texture profile requires declared GLES300 context')
        if kwargs.get('shader_numeric_policy','strict')!='strict' and profile!='gles300':
            raise ValueError('highp shader numeric policy requires GLES300')
        if kwargs.get('coordinate_profile','strict')!='strict' and profile!='glsl330':
            raise ValueError('Apple shader coordinate profile requires glsl330')
        # The pinned preset loader compiles custom equations even for disabled
        # waves/shapes and throws on failure. Shader fallback cannot rescue it.
        from equation_loading import select_equation
        select_equation(None,'per_frame_',policy=equation_loader_policy)
        for prefix,section in source.get('sections',{}).items():
            if prefix not in {'warp_','comp_'}:
                selected=select_equation(section,prefix,policy=equation_loader_policy)
                if selected['compile_status']=='rejected':
                    raise UnresolvedMath('native equation compilation rejected: '+prefix)
                if selected['compile_status'] not in {'accepted','omitted'}:
                    raise UnresolvedMath('native equation compatibility unresolved: '+prefix)
        from stage_resolution import resolve_stages
        plan=resolve_stages(source,profile=profile,compatibility=compatibility)
        trees={}
        for name,prefix in [('warp','warp_'),('composite','comp_')]:
            kind=plan[name]['kind']
            if kind=='unknown':raise UnresolvedMath('unresolved '+name+' stage selection')
            section=source.get('sections',{}).get(prefix,{})
            if kind.startswith('custom_'):
                if section.get('status')!='parsed':raise UnresolvedMath('active shader tree unresolved: '+name)
                trees[name]=section['tree']
            else:trees[name]=None
        pipeline=cls(trees['warp'],trees['composite'],composite_kind=plan['composite']['kind'],
                     source_values=source['values'],language_extensions={
                         name:source.get('sections',{}).get(prefix,{}).get('language_extensions',[])
                         for name,prefix in [('warp','warp_'),('composite','comp_')]},
                     native_samplers={name:compatibility[name]['request']['samplers']
                         for name in ('warp','composite') if plan[name]['kind'].startswith('custom_')},**kwargs)
        pipeline.stage_resolution=plan
        pipeline.equation_loader_policy=equation_loader_policy
        from equation_loading import constant_q_components
        pipeline.known_uniform_components=constant_q_components(source,policy=equation_loader_policy)
        from equation_domains import q_uniform_domains
        pipeline.known_uniform_component_domains=q_uniform_domains(source,policy=equation_loader_policy)
        pipeline.array_initializer_policies={name:source.get('sections',{}).get(prefix,{}).get('array_initializer_policy','legacy-layout-v1')
                                             for name,prefix in [('warp','warp_'),('composite','comp_')]}
        pipeline.global_input_policies={name:source.get('sections',{}).get(prefix,{}).get('implicit_global_input_policy','strict-v1')
                                       for name,prefix in [('warp','warp_'),('composite','comp_')]}
        return pipeline

    def _store(self,field):
        values=np.asarray(field,dtype=np.float32)
        if not np.all(np.isfinite(values)):raise UnresolvedMath('nonfinite pipeline surface')
        return unorm8(values) if self.quantize else np.clip(values,0,1)

    def _rgba(self,rgb):
        if rgb.shape!=(self.height,self.width,3):raise UnresolvedMath('shader ret must be a viewport-sized RGB field')
        if self.shader_numeric_policy==GLES_HIGHP_INFINITY:
            if np.any(np.isnan(rgb)):raise UnresolvedMath('NaN normalized shader output remains unresolved')
            rgb=np.clip(rgb,0,1)
        return self._store(np.concatenate((rgb,np.ones(rgb.shape[:2]+(1,),dtype=np.float32)),axis=-1))

    def _sample_main(self,field,uv,*,wrap,linear):
        from unorm_sampler import PROFILE,sample_unorm8
        if self.main_sampling_profile==PROFILE:return sample_unorm8(field,uv,wrap=wrap,linear=linear,origin='top')
        return self.sample_2d(field,uv,wrap=wrap,linear=linear,origin='top')

    def step(self,*,warp_uv,uniforms:dict,frame_wrap:float,stage_uniforms=None,minimum=(0,0,0),maximum=(1,1,1),
             edge_darken:float=0,warp_polar=None,composite_polar=None,draw=None,draw_scene=None,
             motion_vectors=None,motion_state=None,external_sample=None,on_sample=None,decay=None,
             legacy_time=None,hue_offsets=None,render_time=None,warp_original_uv=None)->PipelineResult:
        uv=np.asarray(warp_uv,dtype=np.float32)
        if uv.shape!=(self.height,self.width,2) or not np.all(np.isfinite(uv)):
            raise UnresolvedMath('explicit finite viewport-sized warp coordinates required')
        original=self.original_uv if warp_original_uv is None else np.asarray(warp_original_uv,dtype=np.float32)
        if original.shape!=uv.shape or not np.all(np.isfinite(original)):
            raise UnresolvedMath('explicit finite viewport-sized original warp coordinates required')
        if not np.isfinite(frame_wrap):raise UnresolvedMath('finite frame wrap required')
        stage_uniforms={} if stage_uniforms is None else stage_uniforms
        if not isinstance(stage_uniforms,dict) or set(stage_uniforms)-{'warp','composite'}:
            raise ValueError('stage uniforms must name warp/composite only')
        if any(not isinstance(values,dict) for values in stage_uniforms.values()):
            raise ValueError('stage uniform dictionaries required')
        if draw is not None and draw_scene is not None:
            raise ValueError('choose draw or source-scene draw callback')
        diffuse=None
        time=legacy_time if render_time is None else render_time
        if decay is not None:
            if not np.isfinite(decay):raise UnresolvedMath('finite live decay required')
            with np.errstate(over='ignore'):
                diffuse=np.array([min(float(np.float32(decay)),1)]*3+[1],dtype=np.float32)
        previous=self.feedback.copy()
        from motion_vectors import motion_active,draw_motion_vectors,motion_uv_surface
        if motion_vectors is not None and motion_state is not None:
            raise ValueError('choose source motion state or explicit callback, not both')
        write_motion=motion_state is not None and motion_active(motion_state)
        motion_source_frame=None
        pending_motion_uv=uv
        if write_motion and self.frame>0:
            previous=self._store(draw_motion_vectors(previous,motion_state,
                previous_uv=self.motion_uv,quantize=self.quantize,
                line_rendering_profile=self.line_rendering_profile,
                raster_subpixel_bits=self.motion_raster_subpixel_bits))
            motion_source_frame=self.motion_uv_frame
        if motion_vectors is not None and self.frame>0:
            previous=self._store(motion_vectors(previous,self.frame))
            if previous.shape!=self.feedback.shape:raise UnresolvedMath('motion vector surface shape changed')
        def update_blur():
            if not self.blur_levels:return {}
            return blur_bank(previous[...,:3],levels=self.blur_levels,minimum=minimum,
                             maximum=maximum,edge_darken=edge_darken,quantize=self.quantize,policy=self.blur_range_policy,
                             sampling_profile=self.texture_sampling_profile)
        old_blur=self.blur;warp_blur_frame=self.blur_source_frame
        if not self.warp_reads_blur:
            old_blur=update_blur();warp_blur_frame=self.frame-1
        low,high=native_ranges(minimum,maximum,policy=self.blur_range_policy)
        aspect_x=min(1,self.width/self.height);aspect_y=min(1,self.height/self.width)
        lowlevel={'_c0':[aspect_x,aspect_y,1/aspect_x,1/aspect_y],
                  '_c1':[0,0,0,0],
                  '_c5':[high[0]-low[0],low[0],high[1]-low[1],low[1]],
                  '_c6':[high[2]-low[2],low[2],low[0],high[0]],
                  '_c7':[self.width,self.height,1/self.width,1/self.height],
                  # MilkdropShader always binds the owned main texture, even
                  # when the authored section references only its dimensions.
                  'texsize_main':[self.width,self.height,1/self.width,1/self.height],
                  '_c13':[low[1],high[1],low[2],high[2]]}

        def stage(tree,name,main,blur,coordinates,polar,colour=None):
            nonlocal pending_motion_uv
            model,expression=self._lower_stage(tree,name,frame_wrap)
            values={**uniforms,**stage_uniforms.get(name,{}),**lowlevel,'_uv':coordinates}
            if name=='warp' and diffuse is not None:values['_vDiffuse']=diffuse
            if colour is not None:values['_vDiffuse']=colour
            if polar is not None:values['_rad_ang']=polar
            def sample(detail,sample_uv):
                texture=detail['canonical_texture'];policy=detail['sampling_policy']
                if texture=='main':
                    if policy.get('wrap') is None or policy.get('linear') is None:
                        raise UnresolvedMath('main sampler policy is unresolved')
                    return self._sample_main(main,sample_uv,wrap=policy['wrap'],linear=policy['linear'])
                if texture in {'blur1','blur2','blur3'}:
                    level=int(texture[-1])
                    if level not in blur:raise UnresolvedMath('required blur level was not supplied')
                    sampled=self.sample_2d(blur[level],sample_uv,wrap=False,linear=True,origin='bottom')
                    return np.concatenate((sampled,np.ones(sampled.shape[:-1]+(1,),dtype=np.float32)),axis=-1)
                if external_sample is None:raise UnresolvedMath('external texture input missing: '+texture)
                return external_sample(detail,sample_uv)
            trace=None if on_sample is None else lambda detail,uv,lanes:on_sample(name,detail,uv,lanes)
            output=evaluate_grid(expression,batch_shape=(self.height,self.width),inputs=values,sample=sample,on_sample=trace,coordinate_profile=self.coordinate_profile,numeric_policy=self.shader_numeric_policy)
            if name=='warp' and write_motion:
                motion=model.environment.get('_mv_tex_coords')
                if motion is None:raise UnresolvedMath('custom warp motion output is missing')
                motion=Field('member',(motion,),'float2',{'field':'xy','swizzle':True})
                if model.effects:motion=Field('sequence',tuple(model.effects)+(motion,),'float2')
                pending_motion_uv=evaluate_grid(motion,batch_shape=(self.height,self.width),inputs=values,sample=sample,coordinate_profile=self.coordinate_profile,numeric_policy=self.shader_numeric_policy)
            return output

        warp_coordinates=np.concatenate((uv,original),axis=-1)
        if self.warp_tree is None:
            if diffuse is None:raise UnresolvedMath('fixed warp requires live decay')
            warped=self._store(self._sample_main(previous,uv,wrap=frame_wrap>.0001,linear=True)*diffuse)
        else:warped=self._rgba(stage(self.warp_tree,'warp',previous,old_blur,warp_coordinates,warp_polar))
        pending_motion_uv=motion_uv_surface(pending_motion_uv,storage_profile=self.motion_uv_storage_profile) if write_motion else None
        new_blur=update_blur() if self.warp_reads_blur else old_blur
        drawn=warped.copy() if draw is None else self._store(draw(warped.copy(),self.frame))
        if draw_scene is not None:
            drawn=self._store(draw_scene(warped.copy(),self.frame,previous.copy()))
        if drawn.shape!=self.feedback.shape:raise UnresolvedMath('drawn feedback surface shape changed')
        # FinalComposite supplies a positive half-texel offset on its UV mesh.
        from composite_mesh import composite_fields
        composite=composite_fields(self.width,self.height,time=time,hue_offsets=hue_offsets,mesh=self.composite_mesh)
        composite_uv=composite['uv']
        if composite_polar is None:composite_polar=composite['polar']
        if self.composite_kind=='legacy_composite':
            from legacy_composite import legacy_display
            displayed=legacy_display(drawn,values=self.source_values,time=time,
                                     hue_offsets=hue_offsets,quantize=self.quantize,
                                     main=motion_state,control_policy=self.legacy_control_policy,
                                     sampling_profile=self.texture_sampling_profile)
        elif self.composite_tree is None:
            displayed=self._rgba(self._sample_main(drawn,composite_uv,wrap=True,linear=True)[...,:3])
        else:displayed=self._rgba(stage(self.composite_tree,'composite',drawn,new_blur,composite_uv,composite_polar,composite.get('diffuse')))
        history={'main_source_frame':self.frame-1,'warp_blur_source_frame':warp_blur_frame,
                 'composite_main_frame':self.frame,'composite_blur_source_frame':self.frame-1,
                 'feedback_is_pre_composite':True,'appearance_prediction_complete':False,
                 'warp_kind':'fixed_warp' if self.warp_tree is None else 'custom_warp',
                 'composite_kind':self.composite_kind}
        history['motion_vector_source_frame']=motion_source_frame
        history['motion_uv_storage_profile']=self.motion_uv_storage_profile
        history['motion_vector_line_profile']=self.line_rendering_profile
        history['motion_vector_raster_subpixel_bits']=self.motion_raster_subpixel_bits
        history['main_sampling_profile']=self.main_sampling_profile
        if self.texture_sampling_profile!='portable':history['texture_sampling_profile']=self.texture_sampling_profile
        history['composite_subpixel_bits']=self.composite_mesh.get('raster_subpixel_bits') if self.composite_kind!='legacy_composite' else None
        result=PipelineResult(self.frame,warped.copy(),drawn.copy(),displayed,history)
        # Commit only after both shader stages succeed; failed evaluation must
        # not silently advance the feedback/blur history.
        if write_motion:
            self.motion_uv=pending_motion_uv.copy();self.motion_uv_frame=self.frame
        self.feedback=drawn.copy();self.blur=new_blur;self.blur_source_frame=self.frame-1;self.frame+=1
        return result
