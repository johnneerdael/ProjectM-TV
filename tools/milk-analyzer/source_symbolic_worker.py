"""Pinned symbolic algebra worker. JSON graphs only; never evaluate source text."""
import json
import math
import sys

SYMPY_VERSION = '1.14.0'
MAX_NODES = 128
MAX_DEPTH = 48


def validate_node(node):
    arity = {'input': 0, 'constant': 0, 'add': 2, 'subtract': 2, 'multiply': 2,
             'sin': 1, 'cos': 1, 'negate': 1, 'sqr': 1, 'unary': 1}
    op = node['op']; detail = node['detail']
    if node['dtype'] != 'float' or detail.get('numeric_domain'):
        raise ValueError('typed or native numeric conversion excluded')
    if op not in arity or len(node['args']) != arity[op]:
        raise ValueError('unsupported original symbolic operation: ' + op)
    if op == 'input' and (set(detail) != {'name'} or not isinstance(detail['name'], str) or
                          not detail['name'] or len(detail['name']) > 256):
        raise ValueError('qualified phase/storage input requires a binding adapter')
    if op == 'constant' and (type(detail.get('value')) not in {int, float} or not math.isfinite(detail['value'])):
        raise ValueError('finite real scalar literal required')
    if op == 'unary' and detail.get('operator') not in {0, 1}:
        raise ValueError('unsupported scalar unary operation')


def differentiate(request, sp):
    nodes = request['program']['nodes']
    if not 1 <= len(nodes) <= MAX_NODES:
        raise ValueError('symbolic source node budget exceeded')
    memo = {}
    active = set()
    symbols = {}
    names = {}

    def visit(index, depth=0):
        if type(index) is not int or not 0 <= index < len(nodes):
            raise ValueError('invalid symbolic node reference')
        if index in memo:
            return memo[index]
        if depth > MAX_DEPTH or index in active:
            raise ValueError('symbolic source depth/cycle budget exceeded')
        active.add(index)
        node = nodes[index]
        validate_node(node)
        op = node['op']
        detail = node['detail']
        if node['dtype'] != 'float' or detail.get('numeric_domain'):
            raise ValueError('typed or native numeric conversion excluded')
        # Validate every original operand before SymPy can cancel/prune it.
        args = [visit(i, depth + 1) for i in node['args']]
        if op == 'input' and not args:
            if set(detail) != {'name'}:
                raise ValueError('qualified phase/storage input requires a binding adapter')
            name = detail.get('name')
            if not isinstance(name, str) or not name or len(name) > 256:
                raise ValueError('invalid scalar input name')
            if name not in symbols:
                symbols[name] = sp.Dummy(real=True)
                names[symbols[name]] = name
            result = symbols[name]
        elif op == 'constant' and not args:
            value = detail.get('value')
            if type(value) not in {int, float} or not math.isfinite(value):
                raise ValueError('finite real scalar literal required')
            result = sp.Rational(float(value))
        elif op in {'add', 'subtract', 'multiply'} and len(args) == 2:
            result = {'add': lambda: args[0] + args[1],
                      'subtract': lambda: args[0] - args[1],
                      'multiply': lambda: args[0] * args[1]}[op]()
        elif op in {'sin', 'cos', 'negate', 'sqr'} and len(args) == 1:
            result = {'sin': lambda: sp.sin(args[0]), 'cos': lambda: sp.cos(args[0]),
                      'negate': lambda: -args[0], 'sqr': lambda: args[0]**2}[op]()
        elif op == 'unary' and len(args) == 1 and detail.get('operator') in {0, 1}:
            result = -args[0] if detail['operator'] == 0 else args[0]
        else:
            raise ValueError('unsupported original symbolic operation: ' + op)
        active.remove(index)
        memo[index] = result
        return result

    expression = visit(request['program']['root'])
    selected = request['input_names']
    if not isinstance(selected, list) or not selected or any(not isinstance(n, str) for n in selected):
        raise ValueError('response input names required')
    derivative = sum((sp.diff(expression, symbols[n]) for n in selected if n in symbols), sp.S.Zero)
    # Avoid broad search over unrelated angle sums. Use the library's focused
    # product-to-sum transformation on the derivative, not whole-source expansion.
    from sympy.simplify.fu import TR8
    for count, _ in enumerate(sp.preorder_traversal(derivative)):
        if count >= 512:
            raise ValueError('symbolic derivative transformation budget exceeded')
    derivative = TR8(derivative)
    emitted = 0

    def emit(value, depth=0):
        nonlocal emitted
        emitted += 1
        if emitted > 512 or depth > MAX_DEPTH:
            raise ValueError('symbolic derivative output budget exceeded')
        if value in names:
            return ['input', names[value]]
        if value.is_Rational:
            return ['rational', str(value.p), str(value.q)]
        if value.func in {sp.Add, sp.Mul}:
            return ['add' if value.func == sp.Add else 'multiply',
                    *[emit(a, depth + 1) for a in value.args]]
        if value.func in {sp.sin, sp.cos}:
            return ['sin' if value.func == sp.sin else 'cos', emit(value.args[0], depth + 1)]
        if value.func == sp.Pow and value.args[1].is_Integer and 0 <= value.args[1] <= 16:
            return ['integer_power', emit(value.args[0], depth + 1), int(value.args[1])]
        raise ValueError('unsupported generated symbolic derivative')

    return {'status': 'derived', 'derivative': emit(derivative),
            'assumed_finite_input_names': sorted(symbols), 'generated_nodes': emitted}


def main():
    import sympy as sp
    if sp.__version__ != SYMPY_VERSION:
        raise ValueError('prepared SymPy ' + SYMPY_VERSION + ' required')
    print(json.dumps({'protocol': 1, 'sympy_version': sp.__version__}), flush=True)
    for line in sys.stdin:
        try:
            if len(line) > 131072:
                raise ValueError('symbolic request byte budget exceeded')
            result = differentiate(json.loads(line), sp)
        except (ValueError, KeyError, TypeError, RecursionError, OverflowError) as error:
            result = {'status': 'unsupported', 'reason': str(error)}
        print(json.dumps(result, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
