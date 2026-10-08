#!/usr/bin/env python3
"""Root-owned exact compiler IR/assembly capture; default only prints argv."""
import argparse,json,shlex,subprocess,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('commands',type=Path);p.add_argument('output',type=Path);p.add_argument('--execute',action='store_true');args=p.parse_args()
entries=json.loads(args.commands.read_text());rows=[x for x in entries if x['file'].endswith('/vendor/projectm-eval/projectm-eval/TreeFunctions.c')]
if len(rows)!=1:raise SystemExit('Expected one actual bundled TreeFunctions compile command')
entry=rows[0];original=entry.get('arguments') or shlex.split(entry['command'])
if '-fno-finite-math-only' in original or '-fno-fast-math' in original:raise SystemExit('Bit candidate must retain original evaluator math flags')
if not any(x in original for x in ('-ffast-math','-Ofast')):raise SystemExit('Expected actual Release/RelWithDebInfo fast-math')
if 'clang' not in Path(original[0]).name:raise SystemExit('LLVM IR capture requires pinned Clang/AppleClang; qualify GNU separately')
args.output.mkdir(parents=True,exist_ok=True);base=[];i=0
while i<len(original):
    if original[i]=='-o':i+=2;continue
    if original[i]=='-c':i+=1;continue
    base.append(original[i]);i+=1
commands=[]
for kind,flags,suffix in [('ir',['-S','-emit-llvm'],'.ll'),('assembly',['-S'],'.s')]:
    destination=args.output/('TreeFunctions'+suffix);argv=base+flags+['-o',str(destination.resolve())];commands.append({'kind':kind,'argv':argv,'destination':str(destination.resolve())});print(shlex.join(argv))
    if args.execute:subprocess.run(argv,cwd=entry['directory'],check=True)
record={'original_entry':entry,'captures':commands,'execution_requested':args.execute,'source_sha256':hashlib.sha256(Path(entry['file']).read_bytes()).hexdigest()}
if args.execute:record['output_sha256']={item['kind']:hashlib.sha256(Path(item['destination']).read_bytes()).hexdigest() for item in commands}
(args.output/'capture-command-identity.json').write_text(json.dumps(record,indent=2)+'\n')
