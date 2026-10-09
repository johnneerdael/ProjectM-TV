from pathlib import Path
import sys,subprocess,hashlib,json
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import build_validation as builder
original=builder.prepare_engine
patch=Path('build/audit/motion-field-proposal/diagnostic-bilerp-oracle-native48x32.patch').resolve()
def prepare(repo,work):
 snapshot,identity=original(repo,work)
 env=dict(__import__('os').environ,GIT_CEILING_DIRECTORIES=str(snapshot.parent))
 subprocess.run(['git','apply','--check',str(patch)],cwd=snapshot,env=env,check=True)
 subprocess.run(['git','apply',str(patch)],cwd=snapshot,env=env,check=True)
 for n in ('PresetMotionVectorsVertexShaderGlsl330.vert','MotionVectorLineVertexShaderGlsl330.vert'):
  assert 'TEST ONLY' in (snapshot/'src/libprojectM/MilkdropPreset/Shaders'/n).read_text()
 return snapshot,identity
builder.prepare_engine=prepare
work=Path('build/audit/motion-field-oracle-native-workers').resolve()
builder.build('ac3dd034c15dced5423feed3077c15c39580823b','native','candidate-native',work)
p=work/'candidate-native/identity.json';d=json.loads(p.read_text());d['diagnostic_engine_patch']={'path':str(patch),'sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'scope':'TEST-ONLY analytic endpoint for exact paired Native48x32 finite diagnostic; invalid for arbitrary presets; never ship'};d['diagnostic_builder_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p.write_text(json.dumps(d,indent=2)+'\n')
