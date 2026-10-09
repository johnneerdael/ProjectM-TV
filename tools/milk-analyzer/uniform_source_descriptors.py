"""One-lane shader execution after a conservative spatial-independence proof.

This is an opt-in primitive, not an automatic full-preset route. The caller must
establish that the expression is the selected complete final custom composite,
bind the actual equation/random/context inputs, and account for any later blit.
It deliberately makes no claims about upstream compilation or rendering success.
"""
import numpy as np
from feedback_field import unorm8
from field_math import UnresolvedMath,GLES_HIGHP_INFINITY
from grid_math import evaluate_grid
from shader_uniformity import UniformityProof
from uniform_descriptors import UniformDescriptorStream


SPATIAL_INPUTS={'_uv','_uv_orig','_rad_ang','_vDiffuse'}


def _spatial_roots(expression,max_nodes=65536):
    pending=[expression];seen=set();blocked=set()
    while pending:
        node=pending.pop()
        if id(node) in seen:continue
        seen.add(id(node))
        if len(seen)>max_nodes:raise UnresolvedMath('uniform spatial dependency budget exceeded')
        if node.op=='input' and node.detail['name'] in SPATIAL_INPUTS:blocked.add(id(node))
        pending.extend(node.args)
    return blocked


def uniform_expression_window(expression,updates,*,viewport,quantize,
                              numeric_policy='strict',arithmetic_profile='separate-float32-v1',
                              warmup_frames=0,settings=None,motion_window_policy='legacy-supported-subset-v1'):
    """Compute descriptors without display fields for an admitted uniform DAG.

    Each update has time and explicitly bound inputs. One unchanged lowered
    expression is required for the window; frame-dependent lowering belongs to
    its producer. Loops/effects/resources and live spatial inputs abstain even
    when a caller supplies a scalar value at one location. No source-only
    appearance or full-preset-success certification is implied by this primitive.
    """
    if not isinstance(updates,list) or not updates:raise ValueError('nonempty declared uniform update schedule required')
    if type(quantize) is not bool:raise ValueError('explicit boolean uniform storage policy required')
    if numeric_policy not in {'strict',GLES_HIGHP_INFINITY}:raise ValueError('unsupported uniform shader numeric policy')
    stream=UniformDescriptorStream(viewport=viewport,warmup_frames=warmup_frames,settings=settings,
                                   motion_window_policy=motion_window_policy)
    blocked=_spatial_roots(expression)
    for update in updates:
        if not isinstance(update,dict) or set(update)!={'time','inputs'} or not isinstance(update['inputs'],dict):
            raise ValueError('uniform updates require exactly time and input dictionary')
        # Named shader coordinates/diffuse are spatial even if one query was
        # supplied. Removing them prevents a point sample passing as a proof.
        inputs={key:value for key,value in update['inputs'].items() if key not in SPATIAL_INPUTS}
        proof=UniformityProof(inputs,viewport,blocked=blocked)
        try:
            if not proof.is_uniform(expression):raise UnresolvedMath('complete final expression is not proven uniform')
        finally:proof.release()
        rgb=np.asarray(evaluate_grid(expression,batch_shape=(1,),inputs=inputs,
                                    numeric_policy=numeric_policy,arithmetic_profile=arithmetic_profile),dtype=np.float32)
        if rgb.shape!=(1,3):raise UnresolvedMath('uniform expression must return complete RGB')
        if numeric_policy==GLES_HIGHP_INFINITY:
            if np.any(np.isnan(rgb)):raise UnresolvedMath('NaN uniform shader output remains unresolved')
            rgb=np.clip(rgb,0,1)
        if not np.all(np.isfinite(rgb)):raise UnresolvedMath('nonfinite uniform shader output remains unresolved')
        rgba=np.concatenate((rgb[0],[np.float32(1)])).astype(np.float32)
        rgba=unorm8(rgba) if quantize else np.clip(rgba,0,1)
        stream.add_uniform(time=update['time'],rgba=rgba)
    result=stream.report()
    result['uniform_source_execution']={
        'policy':'uniform-final-expression-window-v1','shader_lanes_per_update':1,
        'updates':len(updates),'display_fields_constructed':False,'quantize':quantize,
        'numeric_policy':numeric_policy,'arithmetic_profile':arithmetic_profile,
        'selected_final_composite_verified_by_this_function':False,
        'upstream_renderability_verified_by_this_function':False,
        'automatic_corpus_route_enabled':False,
        'limitations':['Caller must establish selected complete final composite and matching bindings',
                       'No arbitrary-future bounds or raster/feedback appearance certification',
                       'Warp displacement and geometry are separate; unavailable optical flow stays null']}
    return result
