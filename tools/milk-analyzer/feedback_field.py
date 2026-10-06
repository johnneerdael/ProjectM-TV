"""Extract and compose supported spatial colour feedback from source expressions.

An affine transfer is a matrix on one RGBA sample plus a constant bias. This
does not replace nonlinear or multi-coordinate shader evaluation. Unresolved
expressions return None; they are never approximated as a zero response.
"""
from dataclasses import dataclass
import re
import numpy as np
from field_math import evaluate,UnresolvedMath,SWIZZLE
from shader_fields import Field
from spatial import sample2d


@dataclass(frozen=True)
class AffineTransfer:
    matrix:np.ndarray
    bias:np.ndarray
    sample:Field|None


def affine_main_transfer(expression:Field,*,inputs=None)->AffineTransfer|None:
    """Retain the sampled coordinate graph, channels and renderer history.

    Supplied uniform inputs are explicit conditions, not a proof over every
    possible audio value. Texture values are symbolic during extraction.
    """
    def width(dtype):
        match=re.fullmatch(r'float([1-4])?',dtype)
        return int(match[1] or 1) if match else None

    def resize(term,count):
        n=len(term.bias)
        if n==count:return term
        if n==1:
            return AffineTransfer(np.repeat(term.matrix,count,axis=0),np.repeat(term.bias,count),term.sample)
        if n>count:return AffineTransfer(term.matrix[:count],term.bias[:count],term.sample)
        return AffineTransfer(np.pad(term.matrix,((0,count-n),(0,0))),np.pad(term.bias,(0,count-n)),term.sample)

    def combine(left,right,op,count):
        left=resize(left,count);right=resize(right,count)
        if left.sample is not None and right.sample is not None and left.sample!=right.sample:
            return None
        sample=left.sample if left.sample is not None else right.sample
        if op=='add':return AffineTransfer(left.matrix+right.matrix,left.bias+right.bias,sample)
        if op=='subtract':return AffineTransfer(left.matrix-right.matrix,left.bias-right.bias,sample)
        if op=='multiply':
            if left.sample is not None and right.sample is not None:return None
            dependent,constant=(left,right) if left.sample is not None else (right,left)
            return AffineTransfer(dependent.matrix*constant.bias[:,None],dependent.bias*constant.bias,sample)
        if op=='divide':
            if right.sample is not None or np.any(right.bias==0):return None
            return AffineTransfer(left.matrix/right.bias[:,None],left.bias/right.bias,sample)
        return None

    def visit(node):
        count=width(node.dtype)
        if count is None:return None
        try:
            value=evaluate(node,inputs=inputs).reshape(-1)
            return AffineTransfer(np.zeros((len(value),4),dtype=np.float32),value,None)
        except UnresolvedMath:pass
        if node.op=='sample' and node.detail.get('canonical_texture')=='main' and node.detail.get('intrinsic')=='tex2D':
            return AffineTransfer(np.eye(4,dtype=np.float32),np.zeros(4,dtype=np.float32),node)
        if node.op=='member' and node.detail.get('swizzle'):
            term=visit(node.args[0])
            if term is None:return None
            indices=[SWIZZLE[c] for c in node.detail['field']]
            return AffineTransfer(term.matrix[indices],term.bias[indices],term.sample)
        if node.op=='cast':
            term=visit(node.args[0]);return resize(term,count) if term else None
        if node.op=='construct':
            terms=[visit(arg) for arg in node.args]
            if any(term is None for term in terms):return None
            samples=[term.sample for term in terms if term.sample is not None]
            if samples and any(sample!=samples[0] for sample in samples[1:]):return None
            return resize(AffineTransfer(np.concatenate([t.matrix for t in terms]),
                         np.concatenate([t.bias for t in terms]),samples[0] if samples else None),count)
        if node.op in {'add','subtract','multiply','divide'}:
            left,right=(visit(arg) for arg in node.args)
            return combine(left,right,node.op,count) if left and right else None
        if node.op=='unary' and node.detail['operator'] in {0,1}:
            term=visit(node.args[0])
            if term is None:return None
            sign=-1 if node.detail['operator']==0 else 1
            return AffineTransfer(sign*term.matrix,sign*term.bias,term.sample)
        return None
    return visit(expression)


def unorm8(value):
    """Round represented float32 inputs to UNORM8 without premature product rounding.

    Nearest-even remains the mathematical contract; native exact halfway ties
    and dithering are not universally verified.
    """
    array=np.asarray(value,dtype=np.float32)
    if not np.all(np.isfinite(array)):raise ValueError('nonfinite framebuffer output')
    return (np.rint(np.clip(array,0,1).astype(np.float64)*255)/255).astype(np.float32)


def apply_affine_transfer(previous,sampling_uv,transfer:AffineTransfer,*,wrap:bool,quantize:bool=True):
    """Compose an extracted warp transfer on explicit pre-composite fields.

    The caller must evaluate transfer.sample.args[0] to produce sampling_uv.
    Main sampling's vertical flip and OpenGL origin compose into top-origin
    sampling on this logical feedback field. Draws/blur/composite are separate.
    """
    field=np.asarray(previous,dtype=np.float32)
    if field.ndim!=3 or field.shape[2] not in (3,4):raise ValueError('RGB/RGBA feedback field required')
    if transfer is None or transfer.sample is None:raise ValueError('sample-dependent affine transfer required')
    if field.shape[2]==3:
        if np.any(transfer.matrix[:,3]!=0):raise ValueError('explicit alpha state required')
        field=np.concatenate((field,np.zeros(field.shape[:2]+(1,),dtype=np.float32)),axis=-1)
    linear=transfer.sample.detail.get('sampling_policy',{}).get('linear',True)
    if linear is None:raise ValueError('sampler filtering policy unresolved')
    sampled=sample2d(field,sampling_uv,wrap=wrap,linear=linear,origin='top')
    result=sampled@transfer.matrix.T+transfer.bias
    if not np.all(np.isfinite(result)):raise ValueError('nonfinite feedback output')
    return unorm8(result) if quantize else np.clip(result,0,1)
