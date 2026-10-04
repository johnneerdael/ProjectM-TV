"""GL feedback proof that an active reference-size change refreshes the cached input."""
import json, shutil, sys
from pathlib import Path
from dataclasses import dataclass, asdict
import numpy as np
import preset_lab.build_worker as builder
from preset_lab.bass_screen import bass_signals
from preset_lab.models import JobSpec, PresetRecord, EngineIdentity, RunConfig
from preset_lab.worker import render_job
from measure import REPO, EVIDENCE, SCRATCH

label=sys.argv[1]
native=SCRATCH/("native-cache-"+label);shutil.copytree(builder.NATIVE,native,dirs_exist_ok=True)
p=native/"worker.cpp";t=p.read_text();needle="            engine.RenderFrame(capture.framebuffer);"
t=t.replace(needle, """            if (frame == 4) engine.SetLineReferenceSize(512, 384);
"""+needle);p.write_text(t);builder.NATIVE=native
repo=SCRATCH/("repo-cache-"+label);patches=repo/"tools/projectm-patches";patches.mkdir(parents=True,exist_ok=True)
(repo/"third_party").mkdir(exist_ok=True)
if not (repo/"third_party/projectm").exists():(repo/"third_party/projectm").symlink_to(REPO/"third_party/projectm",target_is_directory=True)
for source in sorted((REPO/"tools/projectm-patches").glob("*.patch")):
 text=source.read_text()
 if label=="red" and source.name.startswith("0025-"):
  text=text.replace('+        m_diffusionHoldsPreviousFrame = false;\n+    }\n+\n     m_framebuffer.Bind', '+        /* simulate missing scale-change invalidation */\n+    }\n+\n     m_framebuffer.Bind')
  # Target only the newly inserted invalidation adjacent to the scale setter.
  marker='+    if (m_feedbackDiffusion.SetScale'
  start=text.index(marker);end=text.index('     m_framebuffer.Bind',start)
  block=text[start:end].replace('+        m_diffusionHoldsPreviousFrame = false;','+        /* old cache incorrectly remains valid */')
  text=text[:start]+block+text[end:]
 (patches/source.name).write_text(text)
work=SCRATCH/("work-cache-"+label);exe=builder.build_worker(repo,work);_,identity=builder.prepare_engine(repo,work)
root=EVIDENCE/"cache-probe";root.mkdir(exist_ok=True)
# One pulse, then linear identity feedback: variance changes are observable without time/chaos.
preset=(EVIDENCE/"probes/kernel-impulse.milk").read_text().replace('fDecay=0','fDecay=1').replace('ret=0;','ret=GetPixel(uv);')
preset += "wave_0_per_frame1=a=if(above(frame,1),0,1);\n"
(root/"pulse.milk").write_text(preset)
@dataclass(frozen=True,slots=True)
class Config(RunConfig):
 line_reference_width:int=1024
 line_reference_height:int=768
cfg=Config(width=1920,height=1080,fps=30,warmup_seconds=0,measurement_seconds=8/30)
pcm=bass_signals(cfg,SCRATCH/("cache-signal-"+label))["bass-0.30"]
job=JobSpec(PresetRecord("pulse.milk","",0),"cache",pcm,cfg,identity,root,REPO/"core/src/main/assets/textures",SCRATCH/"cache-jobs")
values=[]
def observe(frame):
 weights=frame.mean(axis=2).astype(np.float64);total=weights.sum();assert total>0
 xs=np.arange(cfg.width);ys=np.arange(cfg.height);wx=weights.sum(0);wy=weights.sum(1)
 mx=wx@xs/total;my=wy@ys/total
 values.append([float(wx@((xs-mx)**2)/total),float(wy@((ys-my)**2)/total)])
result=render_job(exe,job,observe,1800)
assert result.status=="success",Path(result.diagnostics_path).read_text()
old=(1920*1080/(1024*768)-1)/6;new=(1920*1080/(512*384)-1)/6
expected=2*new-old
delta=[values[4][i]-values[3][i] for i in [0,1]]
proof={"label":label,"variances":values,"expected_switch_delta":expected,"actual_switch_delta":delta}
(EVIDENCE/("cache-reference-"+label+".json")).write_text(json.dumps(proof,indent=2)+"\n")
print(proof,flush=True)
# Repeated RGBA8 feedback quantizes a sparse pulse; the stale-cache deficit is ~1.32 px².
# This tolerance accommodates the measured quantization while rejecting the old path decisively.
assert max(abs(x-expected) for x in delta)<.20,proof
