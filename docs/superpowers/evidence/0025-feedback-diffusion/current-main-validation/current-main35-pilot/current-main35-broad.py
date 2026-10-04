"""Fresh main35/main36 matched epoch; pilot8 scheduling boundary; old pixels diagnostic only."""
import argparse, fcntl, hashlib, importlib.util, json, os, shutil, subprocess, sys, time, zipfile
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'build/native-4k-current-main/current-main35-broad'
OLD=ROOT/'build/native-4k-current-main/broad-sample';SERIAL='emulator-5582';OWNER=ROOT/'build/native-4k-current-main/emulator'
PROVIDER=ROOT/'docs/superpowers/evidence/0025-feedback-diffusion/shared-core-corpus/run.py'
SOURCES={'baseline':ROOT/'build/native-4k-current-main/merged-core-validation/worker-baseline.json','candidate':ROOT/'build/native-4k-current-main/current-main-mrt-candidate/worker-candidate.json'}
CLASSIC=ROOT/'build/native-4k-current-main/current-main-classic35/worker-baseline.json'
COMMITS={'baseline':'f435dd7c58ea1f16d9d182ecfc5632b77f5b6f98','candidate':'1b2c266331c9624ef7027da86d825096d243e86a'}
FIELDS=['abi','android_fingerprint','egl_version','gl_vendor','gl_renderer','gl_version'];PICKS=[120,150,180,210,239,300,390,479]
canon=lambda d:json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(d):return hashlib.sha256(canon(d).encode()).hexdigest()
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp');tmp.write_text(canon(value)+'\n');os.replace(tmp,path)
def frozen(path,value):
    if path.exists():assert json.loads(path.read_text())==value,'Immutable epoch inputs changed: '+str(path)
    else:atomic(path,value)
def asset_identity(apk):
    with zipfile.ZipFile(apk) as z:items=[{'path':n,'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in sorted(z.namelist()) if n.startswith('assets/') and not n.endswith('/') and n!='assets/backend-identity.json']
    return {'assets_sha256':digest(items),'textures_sha256':digest([i for i in items if i['path'].startswith('assets/textures/')]),'asset_count':len(items)}
def worker(path,role,expected_count,expected_commit):
    record=json.loads(path.read_text());i=record['backend_identity'];apk=Path(record['apk']);assert sha(apk)==record['apk_sha256'];assert len(i['ordered_patches'])==expected_count and i['source_commit']==expected_commit
    with zipfile.ZipFile(apk) as z:
        assert json.loads(z.read('assets/backend-identity.json'))==i;assert hashlib.sha256(z.read(i['core_library_entry'])).hexdigest()==i['core_sha256']
    value={'apk_path':str(apk),'apk_sha256':record['apk_sha256'],'core_sha256':i['core_sha256'],'backend_identity':i,'backend_identity_sha256':digest(i),'source_metadata_path':str(path),'source_metadata_sha256':sha(path)}
    frozen(WORK/'workers'/f'{role}.json',record);return value
def prepare():
    WORK.mkdir(parents=True,exist_ok=True)
    if (WORK/'inputs.json').exists():
        value=json.loads((WORK/'inputs.json').read_text());assert value['sha256']==digest({k:v for k,v in value.items() if k!='sha256'});return value
    selection=json.loads((OLD/'selection.json').read_text());assert selection['sha256']==digest({k:v for k,v in selection.items() if k!='sha256'}) and len(selection['cases'])==64
    frozen(WORK/'selection.json',selection)
    roles={role:worker(path,role,35 if role=='baseline' else 36,COMMITS[role]) for role,path in SOURCES.items()}
    a,b=[roles[r]['backend_identity'] for r in ('baseline','candidate')]
    assert a['ordered_patches']==b['ordered_patches'][:35] and b['ordered_patches'][35]['name']=='0036-feedback-diffusion-compensation.patch'
    assert a['original_core_source_sha256']==b['original_core_source_sha256'] and a['instrumentation']==b['instrumentation'] and a['harness_sources_sha256']==b['harness_sources_sha256']
    assert not any(k.startswith('private_') for i in (a,b) for k in i)
    assets={r:asset_identity(v['apk_path']) for r,v in roles.items()};assert assets['baseline']==assets['candidate']
    proof_path=ROOT/'build/native-4k-current-main/merged-core-validation/current-pair-aar-proof.json';proof=json.loads(proof_path.read_text())
    for entry in proof:
        r=roles[entry['role']];assert sha(entry['aar'])==entry['aar_sha256'] and entry['apk_sha256']==r['apk_sha256'] and entry['core_sha256']==r['core_sha256']
        with zipfile.ZipFile(entry['aar']) as z:assert hashlib.sha256(z.read('jni/arm64-v8a/libprojectmtv.so')).hexdigest()==r['core_sha256']
    frozen(WORK/'normal-aar-proof.json',proof)
    old_protocols={l:json.loads((OLD/l/'protocol.json').read_text()) for l in ('1330','2160','classic-reference')};old_roles={'baseline29':old_protocols['1330']['roles']['baseline'],'candidate790':old_protocols['1330']['roles']['candidate'],'classic29':old_protocols['classic-reference']['roles']['reference']}
    frozen(WORK/'historical-worker-dictionaries.json',old_roles)
    for l,p in old_protocols.items():frozen(WORK/'historical-protocols'/f'{l}.json',p)
    source=OLD/'1330/protocol.json';pcm={}
    for frames,p in old_protocols['1330']['pcm'].items():
        assert sha(p['path'])==p['sha256'];dest=WORK/'signals'/Path(p['path']).name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(p['path'],dest);assert sha(dest)==p['sha256'] and dest.stat().st_size==int(frames)*1470
        pcm[frames]={'path':str(dest),'sha256':sha(dest),'bytes':dest.stat().st_size}
    provider=WORK/'provider-run.py';shutil.copyfile(PROVIDER,provider)
    driver={key:next(iter(json.loads(f.read_text())['result'][key] for f in (OLD/'1330/jobs').glob('*/row.json'))) for key in FIELDS}
    value={'roles':roles,'selection_sha256':selection['sha256'],'pcm':pcm,'asset_identity':assets['baseline'],'expected_driver':driver,'captures':PICKS,'seed':12345,'sample_seed':20261004,
           'clock':old_protocols['1330']['clock'],'adapter_sha256':sha(Path(__file__)),'provider_copy_sha256':sha(provider),'old_protocols':old_protocols,'old_roles':old_roles,
           'scope':'Fresh currentmain35 baseline andmain36 candidate. Oldmain29/790/classic29 pixels only paired historical prerequisite/routing diagnostics; never currentbaseline.'}
    value['sha256']=digest(value);frozen(WORK/'inputs.json',value)
    atomic(WORK/'preparation.json',{'state':'prepared_offline','planned_normal_jobs':512,'planned_classic_jobs':128,'authorized_pilot_normal_jobs':64,'authorized_pilot_classic_jobs':16,'baseline_source':COMMITS['baseline'],'candidate_source':COMMITS['candidate'],'reference_pending':not CLASSIC.exists(),'input_sha256':value['sha256']})
    return value

def execute(args,inputs):
    if not args.parent_confirmed_pilot:raise ValueError('Parent confirmation required; prepare has no device actions')
    shared=(OWNER/'measurement.lock').open('a');fcntl.flock(shared,fcntl.LOCK_EX|fcntl.LOCK_NB)
    own=(WORK/'host.lock').open('a');fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB)
    spec=importlib.util.spec_from_file_location('main35_provider',WORK/'provider-run.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.ROOT=ROOT
    assert sha(Path(__file__))==inputs['adapter_sha256'] and sha(WORK/'provider-run.py')==inputs['provider_copy_sha256']
    launchpath=OWNER/'launch.json';launch=json.loads(launchpath.read_text());launch_sha=sha(launchpath)
    def validate_serial(value):
        if value!=SERIAL:raise ValueError('Only owned5582 authorized')
        return value
    def guard(value):
        validate_serial(value);assert sha(launchpath)==launch_sha and launch['serial']==SERIAL and type(launch['pid']) is int
        assert Path(launch['avd']).resolve().is_relative_to((OWNER/'avds').resolve());cmd=launch['command'];assert cmd[cmd.index('-port')+1]=='5582';name=cmd[cmd.index('-avd')+1]
        os.kill(launch['pid'],0);process=subprocess.check_output(['ps','-p',str(launch['pid']),'-o','command='],text=True)
        assert 'qemu-system-aarch64' in process and f'-avd {name}' in process and '-port 5582' in process
        assert subprocess.check_output(['adb','-s',SERIAL,'shell','getprop','ro.kernel.qemu'],text=True,timeout=30).strip()=='1'
        return {'serial':SERIAL,'pid':launch['pid'],'avd':launch['avd'],'launch_sha256':launch_sha,'launchRoot':str(OWNER),'command':cmd,'ro.kernel.qemu':'1'}
    runner.validate_device=validate_serial;runner.require_owned_emulator=guard;ownership=guard(SERIAL)
    # Parent verified cross-session idleness; refuse an unexpected dedicated worker before installing.
    process=runner.adb(SERIAL,'shell','pidof',runner.PACKAGE,allow_failure=True)
    assert not process.stdout.strip(),'Dedicated worker is live despite exclusive pilot authorization'
    lease={'state':'active','phase':'pilot8-only','pid':os.getpid(),'adapter_sha256':inputs['adapter_sha256'],'ownership':ownership,'source_commits':COMMITS,'started_unix_seconds':time.time()}
    atomic(WORK/'lease.json',lease);print('PILOT_PROCESS '+canon(lease),flush=True)
    records=[c['preset'] for c in json.loads((WORK/'selection.json').read_text())['cases'][:8]];roles=inputs['roles'];protocols={}
    for label,w,h in [('1330',2364,1330),('2160',3840,2160)]:
        p={'backend':'actualcore productionJNI/GLES3 currentmain35 versusMRT36','device_serial':SERIAL,'roles':roles,'ownership':ownership,'pcm':inputs['pcm'],'config':{'width':w,'height':h,'fps':30,'warmup_frames':120,'measurement_frames':360},
           'capture_frames':PICKS,'seed':12345,'clock':inputs['clock'],'selection_sha256':inputs['selection_sha256'],'input_sha256':inputs['sha256'],'asset_identity':inputs['asset_identity'],'expected_driver':inputs['expected_driver'],
           'adapter_sha256':inputs['adapter_sha256'],'provider_sha256':inputs['provider_copy_sha256'],'scope':inputs['scope'],'retention':'native=False;256x144 PNG/native metrics/selected hashes only'}
        p['sha256']=digest(p);protocols[label]=p;frozen(WORK/label/'protocol.json',p)
    original_job=runner.make_job
    def make_job(protocol,*args):
        job=original_job(protocol,*args);job.update(width=protocol['config']['width'],height=protocol['config']['height'],capture_frames=PICKS);return job
    runner.make_job=make_job;original_validate=runner.validate_result
    def validate_result(job,result,frames,directory):
        status=original_validate(job,result,frames,directory)
        if status=='success':
            role=next(r for r in active_roles.values() if r['core_sha256']==job['expected_core_sha256']);assert result['backend_identity']==role['backend_identity']
            assert result['pcm_samples_per_frame']==1470 and result['pcm_uint8_sha256']==job['pcm_uint8_sha256'];assert {k:result[k] for k in FIELDS}==inputs['expected_driver'],'driver changed'
            assert not list(directory.glob('*.rgb'))
        return status
    runner.validate_result=validate_result;active_roles=dict(roles);ordinal=0
    def one(label,protocol,record,role,repeat):
        nonlocal ordinal
        free=shutil.disk_usage(WORK).free
        if free<6*2**30:raise RuntimeError('Diskguard requires6GiB')
        guard(SERIAL);row=runner.run_one(SimpleNamespace(work=WORK/label,timeout=300),protocol,record,role,'selected',repeat,360,native=False);ordinal+=1
        atomic(WORK/'last-job-progress.json',{'ordinal':ordinal,'planned_pilot':80,'profile':label,'preset':record['path'],'role':role,'repeat':repeat,'status':row['status'],'error':row.get('error'),'free_bytes_before_job':free,'updated_unix_seconds':time.time()})
        if row['status']!='success':raise RuntimeError('Pilot failure preserved; stop for scheduling review')
    try:
        for role in ('baseline','candidate'):
            runner.install_role(SERIAL,roles[role],WORK)
            for record in records:
                for label,p in protocols.items():
                    for repeat in (1,2):one(label,p,record,role,repeat)
        if not CLASSIC.exists():
            atomic(WORK/'pilot-state.json',{'state':'normal64_complete_reference_pending','jobs':64,'reference_worker_expected':str(CLASSIC)});return
        reference=worker(CLASSIC,'reference',35,COMMITS['baseline']);ri=reference['backend_identity'];assert ri['private_reference_control']['reference_width']==ri['private_reference_control']['reference_height']==0
        assert ri['ordered_patches']==roles['baseline']['backend_identity']['ordered_patches'] and ri['original_core_source_sha256']==roles['baseline']['backend_identity']['original_core_source_sha256'];runner.validate_observer_pair(roles['baseline'],reference)
        assert asset_identity(reference['apk_path'])==inputs['asset_identity']
        src=Path(reference['apk_path']).parent/'repo/core/src/main/cpp/native-lib.cpp';bsrc=Path(roles['baseline']['apk_path']).parent/'repo/core/src/main/cpp/native-lib.cpp'
        before='projectm_opengl_set_line_reference_size(g_engine.pm, 1024, 768);';after='projectm_opengl_set_line_reference_size(g_engine.pm, 0, 0);';assert bsrc.read_text().count(before)==1 and bsrc.read_text().replace(before,after)==src.read_text()
        p=dict(protocols['1330'],backend='actualcore baseline35 privateclassicref0 control',roles={'reference':reference},config={'width':1182,'height':665,'fps':30,'warmup_frames':120,'measurement_frames':360},reference_control='private line reference0,0 only; shippingbyteidentity false');p.pop('sha256');p['sha256']=digest(p);frozen(WORK/'classic-reference'/'protocol.json',p);active_roles['reference']=reference
        runner.install_role(SERIAL,reference,WORK)
        for record in records:
            for repeat in (1,2):one('classic-reference',p,record,'reference',repeat)
        atomic(WORK/'pilot-state.json',{'state':'pilot80_complete_scheduling_checkpoint','jobs':80,'normal_jobs':64,'classic_jobs':16,'full64_not_authorized':True,'selection_sha256':inputs['selection_sha256']})
        print('PILOT80_COMPLETE',flush=True)
    finally:
        atomic(WORK/'lease.json',dict(lease,state='released',released_unix_seconds=time.time(),terminal_jobs=ordinal));fcntl.flock(shared,fcntl.LOCK_UN)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','pilot']);parser.add_argument('--parent-confirmed-pilot',action='store_true');args=parser.parse_args();inputs=prepare()
    if args.phase=='prepare':print(canon(json.loads((WORK/'preparation.json').read_text())))
    else:execute(args,inputs)
