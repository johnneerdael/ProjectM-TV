"""Exercise the native source translator and offline compiler together."""
import os
from pathlib import Path
import shutil

import pytest

from shader_compat import check_shader


ROOT = Path(__file__).resolve().parents[2]
TRANSLATOR = Path(os.environ.get('MILK_SHADER_TRANSLATOR',
    ROOT / 'build/milk-analyzer/native/milk-shader-translate'))
VALIDATOR = os.environ.get('MILK_GLSLANG_VALIDATOR') or shutil.which('glslangValidator')


@pytest.mark.parametrize('profile', ['glsl330', 'gles300'])
@pytest.mark.parametrize('code,accepted', [
    ('shader_body { ret = .25; }', True),
    ('shader_body { ret = ; }', False),
])
def test_native_translation_and_offline_compiler(profile, code, accepted):
    assert TRANSLATOR.is_file(), 'Build the native shader translator before source tests'
    assert VALIDATOR, 'Install glslangValidator for source compatibility tests'
    result = check_shader(code, stage='composite', profile=profile,
        translator=TRANSLATOR, validator=Path(VALIDATOR), samplers={}, texture_sizes=[])
    assert result['translation']['profile'] == profile
    assert result['translation']['stage'] == 'composite'
    assert result['translation']['engine_archive_sha256']
    assert result['offline_accepted'] is accepted
    assert result['predicted_stage'] == ('custom_composite' if accepted else 'default_composite')
    assert result['translation']['status'] == ('translated' if accepted else 'rejected')
