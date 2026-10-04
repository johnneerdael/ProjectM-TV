"""Summarize final workers only; keep distinct sets, windows and hardware cohorts."""
import csv
import json
import statistics
import sys
from pathlib import Path
from fidelity import report

E=Path(__file__).resolve().parent
CANDIDATE=sys.argv[1] if len(sys.argv)>1 else "production"
controls=set((E/"control18.txt").read_text().splitlines())
for seconds in [4,12]:
    path=E/f"set24-{CANDIDATE}-{seconds}s-raw.json"
    if path.exists():
        subset=[r for r in json.loads(path.read_text()) if r["preset"] in controls]
        assert len({r["preset"] for r in subset})==18
        (E/f"control18-{CANDIDATE}-{seconds}s-report.json").write_text(json.dumps(report(subset),indent=2)+"\n")

rows=[]
details=[]
pending=[]
for seconds in [4,12]:
    noise_path=E/f"noise-{CANDIDATE}-{seconds}s-report.json"
    expanded=E/f"noise-{CANDIDATE}-expanded-{seconds}s-report.json"
    if expanded.exists():noise_path=expanded
    noise=json.loads(noise_path.read_text())["presets"] if noise_path.exists() else {}
    for dataset in ["set24","control18","royal191","gradient","regressions"]:
        path=E/f"{dataset}-{CANDIDATE}-{seconds}s-report.json"
        if not path.exists():pending.append(path.name);continue
        d=json.loads(path.read_text())
        for height in [1330,2160]:
            a=d["summary"][f"baseline-{height}"];b=d["summary"][f"{CANDIDATE}-{height}"]
            row={"set":dataset,"window_s":seconds,"height":height,"rendered":len(d["presets"]),
                 "deterministic":a["n"],"baseline_median_err":a["median_img_err"],
                 "production_median_err":b["median_img_err"],"baseline_luma_within10":a["luma_within10"],
                 "production_luma_within10":b["luma_within10"],"worse_beyond_size_noise":[],"noise_pending":[]}
            for name,p in d["presets"].items():
                runs=p["runs"]
                repeated_stable=all(runs[k]["sha256"]==runs[k+"-repeat"]["sha256"]
                                   for k in [f"baseline-{height}",f"{CANDIDATE}-{height}"])
                if not p["authored_deterministic"] or not repeated_stable:continue
                x,y=runs[f"baseline-{height}"],runs[f"{CANDIDATE}-{height}"]
                band=p["size_band_noise"] or noise.get(name,{}).get("size_band_noise",[])
                delta=y["img_err"]-x["img_err"]
                if delta>1e-4:
                    if not band:row["noise_pending"].append(name)
                    elif delta>max(band)+1e-4:row["worse_beyond_size_noise"].append(name)
                details.append({"set":dataset,"window_s":seconds,"height":height,"preset":name,
                                "img_err_before":x["img_err"],"img_err_after":y["img_err"],
                                "img_err_delta":delta,"size_band_max":max(band) if band else None,
                                **{f"{metric}_{side}":run[metric] for metric in ["luma_ratio","saturation","lap_native","lap_1182"]
                                   for side,run in [("before",x),("after",y)]},
                                "centre_rgb_before":x["centre_rgb"],"centre_rgb_after":y["centre_rgb"]})
            rows.append(row)
(E/f"{CANDIDATE}-summary.json").write_text(json.dumps({"candidate":CANDIDATE,"rows":rows,"pending_reports":pending},indent=2)+"\n")
if details:
    with (E/f"{CANDIDATE}-per-preset.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(details[0]));writer.writeheader();writer.writerows(details)
for row in rows:
    print(row["set"],row["window_s"],row["height"],row["deterministic"],
          round(row["baseline_median_err"],4),"->",round(row["production_median_err"],4),
          "beyond noise",row["worse_beyond_size_noise"],"noise pending",row["noise_pending"])
print("Pending reports:",pending)
