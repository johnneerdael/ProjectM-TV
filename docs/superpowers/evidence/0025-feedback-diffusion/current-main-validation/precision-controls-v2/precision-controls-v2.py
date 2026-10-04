"""Private filtered-RGBA16F ablation, same current35/36 source/clock, full native selected captures."""
import argparse, fcntl, hashlib, importlib.util, json, os, shutil, subprocess, sys, time, zipfile
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[2];WORK=ROOT/'build/native-4k-current-main/precision-controls-v2';OWNER=ROOT/'build/native-4k-current-main/emulator';SERIAL='emulator-5582'
NORMAL=ROOT/'build/native-4k-current-main/current-main35-broad'
NAMES=['$$$ Royal - Mashup (191).milk','Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk','Fed - quadratrail.milk','Fumbling_Foo + En D & Martin - Mandelverse.milk','$$$ Royal - Mashup (255).milk','astral spinorgentics encrustcore nz+.milk']
spec=importlib.util.spec_from_file_location('precision_helpers',ROOT/'build/native-4k-current-main/current-main35-broad.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);helper.WORK=WORK
sha=helper.sha;digest=helper.digest;atomic=helper.atomic;frozen=helper.frozen;canon=helper.canon
def aar_check(role):
    apk=Path(role['apk_path']);aar=apk.parent/'repo/core/build/outputs/aar/core-release.aar';assert aar.exists()
    with zipfile.ZipFile(aar) as z:assert hashlib.sha256(z.read('jni/arm64-v8a/libprojectmtv.so')).hexdigest()==role['core_sha256']
    return {'path':str(aar),'sha256':sha(aar),'core_sha256':role['core_sha256'],'apk_elf_identity':True}
def prepare():
    WORK.mkdir(parents=True,exist_ok=True)
    if (WORK/'inputs.json').exists():
        inputs=json.loads((WORK/'inputs.json').read_text());assert inputs['sha256']==digest({k:v for k,v in inputs.items() if k!='sha256'});return inputs
    current=json.loads((NORMAL/'inputs.json').read_text());assert current['sha256']==digest({k:v for k,v in current.items() if k!='sha256'})
    roles={'baseline':current['roles']['baseline'],'normal':current['roles']['candidate']}
    roles['fp16']=helper.worker(ROOT/'build/native-4k-current-main/filtered-precision-experiment/worker-candidate.json','fp16',36,helper.COMMITS['candidate'])
    roles['reference']=helper.worker(helper.CLASSIC,'reference',35,helper.COMMITS['baseline'])
    normal=roles['normal']['backend_identity'];private=roles['fp16']['backend_identity'];baseline=roles['baseline']['backend_identity'];ref=roles['reference']['backend_identity']
    control=private['private_filtered_precision_experiment'];assert control['shipping_byte_identity'] is False and control['canvas_blur_kernel_preset_clock_rng_pcm_changes'] is False
    assert normal['ordered_patches'][:35]==private['ordered_patches'][:35]==baseline['ordered_patches']==ref['ordered_patches']
    assert normal['ordered_patches'][35]['sha256']==control['pristine_patch_sha256'];assert private['ordered_patches'][35]['sha256']==control['private_patch_sha256']
    for i in (private,baseline,ref):
        assert i['original_core_source_sha256']==normal['original_core_source_sha256'] and i['instrumentation']==normal['instrumentation'] and i['harness_sources_sha256']==normal['harness_sources_sha256']
    assert ref['private_reference_control']['reference_width']==ref['private_reference_control']['reference_height']==0
    nroot=Path(roles['normal']['apk_path']).parent/'repo/third_party/projectm/src';froot=Path(roles['fp16']['apk_path']).parent/'repo/third_party/projectm/src';changes=[]
    for source in nroot.rglob('*'):
        if source.is_file() and source.suffix in ('.cpp','.hpp','.h','.c'):
            other=froot/source.relative_to(nroot);assert other.is_file()
            if sha(source)!=sha(other):changes.append(str(source.relative_to(nroot)))
    assert changes==['libprojectM/MilkdropPreset/FeedbackDiffusion.cpp'],changes
    normal_source=nroot/changes[0];private_source=froot/changes[0]
    old='m_framebuffer.CreateColorAttachment(0, FilteredAttachment);';new='m_framebuffer.CreateColorAttachment(0, FilteredAttachment, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT);'
    assert normal_source.read_text().count(old)==1 and normal_source.read_text().replace(old,new)==private_source.read_text();assert sha(private_source)==control['compiled_feedback_source_sha256']
    raw='m_framebuffer.CreateColorAttachment(0, RawAttachment);';assert normal_source.read_text().count(raw)==private_source.read_text().count(raw)==1
    diff=Path(roles['fp16']['apk_path']).parent/'filtered-attachment-only.diff';assert sha(diff)==control['private_patch_byte_diff_sha256'];shutil.copyfile(diff,WORK/diff.name)
    assets={r:helper.asset_identity(v['apk_path']) for r,v in roles.items()};assert all(a==current['asset_identity'] for a in assets.values())
    aar={r:aar_check(v) for r,v in roles.items()};frozen(WORK/'actual-aar-proof.json',aar)
    for r,v in roles.items():frozen(WORK/'role-dictionaries'/f'{r}.json',v)
    records=[{'path':n,'sha256':sha(ROOT/'core/src/main/assets/presets'/n),'bytes':(ROOT/'core/src/main/assets/presets'/n).stat().st_size} for n in NAMES]
    with zipfile.ZipFile(roles['normal']['apk_path']) as z:
        for r in records:assert hashlib.sha256(z.read('assets/presets/'+r['path'])).hexdigest()==r['sha256']
    pcm={};signal_dir=WORK/'signals';signal_dir.mkdir(exist_ok=True)
    for frames,v in current['pcm'].items():
        assert sha(v['path'])==v['sha256'];dest=signal_dir/Path(v['path']).name;shutil.copyfile(v['path'],dest);assert sha(dest)==v['sha256'] and dest.stat().st_size==int(frames)*1470
        pcm[frames]={'path':str(dest),'sha256':sha(dest),'bytes':dest.stat().st_size}
    probe_root=ROOT/'build/native-4k-current-main/fp16-driver-probe';probe=json.loads((probe_root/'probe-result.json').read_text());manifest=json.loads((probe_root/'run-manifest.json').read_text())
    assert probe['status']=='success' and probe['mixed_framebuffer_status']==probe['expected_complete_status']==36053 and probe['raw_exact'] and probe['half_exact'] and probe['linear_exact']
    assert len(probe['gl_error_checks'])==18 and all(c['error']==0 for c in probe['gl_error_checks']);assert manifest['status']=='finished' and manifest['device_serial']==SERIAL and sha(probe_root/'probe-result.json')==manifest['result_sha256']
    assert {k:probe[k] for k in helper.FIELDS}==current['expected_driver']
    frozen(WORK/'probe-result.json',probe);frozen(WORK/'probe-run-manifest.json',manifest)
    provider=WORK/'provider-run.py';shutil.copyfile(NORMAL/'provider-run.py',provider);assert sha(provider)==current['provider_copy_sha256']
    budget=sum(w*h*3*8*6*2 for w,h in [(2364,1330),(3840,2160)])*3 +1182*665*3*8*6*2
    value={'roles':roles,'records':records,'asset_identity':current['asset_identity'],'expected_driver':current['expected_driver'],'pcm':pcm,'clock':current['clock'],'seed':12345,'capture_frames':helper.PICKS,
           'adapter_sha256':sha(Path(__file__)),'helper_adapter_sha256':sha(ROOT/'build/native-4k-current-main/current-main35-broad.py'),'provider_sha256':sha(provider),'driver_probe_result_sha256':sha(WORK/'probe-result.json'),'driver_probe_manifest_sha256':sha(WORK/'probe-run-manifest.json'),
           'raw_retention_budget_bytes':budget,'planned_jobs':84,'private_format_delta':{'compiled_changed_files':changes,'normal_filtered_format':'defaultunsignedbyteRGBA','private_filtered_format':'GL_RGBA16F/GL_RGBA/GL_HALF_FLOAT','raw_attachment':'unchangeddefaultunsignedbyteRGBA','compiled_source_sha256':sha(private_source)},
           'scope':'Freshbaseline35/normalMRT36/privateFP16+freshtrueclassic35ref0 only. Full8selected native RGB for1182area-MAE/centreRGB/saturation/contrast/sharpness. No primary historical29pixels, fullcorpus, shippingfidelity or TV cost claim.'}
    value['sha256']=digest(value);frozen(WORK/'inputs.json',value)
    atomic(WORK/'preparation.json',{'state':'prepared_offline','planned_jobs':84,'raw_retention_budget_bytes':budget,'raw_retention_budget_GiB':budget/2**30,'initial_required_free_bytes':budget+7*2**30,'cumulative_budget_includes6GiB_reserve_plus1GiB_scratch':True,'inputs_sha256':value['sha256']})
    return value

def run(inputs,args):
    if not args.parent_confirmed:raise ValueError('Need explicit parent runtime authorization')
    assert sha(Path(__file__))==inputs['adapter_sha256'] and sha(ROOT/'build/native-4k-current-main/current-main35-broad.py')==inputs['helper_adapter_sha256']
    shared=(OWNER/'measurement.lock').open('a');fcntl.flock(shared,fcntl.LOCK_EX|fcntl.LOCK_NB);own=(WORK/'host.lock').open('a');fcntl.flock(own,fcntl.LOCK_EX|fcntl.LOCK_NB)
    free=shutil.disk_usage(WORK).free;assert free>=inputs['raw_retention_budget_bytes']+7*2**30,'Insufficient cumulative capturebudget+6GiBreserve+scratch'
    atomic(WORK/'space-budget.json',{'planned_raw_bytes':inputs['raw_retention_budget_bytes'],'free_bytes_before_epoch':free,'required_free_bytes':inputs['raw_retention_budget_bytes']+7*2**30,'disk_guard_each_job_bytes':6*2**30})
    spec=importlib.util.spec_from_file_location('precision_provider',WORK/'provider-run.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.ROOT=ROOT
    assert sha(WORK/'provider-run.py')==inputs['provider_sha256']
    launchpath=OWNER/'launch.json';launch=json.loads(launchpath.read_text());launch_sha=sha(launchpath);probe=json.loads((WORK/'probe-run-manifest.json').read_text());assert probe['launch_sha256']==launch_sha and probe['owned_emulator']['pid']==launch['pid']
    def validate_serial(value):
        if value!=SERIAL:raise ValueError('Onlyowned5582 authorized')
        return value
    def guard(value):
        validate_serial(value);assert sha(launchpath)==launch_sha and launch['serial']==SERIAL and type(launch['pid']) is int and launch['pid']>0
        assert Path(launch['avd']).resolve().is_relative_to((OWNER/'avds').resolve());cmd=launch['command'];assert cmd[cmd.index('-port')+1]=='5582';name=cmd[cmd.index('-avd')+1]
        os.kill(launch['pid'],0);ps=subprocess.check_output(['ps','-p',str(launch['pid']),'-o','command='],text=True);assert 'qemu-system-aarch64' in ps and f'-avd {name}' in ps and '-port 5582' in ps
        assert subprocess.check_output(['adb','-s',SERIAL,'shell','getprop','ro.kernel.qemu'],text=True,timeout=30).strip()=='1'
        return {'serial':SERIAL,'pid':launch['pid'],'launch_sha256':launch_sha,'launchRoot':str(OWNER),'avd':launch['avd'],'command':cmd,'ro.kernel.qemu':'1'}
    runner.validate_device=validate_serial;runner.require_owned_emulator=guard;ownership=guard(SERIAL)
    existing=runner.adb(SERIAL,'shell','pidof',runner.PACKAGE,allow_failure=True);assert not existing.stdout.strip(),'Unexpectedlive dedicatedworker'
    lease={'state':'active','pid':os.getpid(),'adapter_sha256':inputs['adapter_sha256'],'ownership':ownership,'scope':'precision6only;84fresh actualcore jobs','started_unix_seconds':time.time()};atomic(WORK/'lease.json',lease);print('PRECISION_PROCESS '+canon(lease),flush=True)
    base={'backend':'actualcoreJNI/GLES3 current35/36 precisionablation','device_serial':SERIAL,'ownership':ownership,'roles':inputs['roles'],'pcm':inputs['pcm'],'capture_frames':inputs['capture_frames'],'clock':inputs['clock'],'seed':12345,'input_sha256':inputs['sha256'],'asset_identity':inputs['asset_identity'],'expected_driver':inputs['expected_driver'],
          'adapter_sha256':inputs['adapter_sha256'],'provider_sha256':inputs['provider_sha256'],'driver_probe_sha256':inputs['driver_probe_result_sha256'],'scope':inputs['scope'],'retention':'native=True;8selected RGB8 files pluscompactPNG/native metrics; unreadframesnotpixelhashed'}
    protocols={}
    for label,w,h in [('classic',1182,665),('1330',2364,1330),('2160',3840,2160)]:
        p=dict(base,profile=label,config={'width':w,'height':h,'fps':30,'warmup_frames':120,'measurement_frames':360});p['sha256']=digest(p);protocols[label]=p;frozen(WORK/label/'protocol.json',p)
    original_job=runner.make_job
    def make_job(p,*args):
        job=original_job(p,*args);job.update(width=p['config']['width'],height=p['config']['height'],capture_frames=inputs['capture_frames']);return job
    runner.make_job=make_job;original_validate=runner.validate_result
    def validate_result(job,result,frames,directory):
        status=original_validate(job,result,frames,directory)
        if status=='success':
            role=next(v for v in inputs['roles'].values() if v['core_sha256']==job['expected_core_sha256']);assert result['backend_identity']==role['backend_identity']
            assert result['pcm_samples_per_frame']==1470 and result['pcm_uint8_sha256']==job['pcm_uint8_sha256'];assert {k:result[k] for k in helper.FIELDS}==inputs['expected_driver']
        return status
    runner.validate_result=validate_result;ordinal=0
    try:
        for role in ('reference','baseline','normal','fp16'):
            runner.install_role(SERIAL,inputs['roles'][role],WORK)
            labels=['classic'] if role=='reference' else ['1330','2160']
            for record in inputs['records']:
                for label in labels:
                    for repeat in (1,2):
                        free=shutil.disk_usage(WORK).free
                        if free<6*2**30:raise RuntimeError('Diskguard6GiB beforecapture')
                        guard(SERIAL)
                        df=runner.adb(SERIAL,'shell','df','-k','/data','/sdcard').stdout.decode()
                        available=[int(line.split()[3])*1024 for line in df.splitlines()[1:] if len(line.split())>=6 and line.split()[3].isdigit()]
                        native_bytes=protocols[label]['config']['width']*protocols[label]['config']['height']*3*len(inputs['capture_frames'])
                        required_device_bytes=2*native_bytes+128*2**20
                        assert available and min(available)>=required_device_bytes,'Dedicatedjob app-storage budget insufficient'
                        row=runner.run_one(SimpleNamespace(work=WORK/label,timeout=300),protocols[label],record,role,'selected',repeat,360,native=True);ordinal+=1
                        atomic(WORK/'progress.json',{'ordinal':ordinal,'planned':84,'role':role,'profile':label,'preset':record['path'],'repeat':repeat,'status':row['status'],'error':row.get('error'),'free_bytes_before_job':free,'device_free_bytes_before_job':min(available),'required_device_bytes':required_device_bytes,'verified_job_cleanup':'shared provider removes only this job private+dedicated external scratch after validated pull; failures preserved','updated_unix_seconds':time.time()})
                        if row['status']!='success':raise RuntimeError('Precisionjob failure preserved;stop beforeinterpretation')
        atomic(WORK/'completion.json',{'state':'complete_scheduling_checkpoint','jobs':84,'reference_jobs':12,'baseline35_jobs':24,'normal36_jobs':24,'private_fp16_jobs':24,'full64_not_launched':True,'input_sha256':inputs['sha256']});print('PRECISION84_COMPLETE',flush=True)
    finally:
        atomic(WORK/'lease.json',dict(lease,state='released',released_unix_seconds=time.time(),terminal_jobs=ordinal));fcntl.flock(shared,fcntl.LOCK_UN)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['prepare','run']);parser.add_argument('--parent-confirmed',action='store_true');args=parser.parse_args();inputs=prepare()
    if args.phase=='prepare':print(canon(json.loads((WORK/'preparation.json').read_text())))
    else:run(inputs,args)
