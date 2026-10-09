"""Two-target authored recurrence from MilkdropPreset's detail render path.

Equations, prepared geometry and random uniforms are supplied once by the
forecaster. This coordinator executes only mathematical raster stages. It does
not assert resource allocation, shader compilation or GPU precision parity.
"""
import copy
import numpy as np
from authored_canvas import combine_detail,block_downsample


class DetailPipeline:
    def __init__(self,authored,native,*,alpha):
        amount=np.float32(alpha)
        if not np.isfinite(amount) or not 0<=amount<=1:
            raise ValueError('finite detail gain within0..1 required')
        scale=native.width//authored.width
        if scale<2 or native.width!=authored.width*scale or native.height!=authored.height*scale:
            raise ValueError('same integer detail ratio of at least2 required')
        if native.shader_canvas_size!=(authored.width,authored.height):
            raise ValueError('native uniforms must report authored canvas')
        if authored.quantize!=native.quantize:
            raise ValueError('matching target storage required')
        if authored.warp_reads_blur!=native.warp_reads_blur:
            raise ValueError('matching warp blur lifecycle required')
        self.authored=authored
        self.native=native
        self.alpha=float(amount)
        self.scale=scale
        self.authored.feedback=block_downsample(self.native.feedback,scale,quantize=True)

    @property
    def stage_resolution(self):
        return self.native.stage_resolution

    @staticmethod
    def _snapshot(pipeline):
        return {name:copy.deepcopy(getattr(pipeline,name)) for name in
                ('feedback','blur','frame','first_frame','blur_source_frame','motion_uv','motion_uv_frame')}

    def update_gain(self,alpha):
        """Reset on retain-detail class changes; positive gains share state."""
        amount=np.float32(alpha)
        if not np.isfinite(amount) or not 0<=amount<=1:
            raise ValueError('finite detail gain within0..1 required')
        if (amount>0)!=(self.alpha>0):
            # Native pre-composite feedback is the initializer. Composite output
            # never owns recurrence, even when its colours look more natural.
            self.authored.feedback=block_downsample(self.native.feedback,self.scale,quantize=True)
            for pipeline in (self.authored,self.native):
                # Same-size TextureAttachment::ReplaceTexture retains its UV
                # texture, including the native stale-map re-enable behaviour.
                pipeline.first_frame=True
        self.alpha=float(amount)

    def step(self,*,authored_warp_uv,native_warp_uv,uniforms,frame_wrap,
             authored_original_uv=None,native_original_uv=None,
             authored_polar=None,native_polar=None,draw_authored=None,draw_native=None,**kwargs):
        if self.authored.frame!=self.native.frame:
            raise ValueError('authored/native frame schedules differ')
        forbidden={'supplied_blur','supplied_warp','before_geometry','render_composite',
                   'blur_before_motion','write_motion_uv','draw_scene','draw','warp_uv',
                   'warp_original_uv','warp_polar'} & kwargs.keys()
        if forbidden:raise ValueError('coordinator owns stage ordering: '+','.join(sorted(forbidden)))
        snapshots=[self._snapshot(p) for p in (self.authored,self.native)]
        previous_blur=copy.deepcopy(self.authored.blur)
        previous_uv=copy.deepcopy(self.authored.motion_uv)
        previous_uv_frame=self.authored.motion_uv_frame
        try:
            low=self.authored.step(warp_uv=authored_warp_uv,warp_original_uv=authored_original_uv,
                warp_polar=authored_polar,uniforms=uniforms,frame_wrap=frame_wrap,
                draw_scene=draw_authored,render_composite=False,blur_before_motion=True,**kwargs)
            # Both targets consume the previous authored UV map. Native motion
            # minimums and geometry still use the native target's dimensions.
            self.native.motion_uv=previous_uv
            self.native.motion_uv_frame=previous_uv_frame
            warp_blur=previous_blur if self.authored.warp_reads_blur else self.authored.blur
            banks=(warp_blur,self.authored.blur)
            def combine(field):
                return combine_detail(low.warped,field if self.alpha>0 else None,
                    alpha=self.alpha,output_size=(self.native.width,self.native.height),
                    quantize=self.native.quantize,sampling_profile=self.native.texture_sampling_profile)
            base=None
            if self.alpha==0:
                base=combine_detail(low.warped,None,alpha=0,
                    output_size=(self.native.width,self.native.height),
                    quantize=self.native.quantize,sampling_profile=self.native.texture_sampling_profile)
            result=self.native.step(warp_uv=native_warp_uv,warp_original_uv=native_original_uv,
                warp_polar=native_polar,uniforms=uniforms,frame_wrap=frame_wrap,
                supplied_blur=banks,supplied_warp=base,
                before_geometry=combine if self.alpha>0 else None,
                draw_scene=draw_native,write_motion_uv=False,**kwargs)
        except Exception:
            for pipeline,snapshot in zip((self.authored,self.native),snapshots):
                for name,value in snapshot.items():setattr(pipeline,name,value)
            raise
        result.history.update(authored_canvas=[self.authored.width,self.authored.height],
            native_size=[self.native.width,self.native.height],feedback_detail_alpha=self.alpha,
            feedback_detail_scale=self.scale,authored_feedback_is_independent=True,
            authored_warp_blur_source_frame=low.history['warp_blur_source_frame'])
        # Native replay consumes the previous authored map and does not publish.
        # Keep that native flag while reporting the actual producer separately.
        result.history.update(authored_motion_uv_written=low.history['motion_uv_written'],
            authored_motion_uv_frame=self.authored.motion_uv_frame,
            authored_motion_uv_contract=copy.deepcopy(low.history['motion_uv_contract']))
        return result
