import json, sys, glob, statistics as st
from pathlib import Path
rows=[json.loads(Path(f).read_text()) for f in sorted(glob.glob(sys.argv[1]+'/*.json'), key=lambda p:int(Path(p).stem))]
K=['fp1330','dl0_1330','dl05_1330','fp4k','dl0_4k','dl05_4k']
ok=[r for r in rows if 'error' not in r and all('mae' in r.get(k,{}) for k in K+['c1280'])]
print('rows',len(rows),'ok',len(ok)); bad=[(r['preset'][:40],[k for k in K if 'mae' not in r.get(k,{})]) for r in rows if r not in ok]; print('incomplete',bad)
for k in ['c1280']+K:
    m=[r[k]['mae'] for r in ok]; lr=[r[k]['luma_ratio'] for r in ok if r[k].get('luma_ratio')]
    dark=sum(1 for x in lr if x<0.9); 
    print('%-10s MAE mean %.4f median %.4f | luma ratio median %.3f, <0.90: %d, >1.10: %d'%(k,st.mean(m),st.median(m),st.median(lr),dark,sum(1 for x in lr if x>1.1)))
def cmp(a,b,tol=0.05):
    w=l=t=0
    for r in ok:
        x,y=r[a]['mae'],r[b]['mae']
        if x<y*(1-tol): w+=1
        elif x>y*(1+tol): l+=1
        else: t+=1
    return w,t,l
for a,b in [('dl0_1330','fp1330'),('dl05_1330','fp1330'),('dl0_4k','fp4k'),('dl05_4k','fp4k'),('dl05_4k','dl0_4k')]:
    print(f'{a} vs {b} (closer/tie/farther, 5% tol):',cmp(a,b))
for res in ('1330','4k'):
    print(f'\nworst dl0_{res} vs fp{res}:')
    for r in sorted(ok,key=lambda r:-r[f'dl0_{res}']['mae']/max(r[f'fp{res}']['mae'],1e-4))[:6]:
        print('  %-50s fp %.4f dl0 %.4f dl05 %.4f  luma fp %.2f dl0 %.2f'%(r['preset'][:50],r[f'fp{res}']['mae'],r[f'dl0_{res}']['mae'],r[f'dl05_{res}']['mae'],r[f'fp{res}']['luma_ratio'] or 0,r[f'dl0_{res}']['luma_ratio'] or 0))
    print(f'darkest (luma ratio) per config {res}:')
    for k in (f'fp{res}',f'dl0_{res}',f'dl05_{res}'):
        print('  ',k,[(r['preset'][:25],round(r[k]['luma_ratio'],2)) for r in sorted(ok,key=lambda r:r[k]['luma_ratio'] or 9)[:4]])
