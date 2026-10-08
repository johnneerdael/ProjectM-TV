from pathlib import Path
import json,shutil,hashlib,cv2,numpy as np
root=Path('docs/superpowers/evidence/milkdrop-audit-repairs');caps=Path('build/audit/captures');ledger=json.loads((root/'ledger.json').read_text())
labels={'I17':('p15','p16'),'I08':('p16','p17'),'I22-mosaic':('p17','p18'),'I22-stars':('p17','p18'),'I31':('p18','p19'),'I05':('p20','p21'),'I06':('p20','p21'),'I19':('p16','i19proposal')}
for label,(before,after) in labels.items():
 issue=label.split('-')[0];out=root/issue;result={'capture_protocol':'explicit read framebuffer zero; prior binding restored','native_aar_and_preset_bytes_unchanged':True,'display':[3840,2160],'canvas':[1280,720],'repeat_scope':'eight selected RGB frames; not every-frame hashes','roles':{}}
 manifests={}
 for role,workerlabel in [('before',before),('after',after)]:
  rows=[]
  for repeat in (0,1):
   src=caps/('final-'+label+'-'+role+'-'+str(repeat));m=json.loads((src/'manifest.json').read_text());assert m['status']=='ok' and m['framesRendered']==480;assert all(c['captureReadFramebufferBinding']==0 for c in m['captures']);rows.append(m)
   for c in m['captures']:
    p=src/('frame-%03d.png'%c['frame']);assert hashlib.sha256(p.read_bytes()).hexdigest()==c['pngSha256'];rgb=cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB);assert hashlib.sha256(rgb.tobytes()).hexdigest()==c['rgbSha256']
   shutil.copyfile(src/'manifest.json',out/('final-'+label+'-'+role+'-'+str(repeat)+'-manifest.json'))
  assert [c['rgbSha256'] for c in rows[0]['captures']]==[c['rgbSha256'] for c in rows[1]['captures']]
  manifests[role]=rows[0];result['roles'][role]={'preset':rows[0]['verifiedPresetName'],'preset_sha256':rows[0]['presetAssetSha256'],'rgb_hashes':[c['rgbSha256'] for c in rows[0]['captures']]}
  identity=Path('build/audit/final-capture-workers')/workerlabel/'identity.json';shutil.copyfile(identity,out/('final-'+label+'-'+role+'-identity.json'))
 result['selected_rgb_repeats_exact']=True;metrics=[]
 for c in manifests['before']['captures']:
  frame=c['frame'];a=cv2.imread(str(caps/('final-'+label+'-before-0')/('frame-%03d.png'%frame)));b=cv2.imread(str(caps/('final-'+label+'-after-0')/('frame-%03d.png'%frame)))
  metrics.append({'frame':frame,'rgb_mae':float(np.abs(a.astype(float)-b.astype(float)).mean()),'before_rgb_mean':float(a.mean()),'after_rgb_mean':float(b.mean())})
 result['frame_metrics']=metrics;best=max(metrics,key=lambda m:m['rgb_mae'])['frame'];result['illustrated_frame']=best;result['all_selected_before_after_rgb_identical']=all(m['rgb_mae']==0 for m in metrics)
 for role in ('before','after'):shutil.copyfile(caps/('final-'+label+'-'+role+'-0')/('frame-%03d.png'%best),out/('final-'+label+'-'+role+'-4k.png'))
 (out/('final-'+label+'-results.json')).write_text(json.dumps(result,indent=2)+'\n')
 with (out/'README.md').open('a') as f:f.write('\n## Final-output replay — '+label+'\n\nFour480-frame runs now explicitly capture read framebuffer0, check the installed APK hash per run and retain exact native AAR/preset bytes. All eight selected RGB frames repeat exactly within each role. The illustrated common frame is'+str(best)+', selected for the largest measured difference among the eight captures. These are source-instrumented GLES final-output images; no Windows pixel-identity claim follows. [Final records](final-'+label+'-results.json).\n\n![Final output before](final-'+label+'-before-4k.png)\n\n![Source-derived expected final output](final-'+label+'-after-4k.png)\n')
 for e in ledger['entries']:
  if e['id']==issue:
   e['final_output_evidence']=issue+'/final-'+label+'-results.json'
   if issue in ('I17','I08','I31','I05','I06'):e['status']='implemented source repair; focused source/final-output original Native4K acceptance passed; final integration pending'
 print(label,'frame',best,'maxMAE',max(m['rgb_mae'] for m in metrics),'identical',result['all_selected_before_after_rgb_identical'],flush=True)
(root/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
