from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path('tools/native-trails').resolve()));import run_validation as runner
b=Path('build/audit/extended-mode-proposal/arm64-input');device='emulator-5640';assert runner.current_user(device)==0
identity=json.loads((b/'build-result.json').read_text());pcm=Path('build/audit/dot-diagnostics-audio.u8');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(pcm)=='14a59e75249dee0dd15d74487688c248c6a4a4b24a843b6d6f612ccc5c408dbc'
with runner.corpus.session_lock(device,5037):
 target='/data/local/tmp/projectmtv-audit-i21-input';runner.shell(device,'mkdir','-p',target)
 for local,name,expected in [(b/'arm64-input-producer','producer',identity['sha256']),(pcm,'audio.u8',sha(pcm))]:
  runner.adb(device,'push',local,target+'/'+name);actual=runner.shell(device,'sha256sum',target+'/'+name).strip().split();assert len(actual)==2 and actual[0]==expected
 runner.shell(device,'chmod','700',target+'/producer')
 result=runner.shell(device,target+'/producer',target+'/audio.u8',target+'/trace.jsonl',timeout=120);print(result)
 runner.adb(device,'pull',target+'/trace.jsonl',b/'target-trace.jsonl')
 runtime={'device':device,'android_user':0,'fingerprint':runner.shell(device,'getprop','ro.build.fingerprint').strip(),'abi':runner.shell(device,'getprop','ro.product.cpu.abi').strip(),'runtime_libm_sha256':runner.shell(device,'sha256sum','/apex/com.android.runtime/lib64/bionic/libm.so').strip().split()[0],'executable_sha256':identity['sha256'],'transport_sha256':sha(pcm),'trace_sha256':sha(b/'target-trace.jsonl'),'waveSmoothing':0.75,'qualification':'separate source ARM64 producer; no shipping hidden-array observation; no GPU/context/draw'}
 (b/'target-runtime.json').write_text(json.dumps(runtime,indent=2)+'\n');(b/'target-output.txt').write_text(result)
