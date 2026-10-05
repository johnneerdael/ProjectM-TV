from pathlib import Path
import json
root=Path(__file__).resolve().parent
report={}
for preset in ("waltra","hex"):
    result={}
    for frame in (0,1,2,3,11):
        stages={}
        for suffix in ("q.bin","shader-rng.bin","shape0.bin","input.rgb","warp.rgb","blur1.rgb","blur2.rgb","blur3.rgb","geometry.rgb","state.rgb"):
            paths=[root/"gles"/preset/profile/(f"{frame:03d}-"+suffix) for profile in ("authored","standard")]
            if not all(p.exists() for p in paths): stages[suffix]={"missing":True};continue
            a,b=[p.read_bytes() for p in paths]
            value={"exact":a==b,"bytes":len(a),"candidate_bytes":len(b)}
            if suffix.endswith("rgb") and len(a)==len(b):
                differences=[abs(x-y) for x,y in zip(a,b)] if a!=b else []
                value.update(mae_bytes=sum(differences)/len(a),max_bytes=max(differences,default=0),different_bytes=sum(v!=0 for v in differences))
            stages[suffix]=value
        result[str(frame)]=stages
    report[preset]=result
(root/"gles-stage-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
