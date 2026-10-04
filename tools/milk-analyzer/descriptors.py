"""Numerical descriptors from source-model predicted fields, not inspection.

Encoded RGB luma is a proxy, not calibrated screen luminance. Visible motion is
an optical-flow estimate on the source prediction; geometry displacement is
reported separately. Sampling/estimator limits remain explicit.
"""
import cv2
import numpy as np


DEFAULTS = dict(hue_bins=12, value_floor=.05, saturation_floor=.15,
                brightness_jump=.1, rgb_jump=.1, coherent_area=.2,
                motion_min_contrast=.02, flow_consistency_pixels=.5,
                flow_residual_levels=20, motion_support_pixels=12)
LUMA = np.array([.2126,.7152,.0722],dtype=np.float32)


def effective_bins(histogram):
    total=float(np.sum(histogram))
    if total==0:return 0.
    probabilities=np.asarray(histogram,dtype=np.float64)/total
    probabilities=probabilities[probabilities>0]
    return float(np.exp(-np.sum(probabilities*np.log(probabilities))))


def visible_motion(old, new, dt, settings):
    changed=np.abs(new-old)>=settings['brightness_jump']
    empty=dict(available=False,support=0.,median_speed=None,p95_speed=None,
               velocity=None,brightness_change_p95=None,brightening_screen_area=None,
               darkening_screen_area=None,untracked_brightness_change_screen_area=float(changed.mean()),
               reason='insufficient visible texture or correspondence')
    height,width=old.shape
    if min(height,width)<16 or min(float(old.std()),float(new.std()))<settings['motion_min_contrast']:
        return empty
    def normalize(image):
        return np.clip(128+(image-float(image.mean()))/max(float(image.std()),.03)*40,0,255).astype(np.uint8)
    a,b=normalize(old),normalize(new)
    forward=cv2.calcOpticalFlowFarneback(a,b,None,.5,3,15,3,5,1.2,0)
    backward=cv2.calcOpticalFlowFarneback(b,a,None,.5,3,15,3,5,1.2,0)
    x,y=np.meshgrid(np.arange(width,dtype=np.float32),np.arange(height,dtype=np.float32))
    qx,qy=x+forward[...,0],y+forward[...,1]
    reversed_flow=cv2.remap(backward,qx,qy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    reconstructed=cv2.remap(b.astype(np.float32),qx,qy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    gx=cv2.Sobel(a.astype(np.float32),cv2.CV_32F,1,0)
    gy=cv2.Sobel(a.astype(np.float32),cv2.CV_32F,0,1)
    valid=(np.hypot(gx,gy)>8)&(qx>=3)&(qx<width-3)&(qy>=3)&(qy<height-3)
    valid[:3]=valid[-3:]=False;valid[:,:3]=valid[:,-3:]=False
    valid&=np.linalg.norm(forward+reversed_flow,axis=-1)<=settings['flow_consistency_pixels']
    valid&=np.abs(reconstructed-a)<=settings['flow_residual_levels']
    if np.count_nonzero(valid)<settings['motion_support_pixels']:return empty
    velocity=forward/np.array([width*dt,height*dt],dtype=np.float32)
    speed=np.linalg.norm(velocity[valid],axis=-1)
    matched_luma=cv2.remap(new.astype(np.float32),qx,qy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    matched_delta=matched_luma-old
    brightness_change=float(np.percentile(np.abs(matched_delta[valid]),95))
    return dict(available=True,support=float(valid.mean()),median_speed=float(np.median(speed)),
                p95_speed=float(np.percentile(speed,95)),velocity=np.median(velocity[valid],axis=0).tolist(),
                brightness_change_p95=brightness_change,
                brightening_screen_area=float(np.mean(valid&(matched_delta>=settings['brightness_jump']))),
                darkening_screen_area=float(np.mean(valid&(matched_delta<=-settings['brightness_jump']))),
                untracked_brightness_change_screen_area=float(np.mean(changed&~valid)),
                reason='brightness-normalized flow with backward and residual consistency checks')


class DescriptorStream:
    def __init__(self, *, warmup_frames=0, settings=None):
        if type(warmup_frames) is not int or warmup_frames<0:
            raise ValueError('nonnegative integer descriptor warmup required')
        self.settings={**DEFAULTS,**(settings or {})}
        if set(self.settings)!=set(DEFAULTS):raise ValueError('unknown descriptor setting')
        for key,value in self.settings.items():
            if not np.isfinite(value) or value<=0:raise ValueError('positive finite descriptor setting: '+key)
        if type(self.settings['hue_bins']) is not int:raise ValueError('integer hue bin count required')
        self.warmup=warmup_frames;self.seen=0;self.previous=None;self.previous_time=None
        self.rows=[];self.transitions=[];self.hue_mass=np.zeros(self.settings['hue_bins'])

    def add(self, frame):
        time=float(frame['time']);rgba=np.asarray(frame['display'],dtype=np.float32)
        if not np.isfinite(time) or not np.all(np.isfinite(rgba)):
            raise ValueError('finite descriptor time/field required')
        if rgba.ndim!=3 or rgba.shape[-1]!=4 or min(rgba.shape[:2])<1 or np.any((rgba<0)|(rgba>1)):
            raise ValueError('normalized predicted RGBA field required')
        if self.previous_time is not None and time<=self.previous_time:
            raise ValueError('strictly increasing descriptor time required')
        if self.previous is not None and rgba.shape[:2]!=self.previous.shape[:2]:
            raise ValueError('fixed descriptor viewport required')
        rgb=rgba[...,:3].copy();luma=rgb@LUMA
        uv=frame.get('warp_uv');query_displacement=None
        if uv is not None:
            coordinates=np.asarray(uv,dtype=np.float32)
            if coordinates.shape!=rgb.shape[:2]+(2,) or not np.all(np.isfinite(coordinates)):
                raise ValueError('finite viewport-matched warp query field required')
            height,width=rgb.shape[:2]
            x,y=np.meshgrid((np.arange(width,dtype=np.float32)+.5)/width,
                            (np.arange(height,dtype=np.float32)+.5)/height)
            query_displacement=float(np.mean(np.linalg.norm(coordinates.astype(np.float64)-np.stack((x,y),axis=-1),axis=-1)))
        if self.seen>=self.warmup:
            hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
            coloured=(hsv[...,1]>=self.settings['saturation_floor'])&(hsv[...,2]>=self.settings['value_floor'])
            bins=np.floor(hsv[...,0]/360*self.settings['hue_bins']).astype(int)%self.settings['hue_bins']
            histogram=np.bincount(bins[coloured],minlength=self.settings['hue_bins'])
            self.hue_mass+=histogram
            self.rows.append(dict(time=time,mean_luma=float(luma.mean()),contrast=float(luma.std()),
                saturation=float(hsv[...,1].mean()),coloured_fraction=float(coloured.mean()),
                effective_hue_bins=effective_bins(histogram),query_displacement=query_displacement))
            if len(self.rows)>1:
                dt=time-self.previous_time;old_luma=self.previous@LUMA;delta=luma-old_luma
                positive=float(np.mean(delta>=self.settings['brightness_jump']))
                negative=float(np.mean(delta<=-self.settings['brightness_jump']))
                change=abs(float(delta.mean()))
                visible=(np.max(rgb,axis=-1)>=self.settings['value_floor'])|(np.max(self.previous,axis=-1)>=self.settings['value_floor'])
                support=int(np.count_nonzero(visible))
                local_up=float(np.count_nonzero((delta>=self.settings['brightness_jump'])&visible)/support) if support else 0.
                local_down=float(np.count_nonzero((delta<=-self.settings['brightness_jump'])&visible)/support) if support else 0.
                motion=visible_motion(old_luma,luma,dt,self.settings)
                self.transitions.append(dict(dt=dt,mean_luma_jump=change,
                    paired_luma_area_product=change*float(np.mean(np.abs(delta)>=self.settings['brightness_jump'])),
                    brightening_area=positive,darkening_area=negative,
                    visible_brightening_fraction=local_up,visible_darkening_fraction=local_down,
                    brightness_area=float(np.mean(np.abs(delta)>=self.settings['brightness_jump'])),
                    rgb_area=float(np.mean(np.max(np.abs(rgb-self.previous),axis=-1)>=self.settings['rgb_jump'])),
                    coherent_up=positive>=self.settings['coherent_area'] and float(delta.mean())>=self.settings['brightness_jump'],
                    coherent_down=negative>=self.settings['coherent_area'] and float(delta.mean())<=-self.settings['brightness_jump'],
                    motion=motion))
        self.previous=rgb;self.previous_time=time;self.seen+=1

    def report(self):
        rows=self.rows;transitions=self.transitions
        mean=lambda key:float(np.mean([row[key] for row in rows])) if rows else None
        peak=lambda key:max((row[key] for row in transitions),default=None)
        valid=[row['motion'] for row in transitions if row['motion']['available']]
        displacements=[row['query_displacement'] for row in rows if row['query_displacement'] is not None]
        frequency=resolution=nyquist=None;regular=None;spectral_fraction=None
        if len(rows)>=3:
            times=np.array([row['time'] for row in rows]);intervals=np.diff(times)
            regular=bool(np.allclose(intervals,intervals[0],rtol=1e-6,atol=1e-9))
            if regular:
                dt=float(intervals[0]);nyquist=.5/dt;resolution=1/(len(rows)*dt)
                if len(rows)>=16:
                    values=np.array([row['mean_luma'] for row in rows])
                    design=np.stack((times-times[0],np.ones_like(times)),axis=-1)
                    detrended=values-design@np.linalg.lstsq(design,values,rcond=None)[0]
                    power=np.abs(np.fft.rfft(detrended))**2;power[0]=0
                    if float(power.sum())>1e-12:
                        index=int(np.argmax(power));frequency=float(np.fft.rfftfreq(len(rows),dt)[index])
                        spectral_fraction=float(power[index]/power.sum())
        acceleration=[]
        for i in range(1,len(transitions)):
            a,b=transitions[i-1]['motion'],transitions[i]['motion']
            if a['available'] and b['available']:
                acceleration.append(float(np.linalg.norm(np.array(b['velocity'])-a['velocity'])/
                    ((transitions[i]['dt']+transitions[i-1]['dt'])/2)))
        return dict(schema_version=1,basis='Numerical source-predicted display fields; no native visual inspection',
            appearance_accuracy_verified=False,frames_measured=len(rows),warmup_frames=self.warmup,settings=dict(self.settings),
            colour=dict(mean_luma=mean('mean_luma'),mean_contrast=mean('contrast'),mean_saturation=mean('saturation'),
                        mean_coloured_fraction=mean('coloured_fraction'),mean_effective_hue_bins=mean('effective_hue_bins'),
                        temporal_effective_hue_bins=effective_bins(self.hue_mass)),
            flashing=dict(peak_mean_luma_jump=peak('mean_luma_jump'),peak_brightness_change_area=peak('brightness_area'),
                          peak_paired_luma_area_product=peak('paired_luma_area_product'),
                          peak_brightening_screen_area=peak('brightening_area'),peak_darkening_screen_area=peak('darkening_area'),
                          peak_visible_brightening_fraction=peak('visible_brightening_fraction'),
                          peak_visible_darkening_fraction=peak('visible_darkening_fraction'),
                          peak_rgb_change_area=peak('rgb_area'),coherent_brightening_transitions=sum(row['coherent_up'] for row in transitions),
                          coherent_darkening_transitions=sum(row['coherent_down'] for row in transitions),
                          dominant_sampled_brightness_hz=frequency,spectral_peak_fraction=spectral_fraction,
                          frequency_resolution_hz=resolution,nyquist_hz=nyquist,uniform_sampling=regular),
            motion=dict(available_transition_fraction=len(valid)/len(transitions) if transitions else 0.,
                        peak_untracked_brightness_change_screen_area=max((row['motion']['untracked_brightness_change_screen_area'] for row in transitions),default=None),
                        matched_brightness_change_p95=float(np.percentile([row['brightness_change_p95'] for row in valid],95)) if valid else None,
                        peak_matched_brightness_change_p95=max((row['brightness_change_p95'] for row in valid),default=None),
                        peak_matched_brightening_screen_area=max((row['brightening_screen_area'] for row in valid),default=None),
                        peak_matched_darkening_screen_area=max((row['darkening_screen_area'] for row in valid),default=None),
                        mean_supported_area=float(np.mean([row['support'] for row in valid])) if valid else None,
                        median_speed_viewports_per_second=float(np.median([row['median_speed'] for row in valid])) if valid else None,
                        p95_speed_viewports_per_second=float(np.percentile([row['p95_speed'] for row in valid],95)) if valid else None,
                        mean_acceleration_viewports_per_second_squared=float(np.mean(acceleration)) if acceleration else None,
                        mean_warp_query_displacement=float(np.mean(displacements)) if displacements else None),
            structure={'fractal':None},bass_response=None,mood_assignment=None,
            aggregation={'motion_speed':'Median of per-transition supported-pixel medians; upper-tail summary is the 95th percentile of transition pixel-p95 values',
                         'matched_brightness':'Changes along estimated motion correspondence; screen areas include only valid pixels. Missing correspondence is unknown. Peak summaries retain rare transitions; separate peaks need not refer to the same event.',
                         'palette':'Hard circular hue bins on coloured pixels; spatial per-frame and combined temporal diversity reported separately',
                         'flashing':'Peak sampled changes and coherent transition counts; no whole-program no-flashing guarantee'},
            limitations=['Motion is an estimator with incomplete texture/correspondence support',
                         'Frequency covers this sampled window only; aliasing and later events are not ruled out',
                         'RGB luma is an encoded display proxy; physical screen luminance is not calibrated',
                         'Fractal structure, causal bass response and audience thresholds need separate evidence'])
