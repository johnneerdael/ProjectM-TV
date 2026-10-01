from pathlib import Path

import pytest

from preset_lab.dependencies import trace_dependencies
from preset_lab.preset_parser import parse_preset


def analyze(tmp_path, code):
    path = tmp_path / "fixture.milk"
    path.write_text("[preset00]\nfWaveAlpha=0\n" + code)
    return trace_dependencies(parse_preset(path))


def has_path(result, source, sink, via=None, section=None):
    return any(p["audio_input"] == source and p["sink"] == sink
               and (via is None or p["via"] == via)
               and (section is None or p["section"] == section) for p in result.paths)


def test_indirect_structural_path_has_actual_equation_evidence(tmp_path):
    result = analyze(tmp_path, "per_frame_1=q1=bass*2;zoom=1+q1;\n")
    assert result.complete
    assert has_path(result, "bass", "zoom", ["bass", "q1", "zoom"])
    path = next(p for p in result.paths if p["sink"] == "zoom")
    assert path["impact"] == "structural"
    assert path["line"] == 3


def test_overwrites_kill_inactive_dependencies(tmp_path):
    result = analyze(tmp_path, "per_frame_1=q1=bass;q1=0;zoom=q1;wave_r=mid;wave_r=0;\n")
    assert result.complete
    assert not has_path(result, "bass", "zoom")
    assert not has_path(result, "mid", "wave_r")


def test_duplicate_keys_first_gap_and_comments_match_engine(tmp_path):
    path = tmp_path / "parse.milk"
    path.write_text("[preset00]\nper_frame_1=q1=bass; // treb is a comment\n"
                    "per_frame_1=q1=treb;\nper_frame_2=zoom=q1;\n"
                    "per_frame_4=rot=mid;\n leading=invalid;\n")
    parsed = parse_preset(path)
    assert "rot" not in parsed["sections"]["per_frame_"]["code"]
    assert "q1=treb" not in parsed["sections"]["per_frame_"]["code"]
    result = trace_dependencies(parsed)
    assert has_path(result, "bass", "zoom")
    assert not has_path(result, "mid", "rot")
    assert not any(p["audio_input"] == "treb" for p in result.paths)


def test_init_persistence_and_reverse_frame_dependencies(tmp_path):
    result = analyze(tmp_path, "per_frame_init_1=held=bass;\n"
                     "per_frame_1=zoom=held+q2;q2=q1;q1=mid;\n")
    assert has_path(result, "bass", "zoom")
    assert has_path(result, "mid", "zoom")


def test_conditional_assignment_and_control_dependencies(tmp_path):
    result = analyze(tmp_path, "per_frame_1=if(bass>1,q1=mid,q1=treb);zoom=q1;rot=if(bass>1,0,1);\n")
    assert result.complete
    assert has_path(result, "bass", "zoom")
    assert has_path(result, "mid", "zoom")
    assert has_path(result, "treb", "zoom")
    assert has_path(result, "bass", "rot")


def test_q_variables_bridge_per_vertex_shape_wave_and_shader(tmp_path):
    result = analyze(tmp_path, "per_frame_1=q1=bass;\nper_pixel_1=zoom=q1;\n"
                     "shapecode_0_enabled=1\nshape_0_per_frame1=rad=q1;\n"
                     "wavecode_0_enabled=1\nwave_0_per_frame1=t1=q1;\n"
                     "wave_0_per_point1=x=t1+value1;y=sample;\n"
                     "PSVERSION_WARP=2\nwarp_1=`shader_body\nwarp_2=`{\n"
                     "warp_3=`float amount=q1; ret=float3(amount,0,0);\nwarp_4=`}\n")
    assert result.complete, result.unsupported
    assert has_path(result, "bass", "zoom", section="per_pixel_")
    assert has_path(result, "bass", "rad", section="shape_0_per_frame")
    assert has_path(result, "bass", "x", section="wave_0_per_point")
    assert has_path(result, "value1", "x")
    assert not has_path(result, "sample", "y")
    assert has_path(result, "bass", "ret", section="warp_")


def test_scopes_do_not_leak_custom_wave_local_variables(tmp_path):
    result = analyze(tmp_path, "wavecode_0_enabled=1\nwavecode_1_enabled=1\n"
                     "wave_0_per_frame1=private=bass;\nwave_1_per_point1=x=private;\n")
    assert not has_path(result, "bass", "x", section="wave_1_per_point")


def test_disabled_custom_objects_do_not_add_visible_dependencies(tmp_path):
    result = analyze(tmp_path, "wavecode_0_enabled=0\nwave_0_per_point1=x=bass;\n"
                     "shapecode_0_enabled=0\nshape_0_per_frame1=rad=mid;\n")
    assert not has_path(result, "bass", "x")
    assert not has_path(result, "mid", "rad")


def test_shader_branch_control_and_member_overwrite(tmp_path):
    result = analyze(tmp_path, "PSVERSION_COMP=2\ncomp_1=`shader_body\ncomp_2=`{\n"
                     "comp_3=`float3 color=float3(0,0,0); color.x=mid; color.x=0;\n"
                     "comp_4=`if(bass>1) {ret=color;} else {ret=float3(1,1,1);}\ncomp_5=`}\n")
    assert result.complete, result.unsupported
    assert has_path(result, "bass", "ret")
    assert not has_path(result, "mid", "ret")


def test_unsupported_memory_does_not_claim_no_audio_influence(tmp_path):
    result = analyze(tmp_path, "per_frame_1=megabuf(bass)=mid;zoom=megabuf(1);\n")
    assert not result.complete
    assert result.unsupported


def test_sample_position_is_not_an_audio_source(tmp_path):
    result = analyze(tmp_path, "wavecode_0_enabled=1\nwave_0_per_point1=x=sample;y=0.5;\n")
    assert not any(p["audio_input"] == "sample" for p in result.paths)


def test_shader_swizzles_of_expressions_preserve_dependencies(tmp_path):
    result = analyze(tmp_path, "PSVERSION_COMP=2\ncomp_1=`shader_body\ncomp_2=`{\n"
                     "comp_3=`ret=(float3(bass,0,0)*2).xyz;\ncomp_4=`}\n")
    assert result.complete
    assert has_path(result, "bass", "ret")


def test_private_frame_variables_do_not_cross_into_vertex_context(tmp_path):
    result = analyze(tmp_path, "per_frame_1=hidden=bass;\nper_pixel_1=zoom=hidden;\n")
    assert not has_path(result, "bass", "zoom", section="per_pixel_")


def test_wave_point_context_only_imports_q_t_and_visible_wave_state(tmp_path):
    result = analyze(tmp_path, "wavecode_0_enabled=1\nwave_0_per_frame1=hidden=bass; t1=mid;\n"
                     "wave_0_per_point1=x=hidden; y=t1;\n")
    assert not has_path(result, "bass", "x", section="wave_0_per_point")
    assert has_path(result, "mid", "y", section="wave_0_per_point")


def test_wave_sample_values_are_not_global_spectral_inputs(tmp_path):
    result = analyze(tmp_path, "per_frame_1=zoom=value1;\n")
    assert not has_path(result, "value1", "zoom")


def test_only_q1_to_q32_bridge_contexts(tmp_path):
    result = analyze(tmp_path, "per_frame_1=q33=bass;\nper_pixel_1=zoom=q33;\n")
    assert not has_path(result, "bass", "zoom", section="per_pixel_")


def test_inherited_parameters_are_not_attributed_to_unrelated_vertex_lines(tmp_path):
    result = analyze(tmp_path, "per_frame_1=zoom=bass;\nper_pixel_1=rot=mid;\n")
    assert has_path(result, "bass", "zoom", section="per_frame_")
    assert not has_path(result, "bass", "zoom", section="per_pixel_")


def test_builtin_waveform_audio_is_visible_without_eel_references(tmp_path):
    path = tmp_path / "wave.milk"
    path.write_text("[preset00]\nfWaveAlpha=1\nnWaveMode=0\n")
    result = trace_dependencies(parse_preset(path))
    assert has_path(result, "waveform_pcm", "builtin_wave_geometry")
