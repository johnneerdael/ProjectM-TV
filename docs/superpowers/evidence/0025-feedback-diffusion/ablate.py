"""Causal in-place preset ablations; never append duplicate keys."""
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fidelity import REGRESSIONS, image_error
from measure import EVIDENCE, REPO, measure

ROOT=EVIDENCE/"ablations"
ROOT.mkdir(exist_ok=True)

def first_key(text,key,value):
    pattern=re.compile(r"^"+re.escape(key)+r"=.*$",re.M|re.I)
    assert pattern.search(text),key
    return pattern.sub(lambda m:m.group(0).split("=",1)[0]+"="+value,text,count=1)

def code_change(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)

def shader(text,section,code):
    lines=text.splitlines()
    positions=[i for i,l in enumerate(lines) if re.match(section+r"_[0-9]+=",l,re.I)]
    assert positions,section
    insert=positions[0]
    kept=[l for i,l in enumerate(lines) if i not in positions]
    replacement=[f"{section}_{i+1}=`{l}" for i,l in enumerate(code.splitlines())]
    kept[insert:insert]=replacement
    return "\n".join(kept)+"\n"

def cases(name,text):
    yield "original",text
    if name==REGRESSIONS[0]:
        yield "no-red-sharpen",code_change(text,"ret.x += (ret.x - GetBlur3(uv).x)*0.75;","ret.x += 0;")
        for channel in "xyz":
            yield "canvas-"+channel,shader(text,"comp","shader_body\n{\nret = tex2D(sampler_main,uv)."+channel+";\n}")
        yield "no-gradient-offset",code_change(code_change(code_change(text,
            "float2 my_uv = uv - float2(dx,dy)*0.006 + float2(dxb,dyb)*0.003;","float2 my_uv = uv;"),
            "my_uv = uv + float2(dy,-dx)*0.05*(1.2-GetBlur3(uv).y);","my_uv = uv;"),
            "my_uv += uv - float2(dx,dy)*0.03;","my_uv = uv;")
    elif name==REGRESSIONS[1]:
        yield "no-motion",first_key(text,"mv_a","0")
        lines=[l for l in text.splitlines() if l.startswith("warp_") and "ret = max(ret," in l]
        without=text
        for line in lines:
            old=line.split("=",1)[1];without=code_change(without,old,"`// removed max branch")
        assert len(lines)==2
        yield "no-max",without
        yield "no-motion-no-max",first_key(without,"mv_a","0")
    elif name==REGRESSIONS[2]:
        yield "no-motion",first_key(text,"mv_a","0")
        yield "lines-instead-of-dots",first_key(text,"bWaveDots","0")
        probe=shader(text,"warp","shader_body\n{\nfloat2 phase=frac(uv*texsize.xy-0.5);\nret=float3(phase*(1-phase),0);\n}")
        yield "phase-probe",shader(probe,"comp","shader_body\n{\nret=tex2D(sampler_main,uv);\n}")
    elif name==REGRESSIONS[3]:
        without=code_change(text,"ret=max(ret,tex2D(sampler_fc_main,lerp(uv_orig,uv,0.5))*.97); //trails","ret=ret;")
        yield "no-max",without
        yield "no-sharpen",code_change(text,"ret+=(ret-GetBlur1(uv))*0.15;","ret=ret;")
        yield "no-max-no-sharpen",code_change(without,"ret+=(ret-GetBlur1(uv))*0.15;","ret=ret;")
    else:
        old="ret.z = (tex2D(sampler_main, uv_orig).y - ret.y)*2 + 0.5;"
        yield "no-blue-branch",code_change(text,old,"ret.z = 0.5;")
        yield "displaced-blue",code_change(text,old,"ret.z = (tex2D(sampler_main, my_uv - floor(my_uv)).y - ret.y)*2 + 0.5;")
        for channel in "xyz":
            yield "canvas-"+channel,shader(text,"comp","shader_body\n{\nret=tex2D(sampler_main,uv)."+channel+";\n}")

if __name__=="__main__":
    manifest=[]
    for name in REGRESSIONS:
        text=(REPO/"core/src/main/assets/presets"/name).read_text()
        for label,altered in cases(name,text):
            token=hashlib.sha256((name+label).encode()).hexdigest()[:12]
            filename="ablation-"+label+"-"+token+".milk"
            (ROOT/filename).write_text(altered)
            manifest.append({"original":name,"ablation":label,"preset":filename,
                "original_sha256":hashlib.sha256(text.encode()).hexdigest(),"ablation_sha256":hashlib.sha256(altered.encode()).hexdigest()})
    (EVIDENCE/"ablation-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    specs=[("authored","baseline",1182,665,(0,0)),("baseline-1330","baseline",2364,1330,(1024,768)),
           ("p1-1330","p1",2364,1330,(1024,768)),("baseline-2160","baseline",3840,2160,(1024,768)),
           ("p1-2160","p1",3840,2160,(1024,768))]
    def run(args):
        case,spec=args;label,worker,w,h,ref=spec
        r=dict(measure(case["preset"],worker,w,h,reference=ref,preset_root=ROOT))
        r.update(original=case["original"],ablation=case["ablation"],label=label)
        print(case["original"][:30],case["ablation"],label,r["status"],flush=True)
        return r
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(run,[(case,spec) for case in manifest for spec in specs]))
    (EVIDENCE/"ablations-4s-raw.json").write_text(json.dumps(results,indent=2)+"\n")
    report={}
    for case in manifest:
        rows={r["label"]:r for r in results if r["preset"]==case["preset"]}
        gt=rows["authored"]
        report.setdefault(case["original"],{})[case["ablation"]]={label:
            {"img_err":image_error(r,gt),"luma":r["luma"],"luma_ratio":r["luma"]/gt["luma"] if gt["luma"]>.001 else None,
             "centre_rgb":r["centre_rgb"],"sha256":r["sha256"],"output":r["output"]}
            for label,r in rows.items() if r["status"]=="success" and gt["status"]=="success"}
    (EVIDENCE/"ablations-4s-report.json").write_text(json.dumps(report,indent=2)+"\n")
    assert all(r["status"]=="success" for r in results),"Ablation render failure"
