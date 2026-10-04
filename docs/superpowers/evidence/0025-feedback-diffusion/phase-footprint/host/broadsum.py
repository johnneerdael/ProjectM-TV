import json, sys, glob
from pathlib import Path
rows=[json.loads(Path(f).read_text()) for f in sorted(glob.glob(sys.argv[1]+'/*.json'), key=lambda p:int(Path(p).stem))]
cand=sys.argv[2] if len(sys.argv)>2 else 'emuc'
ok=[r for r in rows if 'error' not in r and all('mae' in r.get(k,{}) for k in ('v0','v1',cand,'c1280'))]
print('rows',len(rows),'ok',len(ok))
import statistics as st
for k in ('c1280','v0','v1',cand): print(k,'mean MAE %.4f median %.4f'%(st.mean(r[k]['mae'] for r in ok), st.median(r[k]['mae'] for r in ok)))
gated=[r for r in ok if r['v1']['digest']==r['v0']['digest']]
print('gated/no-op v1==v0:',len(gated))
def cmp(a,b,tol=0.02):
    w=l=t=0
    for r in ok:
        x,y=r[a]['mae'],r[b]['mae']
        if x<y*(1-tol): w+=1
        elif x>y*(1+tol): l+=1
        else: t+=1
    return w,t,l
print(f'{cand} vs v1 (closer/tie/farther, 2% tol):',cmp(cand,'v1'))
print(f'{cand} vs v0:',cmp(cand,'v0'))
print('v1 vs v0:',cmp('v1','v0'))
print(f'{cand} within c1280 MAE:',sum(r[cand]['mae']<=r['c1280']['mae']*1.02 for r in ok),'v1:',sum(r['v1']['mae']<=r['c1280']['mae']*1.02 for r in ok))
print(f'\nworst {cand}/v1 ratios:')
for r in sorted(ok,key=lambda r:-r[cand]['mae']/max(r['v1']['mae'],1e-9))[:8]:
    print('  %-55s v0 %.4f v1 %.4f %s %.4f c1280 %.4f gated=%s'%(r['preset'][:55],r['v0']['mae'],r['v1']['mae'],cand,r[cand]['mae'],r['c1280']['mae'],r['v1']['digest']==r['v0']['digest']))
print(f'\nbest {cand}/v1:')
for r in sorted(ok,key=lambda r:r[cand]['mae']/max(r['v1']['mae'],1e-9))[:8]:
    print('  %-55s v0 %.4f v1 %.4f %s %.4f c1280 %.4f'%(r['preset'][:55],r['v0']['mae'],r['v1']['mae'],cand,r[cand]['mae'],r['c1280']['mae']))
