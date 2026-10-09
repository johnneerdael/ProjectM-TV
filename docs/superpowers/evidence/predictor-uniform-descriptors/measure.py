import sys,json,time,hashlib,tempfile,zipfile,platform
from pathlib import Path
from collections import Counter
import numpy as np
import cv2
sys.path.insert(0,str(Path('tools/milk-analyzer').resolve()))
from forecast import read_source,model_file_hashes
from shader_fields import ShaderFields
from shader_uniformity import UniformityProof
from field_math import numeric_layout
from grid_math import evaluate_grid
from feedback_field import unorm8
from descriptors import DescriptorStream
from uniform_source_descriptors import uniform_expression_window,SPATIAL_INPUTS

reader=Path('build/preset-corpus/source31/adapters/milk-native-reader').resolve()
model_hashes=model_file_hashes()
with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'uniform-control.milk'
    body='MILKDROP_PRESET_VERSION=201\n[preset00]\nPSVERSION_COMP=2\ncomp_1=`shader_body {ret=float3(bass,.5+.2*sin(time),.1);}\n'
    path.write_text(body)
    source=read_source(path,reader=reader)
model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False)
expression=model.lower(source['sections']['comp_']['tree'])
assert model.complete
updates=[{'time':(i+1)/15,'inputs':{'_c2':[(i+1)/15,15,i+1,0],
                                 '_c3':[.04+(i%4)*.18,1,1,1]}} for i in range(60)]
def full():
    stream=DescriptorStream()
    for update in updates:
        rgb=evaluate_grid(expression,batch_shape=(480,854),inputs=update['inputs'])
        rgba=unorm8(np.concatenate((rgb,np.ones((480,854,1),np.float32)),axis=-1))
        stream.add({'time':update['time'],'display':rgba})
    return stream.report()
def small():return uniform_expression_window(expression,updates,viewport=(854,480),quantize=True)
times={'full':[],'uniform':[]};reports={}
for trial in range(3):
    for name,fn in [('full',full),('uniform',small)]:
        start=time.perf_counter();reports[name]=fn();times[name].append(time.perf_counter()-start)
def same(a,b):
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if a is None or isinstance(a,(str,bool,int)):return a==b
    return np.isclose(a,b,rtol=2e-6,atol=2e-7)
assert all(same(reports['full'][key],reports['uniform'][key]) for key in ['colour','flashing','motion','structure'])
report={'scope':'Synthetic uniform final-expression execution plus descriptors only; no equations, warp, feedback, geometry or complete preset timing',
        'model_modules':model_hashes,
        'measurement_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source':body,'reader_sha256':hashlib.sha256(reader.read_bytes()).hexdigest(),
        'engine':source['parser_inputs']['engine'],'viewport':[854,480],'frames':60,'fps':15,
        'backend':{'python':platform.python_version(),'machine':platform.machine(),'cv2':cv2.__version__,
                   'opencv_features':cv2.getCPUFeaturesLine(),'numpy':np.__version__},
        'seconds':times,'median_speedup':float(np.median(times['full'])/np.median(times['uniform'])),
        'parity':{'rtol':2e-6,'atol':2e-7,'groups':['colour','flashing','motion','structure'],
                  'nulls_flags_counts_exact':True},'full_report':reports['full'],'uniform_report':reports['uniform']}
Path('build/preset-corpus/uniform-descriptors/benchmark.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['scope','seconds','median_speedup','parity']}),flush=True)

zip_path=Path('/Users/jneerdael/Downloads/ProjectM-TV-static-effects-review-100-2026-10-09/batch-000001.zip')
rows=[];started=time.perf_counter()
with zipfile.ZipFile(zip_path) as archive,tempfile.TemporaryDirectory() as folder:
    for item in archive.namelist():
        if not item.startswith('presets/') or not item.endswith('.milk'):continue
        raw=archive.read(item);path=Path(folder)/Path(item).name;path.write_bytes(raw)
        source=read_source(path,reader=reader);section=source.get('sections',{}).get('comp_',{})
        row={'name':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'route':'unavailable-authored-composite'}
        if section.get('status')=='parsed':
            model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False,
                main_binding_policy='projectmtv-core-2.2.6-v1',
                global_input_policy=section.get('implicit_global_input_policy','strict-v1'),
                array_initializer_policy=section.get('array_initializer_policy','legacy-layout-v1'))
            try:
                expression=model.lower(section['tree'],language_extensions=section.get('language_extensions',[]))
                if not model.complete:
                    row.update(route='lowering-unresolved',reasons=model.unknown)
                else:
                    pending=[expression];seen=set();inputs={}
                    while pending:
                        node=pending.pop()
                        if id(node) in seen:continue
                        seen.add(id(node))
                        if len(seen)>65536:raise ValueError('candidate dependency budget exceeded')
                        if node.op=='input' and node.detail['name'] not in SPATIAL_INPUTS:
                            dtype,shape=numeric_layout(node.dtype);inputs[node.detail['name']]=np.zeros(shape,dtype=dtype)
                        pending.extend(node.args)
                    proof=UniformityProof(inputs,(480,854))
                    try:uniform=proof.is_uniform(expression)
                    finally:proof.release()
                    row.update(route='uniform-binding-candidate' if uniform else 'spatial-resource-or-unproven',
                               dependencies=sorted(inputs))
            except (ValueError,TypeError,KeyError,RecursionError) as error:row.update(route='lowering-unresolved',reasons=[str(error)])
        rows.append(row)
census={'scope':'Same fixed100 pack sources as static export; parser/lowering/dependency shapes only, no numerical shader or equation execution',
        'count':len(rows),'counts':dict(Counter(row['route'] for row in rows)),
        'seconds':time.perf_counter()-started,'source_zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),
        'reader_sha256':report['reader_sha256'],'rows':rows,
        'limitations':['Candidate means uniform if all declared nonspatial inputs have uniform bindings',
                       'No target compatibility checks supplied; zero presets certified for automatic routing',
                       'Known uniform component inference and loop/texture invariants not modeled here',
                       'Not whole-corpus coverage, visual accuracy or complete export timing']}
Path('build/preset-corpus/uniform-descriptors/census.json').write_text(json.dumps(census,indent=2))
assert model_file_hashes()==model_hashes,'model changed during bounded measurement'
print(json.dumps({k:census[k] for k in ['count','counts','seconds','limitations']}),flush=True)
