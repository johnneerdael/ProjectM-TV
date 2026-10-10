"""Optional Crab fixpoint candidates for a declared source-bound clamp recurrence.

The caller supplies the nominal transfer model. Exact source joins do not prove
that this model covers the complete native phase, initialization or FP semantics.
"""
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import time

from source_shader_compiler import sha256, _digest


def infer_clamp_candidate(source, *, frame_fragment, init_fragment, initial_interval,
                          clamp_bounds, worker, mutate_clamp=False, timeout=20):
    sections=source.get('sections', {})
    if not frame_fragment.strip() or frame_fragment not in sections.get('per_frame_',{}).get('source',''):
        raise ValueError('exact main-frame source fragment required')
    if not init_fragment.strip() or init_fragment not in sections.get('per_frame_init_',{}).get('source',''):
        raise ValueError('exact main-init source fragment required')
    if len(initial_interval)!=2 or len(clamp_bounds)!=2 or not 0<timeout<=60:
        raise ValueError('bounded initialization/clamp query required')
    values=[Fraction(v) for v in [*initial_interval,*clamp_bounds]]
    if any(v.numerator.bit_length()>63 or v.denominator.bit_length()>63 for v in values):
        raise ValueError('rational query exceeds bit budget')
    if values[0]>values[1] or values[2]>values[3]:
        raise ValueError('ordered initialization/clamp intervals required')
    worker=Path(worker).resolve()
    version=subprocess.run([str(worker),'--version'],capture_output=True,text=True,timeout=timeout,check=True).stdout.strip()
    if version!='source-state-crab-worker/1 crabb1eeb1a9402ab0664e962f26f89d923f8514284c':
        raise ValueError('qualified Crab worker version required')
    model={'kind':'nominal-real-clamp-arbitrary-delta-recurrence', 'initial_interval':list(map(str,values[:2])),
           'clamp_bounds':list(map(str,values[2:])), 'delta_domain':'all finite real values', 'mutate_clamp':mutate_clamp}
    started=time.perf_counter();inference=None;reason=None
    try:
        process=subprocess.run([str(worker),*map(str,values),*(['mutation'] if mutate_clamp else [])],
                               capture_output=True,text=True,timeout=timeout)
        if process.returncode:reason='Crab process failed: '+process.stderr[-2000:]
        else:inference=json.loads(process.stdout)
    except (subprocess.TimeoutExpired,json.JSONDecodeError) as error:reason=str(error)
    result={'schema_version':1,'kind':'source-state-crab-candidate', 'status':'candidate_inferred' if inference else 'unknown',
            'preset_sha256':source['preset_sha256'], 'engine':source['parser_inputs']['engine'],
            'engine_archive_sha256':source['parser_inputs']['engine_archive_sha256'],
            'frame_fragment_sha256':sha256(frame_fragment), 'init_fragment_sha256':sha256(init_fragment),
            'declared_model':model, 'worker_sha256':sha256(worker.read_bytes()), 'worker_version':version,
            'inference':inference, 'reason':reason, 'seconds':time.perf_counter()-started,
            'source_model_mapping_verified':False, 'initialization_and_phase_obligations_verified':False,
            'native_numeric_equivalence_verified':False, 'candidate_only':True,
            'limits':'Use inferred intervals as candidates for separate ordered-phase/init/reset proofs. No native-FP, source-wide state or prediction claim.'}
    result['record_sha256']=_digest(result)
    return result
