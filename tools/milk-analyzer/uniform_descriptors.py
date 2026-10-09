"""Descriptor reduction under an explicit complete-output uniformity premise.

Consume one stored RGBA per update, not a framebuffer. Reuse the established
temporal aggregator and retain unsupported optical-flow values as null.
"""
import cv2
import platform
import numpy as np
from descriptors import DescriptorStream,LUMA,effective_bins
from palette_features import hue_entropy


def _qualified_hsv_backend():
    # OpenCV 5.0.0 RGB2HSV_f uses four-float NEON groups followed by a
    # separately rounded scalar tail. Other dispatches need their own proof.
    if (cv2.__version__!='5.0.0' or platform.machine() not in {'arm64','aarch64'}
            or not cv2.useOptimized() or 'NEON' not in cv2.getCPUFeaturesLine()):
        raise ValueError('uniform HSV reduction requires qualified OpenCV 5.0.0 NEON backend')


def _hsv_groups(rgb,count):
    _qualified_hsv_backend()
    values=cv2.cvtColor(np.broadcast_to(rgb,(1,5,3)).copy(),cv2.COLOR_RGB2HSV)[0]
    vector_count=count-count%4
    counts=np.array([vector_count,count%4],dtype=np.int64)
    return values[[0,4]],counts


def _weighted_percentile(values,counts,percentile):
    order=np.argsort(values);values=values[order];counts=counts[order]
    total=int(counts.sum())
    if not total:return None
    rank=(total-1)*percentile/100
    lo=int(np.floor(rank));hi=int(np.ceil(rank));ends=np.cumsum(counts)
    a=values[np.searchsorted(ends,lo,side='right')]
    b=values[np.searchsorted(ends,hi,side='right')]
    return float(a+(b-a)*(rank-lo))


def _palette(rgb,count,settings):
    for threshold in (settings['value_floor'],settings['saturation_floor']):
        if isinstance(threshold,bool) or not np.isfinite(threshold) or threshold<=0:
            raise ValueError('positive finite chromatic thresholds required')
    hsv,counts=_hsv_groups(rgb,count)
    support=(hsv[:,1]>=settings['saturation_floor'])&(hsv[:,2]>=settings['value_floor'])
    bins=np.floor(hsv[:,0]/360*settings['hue_bins']).astype(int)%settings['hue_bins']
    mass=counts*support
    histogram=np.bincount(bins,weights=mass,minlength=settings['hue_bins'])
    chromatic=float(mass.sum())
    distance=np.abs((hsv[:,0].astype(np.float64)-30+180)%360-180)
    warmth=np.cos(np.pi*np.clip((distance-60)/60,0,1))
    return dict(hue_histogram=histogram,chromatic_weight=chromatic,
                chromatic_support=chromatic/count,hue_entropy_nats=hue_entropy(histogram),
                warm_cool=float(np.sum(warmth*mass)/chromatic) if chromatic else None)


def _hue_change(before,after,count,dt,settings):
    if isinstance(dt,bool) or not np.isfinite(dt) or dt<=0:
        raise ValueError('positive finite hue query time interval required')
    old,counts=_hsv_groups(before,count);new,_=_hsv_groups(after,count)
    support=old[:,1]>=settings['saturation_floor']
    support&=(old[:,2]>=settings['value_floor'])&(new[:,2]>=settings['value_floor'])
    support&=new[:,1]>=settings['saturation_floor']
    mass=counts*support
    rate=np.abs((new[:,0].astype(np.float64)-old[:,0]+180)%360-180)/360/dt
    if not np.all(np.isfinite(rate[mass>0])):
        raise ValueError('hue derivative numeric domain unresolved')
    return dict(p95_cycles_per_second=_weighted_percentile(rate,mass,95),
                maximum_cycles_per_second=float(rate[mass>0].max()) if mass.sum() else None,
                matched_chromatic_fraction=float(mass.sum()/count),matched_query_count=int(mass.sum()),
                limitations=['Same-location change can include motion crossings or changed materials',
                             'Shortest circular differences can alias faster hue evolution'])


class UniformDescriptorStream(DescriptorStream):
    def __init__(self,*,viewport,**kwargs):
        if not isinstance(viewport,(tuple,list)) or len(viewport)!=2 or any(type(n) is not int or n<=0 for n in viewport):
            raise ValueError('two positive integer uniform viewport dimensions required')
        super().__init__(**kwargs)
        _qualified_hsv_backend()
        self.width,self.height=viewport;self.size=self.width*self.height
        self.previous_luma=None
        x=(np.arange(self.width)+.5)/self.width
        y=(np.arange(self.height)+.5)/self.height
        self._grid_counts=np.outer(np.bincount(np.minimum((y*3).astype(int),2),minlength=3),
                                   np.bincount(np.minimum((x*3).astype(int),2),minlength=3)).tolist()
        self._centre_count=int(np.count_nonzero((x>=.25)&(x<.75))*np.count_nonzero((y>=.25)&(y<.75)))

    def add(self,frame):
        raise ValueError('uniform descriptor stream requires one proven stored RGBA, not display fields')

    def _mean(self,value,dtype=np.float32):
        # Match the existing repeated-pixel reduction order with a zero-stride
        # read-only view. No RGB/display field is constructed or retained.
        return float(np.broadcast_to(np.asarray(value,dtype=dtype),(self.height,self.width)).mean())

    def add_uniform(self,*,time,rgba,warp_query_displacement=None):
        time=float(time);rgba=np.asarray(rgba,dtype=np.float32)
        if not np.isfinite(time) or rgba.shape!=(4,) or not np.all(np.isfinite(rgba)) or np.any((rgba<0)|(rgba>1)):
            raise ValueError('finite time and normalized uniform RGBA vector required')
        if self.previous_time is not None and time<=self.previous_time:
            raise ValueError('strictly increasing descriptor time required')
        if warp_query_displacement is not None and (not np.isfinite(warp_query_displacement) or warp_query_displacement<0):
            raise ValueError('finite nonnegative proved warp displacement required')
        rgb=rgba[:3].copy()
        # NumPy's width-dependent matmul kernel can round a dot differently
        # from a one-pixel call. Use one row with the real width, not a frame.
        luma=np.float32((np.broadcast_to(rgb,(1,self.width,3)).copy()@LUMA)[0,0])
        if self.seen>=self.warmup:
            visible=bool(np.max(rgb)>=self.settings['value_floor'])
            self.spatial_rows.append({'time':time,'supported_pixels':self.size if visible else 0,
                'screen_fraction':float(visible),'bounds':{'minimum':[0.,0.],'maximum':[1.,1.]} if visible else None,
                'centre_support_pixels':self._centre_count if visible else 0,
                'grid_counts':self._grid_counts if visible else [[0]*3 for _ in range(3)]})
            palette=_palette(rgb,self.size,self.settings)
            # Saturation's full-field conversion runs row by row, whereas
            # palette/hue-change flatten all pixels before conversion.
            hsv=cv2.cvtColor(np.broadcast_to(rgb,(1,self.width,3)).copy(),cv2.COLOR_RGB2HSV)
            histogram=palette['hue_histogram']
            chromatic_mass=palette['chromatic_weight']
            self.hue_mass+=histogram;self.chromatic_mass+=chromatic_mass
            if palette['warm_cool'] is not None:self.warm_mass+=palette['warm_cool']*chromatic_mass
            mean_luma=self._mean(luma)
            contrast=abs(float(np.float32(luma-np.float32(mean_luma))))
            self.rows.append(dict(time=time,mean_luma=mean_luma,contrast=contrast,
                saturation=float(np.broadcast_to(hsv[...,1],(self.height,self.width)).mean()),coloured_fraction=palette['chromatic_support'],
                hue_entropy=palette['hue_entropy_nats'],effective_hue_bins=effective_bins(histogram),
                query_displacement=warp_query_displacement))
            if len(self.rows)>1:
                dt=time-self.previous_time;delta=np.float32(luma-self.previous_luma)
                positive=float(delta>=self.settings['brightness_jump'])
                negative=float(delta<=-self.settings['brightness_jump'])
                changed=float(abs(delta)>=self.settings['brightness_jump'])
                signed=self._mean(delta);change=abs(signed)
                supported=visible or bool(np.max(self.previous)>=self.settings['value_floor'])
                amplitude=np.float32(np.max(np.abs(rgb-self.previous)))
                rgb_area=float(amplitude>=self.settings['rgb_jump'])
                hue=_hue_change(self.previous,rgb,self.size,dt,self.settings)
                def region(area,amount):
                    return {'area':area,'mean_amplitude':self._mean(amount) if area else None,
                            'maximum_amplitude':float(amount) if area else None}
                up=bool(positive>=self.settings['coherent_area'] and signed>=self.settings['brightness_jump'])
                down=bool(negative>=self.settings['coherent_area'] and signed<=-self.settings['brightness_jump'])
                event={'start_time':self.previous_time,'end_time':time,'dt':dt,'signed_mean_luma_delta':signed,
                       'brightening':region(positive,delta),'darkening':region(negative,-delta),
                       'rgb':region(rgb_area,amplitude),'coherent_up':up,'coherent_down':down,
                       'motion_crossing_ruled_out':False}
                motion=dict(available=False,support=0.,median_speed=None,p95_speed=None,velocity=None,
                    brightness_change_p95=None,brightening_screen_area=None,darkening_screen_area=None,
                    untracked_brightness_change_screen_area=changed,
                    reason='insufficient visible texture or correspondence')
                self.transitions.append(dict(dt=dt,mean_luma_jump=change,event=event,hue_change=hue,
                    paired_luma_area_product=change*changed,brightening_area=positive,darkening_area=negative,
                    visible_brightening_fraction=positive if supported else 0.,
                    visible_darkening_fraction=negative if supported else 0.,brightness_area=changed,
                    rgb_area=rgb_area,coherent_up=up,coherent_down=down,motion=motion))
        self.previous=rgb;self.previous_luma=luma;self.previous_time=time;self.seen+=1

    def report(self):
        result=super().report()
        result['uniform_reduction']={'policy':'complete-uniform-output-descriptors-v1',
            'viewport':[self.width,self.height],'display_fields_constructed':False,
            'uniformity_established_by_this_class':False,
            'premise':'Caller proves complete final stored output is uniform for every admitted update',
            'numeric_scope':'Same scalar kernels and temporal aggregator; repeated reduction roundoff retained',
            'optical_flow':'No trackable texture; unsupported flow stays null'}
        return result
