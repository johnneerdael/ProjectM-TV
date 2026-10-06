"""Catch source-to-renderer float32 drift using the production parser and formatter."""
import hashlib
import json
import os
import re
import struct
import subprocess
from pathlib import Path

import pytest

import test_native_reader
from analyzer_test_profiles import validator_path
from shader_compat import check_shader

ROOT = Path(__file__).resolve().parents[2]
READER = Path(os.environ.get("MILK_TEST_CURRENT_BINARIES", test_native_reader.READER.parent)) / "milk-native-reader"
TRANSLATOR = READER.parent / "milk-shader-translate"
ROWS = json.loads((Path(__file__).parent / 'fixtures/float-literal-presets.json').read_text())['rows']


def float_bits(value):
    return struct.pack('<f', value)


def constants(node):
    if isinstance(node, dict):
        if 'renderer_literal' in node:
            yield node
        for value in node.values():
            yield from constants(value)
    elif isinstance(node, list):
        for value in node:
            yield from constants(value)


@pytest.mark.parametrize('row', ROWS, ids=lambda row: row['preset'])
def test_original_preset_literals_roundtrip(row):
    path = ROOT / 'core/src/main/assets/presets' / row['preset']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
    report = json.loads(subprocess.check_output([str(READER), str(path)]))
    inputs = report['parser_inputs']
    assert inputs['float_literal_policy'] == 'float32-roundtrip-v1'
    assert len(inputs['float_formatter_sha256']) == 64
    for witness in row['literals']:
        section = report['sections']['warp_' if witness['section'] == 'warp' else 'comp_']
        assert section['status'] == 'parsed'
        found = [node for node in constants(section['tree'])
                 if node['line'] == witness['generated_ast_line']
                 and float_bits(node['value']) == float_bits(witness['parsed_float32'])]
        assert found, (row['preset'], witness)
        for node in found:
            text = node['renderer_literal']
            assert re.fullmatch(r'float\([-+0-9.eE]+\)', text)
            assert float_bits(float(text[6:-1])) == float_bits(witness['parsed_float32'])


def test_coefficient_and_scale_keep_authored_float32(tmp_path):
    path = tmp_path / 'coefficient.milk'
    path.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\n'
                    'warp_1=`shader_body { ret=(q1*1.00000011920928955078125-1.0)*4194304.0; }\n')
    report = json.loads(subprocess.check_output([str(READER), str(path)]))
    found = list(constants(report['sections']['warp_']['tree']))
    for value in (1.0000001192092896, 4194304.0):
        nodes = [node for node in found if node['value'] == value]
        assert nodes
        for node in nodes:
            assert float_bits(float(node['renderer_literal'][6:-1])) == float_bits(value)


@pytest.mark.parametrize('profile', ['gles300', 'glsl330'])
def test_generated_control_compiles_without_literal_drift(profile):
    assert validator_path().is_file(), 'Install glslangValidator'
    code = 'shader_body { ret=float3((q1*1.00000011920928955078125-1.0)*4194304.0,.375,0); }'
    result = check_shader(code, stage='warp', profile=profile, translator=TRANSLATOR,
                          validator=validator_path(), samplers={}, texture_sizes=[])
    assert result['offline_accepted']
    translation = result['translation']
    assert translation['float_literal_policy'] == 'float32-roundtrip-v1'
    assert len(translation['float_formatter_sha256']) == 64
    numbers = [float(text) for text in re.findall(r'float\(([-+0-9.eE]+)\)', translation['glsl'])]
    assert 1.00000012 in numbers
    assert 4194304.0 in numbers


@pytest.mark.parametrize('profile', ['gles300', 'glsl330'])
def test_overflow_literal_cannot_bind_authored_inf_variable(profile):
    result = check_shader('shader_body { float inf=.5; ret=float3(1e40,inf,0); }',
                          stage='composite', profile=profile, translator=TRANSLATOR,
                          validator=validator_path(), samplers={}, texture_sizes=[])
    assert result['translation']['status'] == 'rejected'
    assert result['offline_accepted'] is False
    assert result['predicted_stage'] == 'default_composite'
