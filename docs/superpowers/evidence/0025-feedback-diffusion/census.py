"""Recompute idiom counts from current assets, then select fixed-seed held-out sets."""
import hashlib
import json
import random
import re
from pathlib import Path
from measure import EVIDENCE, REPO

SEED=20261003

def keys(text):
    result={}
    for line in text.splitlines():
        if "=" not in line:continue
        key,value=line.split("=",1)
        result.setdefault(key.strip().lower(),value.lstrip("`"))
    return result

def shader(values,section):
    lines=[(int(k.rsplit("_",1)[1]),v) for k,v in values.items() if re.fullmatch(section+r"_[0-9]+",k)]
    # Preset shader lines are assembled in numbered order; duplicate keys retain their first value.
    code="\n".join(value for _,value in sorted(lines))
    return re.sub(r"//[^\n]*|/\*.*?\*/","",code,flags=re.S)

census={"seed":SEED,"total":0,"royal191_form":[],"gradient_advection":[],"asset_sha256":{}}
for file in sorted((REPO/"core/src/main/assets/presets").glob("*.milk")):
    census["total"]+=1
    data=file.read_bytes()
    values=keys(data.decode(errors="replace"));w=shader(values,"warp")
    if re.search(r"\bfloat\s+\w+\s*=\s*texsize\s*\.\s*zw\b",w,re.I):
        census["royal191_form"].append(file.name)
    taps=re.search(r"GetBlur\d\s*\(\s*uv\w*\s*[+-][^;]*\)\s*-\s*GetBlur\d\s*\(\s*uv",w) or re.search(r"(GetBlur\d|tex2D\s*\(\s*sampler_blur\d)\s*\([^;]*texsize\.zw",w)
    adv=re.search(r"(GetPixel|tex2D\s*\(\s*sampler_(main|fw_main|fc_main|pw_main|pc_main))\s*\(\s*(uv\w*\s*[+-]|\w+\s*\))",w)
    if taps and adv and "texsize" in w:census["gradient_advection"].append(file.name)
    census["asset_sha256"][file.name]=hashlib.sha256(data).hexdigest()
rng=random.Random(SEED)
for category,n in [("royal191_form",20),("gradient_advection",40)]:
    chosen=sorted(rng.sample(census[category],n))
    census[category+"_sample"]=chosen
    (EVIDENCE/(category+".txt")).write_text("\n".join(chosen)+"\n")
(EVIDENCE/"census.json").write_text(json.dumps(census,indent=2)+"\n")
print({k:len(v) if isinstance(v,list) else v for k,v in census.items() if k!="asset_sha256"})
