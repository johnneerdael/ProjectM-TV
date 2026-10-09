#!/usr/bin/env python3
"""Require all20 actual boundary observations to preserve unchanged compiler policy."""
import json,sys
from pathlib import Path
if len(sys.argv)!=3:raise SystemExit('usage:compare_boundaries.py BASELINE_LOG BITS_CANDIDATE_LOG')
def load(path):
    records={}
    for line in Path(path).read_text().splitlines():
        if line.startswith('BOUNDARY_JSON '):
            item=json.loads(line[len('BOUNDARY_JSON '):]);records[item['name']]=item
    if len(records)!=20:raise SystemExit('Expected20 unique executed boundary records: '+path)
    return records
before=load(sys.argv[1]);after=load(sys.argv[2])
if before.keys()!=after.keys():raise SystemExit('Boundary case sets differ')
changed=[]
for name in before:
    for output in ('q','a','b'):
        if before[name][output]!=after[name][output]:changed.append({'name':name,'output':output,'before':before[name][output],'after':after[name][output]})
print(json.dumps({'boundary_cases':20,'policy_sensitive_cases':sum(x['policySensitive'] for x in after.values()),'baseline_policy_preserved':not changed,'differences':changed},indent=2))
raise SystemExit(1 if changed else 0)
