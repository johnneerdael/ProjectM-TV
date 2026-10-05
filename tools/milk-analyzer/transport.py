"""Sampling-to-feature transport math on explicitly declared source fields.

A shader queries source position q(p). Local visible feature transport uses the
inverse Jacobian. It does not imply brightness gain or a global attractor for a
changing nonlinear feedback field. No native frames are read by this module.
"""
import math
import numpy as np


def _finite(value,name):
    array=np.asarray(value,dtype=np.float64)
    if not np.all(np.isfinite(array)):raise ValueError('nonfinite '+name)
    return array


def sampling_jacobian(coordinates,*,periodic_axes=(False,False)):
    values=_finite(coordinates,'sampling coordinates')
    if values.ndim!=3 or values.shape[-1]!=2 or min(values.shape[:2])<2:
        raise ValueError('regular viewport grid HxWx2 with at least two samples per axis required')
    if len(periodic_axes)!=2 or any(type(v) is not bool for v in periodic_axes):raise ValueError('explicit two-axis periodic policy required')
    height,width=values.shape[:2];partials=[]
    for axis,dimension in [(1,width),(0,height)]:
        difference=np.diff(values,axis=axis)
        for component,periodic in enumerate(periodic_axes):
            if periodic:difference[...,component]=np.mod(difference[...,component]+.5,1)-.5
        derivative=np.empty_like(values)
        if axis==1:
            derivative[:,0]=difference[:,0]*dimension;derivative[:,-1]=difference[:,-1]*dimension
            derivative[:,1:-1]=(difference[:,:-1]+difference[:,1:])*(dimension*.5)
        else:
            derivative[0]=difference[0]*dimension;derivative[-1]=difference[-1]*dimension
            derivative[1:-1]=(difference[:-1]+difference[1:])*(dimension*.5)
        partials.append(derivative)
    return np.stack(partials,axis=-1)


def local_transport(jacobian,*,singular_tolerance=1e-10):
    matrix=_finite(jacobian,'sampling Jacobian')
    if matrix.shape[-2:]!=(2,2):raise ValueError('2x2 sampling Jacobian required')
    if not math.isfinite(singular_tolerance) or singular_tolerance<=0:raise ValueError('positive singular tolerance required')
    singular=np.linalg.svd(matrix,compute_uv=False)
    if np.any(singular[...,-1]<=singular_tolerance):raise ValueError('singular sampling map; inverse feature transport unresolved')
    inverse=np.linalg.inv(matrix)
    return {'forward_jacobian':inverse,'forward_singular_values':np.linalg.svd(inverse,compute_uv=False),
            'area_scale':np.abs(np.linalg.det(inverse)),
            'validity':'local stencil under declared source state; no global brightness or repeated-path guarantee'}


def affine_transport(matrix,offset,*,steps):
    query=_finite(matrix,'affine sampling matrix');translation=_finite(offset,'affine sampling offset')
    if query.shape!=(2,2) or translation.shape!=(2,):raise ValueError('2D affine sampling map required')
    if type(steps) is not int or not 0<=steps<=100000:raise ValueError('finite nonnegative step count required')
    local=local_transport(query);forward=local['forward_jacobian']
    homogeneous=np.eye(3);homogeneous[:2,:2]=forward;homogeneous[:2,2]=-forward@translation
    repeated=np.linalg.matrix_power(homogeneous,steps)
    if not np.all(np.isfinite(repeated)):raise ValueError('nonfinite repeated affine transport')
    return {'forward_per_step':forward,'forward_after_steps':repeated[:2,:2],
            'offset_after_steps':repeated[:2,2],
            'singular_values_after_steps':np.linalg.svd(repeated[:2,:2],compute_uv=False),
            'area_scale_after_steps':abs(float(np.linalg.det(repeated[:2,:2]))),
            'validity':'constant affine sampling map only; assumes no addressing branch changes'}


def separable_fixed_points(scales,offsets,*,periodic_axes=(False,False)):
    """Fixed points q(p)=p per axis, including integer branches of frac(q).

Results are in the closed unit interval. Neutral axes return 'all' when their
offset is an identity addressing branch. This identifies candidate stationary
positions, not global attraction or intensity under nonlinear feedback.
"""
    scales=_finite(scales,'separable scales');offsets=_finite(offsets,'separable offsets')
    if scales.shape!=(2,) or offsets.shape!=(2,) or len(periodic_axes)!=2 or any(type(v) is not bool for v in periodic_axes):
        raise ValueError('two separable axes and explicit periodic policy required')
    result=[]
    for scale,offset,periodic in zip(scales,offsets,periodic_axes):
        denominator=float(scale-1)
        if abs(denominator)<1e-12:
            identity=abs(offset-round(offset))<1e-12 if periodic else abs(offset)<1e-12
            result.append('all' if identity else []);continue
        if periodic:
            lo,hi=sorted([float(offset),float(offset+denominator)])
            start=math.ceil(lo-1e-12);end=math.floor(hi+1e-12)
            if end-start>10000:raise ValueError('too many periodic fixed-point branches')
            branches=range(start,end+1)
        else:branches=[0]
        points=[(branch-offset)/denominator for branch in branches]
        result.append([float(p) for p in points if -1e-10<=p<=1+1e-10])
    return result
