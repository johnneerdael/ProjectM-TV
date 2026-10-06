from analyzer_test_profiles import historical_source
import pytest
from pytest import approx
from shader_fields import ShaderFields
from field_math import evaluate



def lower(code):
    records=['MILKDROP_PRESET_VERSION=201','PSVERSION_COMP=2']
    records += ['comp_'+str(i)+'='+chr(96)+line for i,line in enumerate(code.splitlines(),1)]
    source=historical_source('merged37', ('\n'.join(records)+'\n').encode())
    section=source['sections']['comp_']
    assert section['status']=='parsed'
    model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False,
        array_initializer_policy=section['array_initializer_policy'])
    result=model.lower(section['tree'])
    assert model.complete,model.unknown
    return evaluate(result).tolist()


def test_merged_parser_accepts_sample_as_a_local_expression_name():
    assert lower('shader_body {float3 sample=.2;ret=sample*sample*sample;}')==approx([.008]*3)


def test_merged_macro_preserves_token_precedence_and_declaration_expansion():
    assert lower('#define X 2+3\n#define DECL float3 v=.2;\nshader_body {DECL ret=X*4+v;}')==approx([14.2]*3)


def test_merged_parser_preserves_parenthesized_expression_swizzle():
    assert lower('shader_body {ret=(float3(.2,.4,.6)*2).xyy;}')==approx([.4,.8,.8])

pytestmark = pytest.mark.historical_profile("merged37")
