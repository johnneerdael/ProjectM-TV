import json, sys, numpy as np, cv2
from pathlib import Path
D=Path('.')
def frame(run,f):
    m=json.loads((D/'runs'/run/'manifest.json').read_text())
    img=np.fromfile(D/'runs'/run/'captures'/f'frame-{f}.rgb',dtype=np.uint8).reshape(m['height'],m['width'],3).astype(np.float32)/255
    return cv2.resize(img,(1182,665),interpolation=cv2.INTER_AREA) if m['width']!=1182 else img
p,gain,f=int(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]); runs=sys.argv[4:]
tiles=[]
for run in runs:
    im=(np.clip(frame(f'p{p}-{run}',f)*gain,0,1)*255).astype(np.uint8)
    cv2.putText(im,run,(10,40),cv2.FONT_HERSHEY_SIMPLEX,1.2,(255,255,255),2); tiles.append(im)
while len(tiles)%2: tiles.append(np.zeros_like(tiles[0]))
grid=np.vstack([np.hstack(tiles[i:i+2]) for i in range(0,len(tiles),2)])
out=f'png/p{p}-f{f}-{"_".join(runs)}.png'; cv2.imwrite(out,grid[:,:,::-1]); print(out)
