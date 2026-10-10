"""Optional Slang derivative-program export for selected exact pure helpers.

Preserve authored helper bodies; attach differentiability attributes and a
caller-declared derivative entry. This produces a program, never a range bound.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

from source_shader_compiler import sha256, _digest, validate_join


def export_derivative(case, inspection, *, stage, helper_text, functions,
                      derivative_function, entry_text, slangc, timeout=20):
    validate_join(inspection, case)
    report = case['reports'][stage]; source = report['request']['code']
    if not helper_text.strip() or helper_text not in source or len(helper_text.encode()) > 200_000:
        raise ValueError('bounded exact authored helper substring required')
    if not functions or derivative_function not in functions or any(not re.fullmatch(r'[A-Za-z_]\w*', f) for f in functions):
        raise ValueError('explicit helper and derivative function names required')
    summaries = inspection['stages'][stage].get('inspection', {}).get('original_summary', {}).get('functions', [])
    for name in functions:
        matches = [f for f in summaries if f['name'].split('(')[0] == name]
        if len(matches) != 1 or matches[0]['transitive_resource_names'] or matches[0]['samples']:
            raise ValueError('selected helper must have a unique resource-free compiler summary')
    if re.search(r'\b(?:no_diff|TreatAsDifferentiable|ForwardDerivative|BackwardDerivative)\b', helper_text+entry_text):
        raise ValueError('derivative overrides cannot hide missing responses')
    entry_pattern = (r'\s*\[shader\("compute"\)\]\s*\[numthreads\(1,\s*1,\s*1\)\]\s*'
                     r'void\s+main\([^{}#]*\)\s*\{[^{}#]*\}\s*')
    if re.fullmatch(entry_pattern, entry_text) is None:
        raise ValueError('only the declared compute-main differential wrapper is supported')
    entry_code = re.sub(r'/\*.*?\*/|//[^\n]*', '', entry_text, flags=re.DOTALL)
    if not re.search(r'\bfwd_diff\s*\(\s*'+re.escape(derivative_function)+r'\s*\)\s*\(', entry_code):
        raise ValueError('explicit forward differential entry required')
    annotated = helper_text
    for name in functions:
        pattern = r'(?m)^(\s*(?:float|float[234])\s+'+re.escape(name)+r'\s*\()'
        annotated, count = re.subn(pattern, r'[Differentiable]\n\1', annotated)
        if count != 1:
            raise ValueError('unqualified authored helper declaration')
    compiler_input = annotated + '\n' + entry_text
    slangc = Path(slangc).resolve()
    version = subprocess.run([str(slangc), '-version'], capture_output=True, text=True, timeout=timeout, check=True)
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='milk-slang-inspection-') as directory:
        root=Path(directory); input_path=root/'helpers.slang'; output_path=root/'derivative.hlsl'; input_path.write_text(compiler_input)
        process=subprocess.run([str(slangc), str(input_path), '-target', 'hlsl', '-entry', 'main', '-stage', 'compute', '-o', str(output_path)],
                               capture_output=True, text=True, timeout=timeout)
        output=output_path.read_text() if process.returncode==0 and output_path.exists() else None
    retained_derivative = output is not None and re.search(r'\bs_fwd_' + re.escape(derivative_function) + r'(?:_\d+)?\s*\(', output) is not None
    result={'schema_version':1, 'kind':'source-shader-slang-derivative-program',
            'status':'generated' if retained_derivative else 'unsupported',
            'retained_derivative_function':retained_derivative,
            'preset_sha256':case['preset']['sha256'], 'stage':stage, 'source_sha256':report['source_sha256'],
            'inspection_record_sha256':inspection['record_sha256'], 'helper_text_sha256':sha256(helper_text),
            'functions':list(functions), 'derivative_function':derivative_function,
            'entry_sha256':sha256(entry_text), 'compiler_input_sha256':sha256(compiler_input),
            'compiler_sha256':sha256(slangc.read_bytes()), 'compiler_version':version.stdout.strip(),
            'edits':['Differentiable attributes before selected helper declarations', 'separate explicit differential compute entry'],
            'profile':'slang-hlsl-derivative-inspection', 'generated_program':output,
            'generated_program_sha256':sha256(output) if output is not None else None,
            'diagnostics':(process.stdout+process.stderr)[-4000:], 'seconds':time.perf_counter()-started,
            'reason':None if retained_derivative else 'compiler did not retain the requested derivative function',
            'native_numeric_equivalence_verified':False, 'range_bounds_verified':False,
            'limits':'Derivative program only. Input domains, native arithmetic, clamp/discontinuity boundaries and texture derivatives remain separate obligations.'}
    result['record_sha256']=_digest(result)
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('compatibility',type=Path);p.add_argument('--inspection',type=Path,required=True)
    p.add_argument('--stage',choices=['warp','composite'],required=True);p.add_argument('--helpers',type=Path,required=True)
    p.add_argument('--function',dest='functions',action='append',required=True)
    p.add_argument('--derivative-function',required=True);p.add_argument('--entry',type=Path,required=True)
    p.add_argument('--slangc',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(argv);result=export_derivative(json.loads(a.compatibility.read_text()),json.loads(a.inspection.read_text()),
        stage=a.stage,helper_text=a.helpers.read_text(),functions=a.functions,derivative_function=a.derivative_function,
        entry_text=a.entry.read_text(),slangc=a.slangc)
    a.output.write_text(json.dumps(result,indent=2)+'\n');return 0


if __name__=='__main__':
    raise SystemExit(main())
