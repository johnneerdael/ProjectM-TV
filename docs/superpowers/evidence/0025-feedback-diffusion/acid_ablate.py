"""Separate mixed point-feedback effects from Acid's bilinear advection/sharpening."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from ablate import first_key
from fidelity import image_error
from measure import EVIDENCE, REPO, measure

name="Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk"
text=(REPO/"core/src/main/assets/presets"/name).read_text()
line10=next(line.split("=",1)[1] for line in text.splitlines() if line.startswith("warp_10="))
assert line10.count("(GetPixel(uv) - GetBlur1(uv))*0.1")==1
no_sharpen=first_key(text,"warp_10",line10.replace("(GetPixel(uv) - GetBlur1(uv))*0.1","0"))
root=EVIDENCE/"acid-ablations";root.mkdir(exist_ok=True)
def remove_point_channels(value):
    for key in ["warp_14","warp_15","warp_16"]:value=first_key(value,key,"`// ablated point channel feedback")
    return value
def remove_point_wrap(value):
    return first_key(value,"warp_21","`// ablated point wrap feedback")
cases={"original":text,"no-point-channels":remove_point_channels(text),
       "no-sharpen":no_sharpen,"no-sharpen-no-point":remove_point_wrap(remove_point_channels(no_sharpen)),
       "no-point-wrap":remove_point_wrap(text),"no-point-feedback":remove_point_wrap(remove_point_channels(text)),
       "only-displaced-feedback":first_key(remove_point_wrap(remove_point_channels(text)),"warp_10","`ret=GetPixel(uv_dy);")}
manifest=[]
for label,code in cases.items():
    filename=name if label=="original" else "acid-ablation-"+label+".milk"
    (root/filename).write_text(code)
    manifest.append({"ablation":label,"preset":filename,"original_sha256":hashlib.sha256(text.encode()).hexdigest(),
                     "sha256":hashlib.sha256(code.encode()).hexdigest()})
(EVIDENCE/"acid-ablation-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
specs=[("authored","baseline",1182,665,(0,0)),("baseline-1330","baseline",2364,1330,(1024,768)),
       ("corrected-1330","corrected",2364,1330,(1024,768)),("baseline-2160","baseline",3840,2160,(1024,768)),
       ("corrected-2160","corrected",3840,2160,(1024,768))]
def run(job):
    case,(label,worker,w,h,ref)=job
    result=dict(measure(case["preset"],worker,w,h,reference=ref,preset_root=root))
    result.update(ablation=case["ablation"],label=label)
    print(case["ablation"],label,result["status"],flush=True)
    return result
with ThreadPoolExecutor(max_workers=2) as pool:
    rows=list(pool.map(run,[(c,s) for c in manifest for s in specs]))
report={}
for case in manifest:
    runs={r["label"]:r for r in rows if r["ablation"]==case["ablation"]};gt=runs["authored"]
    report[case["ablation"]]={label:{"img_err":image_error(r,gt),"luma_ratio":r["luma"]/gt["luma"],
                                  "centre_rgb":r["centre_rgb"],"output":r["output"],"identity":r["identity"]}
                                for label,r in runs.items()}
(EVIDENCE/"acid-ablations-4s-raw.json").write_text(json.dumps(rows,indent=2)+"\n")
(EVIDENCE/"acid-ablations-4s-report.json").write_text(json.dumps(report,indent=2)+"\n")
assert all(r["status"]=="success" for r in rows)
