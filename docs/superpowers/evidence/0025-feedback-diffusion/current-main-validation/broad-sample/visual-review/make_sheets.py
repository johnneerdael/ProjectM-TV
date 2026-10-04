"""Offline comparative panels assembled from verified capture PNGs, without resizing."""
import collections, hashlib, json, os
from pathlib import Path
import cv2
import numpy as np

WORK=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
ROOT=WORK.parents[2]
canonical=lambda d:json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
comparison=json.loads((WORK/'classic-reference/comparison.json').read_text())
selection=json.loads((WORK/'selection.json').read_text())
assert comparison['state']=='complete' and comparison['terminal_total_jobs']==640
by=collections.defaultdict(dict)
for case in comparison['cases']:by[case['preset']['path']][case['profile']]=case
def score(item):
    return sum(c['candidate_reference_errors']['thumbnail_mae_256x144_rgb01']-c['baseline_reference_errors']['thumbnail_mae_256x144_rgb01'] for c in item[1].values())/2
farther=sorted([(n,c) for n,c in by.items() if all(v['classification']=='farther' for v in c.values())],key=score,reverse=True)[:3]
closer=sorted([(n,c) for n,c in by.items() if all(v['classification']=='closer' for v in c.values())],key=score)[:3]
mixed_pool=sorted([(n,c) for n,c in by.items() if all(v['classification']=='mixed' for v in c.values())],key=score)
mixed=[mixed_pool[0],next(item for item in mixed_pool if item[1]['1330']['dark_reference_band']=='dark1-5pct')]
groups={'farther':farther,'closer':closer,'mixed':mixed}
short={
'Fumbling_Foo + En D & Martin - Mandelverse.milk':'Fumbling_Foo + En D & Martin - Mandelverse',
'$$$ Royal - Mashup (255).milk':'Royal - Mashup (255)',
'astral spinorgentics encrustcore nz+.milk':'astral spinorgentics encrustcore nz+',
'Stahlregen & Flexi + Geiss + Martin + Rovastar + Telek - DiskWasher (Gentle RMX).milk':'Stahlregen & collaborators - DiskWasher (Gentle RMX)',
'Waltra - Heaven Liquid.milk':'Waltra - Heaven Liquid',
'Martin - Pixies Party (Hakan mash-up) 3-3.milk':'Martin - Pixies Party (Hakan mash-up) 3-3',
'Krash & yin + Phat - Electric universe (uncertainty principle)_remix_v2.milk':'Krash & yin + Phat - Electric universe (uncertainty principle) v2',
'$$$ Royal - Mashup (123).milk':'Royal - Mashup (123) [low-signal example]',
}
protocols={label:json.loads((WORK/label/'protocol.json').read_text()) for label in ('1330','2160','classic-reference')}
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def getrow(label,record,role):
    protocol=protocols[label];key=digest({'protocol_sha256':protocol['sha256'],'preset':record,'role':role,'capture_mode':'selected','repeat':1,'measurement_frames':360})
    path=WORK/label/'jobs'/key/'row.json';row=json.loads(path.read_text())
    assert row['payload_sha256']==digest({k:v for k,v in row.items() if k!='payload_sha256'})
    assert row['status']=='success' and row['result']['core_sha256']==protocol['roles'][role]['core_sha256']
    return path,row
FONT=cv2.FONT_HERSHEY_SIMPLEX
BG=(247,247,247);FG=(24,24,24);MUTED=(80,80,80)
def text(canvas,value,x,y,scale=.66,color=FG,thickness=1):
    cv2.putText(canvas,value,(x,y),FONT,scale,color,thickness,cv2.LINE_AA)
def fittext(canvas,value,x,y,max_width,scale=.72,color=FG,thickness=1):
    while cv2.getTextSize(value,FONT,scale,thickness)[0][0]>max_width:scale-=.02
    text(canvas,value,x,y,scale,color,thickness)
columns=[('Classic control29','1182 x 665','classic-reference','reference'),('Baseline29','2364 x 1330','1330','baseline'),('Candidate30','2364 x 1330','1330','candidate'),('Baseline29','3840 x 2160','2160','baseline'),('Candidate30','3840 x 2160','2160','candidate')]
manifest={'selection_sha256':selection['sha256'],'render_rng_seed':12345,'sample_seed':20261004,'frames':[239,479],
          'producer_thumbnail_dimensions':[256,144],'image_operation':'Decode verified lossless PNG, paste original256x144 pixels unchanged, encode comparison-sheet PNG; no resizing/gamma/contrast edits',
          'source_comparison_sha256':sha(WORK/'classic-reference/comparison.json'),'source_aggregate_sha256':sha(WORK/'aggregate.json'),
          'protocols':{k:{'sha256':v['sha256'],'file_sha256':sha(WORK/k/'protocol.json')} for k,v in protocols.items()},
          'selection_rules':{'farther':'Largest average thumbnail reference-error increase across both resolutions, restricted to primaryfarther at both sizes; three cases',
                             'closer':'Largest average thumbnail reference-error reduction across both resolutions, restricted to primarycloser at both sizes; three cases',
                             'mixed':'Largest thumbnail-error reduction with opposing brightness direction at both sizes, plus one mixed dark-reference case for low-signal context'},
          'metric_scope':'All error summaries average8capture frames120,150,180,210,239,300,390,479; panels show239 and479 only. Brightness=native luma absoluteerror; thumbnail=256x144 RGB MAE; saturation=absoluteerror ofmean thumbnail HSV saturation. Smaller means closer to privateclassic control, not perceptual acceptance.',
          'limitations':comparison['limitations'],'cases':[],'sheets':[]}
for category,chosen in groups.items():
    header=190;caseheight=510;footer=76;width=1472;height=header+len(chosen)*caseheight+footer
    canvas=np.full((height,width,3),BG,dtype=np.uint8)
    relation={'farther':'farther from','closer':'closer to','mixed':'mixed against'}[category]
    text(canvas,'Actual-core broad sample: '+relation+' classic control',64,38,1.05,FG,2)
    text(canvas,'OFFLINE PNG evidence | fixed bass stimulus | render seed12345 | sample seed20261004 | emulator Apple M4 Pro',64,69,.58,MUTED)
    text(canvas,'Native brightness + 256-thumbnail metrics; eight-frame means. Two shown frames are a visual subset. No perceptual acceptance.',64,97,.58,MUTED)
    for i,(label,geometry,_,_) in enumerate(columns):
        x=64+i*272;text(canvas,label,x,137,.72,FG,2);text(canvas,geometry+' -> 256 x 144 PNG',x,163,.51,MUTED)
    sheet_entries=[]
    for index,(name,cases) in enumerate(chosen):
        top=header+index*caseheight;record=cases['1330']['preset'];sampler=next(c for c in selection['cases'] if c['preset']['path']==name)
        item={'preset':record,'short_title':short.get(name,name.removesuffix('.milk')),'category':category,'average_thumbnail_error_delta_both_profiles':score((name,cases)),
              'sampling_group_lexical':sampler['group'],'features_lexical':sampler['features_lexical'],
              'reference_luma_mean':cases['1330']['reference_luma_mean'],'reference_brightness_band':cases['1330']['dark_reference_band'],
              'metrics_by_profile':{label:{'category':c['classification'],'baseline_reference_errors':c['baseline_reference_errors'],'candidate_reference_errors':c['candidate_reference_errors'],
                                         'metric_closeness':c['metric_closeness'],'repeat_exact_selected':c['repeat_exact_selected'],'frame_errors':c['frame_errors']} for label,c in cases.items()},'inputs':[]}
        fittext(canvas,str(index+1)+'. '+item['short_title'],64,top+26,width-128,.78,FG,2)
        band_label={'lit>=5pct':'lit (>=5%)','dark1-5pct':'dark (1-5%)','near_black<1pct':'near black (<1%)'}[item['reference_brightness_band']]
        text(canvas,'Reference mean luma '+format(item['reference_luma_mean'],'.4f')+' | '+band_label+' | lexical group '+sampler['group'],64,top+52,.56,MUTED)
        for offset,label in enumerate(('1330','2160')):
            c=cases[label];a=c['baseline_reference_errors'];b=c['candidate_reference_errors']
            line=(label+'  baseline -> candidate: brightness abs '+f"{a['native_luma_absolute_error']:.4f} -> {b['native_luma_absolute_error']:.4f}"+
                  ' | thumbnail MAE '+f"{a['thumbnail_mae_256x144_rgb01']:.4f} -> {b['thumbnail_mae_256x144_rgb01']:.4f}"+
                  ' | saturation abs '+f"{a['thumbnail_hsv_mean_saturation_error']:.4f} -> {b['thumbnail_hsv_mean_saturation_error']:.4f}")
            text(canvas,line,64,top+78+offset*24,.56,FG)
        for frameoffset,frame in enumerate((239,479)):
            y=top+119+frameoffset*163;text(canvas,str(frame),14,y+77,.61,MUTED,1)
            for i,(_,_,label,role) in enumerate(columns):
                path,row=getrow(label,record,role);sample=next(s for s in row['result']['selected_files'] if s['frame']==frame)
                source=path.parent/'output'/sample['thumbnail_path'];assert sha(source)==sample['thumbnail_sha256'];assert source.stat().st_size==sample['thumbnail_bytes']
                image=cv2.imread(str(source));assert image is not None and image.shape==(144,256,3)
                x=64+i*272;canvas[y:y+144,x:x+256]=image
                entry={'sheet':category+'.png','preset':record,'frame':frame,'column':i,'label':columns[i][0],'source_profile':label,'role':role,'repeat':1,
                       'png_path':str(source.relative_to(WORK)),'png_sha256':sha(source),'row_path':str(path.relative_to(WORK)),'row_sha256':sha(path),
                       'native_selected_sha256':sample['sha256'],'thumbnail_bytes':sample['thumbnail_bytes'],'native_frame_metrics':sample['metrics'],'paste_box_xywh':[x,y,256,144]}
                item['inputs'].append(entry);sheet_entries.append((entry,image))
        cv2.line(canvas,(64,top+caseheight-28),(width-64,top+caseheight-28),(210,210,210),1)
        manifest['cases'].append(item)
    y=height-footer+8;text(canvas,'Frames239/479; all PNG inputs SHA256 verified. Original capture thumbnails pasted without pixel edits or resizing.',64,y,.58,MUTED)
    text(canvas,'Classic = core29 private ref0,0 control. This selected evidence illustrates metric directions; it does not represent full-corpus fidelity.',64,y+28,.58,MUTED)
    output=OUT/(category+'.png');assert cv2.imwrite(str(output),canvas)
    decoded=cv2.imread(str(output));assert decoded.shape==canvas.shape
    for entry,image in sheet_entries:
        x,y,w,h=entry['paste_box_xywh'];assert np.array_equal(decoded[y:y+h,x:x+w],image)
    manifest['sheets'].append({'path':output.name,'sha256':sha(output),'bytes':output.stat().st_size,'dimensions':[width,height],'category':category,'cases':len(chosen),'verified_input_pixels_unchanged':True})
manifest['generator_sha256']=sha(Path(__file__));manifest['sha256']=digest(manifest)
(OUT/'manifest.json').write_text(canonical(manifest)+'\n')
assessment={'scope':'Offline eight-case illustration selected from the completed640-job actualcore sample; fixed frames239/479. Error means use eight capture frames, not just the two shown. No device calls, source changes or perceptual acceptance.',
 'selection':'Three largest primaryfarther thumbnail-error increases at both sizes; three strongest primarycloser decreases; strongest mixed thumbnail improvement and one dark mixed control.',
 'findings':['Mandelverse, Royal255 and astral nz+ are farther on native brightness, thumbnail MAE, native RGB mean and mean thumbnail saturation at both sizes.',
             'DiskWasher, Heaven Liquid and Pixies Party3-3 are closer on all four measured summaries at both sizes.',
             'Electric Universe lowers thumbnail MAE and saturation error while increasing native brightness/RGB-mean errors at both sizes.',
             'Royal123 is a low-signal mixed example: reference native luma2.27%; thumbnail MAE gets lower while brightness and saturation errors get higher. Small absolute changes here deserve signal context.'],
 'low_signal_caveats':'Seven chosen cases have reference meanluma>=5%; Royal123 is dark1-5%. Dark/nearblack reference renders can make numeric improvements look decisive while little image signal is available. Do not treat the illustrated strong cases as prevalence estimates.',
 'hypotheses_only':'Author/family and lexical sampling groups overlap: Royal255/Royal123 have opposite categories despite shared approximate family; shader features can co-occur. Point/mixed/blur/max/gradient lexical labels are sampling proxies, not proven causal mechanisms or predictors of fidelity. Some scalar/frame directions can disagree; inspect saved frame arrays.',
 'manifest_sha256':sha(OUT/'manifest.json'),'cases':[{'preset':c['preset'],'category':c['category'],'reference_brightness_band':c['reference_brightness_band'],'metrics_by_profile':c['metrics_by_profile']} for c in manifest['cases']]}
(OUT/'assessment.json').write_text(canonical(assessment)+'\n')
print(canonical({'sheets':manifest['sheets'],'cases':[{'preset':c['preset']['path'],'category':c['category'],'reference_band':c['reference_brightness_band']} for c in manifest['cases']],'verified_png_inputs':sum(len(c['inputs']) for c in manifest['cases'])}))
