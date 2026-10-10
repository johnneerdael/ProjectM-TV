"""Optional component provenance and scalar-envelope integration controls."""
import os
from pathlib import Path

import pytest

from shader_fields import Field
from source_control_bounds import scalar_value_envelope


def solver_python():
    value = os.environ.get('MILK_PROOF_PYTHON')
    if not value:
        pytest.skip('prepared optional Z3 worker not supplied')
    return Path(value)


def difference():
    value = Field('input', (), 'float', {'name': 'bass'})
    return Field('subtract', (value, value), 'float')


def test_solver_disabled_keeps_scalar_value_output():
    assert 'solver_refinement' not in scalar_value_envelope(difference())


def test_solver_adds_correlated_nominal_value_evidence():
    from source_proofs import ProofSession
    baseline = scalar_value_envelope(difference(), input_domains={'bass': [0, 2]})
    with ProofSession(solver_python()):
        result = scalar_value_envelope(difference(), input_domains={'bass': [0, 2]})
    proof = result['solver_refinement']
    assert proof['status'] == 'bounded'
    assert proof['nominal_value_range'] == [0, 0]
    # Supplementary real proof does not overwrite existing native-facing claims.
    assert result['nominal_value_range'] == baseline['nominal_value_range']
    assert result['native_numeric_certified'] is False


def test_solver_identity_separates_cached_exports(tmp_path):
    from source_proofs import ProofSession
    import effect_family_export
    from test_core2331_warp import BINARIES
    path = tmp_path / 'solver.milk'
    path.write_text('[preset00]\nfWaveAlpha=0\nper_frame_1=rot=bass-bass;\n')
    cache = tmp_path / 'cache'
    plain, _ = effect_family_export.export_preset(path, reader=BINARIES / 'milk-native-reader', cache=cache)
    with ProofSession(solver_python()):
        enriched, hit = effect_family_export.export_preset(path, reader=BINARIES / 'milk-native-reader', cache=cache)
    assert hit is False
    assert enriched['cache_key'] != plain['cache_key']
    assert enriched['provenance']['source_components']['solver']['numeric_model'] == 'nominal-real'
    assert plain['analysis']['uses_rendered_images'] is False
    assert enriched['analysis']['uses_rendered_images'] is False


def test_phase_dependency_export_exposes_previous_frame_audio_path(tmp_path):
    import effect_family_export
    from test_core2331_warp import BINARIES
    path = tmp_path / 'recurrence.milk'
    path.write_text('[preset00]\nfWaveAlpha=0\nper_frame_init_1=a=0;b=0;\n'
                    'per_frame_1=a=b*.5;b=a+bass;rot=a;\n')
    cache = tmp_path / 'cache'
    plain, _ = effect_family_export.export_preset(path, reader=BINARIES / 'milk-native-reader', cache=cache)
    enriched, hit = effect_family_export.export_preset(
        path, reader=BINARIES / 'milk-native-reader', cache=cache, phase_dependencies=True)
    assert hit is False
    assert enriched['cache_key'] != plain['cache_key']
    evidence = enriched['source_dependency_evidence']
    assert 'bass' in evidence['outputs']['rot']['newly_exposed_input_dependencies']
    assert evidence['numeric_bounds_changed'] is False
    assert evidence['guaranteed_visible_audio_reaction'] is False
    assert 'source_dependency_evidence' not in plain


def test_source_mutation_during_supplemental_analysis_is_rejected(tmp_path, monkeypatch):
    import effect_family_export
    import source_stims
    from test_core2331_warp import BINARIES
    path = tmp_path / 'changed.milk'
    path.write_text('[preset00]\nfWaveAlpha=0\n')
    original = source_stims.source_phase_dependency_evidence
    def mutate(source):
        path.write_text('[preset00]\nfWaveAlpha=1\n')
        return original(source)
    monkeypatch.setattr(source_stims, 'source_phase_dependency_evidence', mutate)
    with pytest.raises(ValueError, match='changed during'):
        effect_family_export.export_preset(path, reader=BINARIES / 'milk-native-reader',
                                          phase_dependencies=True, cache=tmp_path / 'cache')
    assert not list((tmp_path / 'cache').glob('*.json'))
