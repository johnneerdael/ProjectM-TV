"""Execute only after isolated timing; clone clean committed recursive sources."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess
parser=argparse.ArgumentParser();parser.add_argument('--sha',required=True);args=parser.parse_args()
root=Path.cwd().resolve();work=root/'build/authored-followup';checkout=work/'fresh-recursive';assert not checkout.exists()
def call(command,log,cwd=root):
 with (work/log).open('ab') as output:
  subprocess.run(command,cwd=cwd,stdout=output,stderr=subprocess.STDOUT,check=True)
call(['git','clone','--shared','--no-checkout',str(root),str(checkout)],'fresh-recursive-checkout.txt')
call(['git','checkout','--detach',args.sha],'fresh-recursive-checkout.txt',checkout)
# Local Git object sources contain the pinned commits, not uncommitted patched files.
# URLs are checkout-local config only; committed .gitmodules stays upstream-authored.
call(['git','config','submodule.third_party/projectm.url',str(root/'third_party/projectm')],'fresh-recursive-checkout.txt',checkout)
call(['git','-c','protocol.file.allow=always','submodule','update','--init','third_party/projectm'],'fresh-recursive-checkout.txt',checkout)
engine=checkout/'third_party/projectm'
call(['git','config','submodule.vendor/projectm-eval.url',str(root/'third_party/projectm/vendor/projectm-eval')],'fresh-recursive-checkout.txt',engine)
call(['git','-c','protocol.file.allow=always','submodule','update','--init','--recursive'],'fresh-recursive-checkout.txt',checkout)
status=subprocess.run(['git','status','--porcelain','--ignore-submodules=none'],cwd=checkout,capture_output=True,text=True,check=True).stdout
assert not status,status
pins=subprocess.run(['git','submodule','status','--recursive'],cwd=checkout,capture_output=True,text=True,check=True).stdout
assert '6f64807467e312034883a4389e6aa80a675458bc' in pins and '22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a' in pins
(checkout/'local.properties').write_text('sdk.dir=/Users/jneerdael/Library/Android/sdk\n')
call(['./gradlew',':core:assembleDebug',':app:assembleRelease','--console=plain'],'fresh-recursive-build.txt',checkout)
result={'source_commit':args.sha,'clean_before_configure':True,'submodule_status':pins,'patches':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((checkout/'tools/projectm-patches').glob('*.patch'))},'artifacts':{}}
for label,path in [('core_debug_aar',checkout/'core/build/outputs/aar/core-debug.aar'),('release_apk',checkout/'app/build/outputs/apk/release/app-release.apk')]:
 assert path.exists();result['artifacts'][label]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(work/'fresh-recursive-results.json').write_text(json.dumps(result,indent=2)+'\n')
print('Fresh committed recursive coreDebug/releaseAPK build passes at',args.sha)
