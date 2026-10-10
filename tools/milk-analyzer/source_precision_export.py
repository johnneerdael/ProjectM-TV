"""Export qualified source calculations to existing precision-analysis tools.

This is an optional query bridge, never an authored-program optimizer. A caller
declares one arithmetic format and finite input domains; phase/storage conversion
and GPU transcendental policies are not inferred from a scalar Field dtype.
"""
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile

from source_symbolic import _program


def _number(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('precision query requires finite scalar constants/domains')
    return format(Decimal.from_float(value), 'f')


def export_precision_query(field, *, input_domains, precision):
    """Return FPTaylor/FPCore requests, retaining unsimplified operation order.

    FPCore is the shared precision-tool interchange format used by Herbie and
    FPBench. FPTaylor's native input keeps explicit rounding on each operation.
    Bounds are premises. An emitted query is not a proof or a native certificate.
    """
    if precision not in {'binary32', 'binary64'}:
        raise ValueError('explicit binary32/binary64 query precision required')
    program = _program(field)
    nodes = program['nodes']
    names = sorted({n['detail']['name'] for n in nodes if n['op'] == 'input'})
    domains = {}
    for name in names:
        domain = input_domains.get(name)
        if (not isinstance(domain, (list, tuple)) or len(domain) != 2 or
                any(type(v) not in {int, float} or not math.isfinite(v) for v in domain) or
                domain[0] > domain[1]):
            raise ValueError('finite ordered input domain required: ' + name)
        domains[name] = list(domain)
    symbols = {name: 'x' + str(i) for i, name in enumerate(names)}
    bits = '32' if precision == 'binary32' else '64'
    bindings = []; definitions = []; values = {}; functions = set()

    def visit(index):
        if index in values:
            return values[index]
        node = nodes[index]; op = node['op']
        if op == 'input':
            value = symbols[node['detail']['name']]
        elif op == 'constant':
            value = _number(node['detail']['value'])
        else:
            args = [visit(i) for i in node['args']]
            if op in {'add', 'subtract', 'multiply'}:
                operator = {'add': '+', 'subtract': '-', 'multiply': '*'}[op]
                fpcore = '(' + operator + ' ' + ' '.join(args) + ')'
                expression = '(' + (' ' + operator + ' ').join(args) + ')'
            elif op in {'sin', 'cos'}:
                functions.add(op)
                fpcore = '(' + op + ' ' + args[0] + ')'
                expression = op + '(' + args[0] + ')'
            elif op == 'sqr':
                fpcore = '(* ' + args[0] + ' ' + args[0] + ')'
                expression = '(' + args[0] + ' * ' + args[0] + ')'
            elif op == 'negate' or op == 'unary' and node['detail']['operator'] == 0:
                fpcore = '(- ' + args[0] + ')'; expression = '(-' + args[0] + ')'
            elif op == 'unary' and node['detail']['operator'] == 1:
                values[index] = args[0]
                return args[0]
            else:
                raise ValueError('unqualified precision query operation: ' + op)
            value = 'n' + str(len(bindings))
            bindings.append('[' + value + ' ' + fpcore + ']')
            definitions.append('  ' + value + ' rnd' + bits + '= ' + expression + ';')
        values[index] = value
        return value

    root = visit(program['root'])
    clauses = ['(<= ' + _number(domains[n][0]) + ' ' + symbols[n] + ' ' + _number(domains[n][1]) + ')'
               for n in names]
    precondition = 'TRUE' if not clauses else '(and ' + ' '.join(clauses) + ')'
    body = root if not bindings else '(let* (' + ' '.join(bindings) + ') ' + root + ')'
    fpcore = '(FPCore (' + ' '.join(symbols.values()) + ') :precision ' + precision + '\n  :pre ' + precondition + '\n  ' + body + ')\n'
    variables = ['  float' + bits + ' ' + symbols[n] + ' in [' + _number(domains[n][0]) + ', ' + _number(domains[n][1]) + '];'
                 for n in names]
    fptaylor = ('Variables\n' + '\n'.join(variables) + '\n' if variables else '')
    if definitions:
        fptaylor += 'Definitions\n' + '\n'.join(definitions) + '\n'
    fptaylor += 'Expressions\n  result rnd' + bits + '= ' + root + ';\n'
    record = {'policy': 'source-pure-precision-query-v1', 'precision': precision,
              'input_domains': domains, 'symbols': symbols, 'source_program': program,
              'fpcore': fpcore, 'fptaylor': fptaylor, 'transcendental_functions': sorted(functions),
              'authored_program_changed': False, 'native_numeric_certified': False,
              'conditions': ['Declared common arithmetic format and round-to-nearest-even policy',
                             'Tool acceptance/results do not certify engine storage, EEL phase or GPU arithmetic',
                             'Transcendental error assumptions require a separately qualified tool/backend policy',
                             'Herbie suggestions apply only to separately labelled new/adapted effects']}
    record['record_sha256'] = hashlib.sha256(json.dumps(record, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return record


def run_fptaylor_js(query, *, bundle, runtime, default_config, timeout=5):
    """Run a caller-supplied FPTaylor JS bundle offline under a bounded process.

    Its portable interval backend lacks trig support. No bundled third-party
    code is distributed; caller identities and all diagnostics are retained.
    This returns a tool-model roundoff bound, never an engine proof certificate.
    """
    if not 0 < timeout <= 60:
        raise ValueError('bounded positive precision-tool timeout required')
    query = json.loads(json.dumps(query, allow_nan=False))
    if query.get('transcendental_functions'):
        raise ValueError('portable FPTaylor JS interval backend excludes trig')
    sealed = {k: v for k, v in query.items() if k != 'record_sha256'}
    if query.get('record_sha256') != hashlib.sha256(json.dumps(sealed, sort_keys=True, allow_nan=False).encode()).hexdigest():
        raise ValueError('precision query identity changed')
    paths = {n: Path(p).resolve(strict=True) for n, p in
             [('bundle', bundle), ('runtime', runtime), ('default_config', default_config)]}
    frozen = {n: p.read_bytes() for n, p in paths.items() if n != 'runtime'}
    config = frozen['default_config'].decode('utf-8')
    identity = {n + '_sha256': hashlib.sha256(data).hexdigest() for n, data in frozen.items()}
    identity['runtime_sha256'] = hashlib.sha256(paths['runtime'].read_bytes()).hexdigest()
    runner = """const fs=require('fs');const vm=require('vm');
const request=JSON.parse(fs.readFileSync(0,'utf8'));const outputs=[];
const context=vm.createContext({onmessage:null,postMessage:x=>outputs.push(x),console,performance});
vm.runInContext(fs.readFileSync(request.binary,'utf8'),context);
context.onmessage({data:request.query});
process.stdout.write(JSON.stringify(outputs)+'\\n');
"""
    request = {'binary': str(paths['bundle']), 'query': {
        'input': query['fptaylor'], 'defaultcfg': config,
        'config': 'verbosity = 0\nopt-max-iters = 1000\nfind-bounds = true\n'}}
    if len(json.dumps(request).encode()) > 262144:
        raise ValueError('bounded precision query/config size required')
    record = {'status': 'unresolved', 'query_sha256': query['record_sha256'],
              'backend': identity, 'native_numeric_certified': False,
              'proof_certificate_available': False, 'uses_rendered_images': False,
              'scope': 'FPTaylor portable interval and common IEEE arithmetic query model'}
    with tempfile.TemporaryDirectory(prefix='source-precision-') as folder:
        script = Path(folder) / 'run.cjs'; script.write_text(runner)
        frozen_bundle = Path(folder) / 'backend.js'; frozen_bundle.write_bytes(frozen['bundle'])
        request['binary'] = str(frozen_bundle)
        try:
            process = subprocess.run([str(paths['runtime']), str(script)], input=json.dumps(request),
                                     capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {**record, 'status': 'timeout', 'reason': 'precision-tool deadline exceeded'}
    record.update(returncode=process.returncode, stderr=process.stderr, stdout=process.stdout)
    if hashlib.sha256(paths['runtime'].read_bytes()).hexdigest() != identity['runtime_sha256']:
        return {**record, 'reason': 'precision runtime identity changed'}
    if len(process.stdout.encode()) > 131072:
        return {**record, 'reason': 'precision response byte budget exceeded'}
    if process.returncode != 0:
        return record
    try:
        messages = json.loads(process.stdout)
        results = messages[-1]
        if not isinstance(results, list) or len(results) != 1:
            raise ValueError('one completed precision-tool result required')
        errors = [e['error'] for e in results[0]['errors'] if e['errorName'] == 'absolute error (exact)']
        if len(errors) != 1 or len(errors[0]) != 2:
            raise ValueError('absolute error result missing')
        upper = errors[0][1]
        if type(upper) not in {int, float} or not math.isfinite(upper) or upper < 0:
            raise ValueError('nonfinite precision error result')
        record.update(status='computed_under_tool_model', upper_absolute_roundoff_error=upper,
                      tool_result=results[0], model_seconds=results[0]['elapsedTime'])
    except (ValueError, TypeError, KeyError, IndexError) as error:
        record['reason'] = str(error)
    return record
