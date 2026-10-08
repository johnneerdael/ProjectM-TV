from pathlib import Path
import json,hashlib,shutil,cv2,numpy as np
root=Path('docs/superpowers/evidence/milkdrop-audit-repairs');caps=Path('build/audit/captures')
groups=[('I09','pi','pidiag-final-audit-pi-precision','pi-diagnostics-final'),('I05','aspect','inputdiag-final-audit-inverse-aspect','input-diagnostics-final'),('I06','wave-time','inputdiag-final-audit-fresh-wave-time','input-diagnostics-final'),('I22','single','dotdiag-final-audit-single-dot','dot-diagnostics-final'),('I22','two','dotdiag-final-audit-two-dots','dot-diagnostics-final'),('I22','ring','dotdiag-final-audit-dot-ring','dot-diagnostics-final')]
for issue,label,prefix,family in groups:
 out=root/issue;dest=out/('final-diagnostic-'+label+'-results.json')
 if dest.exists():continue
 if not all((caps/(prefix+'-'+role+'-'+str(repeat))/'manifest.json').exists() for role in ('before','after') for repeat in (0,1)):print('pending',issue,label,flush=True);continue
 result={'qualification':'Source-instrumented exact-native-AAR private diagnostic APK; final-output read framebuffer0; not shipping APK or Windows rendering proof','display':[3840,2160],'canvas':[1280,720],'roles':{}}
 for role in ('before','after'):
  rows=[]
  for repeat in (0,1):
   src=caps/(prefix+'-'+role+'-'+str(repeat));m=json.loads((src/'manifest.json').read_text());assert m['status']=='ok' and m['framesRendered']==480;assert all(c['captureReadFramebufferBinding']==0 for c in m['captures']);rows.append(m)
   for c in m['captures']:
    p=src/('frame-%03d.png'%c['frame']);assert hashlib.sha256(p.read_bytes()).hexdigest()==c['pngSha256'];rgb=cv2.cvtColor(cv2.imread(str(p)),cv2.COLOR_BGR2RGB);assert hashlib.sha256(rgb.tobytes()).hexdigest()==c['rgbSha256']
   shutil.copyfile(src/'manifest.json',out/('final-diagnostic-'+label+'-'+role+'-'+str(repeat)+'-manifest.json'))
  assert [c['rgbSha256'] for c in rows[0]['captures']]==[c['rgbSha256'] for c in rows[1]['captures']]
  src=caps/(prefix+'-'+role+'-0')/'frame-239.png';shutil.copyfile(src,out/('final-diagnostic-'+label+'-'+role+'-4k.png'));im=cv2.imread(str(src));ys,xs=np.nonzero(im[:,:,2]>32);result['roles'][role]={'nonblack_pixels':int(np.count_nonzero(im.any(axis=2))),'red_x_centroid':float(xs.mean()) if len(xs) else None,'red_y_centroid':float(ys.mean()) if len(ys) else None,'rgb_hashes':[c['rgbSha256'] for c in rows[0]['captures']]}
  shutil.copyfile(Path('build/audit')/family/role/'identity.json',out/('final-diagnostic-'+label+'-'+role+'-identity.json'))
 result['selected_rgb_repeats_exact']=True;dest.write_text(json.dumps(result,indent=2)+'\n')
 with (out/'README.md').open('a') as f:f.write('\n## Final-output finite diagnostic — '+label+'\n\nFour480-frame runs explicitly capture read framebuffer0 and verify the installed APK hash per run. All eight selected RGB repeats are exact. Native AAR and stock assets are preserved except the declared private fixture/index overlay. [Final records](final-diagnostic-'+label+'-results.json).\n\n![Final diagnostic before](final-diagnostic-'+label+'-before-4k.png)\n\n![Source-derived expected final diagnostic](final-diagnostic-'+label+'-after-4k.png)\n')
 print('recorded',issue,label,result['roles']['before']['nonblack_pixels'],result['roles']['after']['nonblack_pixels'],flush=True)
