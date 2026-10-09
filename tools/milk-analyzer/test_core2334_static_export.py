"""Explicit source34 static export keeps actual parser provenance."""
from pathlib import Path
from effect_family_export import export_preset
from engine_profiles import CORE_2334_ENGINE

ROOT=Path(__file__).resolve().parents[2]


def test_explicit_source34_export_has_distinct_engine_and_no_frame_execution(tmp_path):
    preset=tmp_path/'shape.milk'
    preset.write_text('[preset00]\nfWaveAlpha=0\nshapecode_0_enabled=1\n'
                      'shape_0_per_frame1=rad=.2+bass*.1;\n')
    record,hit=export_preset(preset,reader=ROOT/'build/preset-corpus/source34/adapters/milk-native-reader')
    assert not hit and record['status']=='computed'
    assert record['provenance']['engine']==CORE_2334_ENGINE
    assert record['uses_rendered_reference'] is False
    assert record['analysis']['uses_shader_execution'] is False
    assert record['analysis']['uses_equation_execution'] is False
    assert any(e.get('audio_area_response',{}).get('source_model')=='affine_audio_radius'
               for e in record['analysis']['visual_description']['elements'])
