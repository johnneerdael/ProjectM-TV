"""Qualified auxiliary bridge to Naga's official typed IR and validator."""
import json
import re

from source_shader_compiler import sha256, summarize_disassembly


def scalarize_output_interface(hlsl):
    """Split only the generated fixed float4 render-target wrapper, never math."""
    pattern = r'(?m)^(\s*)float4 (\w+)\[(1|2)\] : SV_Target0;$'
    matches = list(re.finditer(pattern, hlsl))
    if len(matches) != 1:
        raise ValueError('unqualified generated fragment output interface')
    match = matches[0]; indent, name, count = match.groups(); count = int(count)
    assignment = f'    stage_output.{name} = {name};'
    declaration = r'\bstatic float4 ' + re.escape(name) + r'\[' + str(count) + r'\];'
    if hlsl.count(assignment) != 1 or len(re.findall(declaration, hlsl)) != 1:
        raise ValueError('unqualified generated fragment output assignment')
    references = re.sub(declaration, '', hlsl[:match.start()]+hlsl[match.end():])
    for subscript in re.findall(r'\b' + re.escape(name) + r'\[([^]]+)\]', references):
        if not subscript.isdigit() or not 0 <= int(subscript) < count:
            raise ValueError('unqualified generated fragment output array access')
    fields = '\n'.join(f'{indent}float4 {name}_inspection{i} : SV_Target{i};' for i in range(count))
    copies = '\n'.join(f'    stage_output.{name}_inspection{i} = {name}[{i}];' for i in range(count))
    return hlsl[:match.start()] + fields + hlsl[match.end():].replace(assignment, copies, 1), count


def inspect_naga(binary, original_disassembly, original_source, root, tools):
    hlsl_path = root/'naga-bridge.hlsl'; binary_path = root/'naga-bridge.spv'
    crossed = tools.run('cross', [binary, '--hlsl', '--shader-model', '50', '--output', hlsl_path])
    if crossed.returncode:
        raise RuntimeError('SPIRV-Cross HLSL inspection bridge failed: ' + crossed.stderr[-2000:])
    original_attempt = tools.run('naga', [binary])
    if original_attempt.returncode:
        raise RuntimeError('Naga original inspection attempt failed')
    original_validation = json.loads(original_attempt.stdout)
    generated = hlsl_path.read_text(); hlsl, count = scalarize_output_interface(generated)
    command = ['-D', '-V', '-Od', '--auto-map-bindings', '--auto-map-locations',
               '--shift-sampler-binding', 'frag', '64', '--shift-UBO-binding', 'frag', '128',
               '-S', 'frag', '-e', 'main', hlsl_path, '-o', binary_path]
    unadapted = tools.run('glslang', command)
    if unadapted.returncode:
        raise RuntimeError('unadapted Vulkan HLSL inspection rejected')
    unadapted_attempt = tools.run('naga', [binary_path])
    if unadapted_attempt.returncode:
        raise RuntimeError('Naga unadapted inspection attempt failed')
    unadapted_validation = json.loads(unadapted_attempt.stdout)
    # Keep only validation outcome here; fully accepted adapted IR follows below.
    unadapted_validation = {k:v for k,v in unadapted_validation.items() if k not in {'module','functions','entries'}}
    hlsl_path.write_text(hlsl)
    compiled = tools.run('glslang', command)
    if compiled.returncode:
        raise RuntimeError('Vulkan HLSL inspection bridge rejected: ' + (compiled.stdout+compiled.stderr)[-2000:])
    validation = tools.run('val', [binary_path])
    if validation.returncode:
        raise RuntimeError('Vulkan HLSL inspection validation failed: ' + validation.stderr[-2000:])
    worker = tools.run('naga', [binary_path])
    if worker.returncode:
        raise RuntimeError('Naga worker failed: ' + worker.stderr[-2000:])
    typed = json.loads(worker.stdout)
    disassembly = tools.run('dis', ['--raw-id', binary_path])
    if disassembly.returncode:
        raise RuntimeError('Naga bridge disassembly failed')
    original = summarize_disassembly(original_disassembly, original_source)
    bridge = summarize_disassembly(disassembly.stdout, hlsl)
    return {'profile': 'vulkan-hlsl50-naga-inspection',
            'edits': ['SPIRV-Cross HLSL50 separates combined texture/sampler descriptors',
                      'scalarize generated fragment-output wrapper; preserve original global output array',
                      'inspection sampler bindings shifted64; uniform-block bindings shifted128',
                      'glslang HLSL Vulkan frontend with -Od; no optimizer inlining'],
            'output_locations': list(range(count)), 'generated_hlsl_sha256': sha256(generated),
            'original_opengl_spirv_attempt': original_validation,
            'unadapted_vulkan_hlsl_attempt': unadapted_validation,
            'adapted_hlsl_sha256': sha256(hlsl), 'bridge_spirv_sha256': sha256(binary_path.read_bytes()),
            'sample_count_preserved': original['sample_count'] == bridge['sample_count'],
            'conversion_count_preserved': original['conversion_count'] == bridge['conversion_count'],
            'original_summary': {'samples': original['sample_count'], 'conversions': original['conversion_count'],
                                 'functions': [f['name'] for f in original['functions']]},
            'bridge_summary': {'samples': bridge['sample_count'], 'conversions': bridge['conversion_count'],
                               'functions': [f['name'] for f in bridge['functions']]},
            'native_numeric_equivalence_verified': False, 'runtime_texture_bindings_verified': False,
            'source_join_scope': 'exact original shader plus hashes of every generated bridge; Naga spans refer to inspection SPIR-V',
            'typed_ir': typed}
