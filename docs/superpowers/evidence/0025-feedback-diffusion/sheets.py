"""Measured comparison sheets: middle frame only; captions use five-frame MAE."""
import json
import sys
import textwrap
from pathlib import Path
import cv2
import numpy as np

E=Path(__file__).resolve().parent
CANDIDATE=sys.argv[1] if len(sys.argv)>1 else "production"
presets={}
for name in ["set24","regressions","noise"]:
    presets.update(json.loads((E/f"{name}-{CANDIDATE}-4s-report.json").read_text())["presets"])

def sheet(filename,title,names):
    width=540;image_height=304;row_height=405
    canvas=np.full((90+len(names)*row_height,width*3,3),24,np.uint8)
    def text(value,x,y,scale=.58):
        cv2.putText(canvas,value,(x,y),cv2.FONT_HERSHEY_SIMPLEX,scale,(235,235,235),1,cv2.LINE_AA)
    text(title,15,30,.72)
    text("Middle frame of a 4 s window after 4 s warm-up; bass-0.30, 30 fps, fixed seed.",15,56)
    for row,name in enumerate(names):
        p=presets[name];y=90+row*row_height
        for i,line in enumerate(textwrap.wrap(name.removesuffix('.milk'),width=115)):
            text(line,15,y+18+i*20,.6)
        for col,(label,key) in enumerate([("Classic 1182x665","authored"),("Native 3840x2160, off","baseline-2160"),("Native 3840x2160, on",f"{CANDIDATE}-2160")]):
            r=p["runs"][key]
            frame=cv2.imread(str(Path(r["output"])/"frame-2.png"));assert frame is not None
            frame=cv2.resize(frame,(width-12,image_height),interpolation=cv2.INTER_AREA)
            x=col*width+6;canvas[y+60:y+60+image_height,x:x+width-12]=frame
            text(label,x+5,y+53)
            text(f"5-frame MAE {r['img_err']:.4f}; mean luma ratio {r['luma_ratio']:.3f}",x+5,y+385,.5)
    path=E/(CANDIDATE+"-"+filename)
    assert cv2.imwrite(str(path),canvas)
    print(path)

sheet("native-feedback.png","Feedback compensation and coupled vector minimum",[
 "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk",
 "$$$ Royal - Mashup (191).milk",
 "suksma - penattrition - geiss crossfire shaders nz+.milk",
 "$$$ Royal - Mashup (103).milk"])
sheet("gated-feedback.png","Conservative shader gate preserves the existing native path",[
 "rce-ordinary - want.milk",
 "TonyMilkdrop - Nuclear [Flexi - help out + alien complex].milk",
 "Flexi + Rovastar + suksma - Fractopia [sth].milk"])
