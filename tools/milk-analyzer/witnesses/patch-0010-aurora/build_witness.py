"""Build deterministic original art/presets for the patch0010 texture-ownership witness."""
from pathlib import Path
import hashlib
import json
import zipfile
import numpy as np
import cv2

ROOT=Path(__file__).resolve().parent
IMAGE='aurora_ownership_core.png'

def art(cold):
    n=512
    yy,xx=np.mgrid[:n,:n].astype(np.float64)
    x=(xx+.5-n/2)/(n/2); y=(yy+.5-n/2)/(n/2)
    r=np.hypot(x,y); a=np.arctan2(y,x)
    if cold:
        facets=np.maximum(0,np.cos(a*6))**9
        rim=.60+.065*np.cos(a*6)
        light=np.exp(-((r-rim)/.018)**2)+.65*np.exp(-((r-.77)/.012)**2)
        light+=.8*np.exp(-((r-.44)/.025)**2)*(.35+.65*facets)
        light+=.45*np.exp(-r*r*4)*(.25+.75*facets)
        halo=.28*np.exp(-((r-.62)/.11)**2)
        base=np.stack((.08*light+.015*halo,.62*light+.18*halo,1.3*light+.7*halo),-1)
        spokes=facets*np.exp(-((r-.72)/.18)**2)*.45
        base+=spokes[...,None]*np.array([.18,.65,1.0])
    else:
        rim=.60+.025*np.sin(a*12+r*13)
        light=np.exp(-((r-rim)/.022)**2)+.4*np.exp(-((r-.79)/.014)**2)
        flames=np.maximum(0,np.sin(a*14+r*22))**4
        light+=.5*flames*np.exp(-((r-.69)/.15)**2)
        light+=.55*np.exp(-r*r*5)*(.5+.5*np.cos(a*7+r*19)**2)
        halo=.32*np.exp(-((r-.62)/.13)**2)
        base=np.stack((1.4*light+.65*halo,.54*light+.15*halo,.045*light+.005*halo),-1)
    base*=np.clip((.99-r)/.08,0,1)[...,None]
    pixels=np.rint(np.clip(base,0,1)*255).astype(np.uint8)
    label='LUNA' if cold else 'SOL'
    font=cv2.FONT_HERSHEY_SIMPLEX;scale=1.0;thick=2
    size=cv2.getTextSize(label,font,scale,thick)[0]
    cv2.putText(pixels,label,((n-size[0])//2,276),font,scale,(205,238,255) if cold else (255,231,166),thick,cv2.LINE_AA)
    return pixels

def numbered(prefix,code):
    return '\n'.join(prefix+str(i)+'='+line for i,line in enumerate(code.strip().splitlines(),1))

def preset(cold):
    center=.70 if cold else .30
    palette=(.18,.65,1.0) if cold else (1.0,.40,.055)
    lines=['MILKDROP_PRESET_VERSION=201','PSVERSION_WARP=2','PSVERSION_COMP=2','[preset00]',
      'fRating=5','fDecay=.90','fGammaAdj=1','fVideoEchoAlpha=0','fWaveAlpha=0','nWaveMode=6',
      'warp=0','zoom=1','rot=0','dx=0','dy=0','sx=1','sy=1','bTexWrap=0',
      'bDarkenCenter=0','bBrighten=0','bDarken=0','bSolarize=0','bInvert=0',
      'ob_size=0','ib_size=0','mv_a=0','b1n=0','b1x=1','b1ed=0']
    lines.append(numbered('per_frame_init_',f"env=0;kick=0;q8={palette[0]};q9={palette[1]};q10={palette[2]};q11={center};"))
    lines.append(numbered('per_frame_',"""
kick=max(.78*kick,min(1.5,max(0,(bass-.95)*1.6)));
env=.92*env+.08*min(2,max(0,bass_att));
q1=kick;q2=env;q3=min(1.5,max(0,mid));q4=min(1.5,max(0,treb));
q5=min(1,max(0,bass-bass_att+.08)*2.4);q6=time*.65;
zoom=1;rot=0;warp=0;dx=0;dy=0;decay=.90;
"""))
    # The only identity-texture consumer is this per-frame custom shape lookup.
    shape={'enabled':1,'sides':4,'additive':0,'thickOutline':0,'textured':1,'num_inst':1,
      'x':center,'y':.5,'rad':.74,'ang':0,'tex_ang':0,'tex_zoom':.7071067812,
      'r':1,'g':1,'b':1,'a':1,'r2':1,'g2':1,'b2':1,'a2':1,'border_a':0,'image':Path(IMAGE).stem}
    lines.extend('shapecode_0_'+k+'='+str(v) for k,v in shape.items())
    lines.append(numbered('shape_0_per_frame',"rad=.74+.12*q1;ang=.04*sin(time*.5);"))
    for index,rad,alpha in [(1,.57,.45),(2,.67,.16)]:
      values={'enabled':1,'sides':64,'additive':1,'textured':0,'num_inst':1,'x':center,'y':.5,
       'rad':rad,'a':0,'a2':0,'border_r':palette[0],'border_g':palette[1],'border_b':palette[2],'border_a':alpha,'thickOutline':1}
      lines.extend(f'shapecode_{index}_'+k+'='+str(v) for k,v in values.items())
      lines.append(numbered(f'shape_{index}_per_frame',f'rad={rad}+.10*q1;border_a={alpha}+.10*q5;'))
    values={'enabled':1,'sides':3,'additive':1,'textured':0,'num_inst':12,'x':center,'y':.5,'rad':.02,
      'r':palette[0],'g':palette[1],'b':palette[2],'a':.20,'r2':1,'g2':1,'b2':1,'a2':.02,'border_a':0}
    lines.extend('shapecode_3_'+k+'='+str(v) for k,v in values.items())
    lines.append(numbered('shape_3_per_frame',"""
phase=instance*6.28318530718/12+q6;
orb=.36+.04*q1;
x=q11+.5625*orb*cos(phase);y=.5+orb*sin(phase);
ang=phase+time*.2;rad=.022+.018*q5;a=.14+.22*q1;
"""))
    for index,samples,dots,spectrum in [(0,256,1,0),(1,128,0,1)]:
      values={'enabled':1,'samples':samples,'sep':0,'bSpectrum':spectrum,'bUseDots':dots,
       'bDrawThick':dots,'bAdditive':1,'scaling':1,'smoothing':.5,
       'r':palette[0],'g':palette[1],'b':palette[2],'a':.30}
      lines.extend(f'wavecode_{index}_'+k+'='+str(v) for k,v in values.items())
    lines.append(numbered('wave_0_per_point',"""
phase=sample*12.56637061436+q6;
rr=.35+.025*sin(phase*5-time*1.2)+.05*q1+value1*.025;
x=q11+.5625*rr*cos(phase);y=.5+rr*sin(phase);
r=.80*q8+.20;g=.80*q9+.20;b=.80*q10+.20;
a=(.10+.15*q2+.10*q5)*(.4+.6*pow(.5+.5*sin(sample*197+time*1.4),2));
"""))
    lines.append(numbered('wave_1_per_point',"""
phase=sample*6.28318530718+time*.18;
rr=.265+.065*q1+min(.07,abs(value1)*.055);
x=q11+.5625*rr*cos(phase);y=.5+rr*sin(phase);
r=.65*q8+.35;g=.65*q9+.35;b=.65*q10+.35;a=.25+.12*q1;
"""))
    lines.append(numbered('warp_',"""
`shader_body {
` float2 c=float2(q11,.5);
` float2 p=(uv-c)/(1.002+.026*q1);
` float angle=.003*sin(time*.55)+.018*q1;
` float cs=cos(angle),sn=sin(angle);
` float2 w=c+float2(p.x*cs-p.y*sn,p.x*sn+p.y*cs);
` ret=GetPixel(w)*(.88-.045*min(q1,1.5));
` float2 metric=(uv-c)*aspect.xy;
` float box=max(abs(metric.x),abs(metric.y));
` ret*=smoothstep(.195,.215,box);
`}
"""))
    lines.append(numbered('comp_',"""
`shader_body {
` float2 p=(uv-float2(q11,.5))*aspect.xy;
` float radius=length(p);
` float angle=atan2(p.y,p.x);
` float rays=pow(saturate(.5+.5*sin(12*angle-time*.8+radius*8)),7);
` float outside=1-smoothstep(.23,.5,radius);
` float protect=smoothstep(.095,.145,radius);
` float beam=rays*exp(-radius*7)*protect*(.03+.035*q1);
` float ripple=pow(saturate(.5+.5*cos(radius*42-time*1.4)),6)*outside*protect*.025;
` ret=GetPixel(uv)+float3(q8,q9,q10)*(beam+ripple);
` ret+=GetBlur1(uv)*(.045+.035*q1)*protect;
` float drift_a=.5+.13*sin(uv.x*9+time*.28);
` float drift_b=.53+.17*cos(uv.x*6-time*.21);
` float mist_a=exp(-pow((uv.y-drift_a)*15,2));
` float mist_b=exp(-pow((uv.y-drift_b)*20,2));
` ret+=float3(q8,q9,q10)*(mist_a*.026+mist_b*.018)*(.6+.25*q2+.15*q1)*smoothstep(.12,.23,radius);
` float stars=saturate((cos(uv.x*181+sin(uv.y*67+time*.08))*cos(uv.y*163+sin(uv.x*77-time*.06))-.96)*14);
` ret+=(.12+float3(q8,q9,q10)*.45)*pow(stars,3)*(.8+.2*sin(time*.8+uv.x*10))*protect;
` ret=pow(saturate(ret),float3(.92,.92,.92));
` ret*=.83+.17*(1-smoothstep(.35,.80,length((uv-.5)*aspect.xy)));
`}
"""))
    return '\n'.join(lines)+'\n'

def main():
    files={}
    for cold,name in [(False,'pack-a'),(True,'pack-b')]:
      folder=ROOT/name;(folder/'presets').mkdir(parents=True,exist_ok=True);(folder/'textures').mkdir(exist_ok=True)
      title='Aurora Ownership - LUNA.milk' if cold else 'Aurora Ownership - SOL.milk'
      (folder/'presets'/title).write_text(preset(cold))
      pixels=art(cold);cv2.imwrite(str(folder/'textures'/IMAGE),cv2.cvtColor(pixels,cv2.COLOR_RGB2BGR))
      with zipfile.ZipFile(ROOT/(name+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(folder.rglob('*')):
          if path.is_file():
            entry=zipfile.ZipInfo(str(path.relative_to(folder)),(1980,1,1,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;z.writestr(entry,path.read_bytes())
      for path in sorted(folder.rglob('*')):
        if path.is_file():files[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT/'asset-hashes.json').write_text(json.dumps(files,indent=2)+'\n')
    print('Created SOL and LUNA packs with per-frame named-image custom-shape consumers')

if __name__=='__main__':main()
