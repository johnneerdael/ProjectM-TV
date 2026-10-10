"""Possible nearest-texel jumps under source lookup motion, not visible flashes."""
from fractions import Fraction


def nearest_sampling_hazards(description):
    from source_sampling_motion import _finite_round
    rows=[]
    def key(r):return r['sample_site_index'],r['sampler']
    def active(matrix):return any(v is None or v>0 for row in matrix for v in row)
    for stage,maps in description['sampling_geometry']['stages'].items():
        if maps is None:continue
        models=description['nonlinear_texture_colour_bounds']['stages'][stage]
        for scenario in (False,True):
            if scenario and 'scenario_colour_envelope' not in models:continue
            model=models['scenario_colour_envelope'] if scenario else models
            direct={key(r):r for r in model['direct_sample_colour_response']['samples']}
            adjacency={}
            for outer in maps:
                response=outer['coordinate_sample_response']
                edges=response.get('scenario_coordinate_response',response)['samples'] if scenario else response['samples']
                for edge in edges:
                    if active(edge['matrix_uv_rgba_gain_upper_bounds']):adjacency.setdefault(key(edge),[]).append(key(outer))
            def route(start):
                pending=list(adjacency.get(start,[]));seen={start}
                while pending:
                    if len(seen)>64:return 'unresolved_nested_path_budget'
                    node=pending.pop()
                    if node in seen:continue
                    seen.add(node)
                    if node in direct and active(direct[node]['matrix_rgb_rgba_gain_upper_bounds']):return 'nested_coordinate_path'
                    pending.extend(adjacency.get(node,[]))
                return None
            for record in maps:
                policy=record['sampling_policy'] or {}
                if policy.get('linear') is not False or policy.get('mipmapped') is not False or policy.get('base_level')!=0:continue
                movement=record['sampling_motion'].get('scenario_sampling_motion') if scenario else record['sampling_motion']
                if movement is None:continue
                rates=movement['maximum_lookup_axis_speed_uv_per_second']
                if not any(v is not None and v>0 for v in rates):continue
                influence=direct.get(key(record));jump=[None]*3
                if influence is not None and active(influence['matrix_rgb_rgba_gain_upper_bounds']):
                    kind='direct_rgb_path'
                    for i,row in enumerate(influence['matrix_rgb_rgba_gain_upper_bounds']):
                        if all(v is not None for v in row):jump[i]=_finite_round(sum(map(Fraction,row)),upper=True)
                else:
                    kind=route(key(record))
                    if kind is None:continue
                curves=record['offset_controls'];crossings=None
                if policy.get('wrap') is True and len(curves)==2 and all(c['curve_kind'] in {'constant','linear_time'} for c in curves):
                    crossings=[0. if c['curve_kind']=='constant' else abs(c['signed_linear_rate_per_second']) for c in curves]
                rows.append({'kind':'nearest_lookup_temporal_jumps','stage':stage,
                    'sample_site_index':record['sample_site_index'],'sampler':record['sampler'],
                    'canonical_texture':record['canonical_texture'],'rgb_influence_route':kind,
                    'input_scenario_sha256':model['input_scenario_sha256'] if scenario else None,
                    'maximum_lookup_axis_speed_uv_per_second':rates,
                    'grid_crossing_rate_coefficients_per_uploaded_dimension':crossings,
                    'rgb_jump_upper_bounds_from_direct_response':jump,
                    'visible_flash_frequency_hz':None,'visible_flashing_verified':False,
                    'scope':'possible local sample-value jumps from source-time motion through nearest texel selection',
                    'conditions':['Selected authored shader path reaches this lookup; other inputs, spatial/native mesh and texture history fixed',
                        'Adjacent texels must differ and the trajectory must cross a relevant cell boundary for a value jump',
                        'Positive movement ceilings may not be reached; constant textures or fixed/clamped selected cells can stay unchanged',
                        'Crossing coefficients apply only to nominal constant drift with repeat addressing between clock resets/wraps',
                        'For actual uploaded W/H, sum W*coefficient_x+H*coefficient_y for grid-boundary crossings; simultaneous axes can coincide',
                        'Grid crossings are not distinct texel changes or flashes; dimension-one axes and equal neighbours can preserve values',
                        'Direct jump ceilings assume all sampled lanes in [0,1] and other samples fixed; nested or unsupported jump magnitudes remain unknown',
                        'Native rounding/cadence, masks, geometry/prominence, later composition and feedback determine actual visibility; no mood verdict']})
    return rows
