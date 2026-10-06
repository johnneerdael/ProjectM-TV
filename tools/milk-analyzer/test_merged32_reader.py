from analyzer_test_profiles import historical_source
import pytest
from shader_fields import ShaderFields
from field_math import evaluate



def test_current_global_uniform_copy_uses_its_actual_declaration_flags():
    raw=('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\n'
         'comp_1='+chr(96)+'shader_body {q18=1;ret=q19;}\n').encode()
    source=historical_source('merged32',raw)
    section=source['sections']['comp_']
    model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False)
    result=model.lower(section['tree'])
    assert model.complete,model.unknown
    assert list(evaluate(result,inputs={'_qe':[0,0,.4,0]}))==[.4]*3

pytestmark = pytest.mark.historical_profile("merged32")
