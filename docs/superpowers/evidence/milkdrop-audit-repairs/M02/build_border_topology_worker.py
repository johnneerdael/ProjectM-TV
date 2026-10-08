from pathlib import Path
import sys,subprocess,hashlib,json
sys.path.insert(0,str(Path('tools/native-trails').resolve()))
import build_validation as builder
original=builder.prepare_engine
patch=Path('build/audit/border-topology-proposal/original-border-fan-topology.patch').resolve()
def prepare(repo,work):
 snapshot,identity=original(repo,work)
 subprocess.run(['git','apply','--check',str(patch)],cwd=snapshot,check=True)
 subprocess.run(['git','apply',str(patch)],cwd=snapshot,check=True)
 return snapshot,identity
builder.prepare_engine=prepare
work=Path('build/audit/border-topology-native-workers').resolve()
builder.build('ac3dd034c15dced5423feed3077c15c39580823b','native','candidate-native',work)
p=work/'candidate-native/identity.json';d=json.loads(p.read_text());d['diagnostic_engine_patch']={'path':str(patch),'sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'scope':'original fan triangle diagonals; same counts/current float palette; outside canonical source; outside canonical series; full source hashes identify instrumented candidate'};d['diagnostic_builder_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p.write_text(json.dumps(d,indent=2)+'\n')
