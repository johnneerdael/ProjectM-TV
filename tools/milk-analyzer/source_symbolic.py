"""Optional isolated SymPy component over existing source graphs and range maths."""
from collections import OrderedDict
from contextvars import ContextVar
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import subprocess
import threading
import time

ACTIVE = ContextVar('source_symbolic_component', default=None)
WORKER = Path(__file__).with_name('source_symbolic_worker.py')


def active_identity():
    session = ACTIVE.get()
    return None if session is None else session.identity


def _program(field):
    nodes = []
    memo = {}
    active = set()

    def visit(node, depth=0):
        key = id(node)
        if key in memo:
            return memo[key]
        if depth > 48 or key in active or len(nodes) >= 128:
            raise ValueError('symbolic source graph budget/cycle exceeded')
        from source_symbolic_worker import validate_node
        validate_node({'op':node.op,'dtype':node.dtype,'args':node.args,'detail':node.detail})
        active.add(key)
        index = len(nodes)
        nodes.append(None)
        memo[key] = index
        args = [visit(a, depth + 1) for a in node.args]
        nodes[index] = {'op': node.op, 'dtype': node.dtype, 'args': args, 'detail': node.detail}
        active.remove(key)
        return index

    root = visit(field)
    return {'root': root, 'nodes': nodes}


def _lower(tree, domains, derived, depth=0):
    from shader_fields import Field
    if depth > 48:
        raise ValueError('generated derivative depth exceeded')
    op = tree[0]
    if op == 'input':
        return Field('input', dtype='float', detail={'name': tree[1]})
    if op == 'rational':
        value = Fraction(int(tree[1]), int(tree[2]))
        rounded = float(value)
        if not math.isfinite(rounded) or value != 0 and rounded == 0:
            raise ValueError('symbolic derivative coefficient overflow/underflow')
        if Fraction(rounded) == value:
            return Field('constant', dtype='float', detail={'value': rounded})
        low = rounded if Fraction(rounded) < value else math.nextafter(rounded, -math.inf)
        high = rounded if Fraction(rounded) > value else math.nextafter(rounded, math.inf)
        if not all(math.isfinite(v) for v in (low, high)):
            raise ValueError('symbolic derivative coefficient enclosure overflow')
        name = ':symbolic-rational-' + str(len(derived))
        while name in domains or name in derived:
            name += '_'
        domains[name] = [low, high]
        derived.add(name)
        return Field('input', dtype='float', detail={'name': name})
    if op in {'sin', 'cos'}:
        return Field(op, (_lower(tree[1], domains, derived, depth + 1),), 'float')
    if op == 'integer_power':
        base = _lower(tree[1], domains, derived, depth + 1)
        exponent = tree[2]
        if type(exponent) is not int or not 0 <= exponent <= 16:
            raise ValueError('unsupported derivative exponent')
        value = Field('constant', dtype='float', detail={'value': 1.})
        for _ in range(exponent):
            value = Field('multiply', (value, base), 'float')
        return value
    if op in {'add', 'multiply'} and len(tree) > 1:
        args = [_lower(a, domains, derived, depth + 1) for a in tree[1:]]
        value = args[0]
        for other in args[1:]:
            value = Field(op, (value, other), 'float')
        return value
    raise ValueError('unsupported derivative protocol operation')


class SymbolicSession:
    """One caller-owned reusable worker; a timeout disables this session."""

    def __init__(self, python, *, timeout=1., startup_timeout=10.):
        if not 0 < timeout <= 10 or not 0 < startup_timeout <= 30:
            raise ValueError('bounded positive worker timeouts required')
        # Preserve a venv executable's path: resolving its symlink would run
        # the base Python without that environment's optional dependencies.
        self.python = Path(python).absolute()
        if not self.python.is_file():
            raise ValueError('prepared symbolic Python executable required')
        self.timeout = timeout
        self.startup_timeout = startup_timeout
        self.process = None
        self.failure = None
        self.cache = OrderedDict()
        self.stats = {'queries': 0, 'cache_hits': 0, 'timeouts': 0}
        self.lock = threading.Lock()
        self.buffer = b''
        self.identity = {'policy': 'source-sympy-nominal-response-v1', 'sympy_version': '1.14.0',
                         'worker_sha256': hashlib.sha256(WORKER.read_bytes()).hexdigest(),
                         'python': str(self.python), 'timeout_seconds': timeout}

    def _read(self, seconds, *, deadline=None):
        deadline = time.monotonic() + seconds if deadline is None else deadline
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout, selectors.EVENT_READ)
            while b'\n' not in self.buffer:
                left = deadline - time.monotonic()
                if left <= 0 or not selector.select(left):
                    raise TimeoutError('symbolic worker time budget exceeded')
                block = os.read(self.process.stdout.fileno(), 65536)
                if not block:
                    raise ValueError('symbolic worker closed its output')
                self.buffer += block
                if len(self.buffer) > 131072:
                    raise ValueError('symbolic response byte budget exceeded')
        line, self.buffer = self.buffer.split(b'\n', 1)
        return json.loads(line)

    def _write(self, payload, deadline):
        offset = 0
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdin, selectors.EVENT_WRITE)
            while offset < len(payload):
                left = deadline - time.monotonic()
                if left <= 0 or not selector.select(left):
                    raise TimeoutError('symbolic worker request time budget exceeded')
                try:
                    count = os.write(self.process.stdin.fileno(), payload[offset:])
                except BlockingIOError:
                    continue
                if count == 0:
                    raise ValueError('symbolic worker stopped reading requests')
                offset += count

    def close(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.kill()
            self.process.wait(timeout=5)
            self.process.stdin.close()
            self.process.stdout.close()

    def __enter__(self):
        self.token = ACTIVE.set(self)
        return self

    def __exit__(self, *args):
        ACTIVE.reset(self.token)
        self.close()

    def query(self, program, input_names):
        request = {'program': program, 'input_names': sorted(input_names)}
        encoded = json.dumps(request, sort_keys=True, allow_nan=False).encode()
        if len(encoded) > 131072:
            return {'status': 'unsupported', 'reason': 'symbolic request byte budget exceeded'}
        key = hashlib.sha256(encoded).hexdigest()
        with self.lock:
            if key in self.cache:
                self.stats['cache_hits'] += 1
                self.cache.move_to_end(key)
                return self.cache[key]
            if self.failure is not None:
                return {'status': 'unavailable', 'reason': self.failure}
            try:
                if self.process is None:
                    self.process = subprocess.Popen([str(self.python), '-u', str(WORKER)],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
                    os.set_blocking(self.process.stdin.fileno(), False)
                    ready = self._read(self.startup_timeout)
                    if ready != {'protocol': 1, 'sympy_version': '1.14.0'}:
                        raise ValueError('symbolic worker version/protocol mismatch')
                self.stats['queries'] += 1
                deadline = time.monotonic() + self.timeout
                self._write(encoded + b'\n', deadline)
                result = self._read(self.timeout, deadline=deadline)
                self.cache[key] = result
                if len(self.cache) > 4096:
                    self.cache.popitem(last=False)
                return result
            except (OSError, ValueError, TimeoutError) as error:
                self.failure = str(error)
                self.stats['timeouts'] += isinstance(error, TimeoutError)
                self.close()
                return {'status': 'unavailable', 'reason': self.failure}


def refine_response(field, input_names, input_domains, original_report):
    """Return additional nominal derivative bounds; never certify native maths."""
    session = ACTIVE.get()
    if session is None:
        return None
    result = {'policy': session.identity['policy'], 'backend': session.identity,
              'status': 'unsupported', 'maximum_absolute_control_change_per_audio_unit': None,
              'native_numeric_certified': False, 'unknown_reasons': [],
              'conditions': ['Pure nominal real source formula and finite original inputs/intermediates',
                             'Native rounding, conversions, texture/state evolution and visibility remain separate']}
    try:
        if (not original_report['supported_nominal_formula'] and original_report['unknown_reasons'] !=
                ['unsupported input, discontinuous operation or unproved denominator domain']):
            raise ValueError('Original source calculation failure retained: ' + '; '.join(original_report['unknown_reasons']))
        for name, span in (input_domains or {}).items():
            if (not isinstance(name, str) or not isinstance(span, (list, tuple)) or len(span) != 2 or
                    any(type(v) not in {int, float} or not math.isfinite(v) for v in span) or span[0] > span[1]):
                raise ValueError('invalid declared symbolic input domain')
        from source_control_bounds import compound_time_bounds
        original_values = compound_time_bounds(field, _value_only=True, _input_domains=input_domains)
        if (not original_values['supported_nominal_formula'] and original_values['unknown_reasons'] !=
                ['unsupported input, discontinuous operation or unproved denominator domain']):
            raise ValueError('Original source value-domain failure retained: ' + '; '.join(original_values['unknown_reasons']))
        response = session.query(_program(field), input_names)
        if response['status'] != 'derived':
            result.update(status=response['status'], unknown_reasons=[response['reason']])
            return result
        domains = dict(input_domains or {})
        # Reserve real source names before introducing any coefficient inputs.
        derived = set(response['assumed_finite_input_names'])
        expression = _lower(response['derivative'], domains, derived)
        from source_control_bounds import scalar_value_envelope
        bound = scalar_value_envelope(expression, input_domains=domains)
        span = bound['nominal_value_range']
        maximum = None if span is None else max(map(abs, span))
        result.update(status='bounded' if maximum is not None else 'unbounded',
                      maximum_absolute_control_change_per_audio_unit=maximum,
                      derivative_program=response['derivative'],
                      assumed_finite_input_names=response['assumed_finite_input_names'],
                      unknown_reasons=bound['unknown_reasons'])
    except (ValueError, TypeError, RecursionError, OverflowError, ZeroDivisionError) as error:
        result['unknown_reasons'] = [str(error)]
    return result
