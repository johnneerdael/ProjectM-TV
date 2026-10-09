"""Execute after isolated timing; link unchanged production GLSL ES3 source pairs."""
from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path('build/authored-followup');folder=root/'shader-link';assert not folder.exists();folder.mkdir()
source=root/'engine/src/libprojectM/MilkdropPreset/Shaders';validator=shutil.which('glslangValidator');assert validator
vs=(source/'PresetWarpVertexShaderGlsl330.vert').read_bytes();fs=(source/'PresetWarpFragmentShaderGlsl330.frag').read_bytes();rows=[]
for variant,define in [('legacy','#define PROJECTM_LEGACY_WARP\n'),('custom-contract','')]:
 vertex=folder/(variant+'.vert');fragment=folder/(variant+'.frag');vertex.write_bytes(('#version 300 es\n'+define).encode()+vs);fragment.write_bytes(b'#version 300 es\n'+fs)
 result=subprocess.run([validator,'-l',str(vertex),str(fragment)],capture_output=True,text=True)
 (folder/(variant+'.txt')).write_text(result.stdout+result.stderr);result.check_returncode()
 rows.append({'variant':variant,'vertex_sha256':hashlib.sha256(vertex.read_bytes()).hexdigest(),'fragment_sha256':hashlib.sha256(fragment.read_bytes()).hexdigest(),'status':'pass'})
(folder/'identity.json').write_text(json.dumps({'source_vertex_sha256':hashlib.sha256(vs).hexdigest(),'source_fragment_sha256':hashlib.sha256(fs).hexdigest(),'header':'production #version 300 es; legacy define only where real accessor supplies it','pairs':rows},indent=2)+'\n')
print('Both unchanged production warp variants link as GLSL ES3.00')
