"""Provisional activity contributions for scoring research.

These mappings are hypotheses, not calibrated perceptual percentages. Missing
contributions remain absent; a maximum is not proof that all effects are known.
"""
import math
from numbers import Real


def combine_activity(base, *, coherent_flash=None, component_burst=None):
    values=[v for v in [base,coherent_flash,component_burst] if v is not None]
    if any(isinstance(v,bool) or not isinstance(v,Real) or not math.isfinite(v) or not 0<=v<=100 for v in values):
        raise ValueError('Known activity contributions must be finite scores from zero to 100')
    return max(values) if values else None


def coherent_flash_proxy(descriptors, *, fps):
    flashing=descriptors['flashing'];frames=descriptors['frames_measured']
    product=flashing.get('peak_paired_luma_area_product')
    if product is None:return None
    up=flashing['coherent_brightening_transitions'];down=flashing['coherent_darkening_transitions']
    values=[fps,frames,product,up,down]
    if any(isinstance(v,bool) or not isinstance(v,Real) or not math.isfinite(v) for v in values):
        raise ValueError('Finite measured flash evidence required')
    if fps<=0 or frames<=0 or not 0<=product<=1 or min(up,down)<0:
        raise ValueError('Invalid flash evidence domain')
    paired_rate=min(up,down)/(frames/fps)
    return 100*math.sqrt(product)*min(1,paired_rate)
