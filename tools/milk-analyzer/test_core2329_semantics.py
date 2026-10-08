"""Cache-only release source identity retains established predictor math policies."""
from pathlib import Path
import json
import pytest

ENGINE={'commit':'6f64807467e312034883a4389e6aa80a675458bc',
        'patches_sha256':'01d259c40d364f8d55b9ee43ab29dcf39fd85f107908969c23671b3cea064457'}


def test_release29_source_reader_and_inherited_math():
    from forecast import read_source,PRODUCTION_EQUATION_ENGINES,source_centre_policies
    from engine_profiles import CORE_2329_ENGINE,matches
    from legacy_composite import source_tint_amount
    from composite_mesh import CORE_2322_CENTRES
    from primitives import CORE_2322_SHAPE_CENTRES
    root=Path(__file__).resolve().parents[2]
    reader=root/'build/preset-corpus/source29/adapters/milk-native-reader'
    if not reader.exists():pytest.skip('prepared release29 source adapters required')
    source=read_source(root/'core/src/main/assets/presets/$$$ Royal - Mashup (1).milk',reader=reader)
    assert source['parser_inputs']['engine']==ENGINE==CORE_2329_ENGINE
    assert matches(ENGINE)
    assert PRODUCTION_EQUATION_ENGINES['projectmtv-core-2.3.29-cold-thread-v1']==ENGINE
    assert source_centre_policies(ENGINE,{})==(CORE_2322_CENTRES,CORE_2322_SHAPE_CENTRES)
    assert source_tint_amount({'values':{'fShader':'.25'},'parser_inputs':{'engine':ENGINE}})==.25
    assert not matches({**ENGINE,'patches_sha256':'0'*64})
