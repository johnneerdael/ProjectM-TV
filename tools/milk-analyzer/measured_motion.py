"""Sealed source-input-only numerical motion sampler, separate from strict math.

The executor is an auxiliary GLES vertex operator. It never receives display or
reference fields, and must bind its returns to exact inputs and a zero-render
context. Hardware arithmetic is measured, not independently reconstructed.
"""
import copy
import hashlib
import json
from pathlib import Path

import numpy as np

PROFILE = 'measured-gles300-vertex-half-v1'
BASIS = 'source-with-measured-operator'


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _bytes(values):
    return np.asarray(values, dtype='<f4').tobytes()


class MeasuredMotionSampler:
    def __init__(self, executor, *, identity, directory):
        qualified = json.loads((Path(__file__).parent /
            'fixtures/measured-motion-operator-bound-v2-2026-10-07.json').read_text())['identity']
        source_hash = _sha((Path(__file__).parent / 'MotionSamplerOperator.java').read_bytes())
        executor_hash = _sha((Path(__file__).parent / 'native_motion_executor.py').read_bytes())
        if (identity != qualified or identity.get('operator_source_sha256') != source_hash or
                identity.get('executor_source_sha256') != executor_hash):
            raise ValueError('measured motion operator identity is not qualified')
        if not callable(executor):
            raise ValueError('measured motion operator executor required')
        self._identity = copy.deepcopy(identity)
        self._executor = executor
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=False)
        self._calls = []
        self._attempts = 0

    @property
    def identity(self):
        return copy.deepcopy(self._identity)

    def __call__(self, field, queries, *, wrap, linear, origin):
        if wrap is not False or linear is not True or origin != 'bottom':
            raise ValueError('measured motion operator addressing requires linear bottom-origin clamp')
        field = np.asarray(field, dtype=np.float32).copy()
        queries = np.asarray(queries, dtype=np.float32).copy()
        if (field.ndim != 3 or field.shape[-1] != 2 or not 1 <= field.shape[0] <= 768 or
                not 1 <= field.shape[1] <= 1024 or not np.all(np.isfinite(field))):
            raise ValueError('measured motion operator requires finite two-channel half map')
        with np.errstate(over='ignore'):
            stored = field.astype(np.float16).astype(np.float32)
        if not np.array_equal(stored, field):
            raise ValueError('measured motion operator requires actual finite half texels')
        if (queries.ndim != 2 or queries.shape[1] != 2 or not 1 <= len(queries) <= 3072 or
                not np.all(np.isfinite(queries))):
            raise ValueError('measured motion operator requires finite query pairs')
        number = self._attempts
        self._attempts += 1
        folder = self._directory / f'{number:06d}'
        folder.mkdir()
        files = {}
        def save(name, raw):
            with (folder / name).open('xb') as stream:
                stream.write(raw)
            files[f'{number:06d}/{name}'] = _sha(raw)
        map_hash = _sha(_bytes(field))
        query_hash = _sha(_bytes(queries))
        save('input-map.f32', _bytes(field))
        save('input-queries.f32', _bytes(queries))
        try:
            output, evidence = self._executor(field.copy(), queries.copy(),
                wrap=False, linear=True, origin='bottom')
            output = np.asarray(output, dtype=np.float32)
            if output.shape != queries.shape or not np.all(np.isfinite(output)):
                raise ValueError('measured motion operator returned invalid samples')
            if not isinstance(evidence, dict) or evidence.get('identity') != self._identity:
                raise ValueError('measured motion operator result identity mismatch')
            for key in ('core_frame_serial_before', 'core_frame_serial_after', 'preset_draws'):
                if type(evidence.get(key)) is not int or evidence[key] != 0:
                    raise ValueError('measured motion operator rendered or unknown core frames')
            for key, expected in [('input_map_sha256', map_hash),
                    ('input_queries_sha256', query_hash), ('output_sha256', _sha(_bytes(output))),
                    ('physical_map_sha256', _sha(_bytes(field[::-1]))),
                    ('executor_source_sha256', self._identity['executor_source_sha256'])]:
                if evidence.get(key) != expected:
                    raise ValueError('measured motion operator result is not bound to input/output: ' + key)
            save('output.f32', _bytes(output))
            save('evidence.json', (json.dumps(evidence, sort_keys=True, indent=2)+'\n').encode())
            record = dict(input_map_sha256=map_hash, input_queries_sha256=query_hash,
                          output_sha256=_sha(_bytes(output)), files=files,
                          map_shape=list(field.shape), query_count=len(queries))
            self._calls.append(record)
            return output.copy()
        except Exception as error:
            (folder / 'failure.json').write_text(json.dumps({'status': 'unresolved',
                'reason': str(error), 'files': files}, indent=2)+'\n')
            raise

    def report(self):
        for call in self._calls:
            for name, digest in call['files'].items():
                if _sha((self._directory / name).read_bytes()) != digest:
                    raise ValueError('measured motion operator saved evidence changed')
        return dict(basis=BASIS, profile=PROFILE, identity=self.identity,
                    call_count=len(self._calls), attempts=self._attempts,
                    directory=str(self._directory), calls=copy.deepcopy(self._calls),
                    uses_reference_preset_frames=False, independent_sampler_math=False)
