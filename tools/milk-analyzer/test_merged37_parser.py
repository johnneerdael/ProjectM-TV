import json,subprocess,tempfile
from pathlib import Path
from pytest import approx
from shader_fields import ShaderFields
from field_math import evaluate

READER=Path(__file__).resolve().parents[2]/'build/milk-analyzer/merged37-native/milk-native-reader'


def lower(code):
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'control.milk'
        records=['MILKDROP_PRESET_VERSION=201','PSVERSION_COMP=2']
        records += ['comp_'+str(i)+'='+chr(96)+line for i,line in enumerate(code.splitlines(),1)]
        path.write_text('\n'.join(records)+'\n')
        source=json.loads(subprocess.check_output([str(READER),str(path)]))
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
