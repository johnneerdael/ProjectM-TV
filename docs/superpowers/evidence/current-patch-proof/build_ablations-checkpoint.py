from pathlib import Path
import subprocess, json, shutil, os, concurrent.futures
ROOT=Path(__file__).resolve().parents[2];WORK=Path(__file__).resolve().parent
NDK=Path('/Users/jneerdael/Library/Android/sdk/ndk/27.3.13750724')
PATCHES={int(p.name[:4]):p for p in (ROOT/'tools/projectm-patches').glob('*.patch')}
def build(number):
 role='without-'+str(number).zfill(4); dest=WORK/'ablations'/role;dest.mkdir(parents=True,exist_ok=False)
 engine=dest/'engine';shutil.copytree(WORK/'patched-capture-engine',engine)
 patch=PATCHES[number]
 subprocess.run(['git','apply','--reverse',str(patch)],cwd=engine,env=dict(os.environ,GIT_CEILING_DIRECTORIES=str(engine.parent)),check=True,capture_output=True)
 with (dest/'build.log').open('w') as log:
  subprocess.run(['cmake','-S',str(WORK/'harness'),'-B',str(dest/'ndk-build'),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(NDK/'build/cmake/android.toolchain.cmake'),'-DANDROID_ABI=arm64-v8a','-DANDROID_PLATFORM=android-34','-DANDROID_STL=c++_static','-DCMAKE_BUILD_TYPE=Release','-DPROJECTM_SOURCE='+str(engine),'-DPATCH_PROOF_TV=ON'],stdout=log,stderr=subprocess.STDOUT,check=True)
  subprocess.run(['cmake','--build',str(dest/'ndk-build'),'-j','2'],stdout=log,stderr=subprocess.STDOUT,check=True)
 (dest/'complete.json').write_text(json.dumps({'removed_patch':patch.name,'base':'current13-no-binary-cache','method':'git apply --reverse after deterministic instrumentation; exact patch reverse-check succeeded'}))
 print(role,'built',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 list(pool.map(build,[4,6,7,8,11,12,13,2,3,5,9,10]))
