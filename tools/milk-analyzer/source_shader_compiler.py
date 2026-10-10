"""Optional source-bound shader inventories from official compiler CLI output.

Never selects a native branch or evaluates a shader. GLES300 ASTs keep the exact
translation; SPIR-V is a separately labelled GLES310/OpenGL inspection profile.
Text summaries read spirv-dis output, never parse binary instructions themselves.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import time


def sha256(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False))


def _hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def _source_join(case, stage, report):
    request = report['request']; translation = report['translation']
    if request.get('profile') != 'gles300' or translation.get('profile') != 'gles300':
        raise ValueError('exact GLES300 source profile required')
    if request.get('stage') != stage or translation.get('stage') != stage:
        raise ValueError('source stage mismatch')
    if report.get('source_sha256') != sha256(request['code']):
        raise ValueError('authored shader hash mismatch')
    if translation.get('engine') != case['engine'] or translation.get('engine_archive_sha256') != case['engine_archive_sha256']:
        raise ValueError('source engine/archive mismatch')
    if report.get('native_driver_verified') is not False or translation.get('native_driver_verified') is not False:
        raise ValueError('offline compiler cannot claim native verification')
    if not all(_hash(v) for v in (case['preset']['sha256'], case['engine_archive_sha256'],
                                  report.get('translator_sha256'), report.get('validator_sha256'))):
        raise ValueError('source/compiler hashes required')
    glsl = translation['glsl']
    if not isinstance(glsl, str) or not glsl.startswith('#version 300 es\n') or len(glsl.encode()) > 1_000_000:
        raise ValueError('bounded exact GLES300 translation required')
    return {'preset_sha256': case['preset']['sha256'], 'authored_source_sha256': report['source_sha256'],
            'request_sha256': _digest(request), 'translation_sha256': _digest(translation),
            'translated_glsl_sha256': sha256(glsl), 'engine': case['engine'],
            'engine_archive_sha256': case['engine_archive_sha256'],
            'translator_sha256': report['translator_sha256'], 'saved_validator_sha256': report['validator_sha256'],
            'stage': stage, 'native_profile': 'gles300'}


class CompilerTools:
    NAMES = {'glslang': 'glslangValidator', 'opt': 'spirv-opt', 'dis': 'spirv-dis',
             'val': 'spirv-val', 'cross': 'spirv-cross'}
    ALLOWED_PASSES = {'--eliminate-dead-functions', '--compact-ids', '--remove-duplicates'}

    def __init__(self, paths=None, *, timeout=20, passes=None, naga_worker=None):
        self.passes = list(passes if passes is not None else ['--eliminate-dead-functions', '--compact-ids'])
        if any(p not in self.ALLOWED_PASSES for p in self.passes):
            raise ValueError('unqualified optimizer pass; blanket inlining/SSA rewriting unavailable')
        if not 0 < timeout <= 60:
            raise ValueError('compiler timeout must be between zero and 60 seconds')
        self.timeout = timeout
        self.paths = {k: Path((paths or {}).get(k) or shutil.which(v) or v).resolve()
                      for k, v in self.NAMES.items()}
        if naga_worker is not None:
            self.paths['naga'] = Path(naga_worker).resolve()
        self.identities = {}
        for key, path in self.paths.items():
            if not path.is_file():
                raise ValueError(f'optional compiler tool unavailable: {key}')
            # SPIRV-Cross prints its build identity in the first --help line.
            process = self.run(key, ['--help' if key == 'cross' else '--version'])
            self.identities[key] = {'path': str(path), 'sha256': sha256(path.read_bytes()),
                                    'version': process.stdout.splitlines()[:6] + process.stderr.splitlines()[:1]}

    def run(self, key, args):
        return subprocess.run([str(self.paths[key]), *map(str, args)], capture_output=True,
                              text=True, errors='replace', timeout=self.timeout)


def _location(line, source, *, logical_file_id=None, physical=False):
    if not physical and re.search(r'(?m)^\s*#\s*line\b', source):
        return {'source': 'translated-glsl-logical', 'line': line, 'text': None,
                'logical_file_id': logical_file_id, 'reason': '#line mapping not qualified'}
    lines = source.splitlines()
    return {'source': 'translated-glsl', 'line': line,
            'logical_file_id': logical_file_id,
            'text': lines[line-1] if 0 < line <= len(lines) else None}


def _ast_summary(text, source):
    records = []
    for line in text.splitlines():
        match = re.match(r'\d+:(\d+)\s+(.*)', line)
        if match and any(k in match[2] for k in ('Function Definition:', 'Convert ', 'Loop with', 'Test condition')):
            records.append({'description': match[2], 'source': _location(int(match[1]), source, logical_file_id=line.split(':',1)[0])})
    return {'profile': 'gles300', 'sha256': sha256(text), 'records': records,
            'numeric_contract': 'exact translated source, original casts and precision qualifiers retained'}


def summarize_disassembly(text, source):
    """Inventory official text records; do not infer numerical or path feasibility."""
    instructions = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        # OpSource contains quoted multi-line source: it is intentionally excluded.
        match = re.match(r'(?:(%\S+)\s*=\s*)?(Op\w+)(?:\s+(.*))?$', line)
        if match and match[2] != 'OpSource':
            instructions.append((match[1], match[2], shlex.split(match[3] or '', posix=True)))
    names = {args[0]: args[1] for _, op, args in instructions if op == 'OpName'}
    globals_ = {}; functions = []; function = None; block = None; location = None
    histogram = Counter()
    types = [{'id': result, 'op': op, 'operands': args}
             for result, op, args in instructions if op.startswith('OpType')]
    decorations = [{'op': op, 'operands': args} for _, op, args in instructions
                   if op in {'OpDecorate', 'OpMemberDecorate'}]
    entries = [args[1] for _, op, args in instructions if op == 'OpEntryPoint']
    for result, op, args in instructions:
        histogram[op] += 1
        if op == 'OpLine':
            location = _location(int(args[1]), source, logical_file_id=args[0])
        elif op == 'OpNoLine':
            location = None
        elif op == 'OpFunction':
            function = {'id': result, 'name': names.get(result, result), 'calls': [], 'blocks': [],
                        'loops': [], 'selections': [], 'conversions': [], 'samples': [],
                        'direct_resource_ids': [], 'instruction_count': 0}
            functions.append(function); block = None
        elif op == 'OpFunctionEnd':
            function = None; block = None; location = None
        elif function is None and op == 'OpVariable':
            globals_[result] = {'id': result, 'name': names.get(result, result), 'storage_class': args[1]}
        if function is None:
            continue
        function['instruction_count'] += 1
        if op == 'OpLabel':
            block = {'id': result, 'successors': []}; function['blocks'].append(block)
        elif op == 'OpBranch' and block is not None:
            block['successors'] = args[:1]
        elif op == 'OpBranchConditional' and block is not None:
            block['successors'] = args[1:3]
        elif op == 'OpSwitch' and block is not None:
            block['successors'] = [args[1], *args[3::2]]
        elif op == 'OpFunctionCall':
            function['calls'].append({'target': args[1], 'name': names.get(args[1], args[1]), 'source': location})
        elif op == 'OpLoopMerge':
            function['loops'].append({'header': block['id'], 'merge': args[0], 'continue': args[1], 'source': location})
        elif op == 'OpSelectionMerge':
            function['selections'].append({'header': block['id'], 'merge': args[0], 'source': location})
        if op.startswith('OpConvert') or op in {'OpBitcast', 'OpFConvert', 'OpSConvert', 'OpUConvert'}:
            function['conversions'].append({'op': op, 'result': result, 'operands': args, 'source': location})
        if op.startswith(('OpImageSample', 'OpImageFetch', 'OpImageGather', 'OpImageRead', 'OpImageWrite')):
            function['samples'].append({'op': op, 'result': result, 'operands': args, 'source': location})
        function['direct_resource_ids'].extend(a for a in args if a in globals_)
    by_id = {f['id']: f for f in functions}
    for f in functions:
        own = set(f['direct_resource_ids']); reachable = {f['id']}; pending = [f['id']]
        while pending:
            current = by_id[pending.pop()]
            own.update(current['direct_resource_ids'])
            for call in current['calls']:
                target = call['target']
                if target in by_id and target not in reachable:
                    reachable.add(target); pending.append(target)
        f['direct_resource_ids'] = sorted(set(f['direct_resource_ids']))
        f['transitive_resource_names'] = sorted({globals_[g]['name'] for g in own})
        f['reachable_function_ids'] = sorted(reachable)
    return {'entry_points': entries, 'functions': functions, 'globals': list(globals_.values()),
            'types': types, 'decorations': decorations,
            'op_counts': dict(sorted(histogram.items())), 'instruction_count': sum(histogram.values()),
            'conversion_count': sum(len(f['conversions']) for f in functions),
            'sample_count': sum(len(f['samples']) for f in functions),
            'scope': 'syntactic emitted function/CFG/resource inventory; no feasibility or numeric bounds'}


def _resources(reflection, request, source):
    resources = []
    for category, values in reflection.items():
        if not isinstance(values, list) or category == 'entryPoints':
            continue
        for resource in values:
            if not isinstance(resource, dict) or 'name' not in resource:
                continue
            name = resource['name']
            declarations = [_location(i, source, physical=True) for i, line in enumerate(source.splitlines(), 1)
                            if re.search(r'\b(?:uniform|in|out)\b.*\b' + re.escape(name) + r'\b', line)]
            resources.append({**resource, 'category': category, 'translated_declarations': declarations,
                              'request_sampler_type': request.get('samplers', {}).get(name),
                              'binding_scope': 'auto-assigned inspection interface, never native texture unit'})
    return resources


def _inspect(report, tools, join):
    source = report['translation']['glsl']; result = dict(join)
    with tempfile.TemporaryDirectory(prefix='milk-shader-inspection-') as directory:
        root = Path(directory); exact = root/'exact.frag'; exact.write_text(source)
        ast = tools.run('glslang', ['-i', '-S', 'frag', exact])
        if ast.returncode not in {0, 2}:
            raise RuntimeError(f'exact AST tool failure (exit {ast.returncode})')
        result['exact_ast'] = _ast_summary(ast.stdout.replace(str(root), '<temporary>'), source)
        if ast.returncode:
            result.update(status='exact_ast_rejected', diagnostics=(ast.stdout + ast.stderr)[-4000:]); return result
        inspection_source = source.replace('#version 300 es', '#version 310 es', 1)
        fragment = root/'inspection.frag'; fragment.write_text(inspection_source)
        binary = root/'original.spv'; normalized = root/'normalized.spv'
        compiled = tools.run('glslang', ['-G', '-g', '--auto-map-locations', '--auto-map-bindings',
                                         '-S', 'frag', fragment, '-o', binary])
        if compiled.returncode not in {0, 2}:
            raise RuntimeError(f'inspection compiler failure (exit {compiled.returncode})')
        if compiled.returncode:
            result.update(status='inspection_rejected', diagnostics=(compiled.stdout + compiled.stderr)[-4000:]); return result
        original = tools.run('dis', ['--raw-id', binary])
        optimized = tools.run('opt', [*tools.passes, binary, '-o', normalized])
        for process in (original, optimized):
            if process.returncode:
                raise RuntimeError('compiler inspection tool failed: ' + process.stderr[-4000:])
        validation = tools.run('val', ['--target-env', 'opengl4.5', normalized])
        disassembly = tools.run('dis', ['--raw-id', normalized])
        reflected = tools.run('cross', [normalized, '--reflect'])
        for process in (validation, disassembly, reflected):
            if process.returncode:
                raise RuntimeError('compiler inspection tool failed: ' + process.stderr[-4000:])
        reflection = json.loads(reflected.stdout)
        result.update(status='analyzed', inspection={
            'profile': 'gles310-opengl-inspection', 'source_sha256': sha256(inspection_source),
            'edits': ['first version directive 300 es -> 310 es', 'auto-map interface locations', 'auto-map resource bindings'],
            'passes': tools.passes, 'native_driver_verified': False, 'runtime_texture_bindings_verified': False,
            'native_numeric_equivalence_verified': False, 'uses_shader_execution': False,
            'original_spirv_sha256': sha256(binary.read_bytes()), 'normalized_spirv_sha256': sha256(normalized.read_bytes()),
            'original_summary': summarize_disassembly(original.stdout, source),
            'normalized_summary': summarize_disassembly(disassembly.stdout, source),
            'resources': _resources(reflection, report['request'], source), 'reflection': reflection})
        if 'naga' in tools.paths:
            from source_shader_naga import inspect_naga
            try:
                result['inspection']['naga'] = inspect_naga(binary, original.stdout, source, root, tools)
            except (ValueError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
                result['inspection']['naga'] = {'status': 'bridge_unknown', 'reason': str(error)}
    return result


def analyze_case(case, tools):
    # Validate every translated input before invoking any tools.
    joins = {stage: _source_join(case, stage, report) for stage, report in case['reports'].items()
             if report.get('translation', {}).get('status') == 'translated'}
    result = {'schema_version': 1, 'kind': 'source-shader-compiler-inspection',
              'preset': case['preset'], 'case_sha256': _digest(case),
              'tools': tools.identities if tools is not None else {}, 'stages': {},
              'limits': 'Auxiliary source inventory only. No appearance, native bindings, GPU execution or arithmetic equivalence claim.'}
    for stage, report in case['reports'].items():
        started = time.perf_counter()
        if stage not in joins:
            record = {'status': 'translation_unavailable', 'translation_status': report.get('translation', {}).get('status')}
        else:
            try:
                record = _inspect(report, tools, joins[stage])
            except (subprocess.TimeoutExpired, RuntimeError, json.JSONDecodeError) as error:
                record = {**joins[stage], 'status': 'inspection_unknown', 'reason': str(error)}
        record['seconds'] = time.perf_counter() - started
        result['stages'][stage] = record
    result['record_sha256'] = _digest(result)
    return result


def validate_join(result, case):
    payload = {k: v for k, v in result.items() if k != 'record_sha256'}
    if result.get('record_sha256') != _digest(payload):
        raise ValueError('inspection result seal mismatch')
    if result.get('case_sha256') != _digest(case):
        raise ValueError('inspection source join mismatch')
    if result.get('schema_version') != 1 or result.get('kind') != 'source-shader-compiler-inspection':
        raise ValueError('inspection schema mismatch')
    for stage, report in case['reports'].items():
        if report.get('translation', {}).get('status') == 'translated':
            join = _source_join(case, stage, report); record = result['stages'][stage]
            if any(record.get(k) != v for k, v in join.items()):
                raise ValueError('inspection source join mismatch')
            inspection = record.get('inspection', {})
            if inspection and inspection.get('profile') != 'gles310-opengl-inspection':
                raise ValueError('inspection profile mismatch')
            if any(inspection.get(k, False) is not False for k in ('native_driver_verified', 'runtime_texture_bindings_verified', 'native_numeric_equivalence_verified', 'uses_shader_execution')):
                raise ValueError('inspection cannot certify native behavior')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('compatibility', nargs='+', type=Path, help='saved source-bound compatibility case JSONs')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--timeout', type=float, default=20)
    parser.add_argument('--naga-worker', type=Path, help='optional pinned official Naga IR worker executable')
    parser.add_argument('--pass', dest='passes', action='append', choices=sorted(CompilerTools.ALLOWED_PASSES))
    args = parser.parse_args(argv)
    tools = CompilerTools(timeout=args.timeout, passes=args.passes, naga_worker=args.naga_worker); args.output.mkdir(parents=True, exist_ok=True)
    for path in args.compatibility:
        data = path.read_bytes(); case = json.loads(data); result = analyze_case(case, tools)
        if path.read_bytes() != data:
            raise ValueError('compatibility source changed during inspection')
        validate_join(result, case)
        (args.output/(case['preset']['sha256'] + '.json')).write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        print(json.dumps({'preset': case['preset']['relative_path'], 'stages': {k: v['status'] for k, v in result['stages'].items()}}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
