"""Offline target compatibility; compiler acceptance is not visual prediction."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def check_shader(code: str, *, stage: str, profile: str, translator: Path,
                 validator: Path, samplers: dict[str, str], texture_sizes: list[str]) -> dict:
    if stage not in {'warp', 'composite'}:
        raise ValueError('explicit warp/composite stage required')
    if profile not in {'glsl330', 'gles300'}:
        raise ValueError('explicit glsl330/gles300 profile required')
    request = {'code': code, 'stage': stage, 'profile': profile,
               'samplers': samplers, 'texture_sizes': texture_sizes}
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        input_file = root/'request.json'
        input_file.write_text(json.dumps(request))
        try:
            translated = subprocess.run([str(translator), str(input_file)], capture_output=True,
                                        text=True, errors='replace', timeout=15)
            translation_diagnostics=translated.stderr
            if translated.returncode:
                translation={'status':'unknown','reason':f'native translator process exit {translated.returncode}'}
            else:
                try:translation=json.loads(translated.stdout)
                except json.JSONDecodeError:
                    translation={'status':'unknown','reason':'native translator returned invalid JSON'}
        except subprocess.TimeoutExpired:
            translation={'status':'unknown','reason':'native translator time budget exceeded'}
            translation_diagnostics=''
        accepted = None if translation['status']=='unknown' else False
        compiler_diagnostics = ''
        if translation['status'] == 'translated':
            fragment = root/'shader.frag'
            fragment.write_text(translation['glsl'])
            process = subprocess.run([str(validator), '-S', 'frag', str(fragment)],
                                     capture_output=True, text=True, errors='replace', timeout=15)
            # Exit status alone cannot hide a process crash as a shader rejection.
            if process.returncode not in {0, 2}:
                raise RuntimeError('offline compiler failed: ' + process.stderr + process.stdout)
            accepted = process.returncode == 0
            compiler_diagnostics = process.stdout + process.stderr
        return {'source_sha256': hashlib.sha256(code.encode()).hexdigest(), 'request': request,
                'translation': translation, 'translation_diagnostics': translation_diagnostics,
                'translator_sha256': hashlib.sha256(translator.read_bytes()).hexdigest(),
                'validator_sha256': hashlib.sha256(validator.read_bytes()).hexdigest(),
                'offline_accepted': accepted, 'compiler_diagnostics': compiler_diagnostics,
                'predicted_stage': (None if accepted is None else 'custom_' + stage if accepted else
                                    'fixed_warp' if stage == 'warp' else 'default_composite'),
                'native_driver_verified': False,
                'limits': 'Prediction conditional on explicit descriptor/profile matching, native driver '
                          'compilation/linking, texture loading and fallback initialization. '
                          'Offline acceptance does not prove numeric domains or appearance.'}
