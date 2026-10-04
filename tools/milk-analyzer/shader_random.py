"""Source-generated shader random uniforms under an explicit lifecycle/profile.

No renderer observations are inputs. The seed is the actual post-mix C-rand
seed, not an inferred lab seed. Constructors, idle/fallback instances and load
order must be supplied; host-libc results do not establish Android equivalence.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import numpy as np


RANDOM_NAMES = {'rand_frame', 'rand_preset'} | {
    f'rot_{group}{i}' for group in ('s', 'd', 'f', 'vf', 'uf', 'rand') for i in range(1, 5)}


def execute_ledger(binary: Path, *, seed: int, events: list[dict], timeout=30) -> dict:
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError('explicit uint32 post-mix C-rand seed required')
    if not isinstance(events, list):
        raise ValueError('explicit random lifecycle event list required')
    for event in events:
        if (not isinstance(event, dict) or event.get('kind') not in {'construct', 'load'} or
                not isinstance(event.get('id'), str) or not event['id']):
            raise ValueError('invalid shader random lifecycle event')
    request = json.dumps(dict(seed=seed, events=events), allow_nan=False)
    binary = Path(binary).resolve()
    binary_sha = hashlib.sha256(binary.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='milk-random-') as directory:
        path = Path(directory) / 'request.json'
        path.write_text(request)
        process = subprocess.run([str(binary), str(path)], capture_output=True, text=True, timeout=timeout)
    if process.returncode:
        raise ValueError('shader random source evaluation failed: ' + process.stderr.strip())
    result = json.loads(process.stdout)
    if result.get('schema_version') != 1 or result.get('seed') != seed:
        raise ValueError('random input response identity mismatch')
    records = result.get('events', [])
    if len(records) != len(events):
        raise ValueError('random event ledger is incomplete')
    expected_draws = 0
    for event, record in zip(events, records):
        if any(record.get(key) != event[key] for key in ('kind', 'id')):
            raise ValueError('random event order mismatch')
        if record.get('draws_before') != expected_draws:
            raise ValueError('random stream position mismatch')
        expected_draws += 184 if event['kind'] == 'construct' else 28
        if record.get('draws_after') != expected_draws:
            raise ValueError('random consumption differs from pinned source')
    if result.get('draws_consumed') != expected_draws:
        raise ValueError('random draw total mismatch')
    loads = [i for i, event in enumerate(events) if event['kind'] == 'load']
    if [row.get('event_index') for row in result.get('loads', [])] != loads:
        raise ValueError('random load result order mismatch')
    for i in loads:
        bind_random_uniforms(result, event_index=i, shader_id=events[i]['id'],
                             time=events[i]['time'], profile=result['profile'])
    result.update(binary_sha256=binary_sha,
                  request_sha256=hashlib.sha256(request.encode()).hexdigest())
    return result


def bind_random_uniforms(result: dict, *, event_index: int, shader_id: str, time: float, profile: dict) -> dict:
    if result.get('schema_version') != 1 or result.get('profile') != profile:
        raise ValueError('shader random profile mismatch')
    if type(event_index) is not int or event_index < 0:
        raise ValueError('nonnegative random event index required')
    matches = [row for row in result.get('loads', []) if row.get('event_index') == event_index]
    if len(matches) != 1 or matches[0].get('id') != shader_id:
        raise ValueError('shader random load identity mismatch')
    with np.errstate(over='ignore'):
        native_time = np.float32(time)
    if not np.isfinite(native_time) or matches[0].get('time') != float(native_time):
        raise ValueError('shader random load time mismatch')
    uniforms = matches[0].get('uniforms')
    if not isinstance(uniforms, dict) or set(uniforms) != RANDOM_NAMES:
        raise ValueError('shader random uniform bank is incomplete')
    bank = {}
    for name, value in uniforms.items():
        values = np.asarray(value, dtype=np.float32)
        shape = (4, 3) if name.startswith('rot_') else (4,)
        if values.shape != shape or not np.all(np.isfinite(values)):
            raise ValueError('finite correctly shaped shader random uniform required: ' + name)
        bank[name] = values.tolist()
    return bank
