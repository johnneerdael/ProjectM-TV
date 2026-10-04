"""Export complete score-bound review assets for the unchanged core category API."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from audience_policy import labels_for_intensity
from audience_ranking import relative_activity_ranks
from core_backend import reusable_result


def export_collection(corpus, results, output, *, identity, weights, run_metadata=None):
    rows=[];paths=set()
    for preset in corpus:
        name=preset['preset'];sha=preset['sha256'];row=results.get(sha)
        if name in paths or any(c in name for c in '\n\r\t'):
            raise ValueError('Duplicate or index-unsafe preset path')
        paths.add(name)
        if not row or not reusable_result(row,identity) or row.get('preset')!=name or row.get('sha256')!=sha:
            raise ValueError('Complete matching score required: '+name)
        rows.append({'preset':name,'sha256':sha,'score':row['score'],'labels':labels_for_intensity(row['score'])})
    if not rows:raise ValueError('Empty corpus cannot be a complete review collection')
    for row,rank in zip(rows,relative_activity_ranks([r['score'] for r in rows])):row['rank']=rank
    groups={'all':rows,'chill':[r for r in rows if 'Chill' in r['labels']],
            'normal':[r for r in rows if 'Normal' in r['labels']],
            'party':[r for r in rows if 'Party' in r['labels']]}
    aliases={'all':'all','chill':'ambient','normal':'pop','party':'dance'}
    output=Path(output);directory=output/'preset-genres/genres';directory.mkdir(parents=True,exist_ok=True)
    files=[]
    for group,selected in groups.items():
        path=directory/(aliases[group]+'.idx')
        path.write_text(''.join(f"{row['preset']}\t{weights.get(row['preset'],0)}\n" for row in selected),encoding='utf-8')
        files.append(path)
    table=output/'audience-scores.tsv'
    table.write_text(''.join(f"{r['preset']}\t{r['score']:.8f}\t{r['rank']:.8f}\n" for r in rows),encoding='utf-8');files.append(table)
    manifest={'schema_version':1,'identity':identity,'corpus_count':len(rows),'scored':len(rows),'unscored':0,
              'counts':{group:len(selected) for group,selected in groups.items()},'core_aliases':aliases,
              'bands':{'Chill':[0,30],'Normal':[25,75],'Party':[70,100]},
              'rank_semantics':'Relative ordering in this collection; does not change intensity bands',
              'checksums':{str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              'run_metadata':run_metadata or {},'presets':rows}
    (output/'audience-review.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    return manifest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--aar',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();metadata=json.loads((args.run/'run-identity.json').read_text())
    if hashlib.sha256(args.aar.read_bytes()).hexdigest()!=metadata['aar_sha256']:
        raise ValueError('Review AAR differs from scoring AAR')
    corpus=json.loads((args.run/'corpus.json').read_text())['cases']
    results={p.stem:json.loads(p.read_text()) for p in (args.run/'results').glob('*.json')}
    with zipfile.ZipFile(args.aar) as archive:
        weights={}
        for line in archive.read('assets/presets.idx').decode('utf-8').splitlines():
            parts=line.split('\t');weights[parts[0]]=int(parts[1]) if len(parts)>1 else 0
        expected={name.removeprefix('assets/presets/'):hashlib.sha256(archive.read(name)).hexdigest()
                  for name in archive.namelist() if name.startswith('assets/presets/') and name.lower().endswith('.milk')}
    if {r['preset']:r['sha256'] for r in corpus}!=expected:
        raise ValueError('Scoring corpus differs from published AAR')
    result=export_collection(corpus,results,args.output,identity=metadata['identity'],weights=weights,run_metadata=metadata)
    print(json.dumps({'status':'complete','counts':result['counts'],'output':str(args.output)}))


if __name__=='__main__':main()
