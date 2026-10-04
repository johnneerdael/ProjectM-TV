"""metrics.py LABEL... : luma ratio / MAE(1182 area) / contrast / laplacian vs classic, per preset."""
import json, sys
from pathlib import Path
import cv2, numpy as np
D = Path(__file__).resolve().parent
NAMES = ['Royal191', 'Fed quadtrail', 'astral nz+', 'Mandelverse', 'Acid Mandala', 'Royal255', 'FedNoBlur', 'FedNoWave', 'R191a', 'R191b']
PICKS = [120, 150, 180, 210, 239, 300, 390, 479]
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
def frame(run, f):
    m = json.loads((D / 'runs' / run / 'manifest.json').read_text())
    img = np.fromfile(D / 'runs' / run / 'captures' / f'frame-{f}.rgb', dtype=np.uint8).reshape(m['height'], m['width'], 3).astype(np.float32) / 255
    if SUB and m['width'] == 3546: return img[1::3, 1::3]
    return cv2.resize(img, (1182, 665), interpolation=cv2.INTER_AREA if m['width'] > 1182 else cv2.INTER_LINEAR) if m['width'] != 1182 else img
import os
SUB = os.environ.get('SUB') == '1'
res = {}
for label in sys.argv[1:]:
    for i, name in enumerate(NAMES):
        if not (D / 'runs' / f'p{i}-{label}' / 'manifest.json').exists() or not (D / 'runs' / f'p{i}-classic' / 'manifest.json').exists(): continue
        cl = [frame(f'p{i}-classic', f) for f in PICKS]; im = [frame(f'p{i}-{label}', f) for f in PICKS]
        cll = np.mean([(x @ LUMA).mean() for x in cl]); l = np.mean([(x @ LUMA).mean() for x in im])
        mae = np.mean([np.abs(a - b).mean() for a, b in zip(im, cl)])
        con = np.mean([(x @ LUMA).std() for x in im]); clc = np.mean([(x @ LUMA).std() for x in cl])
        res[f'{name}/{label}'] = dict(luma_ratio=float(l / cll), mae=float(mae), contrast=float(con), classic_contrast=float(clc))
        print(f'{name:14} {label:14} ratio {l/cll:7.3f}  MAE {mae:.4f}  contrast {con:.4f} (classic {clc:.4f})')
(D / f'metrics-{"_".join(sys.argv[1:])[:80]}.json').write_text(json.dumps(res, indent=1))
