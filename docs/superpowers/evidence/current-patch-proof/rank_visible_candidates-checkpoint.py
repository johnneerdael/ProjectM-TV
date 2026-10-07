from pathlib import Path
import sys,re,json,hashlib,math
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/preset-lab/src'))
from preset_lab.preset_parser import parse_preset
presets=ROOT/'core/src/main/assets/presets';result={'0009':[],'0012':[],'0013':[]};errors=[]
def num(v,k,default=0):
 try:return float(v.get(k,default))
 except ValueError:return default
for p in sorted(presets.glob('*.milk')):
 try:d=parse_preset(p)
 except ValueError as e:errors.append({'name':p.name,'error':str(e)});continue
 v={};
 for k,value in d['values'].items():v.setdefault(k.lower(),value)
 text=p.read_text(errors='replace').lower();lines=text.splitlines();code='\n'.join(x['code'] for x in d['sections'].values()).lower();features=[];shape_score=0;shape_count=0;minrad=1
 for i in range(4):
  pre=f'shapecode_{i}_'
  if num(v,pre+'enabled')==0:continue
  shape_count+=1;instances=max(1,min(1024,num(v,pre+'num_inst',1)));radius=num(v,pre+'rad',.1);alpha=max(num(v,pre+'a',1),num(v,pre+'a2',1));body=d['sections'].get(f'shape_{i}_per_frame',{}).get('code','').lower()
  numeric=[float(x) for x in re.findall(r'\brad\s*=\s*([0-9]*\.[0-9]+|[0-9]+(?:e-?[0-9]+)?)',body)]
  small=min([radius]+[x for x in numeric if x>0]);minrad=min(minrad,small)
  score=math.log2(instances+1)*3+min(alpha,2)*2
  if 0<small<=.008:score+=20
  if 'rad' in body and ('gmegabuf' in body or 'megabuf' in body):score+=10
  if num(v,pre+'textured')==0:score+=2
  shape_score+=score;features.append({'shape':i,'instances':instances,'configured_radius':radius,'literal_radius_hint':small,'alpha':alpha})
 if shape_count:
  result['0012'].append({'filename':p.name,'score':shape_score,'features':features,'asset_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 comp=d['sections'].get('comp_',{}).get('code','').lower();warp=d['sections'].get('warp_',{}).get('code','').lower()
 version=num(v,'milkdrop_preset_version',100);compver=num(v,'psversion_comp',num(v,'psversion',0))
 if version>=200 and compver>0 and re.search(r'\bsampler_(?:[fp][wc]_)?main\b',comp):
  terms=[t for t in ['texsize','fract','frac','floor','sin(','cos(','pow(','grad','blur','sampler_pc_main','sampler_pw_main'] if t in comp]
  score=5+len(terms)*2+shape_count*2+min(shape_score/5,20)
  if 'gradient' in text or 'reaction' in p.name.lower() or 'grid' in p.name.lower() or 'mandala' in p.name.lower():score+=12
  if re.search(r'\bret\s*(?:\.rgb|\.xyz)?\s*=\s*tex2d\(\s*sampler_main\s*,\s*uv\s*\)',comp):score+=8
  result['0013'].append({'filename':p.name,'score':score,'features':terms,'shapes':features,'asset_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for tex in ['chloemall','plane','noise64']:
  if re.search(r'sampler_(?:[fp][wc]_)?'+tex+r'\b|shapecode_[0-3]_image=(?:[fp][wc]_)?'+tex+r'\b',text):
   result['0009'].append({'filename':p.name,'texture':tex,'score':100 if tex=='chloemall' else 90 if tex=='plane' else 80,'asset_sha256':hashlib.sha256(p.read_bytes()).hexdigest()});break
for key in result:result[key].sort(key=lambda x:(-x['score'],x['filename']))
out={'scope':'Source-only candidate ranking across all bundled presets; source predicates are not rendered defect proof','count':len(list(presets.glob('*.milk'))),'parse_errors':errors,'candidate_counts':{k:len(v) for k,v in result.items()},'ranked':result}
(ROOT/'build/patch-proof/visible-candidate-inventory.json').write_text(json.dumps(out,indent=2)+'\n')
print('scanned',out['count'],'errors',len(errors),'candidates',out['candidate_counts'])
for key,rows in result.items():
 print('\nPATCH',key)
 for row in rows[:25]:print(round(row['score'],2),row['filename'],str(row.get('features',row.get('texture')))[:140])
