import json
from pathlib import Path
import subprocess
import tempfile
from shader_fields import ShaderFields
from field_math import evaluate

READER=Path(__file__).resolve().parents[2]/'build/milk-analyzer/merged32-native/milk-native-reader'


def test_current_global_uniform_copy_uses_its_actual_declaration_flags():
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'test.milk'
        path.write_text('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\n'
                        'comp_1='+chr(96)+'shader_body {q18=1;ret=q19;}\n')
        source=json.loads(subprocess.check_output([str(READER),str(path)]))
    section=source['sections']['comp_']
    model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False)
    result=model.lower(section['tree'])
    assert model.complete,model.unknown
    assert list(evaluate(result,inputs={'_qe':[0,0,.4,0]}))==[.4]*3
