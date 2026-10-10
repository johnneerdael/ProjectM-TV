"""Verify and summarize source-only sample coverage, never appearance accuracy."""
import collections
import ast
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import jsonschema

ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'tools/milk-analyzer'))
from corpus_store import atomic_json,digest,file_hash


def summarize(folder,output,log_path=None):
    manifest=json.loads((folder/'run-manifest.json').read_text());identity=manifest['configuration'];run_identity=digest(manifest)
    selected={p['relative_path']:p for p in manifest['presets']};results={}
    statuses=collections.Counter();stages=collections.Counter();families=collections.defaultdict(set)
    flags=collections.defaultdict(set);gaps=collections.defaultdict(set);unstructured=[];schema_errors=[];outcomes=[];compile_counts=collections.Counter()
    schema=json.loads((ROOT/'tools/milk-analyzer/export-contract/source-appearance.schema.json').read_text())
    v=jsonschema.Draft202012Validator(schema)
    def reasons(x,preset,group):
        if isinstance(x,dict):
            for reason in x.get('unknown_reasons',[]):gaps[(group,str(reason))].add(preset)
            for value in x.values():reasons(value,preset,group)
        elif isinstance(x,list):
            for value in x:reasons(value,preset,group)
    for path in sorted((folder/'results').glob('*.json')):
        r=json.loads(path.read_text());name=r['preset']['relative_path'];expected=selected[name]
        assert r['run_identity']==run_identity and r['preset']==expected,name
        assert file_hash(ROOT/'core/src/main/assets/presets'/name)==expected['sha256'],name
        results[name]=(path,file_hash(path));statuses[r['status']]+=1
        if r['analysis'] is None:
            outcomes.append({'preset':expected,'status':r['status'],'error':r.get('error')});continue
        a=r['analysis'];assert a['preset_sha256']==expected['sha256'],name
        assert r['provenance']['model_modules']==identity['model_modules'],name
        assert not any(a[k] for k in ('uses_rendered_images','uses_shader_execution','uses_equation_execution')),name
        proof=json.loads((folder/'compatibility'/Path(name).with_suffix('.json')).read_text())
        assert proof['preset']==expected and proof['record_sha256']==digest({k:x for k,x in proof.items() if k!='record_sha256'}),name
        assert proof['record_sha256']==r['provenance']['offline_compile_evidence']['record_sha256'],name
        assert a['compatibility_sha256']==digest(proof['reports']),name
        for stage,p in proof['reports'].items():compile_counts[(stage,str(p['offline_accepted']))]+=1
        for stage in ('warp','composite'):stages[(stage,a['stages'][stage]['kind'])]+=1
        for f in a['families']:families[f['mechanism']].add(name)
        for reason in a['unknowns']:gaps[('source_interpretation',str(reason))].add(name)
        d=a['visual_description'];errors=list(v.iter_errors(d))
        if errors:schema_errors.append({'preset':expected,'errors':[{'path':list(e.path),'message':e.message} for e in errors[:10]]})
        if 'sampling_geometry' not in d:
            unstructured.append({'preset':expected,'description':d});continue
        flags['structured'].add(name)
        for group in ('native_warp_displacement','native_spatial_displacement','nonlinear_texture_colour_bounds','feedback_colour_sensitivity','sampling_geometry'):
            reasons(d[group],name,group)
        if d['native_warp_displacement']['status']=='bounded_uniform_sampling_displacement':flags['uniform_native_displacement'].add(name)
        if d['native_spatial_displacement']['status']=='bounded_spatial_sampling_displacement':flags['spatial_native_displacement'].add(name)
        for hazard in d['activity']['flashing']['hazards']:flags['flash_mechanism:'+hazard['kind']].add(name)
        for stage,maps in d['sampling_geometry']['stages'].items():
            for lookup in maps or []:
                motion=lookup['sampling_motion']
                for part,scenario in ((motion,False),(motion.get('scenario_sampling_motion'),True)):
                    if part is None:continue
                    rates=part['maximum_lookup_axis_speed_uv_per_second'];suffix='scenario' if scenario else 'default'
                    if any(x is not None for x in rates):flags['lookup_partial_time_bound:'+suffix].add(name)
                    if any(x is not None and x>0 for x in rates):flags['lookup_positive_time_ceiling:'+suffix].add(name)
        response=d['feedback_colour_sensitivity']
        for part,scenario in ((response,False),(response.get('scenario_feedback_colour_sensitivity'),True)):
            if part is None:continue
            suffix='scenario' if scenario else 'default'
            if part['maximum_fixed_coordinate_feedback_sample_gain'] is not None:flags['feedback_sample_gain:'+suffix].add(name)
            if part['maximum_previous_image_colour_gain'] is not None:flags['previous_image_operator_gain:'+suffix].add(name)
            if part['sufficient_raw_warp_colour_contraction'] is True:flags['raw_warp_sufficient_contraction:'+suffix].add(name)
    archived=set();batch_count=0
    for path in sorted(folder.glob('batch-*.zip')):
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None,path.name
            b=json.loads(z.read('batch-manifest.json'));assert b['run_identity']==run_identity,path.name
            for row in b['results']:
                name=row['preset']['relative_path'];assert name not in archived,name
                assert row['preset']==selected[name] and results[name][1]==row['result_sha256'],name
                assert hashlib.sha256(z.read(row['result_file'])).hexdigest()==row['result_sha256'],name
                assert hashlib.sha256(z.read('presets/'+name)).hexdigest()==selected[name]['sha256'],name
                archived.add(name)
        batch_count+=1
    assert len(results)==len(selected)==len(archived),('incomplete',len(results),len(selected),len(archived))
    priority=[{'descriptor_group':group,'reason':reason,'affected_presets':len(names),'presets':sorted(names)}
        for (group,reason),names in sorted(gaps.items(),key=lambda x:(-len(x[1]),x[0]))]
    report={'kind':'source-only-random-sample-coverage','sample_size':len(selected),'corpus_size':identity['corpus_count'],
        'run_identity':run_identity,'sampling_seed':identity['sampling_seed'],'model_modules':identity['model_modules'],
        'status_counts':dict(statuses),'structured_descriptions':len(flags['structured']),
        'schema_valid_descriptions':len(results)-len(schema_errors)-len(outcomes),
        'stage_counts':{':'.join(k):n for k,n in stages.items()},'offline_compile_counts':{':'.join(k):n for k,n in compile_counts.items()},
        'source_family_preset_counts':{k:len(n) for k,n in sorted(families.items())},
        'conditional_trait_preset_counts':{k:len(n) for k,n in sorted(flags.items())},
        'unstructured_cases':unstructured,'schema_failures':schema_errors,'error_or_timeout_cases':outcomes,
        'archive_batches':batch_count,'verified_archive_pairs':len(archived),'source_hashes_verified':len(results),
        'descriptor_gap_priority':priority,'appearance_accuracy_verified':False,'mood_accuracy_verified':False,
        'limitations':['Computed is a terminal export status, not complete interpretation or mood accuracy',
            'Counts are source mechanisms or conditional bounds; zero partial rates are not no-motion/no-flash proofs',
            'Descriptor-specific unknown reasons can overlap and can coexist with other supported models',
            'Sampler/compiler acceptance is source-bound offline evidence, not driver/runtime image validation']}
    grouped=collections.defaultdict(set);sections=collections.defaultdict(set)
    for row in priority:
        if row['descriptor_group']!='source_interpretation':continue
        try:gap=ast.literal_eval(row['reason'])
        except (ValueError,SyntaxError):gap={'reason':row['reason'],'section':'unknown'}
        grouped[gap['reason']].update(row['presets']);sections[gap['reason']].add(gap['section'])
    report['source_gap_by_reason']=[{'reason':k,'affected_presets':len(names),'sections':sorted(sections[k]),'presets':sorted(names)}
        for k,names in sorted(grouped.items(),key=lambda x:(-len(x[1]),x[0]))]
    report['descriptor_gap_scope']=['source_interpretation','native_warp_displacement','native_spatial_displacement',
        'nonlinear_texture_colour_bounds','feedback_colour_sensitivity','sampling_geometry']
    report['summary_tool_sha256']=file_hash(__file__)
    if log_path is not None:
        log=[json.loads(line) for line in log_path.read_text().splitlines() if line.startswith('{')]
        last=next(x for x in reversed(log) if x['event']=='finished')
        times=sorted(x['elapsed_seconds'] for x in log if x['event']=='preset_completed')
        assert len(times)==len(selected) and last['counts']==dict(statuses)
        report['timing']={'wall_seconds_including_batch_archives':last['wall_seconds'],
            'per_preset_mean_seconds':sum(times)/len(times),'per_preset_median_seconds':times[len(times)//2],
            'per_preset_max_seconds':max(times),'scope':'source parsing, offline compile/validation and static export; no simulation'}
    controls={p.name for p in (ROOT/'build/preset-corpus/static-review-presets').glob('*.milk')}
    report['sampling_control_overlap']=len(controls&selected.keys())
    atomic_json(output,report)
    print(json.dumps({k:report[k] for k in ('sample_size','status_counts','structured_descriptions','schema_valid_descriptions','conditional_trait_preset_counts','archive_batches','verified_archive_pairs')},indent=2))


if __name__=='__main__':
    summarize(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]) if len(sys.argv)>3 else None)
