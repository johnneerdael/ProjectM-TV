"""Select active shader stages from the native reader's canonical file values."""
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

import test_native_reader
from source_context import scalar
from stage_resolution import resolve_stages


ROOT = Path(__file__).resolve().parents[2]
CODE = 'shader_body { ret = .25; }'


def read_control(settings, version=201):
    return test_native_reader.NativeReaderTest().read(
        settings + '\nwarp_1=`' + CODE + '\ncomp_1=`' + CODE + '\n',
        version=version,
    )


def test_real_acid_mandala_reader_output_does_not_disable_active_shaders():
    preset = ROOT / 'core/src/main/assets/presets/Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk'
    assert hashlib.sha256(preset.read_bytes()).hexdigest() == '163034eb002666dfd1966444dedd1a47853131e915a5cb2745bd09ff52a4e230'
    source = json.loads(subprocess.check_output([str(test_native_reader.READER), str(preset)]))
    assert source['values']['milkdrop_preset_version'] == '201'
    assert source['values']['psversion_warp'] == '3'
    assert source['values']['psversion_comp'] == '2'
    stages = resolve_stages(source, profile='gles300', compatibility={})
    for name, version in [('warp', 3), ('composite', 2)]:
        assert stages[name]['shader_version'] == version
        assert stages[name]['kind'] == 'unknown'
        assert stages[name]['reason'] == 'missing, stale or unresolved target compatibility evidence'


@pytest.mark.parametrize('version,settings,want', [
    (200, 'PSVERSION=3', (3, 3)),
    (201, 'pSvErSiOn_wArP=3\nPsVeRsIoN_CoMp=0', (3, 0)),
    (201, '', (2, 2)),
    (100, 'PSVERSION_WARP=3\nPSVERSION_COMP=3', (0, 0)),
])
def test_native_version_gates_and_defaults_follow_normalized_values(version, settings, want):
    source = read_control(settings, version)
    stages = resolve_stages(source, profile='gles300', compatibility={})
    assert (stages['warp']['shader_version'], stages['composite']['shader_version']) == want
    assert stages['warp']['kind'] == ('unknown' if want[0] > 0 else 'fixed_warp')
    assert stages['composite']['kind'] == ('unknown' if want[1] > 0 else 'legacy_composite')


def test_case_insensitive_lookup_preserves_native_scalar_conversion_and_defaults():
    values = read_control('fWaRpScAlE=2.5suffix\nbTeXwRaP=-1')['values']
    assert scalar(values, 'fWarpScale', 1.0, 'float') == 2.5
    assert scalar(values, 'FWARPSCALE', 1.0, 'float') == 2.5
    assert scalar(values, 'bTexWrap', 1, 'bool') == 1
    assert scalar(values, 'MISSING_SETTING', 7, 'int') == 7


def test_native_active_stages_use_matching_offline_acceptance():
    from shader_compat import check_shader
    import test_shader_compat

    source = read_control('PSVERSION_WARP=2\nPSVERSION_COMP=2')
    compatibility = {}
    for name, prefix in [('warp', 'warp_'), ('composite', 'comp_')]:
        compatibility[name] = check_shader(
            source['sections'][prefix]['source'],
            stage=name,
            profile='gles300',
            translator=test_shader_compat.TRANSLATOR,
            validator=Path(test_shader_compat.VALIDATOR),
            samplers={},
            texture_sizes=[],
        )
        assert compatibility[name]['offline_accepted'] is True
    stages = resolve_stages(source, profile='gles300', compatibility=compatibility)
    assert stages['warp']['kind'] == 'custom_warp'
    assert stages['composite']['kind'] == 'custom_composite'
    assert stages['warp']['conditional_on_native_profile'] is True
    assert stages['composite']['conditional_on_native_profile'] is True
