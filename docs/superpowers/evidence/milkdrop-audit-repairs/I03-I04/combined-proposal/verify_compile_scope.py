#!/usr/bin/env python3
"""Read actual CMake compilation commands; do not infer effective flags from prose."""
import argparse,json,shlex
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('commands',type=Path);parser.add_argument('--baseline',action='store_true');args=parser.parse_args()
entries=json.loads(args.commands.read_text());evaluator=[e for e in entries if '/vendor/projectm-eval/projectm-eval/' in e['file'] and e['file'].endswith('.c')]
if not evaluator:raise SystemExit('No real bundled evaluator C compilation found')
observed=[];treeCount=0
for item in evaluator:
    tokens=item.get('arguments') or shlex.split(item['command']);name=Path(item['file']).name
    overrides=[i for i,arg in enumerate(tokens) if arg=='-fno-finite-math-only'];fast=[i for i,arg in enumerate(tokens) if arg in ('-ffast-math','-Ofast')]
    if not fast:raise SystemExit('Expected Release/RelWithDebInfo evaluator fast-math: '+item['file'])
    if name=='TreeFunctions.c':
        treeCount+=1
        if args.baseline:
            if overrides:raise SystemExit('Baseline unexpectedly has finite-only override')
        elif len(overrides)!=1 or overrides[0]<=max(fast):raise SystemExit('TreeFunctions override missing, duplicated, or before fast-math')
    elif overrides:raise SystemExit('Finite-only override escaped TreeFunctions.c: '+item['file'])
    observed.append({'file':item['file'],'directory':item['directory'],'argv':tokens,'fast_positions':fast,'finite_override_positions':overrides})
if treeCount!=1:raise SystemExit('Expected exactly one actual TreeFunctions compilation')
print(json.dumps({'actual_evaluator_units':len(evaluator),'TreeFunctions_units':treeCount,'baseline':args.baseline,'source_scope_verified':True,'commands':observed},indent=2))
