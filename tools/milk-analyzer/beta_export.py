"""Export and verify complete, source-bound predictive collections (beta)."""
import argparse
import hashlib
import json
import math
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'preset-lab/src'))
from preset_lab.identity import canonical_json,digest,file_digest
from preset_lab.inventory import inventory,read_index
from beta_collections import BANDS,ranked_rows

EXPECTED_PROFILE={'frames':420,'warmup':60,'fps':30,'width':128,'height':72,'motion_fps':10}
PUBLISHED_CORE=json.loads((Path(__file__).parent/'profiles/published-core-v2.3.3.json').read_text())


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_identity(facts):
    content={k:v for k,v in facts.items() if k!='identity'}
    if facts.get('identity')!=hashlib.sha256(json.dumps(content,sort_keys=True).encode()).hexdigest():
        raise ValueError('Run identity mismatch')
    if facts.get('backend')!='released-projectmtv-core-jni' or facts.get('profile')!=EXPECTED_PROFILE:
        raise ValueError('Published-AAR numerical protocol required')
    source=Path(__file__).parent
    for key,path in [('scorer_sha256',source/'beta_score.py'),
                     ('descriptor_sha256',source/'descriptors.py'),
                     ('model_sha256',source/'profiles/audience-model-v1.json')]:
        if facts.get(key)!=file_digest(path):raise ValueError('Scoring implementation/model differs')
    runtime=facts.get('runtime_sha256',{})
    if set(runtime)!={'core.aar','libprojectmtv.so','classes.dex','libbackendclock.so','input.f32'}:
        raise ValueError('Incomplete runtime identity')
    if runtime['core.aar']!=facts.get('aar_sha256') or runtime['libprojectmtv.so']!=facts.get('native_arm64_sha256'):
        raise ValueError('Runtime artifact identity differs')


def check_activity(row):
    features=row.get('features')
    if (not isinstance(features,list) or len(features)!=4
            or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 for x in features)):
        raise ValueError('Invalid activity features')
    up,down,peak=(row.get(k) for k in ('coherent_up','coherent_down','paired_flash_peak'))
    if (any(type(x) is not int or not 0<=x<=360 for x in (up,down))
            or isinstance(peak,bool) or not isinstance(peak,(int,float)) or not math.isfinite(peak) or not 0<=peak<=1):
        raise ValueError('Invalid coherent activity features')
    if not math.isclose(features[0],(up+down)/12,rel_tol=1e-10,abs_tol=1e-10):
        raise ValueError('Inconsistent coherent activity rate')
    model=load(Path(__file__).parent/'profiles/audience-model-v1.json')['model']
    raw=model['intercept']+sum(w*math.log1p(x)/s for w,x,s in zip(model['weights'],features,model['feature_scale']))
    expected=max(raw,100*math.sqrt(peak)*min(1,min(up,down)/12))
    value=row.get('raw_activity')
    if (isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value)
            or not math.isclose(value,expected,rel_tol=1e-10,abs_tol=1e-10)):
        raise ValueError('Raw activity differs from frozen numerical model')
    if row.get('motion_basis') not in ('bidirectional10Hzflow','direct_temporal_change_over_spatial_gradient_proxy'):
        raise ValueError('Unknown activity motion estimator')


def source_inventory(assets):
    records,metadata=inventory(assets/'presets',assets/'presets.idx',assets/'textures')
    return {r.path:{'preset':r.path,'sha256':r.sha256,'weight_mb':r.weight_mb} for r in records},metadata


def check_aar(aar,assets,facts,known,metadata):
    if any(facts.get(k)!=PUBLISHED_CORE[k] for k in ('release','aar_sha256','native_arm64_sha256')):
        raise ValueError('Run did not use the pinned standard published AAR')
    if file_digest(aar)!=facts.get('aar_sha256'):raise ValueError('AAR hash differs')
    with zipfile.ZipFile(aar) as z:
        if hashlib.sha256(z.read('jni/arm64-v8a/libprojectmtv.so')).hexdigest()!=facts['native_arm64_sha256']:
            raise ValueError('AAR native library differs')
        if z.read('assets/presets.idx')!=(assets/'presets.idx').read_bytes():
            raise ValueError('Master index/weights differ from scored AAR')
        names={n.removeprefix('assets/presets/') for n in z.namelist()
               if n.startswith('assets/presets/') and n.lower().endswith('.milk')}
        if names!=set(known):raise ValueError('AAR preset inventory differs')
        for name,row in known.items():
            if hashlib.sha256(z.read('assets/presets/'+name)).hexdigest()!=row['sha256']:
                raise ValueError('Preset source differs from scored AAR: '+name)
        textures={n.removeprefix('assets/textures/'):hashlib.sha256(z.read(n)).hexdigest()
                  for n in z.namelist() if n.startswith('assets/textures/') and not n.endswith('/')}
        if textures!={r['path']:r['sha256'] for r in metadata['textures']}:
            raise ValueError('Texture pack differs from scored AAR')


def read_complete_results(run,facts,known):
    cases=load(run/'corpus.json')['cases']
    if len(cases)!=len(known) or {r['preset']:r['sha256'] for r in cases}!={n:r['sha256'] for n,r in known.items()}:
        raise ValueError('Run corpus differs from complete source inventory')
    rows=[]
    for name,source in sorted(known.items(),key=lambda pair:pair[0].encode()):
        path=run/'results'/(source['sha256']+'.json')
        if not path.is_file():raise ValueError('Missing result: '+name)
        row=load(path)
        if (row.get('status')!='scored' or row.get('identity')!=facts['identity']
                or row.get('preset')!=name or row.get('sha256')!=source['sha256']):
            raise ValueError('Unscored/stale result: '+name)
        meta=row.get('metadata',{})
        if (meta.get('backend')!='published-core-jni' or meta.get('preset')!=name
                or any(meta.get(k)!=EXPECTED_PROFILE[k] for k in ('frames','width','height','fps'))
                or meta.get('skipped_count')!=0 or meta.get('indexed_count')!=1):
            raise ValueError('Native selection/schedule/skip result differs: '+name)
        check_activity(row)
        rows.append({**source,'raw_activity':row.get('raw_activity'),'has_activity':row.get('has_activity'),
                     'features':row.get('features'),'motion_basis':row.get('motion_basis'),
                     **{k:row[k] for k in ('coherent_up','coherent_down','paired_flash_peak')},
                     **{k:row[k] for k in ('all_stationary','mean_luma','mean_contrast') if k in row},
                     'metadata':meta,
                     'appearance_accuracy_verified':False})
    return ranked_rows(rows)


def export_bundle(run,aar,assets,destination):
    facts=load(run/'run-identity.json');check_identity(facts)
    known,metadata=source_inventory(assets);check_aar(aar,assets,facts,known,metadata)
    rows=read_complete_results(run,facts,known)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        staged=Path(temporary)/'bundle';(staged/'genres').mkdir(parents=True)
        (staged/'presets.jsonl').write_text(''.join(canonical_json(r)+'\n' for r in rows),encoding='utf-8')
        groups={}
        for group,band in BANDS.items():
            members=[r for r in rows if group in r['groups']]
            if not members:raise ValueError('No eligible members for '+group)
            (staged/'genres'/(group+'.idx')).write_text(''.join(f"{r['preset']}\t{r['weight_mb']}\n" for r in members),encoding='utf-8')
            groups[group]={'label':group.title(),'range':list(band),'count':len(members)}
        manifest={'schema_version':2,'status':'beta','default':'all','groups':groups,
                  'total_presets':len(rows),'inactive_presets':sum(not r['group_eligible'] for r in rows),
                  'ranking':'collection-relative average ordinal positions, ties preserved, endpoints 1 and 100',
                  'inactive_policy':'score 1, retained in All, excluded from curated groups',
                  'appearance_accuracy_verified':False,'rendering_policy':'capped',
                  'published_artifact':PUBLISHED_CORE,
                  'random_policy':'helper calls srand(12345); native evaluator keeps its thread-local seed; shader/noise/image random_device choices are not fixed; one load per preset',
                  'feature_names':['coherent_luma_transitions_per_second','median_motion_viewports_per_second',
                                   'mean_acceleration_viewports_per_second_squared','same_pixel_luma_delta_p95_over_30Hz_frame_pairs'],
                  'evidence':facts,'library_sha256':metadata['library_sha256'],
                  'texture_sha256':metadata['texture_sha256'],
                  'checksums':{p.relative_to(staged).as_posix():file_digest(p)
                               for p in sorted(staged.rglob('*')) if p.is_file()}}
        manifest['generation_identity']=digest(manifest)
        (staged/'manifest.json').write_text(canonical_json(manifest)+'\n',encoding='utf-8')
        verify_bundle(staged,assets)
        backup=destination.with_name(destination.name+'.previous')
        if backup.exists():raise ValueError('Unfinished prior collection publication')
        if destination.exists():destination.rename(backup)
        try:staged.rename(destination)
        except BaseException:
            if backup.exists():backup.rename(destination)
            raise
        if backup.exists():shutil.rmtree(backup)
    return manifest


def verify_bundle(bundle,assets):
    manifest=load(bundle/'manifest.json')
    content={k:v for k,v in manifest.items() if k!='generation_identity'}
    if manifest.get('generation_identity')!=digest(content):raise ValueError('Manifest checksum mismatch')
    if (manifest.get('schema_version')!=2 or manifest.get('status')!='beta'
            or manifest.get('default')!='all' or set(manifest.get('groups',{}))!=set(BANDS)
            or manifest.get('appearance_accuracy_verified') is not False or manifest.get('rendering_policy')!='capped'):
        raise ValueError('Unexpected collection policy')
    check_identity(manifest['evidence'])
    if manifest.get('published_artifact')!=PUBLISHED_CORE:
        raise ValueError('Published artifact identity differs')
    if any(manifest['evidence'].get(k)!=PUBLISHED_CORE[k] for k in ('release','aar_sha256','native_arm64_sha256')):
        raise ValueError('Evidence differs from published artifact')
    required={'presets.jsonl'}|{'genres/'+g+'.idx' for g in BANDS}
    if set(manifest['checksums'])!=required:raise ValueError('Unexpected/missing collection files')
    if {p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()}!=required|{'manifest.json'}:
        raise ValueError('Retired or unexpected assets present')
    for name,expected in manifest['checksums'].items():
        if file_digest(bundle/name)!=expected:raise ValueError('Collection file checksum mismatch')
    known,metadata=source_inventory(assets)
    if (metadata['library_sha256']!=manifest['library_sha256']
            or metadata['texture_sha256']!=manifest['texture_sha256']):
        raise ValueError('Source library/texture identity differs')
    rows=[json.loads(line) for line in (bundle/'presets.jsonl').read_text().splitlines()]
    if len(rows)!=len(known) or {r['preset'] for r in rows}!=set(known):raise ValueError('Incomplete/duplicate score inventory')
    expected=ranked_rows(rows)
    for row,ranked in zip(rows,expected):
        check_activity(row)
        if (any(row.get(k)!=v for k,v in known[row['preset']].items())
                or any(row.get(k)!=ranked[k] for k in ('score','group_eligible','groups'))
                or row.get('appearance_accuracy_verified') is not False):
            raise ValueError('Source/weight/score/membership mismatch')
    if manifest['total_presets']!=len(rows) or manifest['inactive_presets']!=sum(not r['group_eligible'] for r in rows):
        raise ValueError('Collection coverage counts differ')
    for group,band in BANDS.items():
        data=manifest['groups'][group]
        index=read_index(bundle/'genres'/(group+'.idx'))
        members={r['preset']:r['weight_mb'] for r in rows if group in r['groups']}
        if data.get('range')!=list(band) or data.get('count')!=len(members) or index!=members:
            raise ValueError('Group index differs from ranked membership')
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--assets',type=Path,default=Path(__file__).resolve().parents[2]/'core/src/main/assets')
    p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--check',action='store_true')
    p.add_argument('--run',type=Path);p.add_argument('--aar',type=Path)
    args=p.parse_args()
    if args.check:result=verify_bundle(args.bundle,args.assets)
    else:
        if args.run is None or args.aar is None:p.error('--run and --aar required for export')
        result=export_bundle(args.run,args.aar,args.assets,args.bundle)
    print(json.dumps({'status':result['status'],'total':result['total_presets'],'groups':result['groups']},indent=2))


if __name__=='__main__':main()
