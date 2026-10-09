from pathlib import Path
import sys,subprocess,hashlib,json
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import build_validation as builder
original=builder.prepare_engine
patch=Path('build/audit/shape-thick-proposal/i24-grouped-live-shape-thick.patch').resolve()
def prepare(repo,work):
 snapshot,identity=original(repo,work)
 env=dict(__import__('os').environ,GIT_CEILING_DIRECTORIES=str(snapshot.parent))
 subprocess.run(['git','apply','--check',str(patch)],cwd=snapshot,env=env,check=True)
 subprocess.run(['git','apply',str(patch)],cwd=snapshot,env=env,check=True)
 assert 'draw.thick' in (snapshot/'src/libprojectM/MilkdropPreset/CustomShape.cpp').read_text()
 assert 'DrawSegments' in (snapshot/'src/libprojectM/MilkdropPreset/LineRenderer.cpp').read_text()
 return snapshot,identity
builder.prepare_engine=prepare
work=Path('build/audit/shape-thick-grouped-v2-native-workers').resolve()
builder.build('ac3dd034c15dced5423feed3077c15c39580823b','native','candidate-native',work)
p=work/'candidate-native/identity.json';d=json.loads(p.read_text());d['diagnostic_engine_patch']={'path':str(patch),'sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'scope':'Experimental I24 evaluated per-instance thickness plus bounded disjoint transparent grouping; Native qualification required; outside canonical series'};d['diagnostic_builder_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p.write_text(json.dumps(d,indent=2)+'\n')
