"""GPU impulse proof of variance, independent of the factory's tap enumeration."""
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from measure import Config, EVIDENCE, REPO, SCRATCH, signal
from preset_lab.models import EngineIdentity, JobSpec, PresetRecord
from preset_lab.worker import render_job

CANDIDATE=sys.argv[1] if len(sys.argv)>1 else "final"

root=EVIDENCE/"probes";root.mkdir(exist_ok=True)
name="kernel-impulse.milk"
(root/name).write_text("""MILKDROP_PRESET_VERSION=201
PSVERSION=2
PSVERSION_WARP=2
PSVERSION_COMP=2
[preset00]
fGammaAdj=1
fVideoEchoAlpha=0
zoom=1
rot=0
warp=0
sx=1
sy=1
ob_a=0
ib_a=0
fDecay=0
fWaveAlpha=0
mv_a=0
shapecode_0_enabled=0
shapecode_0_num_inst=1
shapecode_0_sides=4
shapecode_0_additive=0
shapecode_0_textured=0
shapecode_0_x=0.5
shapecode_0_y=0.5
shapecode_0_rad=0.002
shapecode_0_ang=0.7853981633974483
shapecode_0_r=1
shapecode_0_g=1
shapecode_0_b=1
shapecode_0_a=1
shapecode_0_r2=1
shapecode_0_g2=1
shapecode_0_b2=1
shapecode_0_a2=1
shapecode_0_border_a=0
wavecode_0_enabled=1
wavecode_0_samples=32
wavecode_0_bUseDots=1
wavecode_0_bDrawThick=0
wavecode_0_bAdditive=1
wavecode_0_smoothing=0
wavecode_0_r=1
wavecode_0_g=1
wavecode_0_b=1
wavecode_0_a=1
wave_0_per_point1=x=0.5; y=0.5;
warp_1=`shader_body
warp_2=`{
warp_3=`ret=0;
warp_4=`}
comp_1=`shader_body
comp_2=`{
comp_3=`ret=tex2D(sampler_main,uv).rgb;
comp_4=`}
""")

def run(args):
    w,h,ref,worker=args
    info=json.loads((EVIDENCE/f"worker-{worker}.json").read_text())
    cfg=Config(width=w,height=h,fps=30,warmup_seconds=4,measurement_seconds=4,
               line_reference_width=ref[0],line_reference_height=ref[1])
    job=JobSpec(PresetRecord(name,"",0),"kernel-proof",signal(4),cfg,EngineIdentity(**info["identity"]),
                root,REPO/"core/src/main/assets/textures",SCRATCH/"probe-jobs")
    saved=None
    def observe(frame):
        nonlocal saved
        saved=frame
    result=render_job(Path(info["exe"]),job,observe,1800)
    assert result.status=="success",Path(result.diagnostics_path).read_text()
    weights=saved.mean(axis=2).astype(np.float64)
    total=weights.sum();assert total>0,(args,result.diagnostics_path)
    xs=np.arange(w);ys=np.arange(h)
    wx=weights.sum(axis=0);wy=weights.sum(axis=1)
    mx=float(wx@xs/total);my=float(wy@ys/total)
    vx=float(wx@((xs-mx)**2)/total);vy=float(wy@((ys-my)**2)/total)
    cov=float(((weights*(xs-mx)[None,:]).sum(axis=1)@(ys-my))/total)
    return {"worker":worker,"size":[w,h],"reference":ref,"mass":float(total),
            "identity":info["identity"],
            "mean":[mx,my],"variance":[vx,vy],"covariance":cov,
            "sha256":hashlib.sha256(saved).hexdigest(),"diagnostics":str(result.diagnostics_path)}

sizes=[(1920,1080,(1024,768)),(2364,1330,(1024,768)),(2560,1440,(1024,768)),
       (3840,2160,(1024,768)),(1024,768,(1024,768)),(1920,1080,(128,96))]
with ThreadPoolExecutor(max_workers=3) as pool:
    rows=list(pool.map(run,[(w,h,ref,worker) for w,h,ref in sizes for worker in ["baseline",CANDIDATE]]))
proof=[]
for w,h,ref in sizes:
    a,b=[r for r in rows if r["size"]==[w,h] and r["reference"]==ref]
    wanted=min(1.9,max(0,(w*h/(ref[0]*ref[1])-1)/6))
    delta=[b["variance"][i]-a["variance"][i] for i in [0,1]]
    row={"size":[w,h],"reference":ref,"expected_variance":wanted,"measured_added_variance":delta,
         "centroid_delta":[b["mean"][i]-a["mean"][i] for i in [0,1]],
         "covariance_delta":b["covariance"]-a["covariance"],"mass_ratio":b["mass"]/a["mass"],
         "baseline":a,"candidate":b}
    proof.append(row)
(EVIDENCE/f"gpu-impulse-proof-{CANDIDATE}.json").write_text(json.dumps(proof,indent=2)+"\n")
for row in proof:
    print({k:v for k,v in row.items() if k not in ["baseline","candidate"]},flush=True)
    assert max(abs(v-row["expected_variance"]) for v in row["measured_added_variance"])<.025,row
    assert max(abs(v) for v in row["centroid_delta"])<.025,row
    assert abs(row["covariance_delta"])<.025,row
    if row["expected_variance"]==0:assert row["baseline"]["sha256"]==row["candidate"]["sha256"]
