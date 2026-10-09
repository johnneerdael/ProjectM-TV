#!/usr/bin/env python3
"""Print a reviewable frozen-archive link command; root explicitly opts into execution."""
from pathlib import Path
import argparse,hashlib,json,shlex,subprocess
parser=argparse.ArgumentParser()
parser.add_argument('--execute',action='store_true')
args=parser.parse_args()
base=Path(__file__).resolve().parent
identity=json.loads((base/'frozen-link-inputs.json').read_text())
cxx=Path(identity['frozen_cxx_directory']);engine=Path(identity['frozen_engine_source'])
frozen_argv=shlex.split(identity['frozen_pcm_compilation']['command'])
compiler=frozen_argv[0]
sysroot=next(arg for arg in frozen_argv if arg.startswith('--sysroot='))
lib=cxx/'projectm/src/libprojectM/libprojectM-4.a'
for item in identity['frozen_archives']:
    path=Path(item['path']);hasher=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):hasher.update(chunk)
    if hasher.hexdigest()!=item['sha256']:raise SystemExit('Frozen archive hash changed: '+str(path))
output=base/'arm64-input-producer'
argv=[compiler,'--target=aarch64-none-linux-android21',sysroot,'-std=gnu++17','-O2','-g','-fPIE','-pie',
      '-fdata-sections','-ffunction-sections','-fvisibility=hidden','-Wl,--gc-sections','-static-libstdc++',
      '-DPROJECTM_CXX_STATIC_DEFINE','-DPROJECTM_STATIC_DEFINE','-DUSE_GLES',
      '-I'+str(engine/'src/libprojectM'),'-I'+str(engine/'src/libprojectM/MilkdropPreset'),'-I'+str(engine/'vendor'),'-I'+str(engine/'vendor/glad/include'),
      '-I'+str(engine/'src/api/include'),'-I'+str(cxx/'projectm/include'),'-I'+str(cxx/'projectm/src/api/include'),
      '-I'+str(engine/'vendor/projectm-eval/projectm-eval/api'),'-include',str(cxx/'projectm/include/config.h'),
      str(base/'arm64_input_producer.cpp'),str(lib),'-llog','-lGLESv3','-lEGL','-landroid','-latomic','-lm','-o',str(output)]
print(shlex.join(argv))
(base/'link-command.json').write_text(json.dumps({'argv':argv,'uses_existing_frozen_archive':True,'new_shipping_exports':False,'execution_requested':args.execute},indent=2)+'\n')
if args.execute:
    subprocess.run(argv,check=True)
    result={'executable':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((base/'arm64_input_producer.cpp').read_bytes()).hexdigest(),'sink_sha256':hashlib.sha256((base/'constructor_sink.hpp').read_bytes()).hexdigest(),'argv':argv,'target':'aarch64 Android21','qualification':'separate source-instrumented CPU producer; no hidden shipping JNI array observation'}
    (base/'build-result.json').write_text(json.dumps(result,indent=2)+'\n')
