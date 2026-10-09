from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for role in ['with-0019','without-0019']:
 source=root/role/'engine';out=root/role/'native-build'
 out.mkdir(exist_ok=True)
 with (root/role/'build.log').open('w') as log:
  subprocess.run(['cmake','-S',str(root/'harness'),'-B',str(out),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DCATALOG_TV=ON','-DPROJECTM_SOURCE='+str(source)],check=True,stdout=log,stderr=subprocess.STDOUT)
  subprocess.run(['cmake','--build',str(out),'-j','6'],check=True,stdout=log,stderr=subprocess.STDOUT)
 worker=out/'preset-lab-worker'
 receipt={'role':role,'worker':str(worker),'worker_sha256':sha(worker),'source':{p.relative_to(source).as_posix():sha(p) for p in sorted(source.rglob('*')) if p.is_file()},'harness':{p.relative_to(root/'harness').as_posix():sha(p) for p in sorted((root/'harness').rglob('*')) if p.is_file()}}
 (root/role/'identity.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(role,worker,flush=True)
