"""Export complete score-bound review assets for the unchanged core category API."""
import argparse
import hashlib
import json
import math
import sys
import tempfile
import zipfile
from pathlib import Path

from preset_lab.inventory import read_index

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


def verify_review_assets(output, aar):
    output=Path(output);aar=Path(aar)
    manifest=json.loads((output/'audience-review.json').read_text())
    if hashlib.sha256(aar.read_bytes()).hexdigest()!=manifest['run_metadata']['aar_sha256']:
        raise ValueError('Review AAR identity differs')
    with zipfile.ZipFile(aar) as archive:
        expected={name.removeprefix('assets/presets/'):hashlib.sha256(archive.read(name)).hexdigest()
                  for name in archive.namelist() if name.startswith('assets/presets/') and name.lower().endswith('.milk')}
        with tempfile.TemporaryDirectory(prefix='milk-review-index-') as temporary:
            master=Path(temporary)/'presets.idx'
            master.write_bytes(archive.read('assets/presets.idx'))
            weights=read_index(master)
    if weights.keys()!=expected.keys() or any(weight>2**31-1 for weight in weights.values()):
        raise ValueError('Published master index differs from supported preset corpus/weights')
    rows=manifest['presets']
    if manifest['core_aliases']!={'all':'all','chill':'ambient','normal':'pop','party':'dance'}:
        raise ValueError('Review core aliases differ')
    if manifest['bands']!={'Chill':[0,30],'Normal':[25,75],'Party':[70,100]}:
        raise ValueError('Review intensity bands differ')
    if (manifest['unscored']!=0 or manifest['scored']!=len(expected) or manifest['corpus_count']!=len(expected)
            or len(rows)!=len(expected) or {r['preset']:r['sha256'] for r in rows}!=expected):
        raise ValueError('Review collection is not the complete published corpus')
    for row in rows:
        if not reusable_result({'identity':'verified','status':'scored','score':row['score']},'verified'):
            raise ValueError('Invalid review intensity')
        if row['labels']!=labels_for_intensity(row['score']):raise ValueError('Score labels differ from bands')
        if isinstance(row['rank'],bool) or not isinstance(row['rank'],(int,float)) or not math.isfinite(row['rank']) or not 1<=row['rank']<=100:
            raise ValueError('Invalid review relative rank')
    ranks=relative_activity_ranks([r['score'] for r in rows])
    if any(abs(row['rank']-rank)>1e-8 for row,rank in zip(rows,ranks)):
        raise ValueError('Relative ranks differ from score ordering')
    expected_table=''.join(f"{r['preset']}\t{r['score']:.8f}\t{r['rank']:.8f}\n" for r in rows)
    if (output/'audience-scores.tsv').read_text(encoding='utf-8')!=expected_table:
        raise ValueError('Displayed scores differ from manifest')
    for group,label in (('all',None),('chill','Chill'),('normal','Normal'),('party','Party')):
        alias=manifest['core_aliases'][group]
        index=output/f'preset-genres/genres/{alias}.idx'
        actual=list(read_index(index).items()) if index.stat().st_size else []
        selected=[r['preset'] for r in rows if label is None or label in r['labels']]
        if actual!=[(name,weights[name]) for name in selected] or manifest['counts'][group]!=len(selected):
            raise ValueError('Group membership or memory weights differ from published scores/index: '+group)
    for name,expected_hash in manifest['checksums'].items():
        if hashlib.sha256((output/name).read_bytes()).hexdigest()!=expected_hash:
            raise ValueError('Review asset checksum differs: '+name)
    return manifest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',type=Path)
    parser.add_argument('--aar',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--verify',action='store_true')
    parser.add_argument('--model',type=Path,default=Path(__file__).parent/'profiles/audience-model-v1.json')
    args=parser.parse_args()
    if args.verify:
        result=verify_review_assets(args.output,args.aar)
        print(json.dumps({'status':'verified','scored':result['scored'],'counts':result['counts']}));return
    if args.run is None:parser.error('--run required for export')
    from score_audit import audit_run
    audit=audit_run(args.run,args.model)
    if not audit['ready']:
        print(json.dumps({'status':'incomplete',
            'audit':{k:v for k,v in audit.items() if k!='issues'},
            'audit_command':[sys.executable,str(Path(__file__).with_name('score_audit.py')),
                '--run',str(args.run),'--model',str(args.model),
                '--output',str(args.output.parent/'score-audit.json')]}))
        raise SystemExit(1)
    metadata=json.loads((args.run/'run-identity.json').read_text())
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
