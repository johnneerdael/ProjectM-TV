"""Measure named fidelity sets with repetition and per-preset size-band controls."""
import argparse
import json
import statistics
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cv2
import numpy as np
from measure import EVIDENCE, measure

REGRESSIONS=["TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk",
 "suksma - penattrition - geiss crossfire shaders nz+.milk", "$$$ Royal - Mashup (103).milk",
 "rce-ordinary - want.milk", "TonyMilkdrop - Nuclear [Flexi - help out + alien complex].milk"]

def image_error(a,b):
    errors=[]
    for i in range(5):
        x=cv2.imread(str(Path(a["output"])/f"frame-{i}.png"))
        y=cv2.imread(str(Path(b["output"])/f"frame-{i}.png"))
        assert x is not None and y is not None
        errors.append(float(np.abs(x.astype(np.int16)-y.astype(np.int16)).mean()/255))
    return float(np.mean(errors))

def report(results):
    grouped={}
    for r in results:grouped.setdefault(r["preset"],{})[r["label"]]=r
    output={"presets":{},"summary":{}}
    for preset,runs in grouped.items():
        ground=runs["authored"]
        row={}
        for label,r in runs.items():
            row[label]={k:r[k] for k in ["status","sha256","config","identity","output"]}
            if r["status"]=="success" and ground["status"]=="success":
                row[label].update(img_err=image_error(r,ground),luma=r["luma"],
                    luma_ratio=r["luma"]/ground["luma"] if ground["luma"]>.001 else None,
                    centre_rgb=r["centre_rgb"],saturation=r["saturation"],
                    lap_native=r["lap_native"],lap_1182=r["lap_1182"])
        deterministic=(runs.get("authored-repeat",ground)["sha256"]==ground["sha256"])
        noise=[r["img_err"] for label,r in row.items() if label.startswith("noise-") and "img_err" in r]
        output["presets"][preset]={"authored_deterministic":deterministic,"size_band_noise":noise,"runs":row}
    labels=sorted({label for row in output["presets"].values() for label in row["runs"]})
    for label in labels:
        rows=[p["runs"][label] for p in output["presets"].values() if p["authored_deterministic"]
              and label in p["runs"] and "img_err" in p["runs"][label]]
        if rows:
            ratios=[r["luma_ratio"] for r in rows if r["luma_ratio"] is not None]
            output["summary"][label]={"n":len(rows),"mean_img_err":statistics.mean(r["img_err"] for r in rows),
                "median_img_err":statistics.median(r["img_err"] for r in rows),
                "luma_within10":sum(abs(r-1)<=.1 for r in ratios)}
    return output

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--set",default="set24")
    parser.add_argument("--label")
    parser.add_argument("--seconds",type=int,default=4)
    parser.add_argument("--workers",default="baseline,p1,p2")
    parser.add_argument("--concurrency",type=int,default=4)
    parser.add_argument("--noise",action="store_true")
    parser.add_argument("--repeat-all",action="store_true")
    args=parser.parse_args()
    names=REGRESSIONS if args.set=="regressions" else (EVIDENCE/f"{args.set}.txt").read_text().splitlines()
    specs=[("authored","baseline",1182,665,(0,0),0), ("authored-repeat","baseline",1182,665,(0,0),1)]
    for worker in args.workers.split(","):
        specs += [(worker+"-"+str(h),worker,w,h,(1024,768),0) for w,h in [(2364,1330),(3840,2160)]]
        if args.repeat_all:
            specs += [(worker+"-"+str(h)+"-repeat",worker,w,h,(1024,768),1) for w,h in [(2364,1330),(3840,2160)]]
    jobs=[(name,*spec) for name in names for spec in specs]
    if args.noise:
        for name in names:
            for scale in [.98,.99,1.01,1.02]:
                jobs.append((name,f"noise-{scale}","baseline",round(1182*scale),round(665*scale),(0,0),0))
    def run(job):
        name,label,worker,w,h,ref,rep=job
        result=dict(measure(name,worker,w,h,reference=ref,seconds=args.seconds,repeat=rep))
        result["label"]=label
        print(name[:45],label,result["status"],round(result.get("luma",0),5),flush=True)
        return result
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        results=list(pool.map(run,jobs))
    stem=args.label or f"{args.set}-{args.seconds}s"
    raw=EVIDENCE/f"{stem}-raw.json"
    raw.write_text(json.dumps(results,indent=2)+"\n")
    output=report(results)
    (EVIDENCE/f"{stem}-report.json").write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output["summary"],indent=2),flush=True)
    assert all(r["status"]=="success" for r in results),"Failed renders in raw report"

if __name__=="__main__":main()
