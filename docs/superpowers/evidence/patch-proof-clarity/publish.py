"""Select unchanged lossless frames and bind matched close-ups to their receipts."""
import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path
from PIL import Image

PAIRS = [
    ('escape', '0028', 0, [1400,650,1100,750],
     'The crossed border bands now have the original strip-fan coverage. In the left image, one side pinches into a diagonal; the right retains the matching band around the centre. This is an unchanged bundled preset, not a synthetic shape.'),
    ('crush', '0021', 239, [1600,600,1100,1050],
     'The central glow separates into readable loops on the right. The old input stretches the feedback differently; the fix restores the aspect compensation used by the preset.'),
    ('carnival', '0021', 239, [1250,650,1100,1000],
     'Look at the fine coloured pattern across the centre. Custom-wave colours follow their own host clock rather than inheriting the slowed main-equation clock.'),
    ('swirl', '0023', 239, [1200,500,1200,1300],
     'The central spiral builds a denser curl with distinct strands on the right. Restoring the original oscillator direction changes how the existing strokes accumulate; their authored warp strength and draw count stay the same.'),
    ('nebula', '0030', 0, [2560,768,128,128],
     'Three purple/white authored dots remain in both panels. The extra green/grey dots on the left disappear: they were invented by line interpolation. Dot mode now preserves the preset\'s discrete star positions.'),
    ('city-alt', '0032', 0, [768,128,64,64],
     'The white corner has a fuller, continuous outline on the right. This preset asks four overlay instances to become thick; previously their live thickness was ignored.'),
    ('salad', '0033', 209, [1200,400,1200,1200],
     'A real beat-gated preset: the returned vectors inject strokes using the latest completed distortion. The coloured rings develop differently instead of continuing from an older hidden-frame motion field. This frame shows the accumulated effect, not a promise of extra sharpness in every preset.'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def figure(pair, preset):
    name, patch, frame, crop, caption = pair
    x,y,w,h = crop
    rows=[]
    for zoom in (True, False):
        panels=[]
        for role in ('without-' + patch, 'full'):
            label = f'Only {patch} disabled' if role != 'full' else 'ProjectM TV · fix enabled'
            url=f'../../images/patches/clarity/{name}-{role}.png'
            image_url=f'../../images/patches/clarity/{name}-{role}-crop.png' if zoom else url
            size = f' width="{w}" height="{h}" class="patch-detail"' if zoom else ' width="3840" height="2160"'
            panels.append(f'<div class="patch-panel"><strong>{label}</strong><a href="{url}" aria-label="Open unchanged 4K {html.escape(name)} frame, {label}"><img src="{image_url}" alt="{html.escape(name)}: {label}, {"matched close-up" if zoom else "full frame"}"{size} loading="lazy"></a></div>')
        rows.append('<div class="patch-panels">'+'\n'.join(panels)+'</div>')
    return ('<figure class="patch-comparison patch-causal" data-witness="'+name+'">\n'+rows[0]+
            f'\n<figcaption><strong>{html.escape(preset)}</strong><br>{html.escape(caption)}<br>Native 3840×2160, frame {frame}; matched {w}×{h} pixel crop at ({x}, {y}). Click either close-up for its original 4K frame. No exposure or colour adjustment.</figcaption>\n'+
            '<details><summary>See both full 4K frames</summary>\n'+rows[1]+'\n</details>\n</figure>\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    args=p.parse_args()
    evidence=args.repo/'docs/superpowers/evidence/patch-proof-clarity'
    assets=args.repo/'docs/user-guide/images/patches/clarity'
    assets.mkdir(parents=True,exist_ok=True)
    records=[]
    workers={}
    for pair in PAIRS:
        name,patch,frame,crop,caption=pair
        capture=args.work/'captures'/name
        comparison=json.loads((capture/'comparison.json').read_text())
        record={'name':name,'patch':patch,'frame':frame,'crop':crop,'caption':caption,
                'inputs':comparison['inputs'],'roles':{}}
        for role in ('without-'+patch,'full'):
            identity=comparison['roles'][role]['identity']
            if role in workers and workers[role]!=identity:
                raise ValueError('Conflicting frozen worker identity: '+role)
            workers[role]=identity
            run=capture/f'{role}-0'
            path=run/f'frame-{frame:03d}.png'
            image=Image.open(path).convert('RGB')
            hashes=comparison['roles'][role]['rgb_sha256']
            if sha(image.tobytes())!=hashes[str(frame)]:raise ValueError('selected RGB mismatch')
            asset=assets/f'{name}-{role}.png'
            shutil.copyfile(path,asset)
            x,y,w,h=crop
            closeup=assets/f'{name}-{role}-crop.png'
            image.crop((x,y,x+w,y+h)).save(closeup)
            record['roles'][role]={'asset_sha256':sha(asset.read_bytes()),'rgb_sha256':hashes[str(frame)],'crop_sha256':sha(closeup.read_bytes()),
                'identity_ref':role,'runs':[]}
            for repeat in range(2):
                run=capture/f'{role}-{repeat}'
                request=json.loads((run/'job.json').read_text())
                result=json.loads((run/'result.json').read_text())
                assert request['identity']==workers[role] and result['manifest']['identity']==workers[role]
                request['identity']={'worker_ref':role}
                result['manifest']['identity']={'worker_ref':role}
                record['roles'][role]['runs'].append({'request':request,'result':result})
        record['preset']=Path(record['roles']['full']['runs'][0]['request']['preset_path']).name
        record['figure_html']=figure(pair, record['preset'])
        records.append(record)
    for role, identity in workers.items():
        if role=='full':continue
        for name in identity['source_delta']:
            if name.endswith('.orig'):continue
            for side, source in [('full',args.work/'full/source'),(role,args.work/role/'source')]:
                target=evidence/'source-deltas'/side/name
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source/name,target)
    write(evidence/'workers.json',workers)
    write(evidence/'gallery.json',records)
    (evidence/'figures.html').write_text('\n'.join(record['figure_html'] for record in records))
    print(len(records),'pairs selected without changing PNG pixels')


if __name__ == '__main__':
    main()
