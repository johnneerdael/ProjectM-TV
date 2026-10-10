"""Native feedback displacement propagated through affine authored lookups."""
import math
from fractions import Fraction


def _norm_upper(values):
    exact=sum(Fraction(v)**2 for v in values)
    if exact==0:return 0.
    try:value=math.sqrt(float(exact))
    except OverflowError:return None
    if not math.isfinite(value) or value==0:return None
    if Fraction(value)**2<exact:value=math.nextafter(value,math.inf)
    return value if math.isfinite(value) else None


def native_lookup_transport(description):
    displacement=description['native_warp_displacement'];rows=[]
    def bound(matrix):
        gains=[_norm_upper([r[i] for r in matrix]) for i in (0,1)]
        if any(v is None for v in gains):return None
        return {'aspect_corrected_native_terms':displacement['rms_upper_bound_terms'],
            'matrix_gain_terms':{'inverse_aspect_x':gains[0],'inverse_aspect_y':gains[1]},
            'formula':'native_rms_bound(aspectX,aspectY) * (gain_x/aspectX + gain_y/aspectY)'}
    for stage,maps in description['sampling_geometry']['stages'].items():
        for lookup in maps or []:
            row={'stage':stage,'sample_site_index':lookup['sample_site_index'],'sampler':lookup['sampler'],
                'canonical_texture':lookup['canonical_texture'],'native_mesh_contribution':'unknown',
                'rms_lookup_displacement_uv_upper_bound_terms':None,
                'feedback_step_unit':'source_texture_uv/feedback_step','texel_alignment_included':False,
                'visible_screen_speed':None,'unknown_reasons':[],
                'conditions':['Selected authored warp lookup has a constant-affine or globally Lipschitz mesh-UV map and bounded uniform native controls',
                    'Nonlinear certificates require finite valid source domains for both coordinates and every point of their connecting path',
                    'Compare mesh-warped versus original UV at the same frame/control values; uniform shader offsets cancel',
                    'Supply finite positive renderer aspectX/Y; divide native aspect-corrected displacement by each aspect before the shader map',
                    'Uniform original UV area RMS, not a pointwise jump bound, temporal derivative or forward feature speed',
                    'Texel alignment, mesh/pixel precision, clipping/wrapping, texture history and later passes remain separate',
                    'Repeated main-texture sampling is feedback transport; external textures alone do not establish repeated feature motion']}
            matrix=lookup['matrix_uv4'];response_model='affine_mesh_uv'
            if matrix is None and lookup['mesh_uv_response']['global_lipschitz_domain_verified']:
                matrix=[r+[0,0] for r in lookup['mesh_uv_response']['matrix_uv_output_input_gain_upper_bounds']]
                response_model='nonlinear_mesh_uv_lipschitz'
            row['lookup_response_model']=response_model if matrix is not None else None
            if stage!='warp' or matrix is not None and all(v==0 for r in matrix for v in r[:2]):
                row['native_mesh_contribution']='bypassed'
            elif matrix is None:row['unknown_reasons']=['authored lookup is not a supported constant-affine map']
            elif response_model=='affine_mesh_uv' and lookup['sampling_motion']['unknown_reasons']:
                row['unknown_reasons']=list(lookup['sampling_motion']['unknown_reasons'])
            elif displacement['status']!='bounded_uniform_sampling_displacement':
                row['unknown_reasons']=['native uniform sampling displacement domain unresolved']
            else:
                terms=bound(matrix)
                if terms is None:row['unknown_reasons']=['lookup column norm is nonfinite or unrepresentable']
                else:
                    row['native_mesh_contribution']='bounded'
                    row['rms_lookup_displacement_uv_upper_bound_terms']=terms
            extra=lookup['mesh_uv_response'].get('scenario_mesh_uv_response')
            if extra is not None and extra['global_lipschitz_domain_verified'] and displacement['status']=='bounded_uniform_sampling_displacement' and stage=='warp':
                scenario_matrix=[r+[0,0] for r in extra['matrix_uv_output_input_gain_upper_bounds']]
                terms=bound(scenario_matrix)
                row['scenario_native_lookup_transport']={'native_mesh_contribution':'bounded' if terms is not None else 'unknown',
                    'rms_lookup_displacement_uv_upper_bound_terms':terms,'lookup_response_model':'nonlinear_mesh_uv_lipschitz',
                    'input_scenario_sha256':extra['input_scenario_sha256'],'observed_runtime_inputs':False,'runtime_binding_verified':False}
            rows.append(row)
    return rows


def native_nearest_hazards(description,transport):
    """Possible feedback jumps; positive ceilings alone never prove visible motion."""
    lookups={(stage,r['sample_site_index'],r['sampler']):r for stage,maps in
        description['sampling_geometry']['stages'].items() for r in maps or []}
    hazards=[]
    for row in transport:
        if row['native_mesh_contribution']!='bounded' or row['canonical_texture']!='main':continue
        lookup=lookups[(row['stage'],row['sample_site_index'],row['sampler'])];p=lookup['sampling_policy'] or {}
        if p.get('linear') is not False or p.get('mipmapped') is not False or p.get('base_level')!=0:continue
        terms=row['rms_lookup_displacement_uv_upper_bound_terms'];native=terms['aspect_corrected_native_terms']
        if not any(v>0 for v in native.values()) or not any(v>0 for v in terms['matrix_gain_terms'].values()):continue
        hazards.append({'kind':'nearest_native_feedback_displacement','stage':row['stage'],
            'sample_site_index':row['sample_site_index'],'sampler':row['sampler'],
            'canonical_texture':'main','visible_flashing_verified':False,'visible_flash_frequency_hz':None,
            'scope':'possible nearest-cell changes under repeated native feedback transport',
            'conditions':['Positive nominal RMS ceiling does not prove displacement or a texel boundary crossing',
                'The retained image must have differing texels and the lookup/colour path must preserve their change',
                'Native controls act each feedback step; this does not assert a per-second coordinate derivative',
                'RMS is not a pointwise jump-size bound; wrapping, storage, texel alignment and native precision remain separate',
                'Shader selection, masks, primitive coverage, history and later composition determine visible flashes; no mood verdict']})
    return hazards
