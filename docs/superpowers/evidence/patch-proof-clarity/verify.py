"""Check published RGB, independent repeats, matched crops and source deltas."""
import hashlib
import html
import json
import re
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'patch-visual-catalog'))
from guide_bindings import Fragment

EXPECTED_PAIRS={('escape','0028'),('crush','0021'),('carnival','0021'),
                ('swirl','0023'),('nebula','0030'),('city-alt','0032'),('salad','0033')}
FROZEN_RECEIPT_SHA256='d6bbf19c6d02434168b290e8ea24d0d9b0877b40fd8a87e7dda179f035b5bd42'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    evidence=Path(__file__).resolve().parent
    repo=evidence.parents[3]
    gallery=json.loads((evidence/'gallery.json').read_text())
    assert len(gallery)==len(EXPECTED_PAIRS)
    assert {(pair['name'],pair['patch']) for pair in gallery}==EXPECTED_PAIRS
    workers=json.loads((evidence/'workers.json').read_text())
    frozen={'workers':workers,'captures':[{key:p[key] for key in ('name','patch','frame','inputs')}|
            {'roles':{role:{key:r[key] for key in ('identity_ref','asset_sha256','rgb_sha256','runs')}
                      for role,r in p['roles'].items()}} for p in gallery]}
    assert sha(json.dumps(frozen,sort_keys=True,separators=(',',':'),allow_nan=False).encode())==FROZEN_RECEIPT_SHA256
    full=json.loads((repo/'docs/superpowers/evidence/patch-visual-catalog/patched-source-tree.json').read_text())
    assert workers['full']['source_tree']==full
    allowed={'0021':{'CustomWaveform.cpp','PerPixelContext.cpp','WaveformPerPointContext.cpp','WaveformPerPointContext.hpp'},
             '0023':{'MilkdropStaticShaders.cpp.in'},'0028':{'Border.cpp'},'0030':{'CustomWaveform.cpp'},
             '0032':{'CustomShape.cpp','CustomShape.hpp'},'0033':{'MilkdropPreset.cpp'}}
    for role,worker in workers.items():
        if role=='full':continue
        patch=role.removeprefix('without-')
        delta={name for name in full.keys() | worker['source_tree'].keys()
               if full.get(name)!=worker['source_tree'].get(name)}
        assert delta==set(worker['source_delta'])
        production={Path(name).name for name in delta if not name.endswith('.orig')}
        assert production==allowed[patch],(role,production)
        for name in delta:
            if name.endswith('.orig'):assert worker['source_tree'][name]==full[name.removesuffix('.orig')]
        recorded=worker['reversed_patch']
        assert sha((repo/'tools/projectm-patches'/recorded['name']).read_bytes())==recorded['sha256']
        with tempfile.TemporaryDirectory(prefix='patch-proof-source-') as folder:
            temporary=Path(folder)
            for name in delta:
                if name.endswith('.orig'):continue
                original=evidence/'source-deltas/full'/name
                candidate=evidence/'source-deltas'/role/name
                assert sha(original.read_bytes())==full[name]
                assert sha(candidate.read_bytes())==worker['source_tree'][name]
                target=temporary/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(original,target)
            if patch=='0023':
                getter=temporary/'src/libprojectM/MilkdropPreset/MilkdropStaticShaders.cpp.in'
                content=getter.read_text();assert content.count('#define PROJECTM_LEGACY_WARP\\n')==1
                getter.write_text(content.replace('#define PROJECTM_LEGACY_WARP\\n',''))
            else:
                subprocess.run(['patch','-p1','-R','-i',str(repo/'tools/projectm-patches'/recorded['name'])],
                               cwd=temporary,check=True,capture_output=True)
            for name in delta:
                if not name.endswith('.orig'):
                    assert sha((temporary/name).read_bytes())==worker['source_tree'][name],role
    textures=repo/'core/src/main/assets/textures'
    observed_textures={p.relative_to(textures).as_posix():sha(p.read_bytes()) for p in sorted(textures.rglob('*')) if p.is_file()}
    css=(repo/'docs/user-guide/stylesheets/projectm.css').read_text()
    assert 'aspect-ratio: 16 / 9;' in css
    guide=(repo/'docs/user-guide/engine/patches.md').read_text()
    actual=re.findall(r'<figure class="patch-comparison patch-causal".*?</figure>\n',guide,re.S)
    assert len(actual)==len(gallery)
    for pair in gallery:
        assert pair['figure_html'] in actual,pair['name']
        assert pair['inputs']['texture_inventory']==observed_textures
        expected_roles={'full','without-'+pair['patch']}
        assert set(pair['roles'])==expected_roles
        assert expected_roles<=workers.keys()
        x,y,w,h=pair['crop'];assert 0<=x<x+w<=3840 and 0<=y<y+h<=2160
        figure=Fragment(pair['figure_html']).root
        assert f"<strong>{html.escape(pair['preset'])}</strong>" in pair['figure_html']
        panels=list(figure.nodes('div','patch-panel'))
        assert len(panels)==4
        for index,panel in enumerate(panels):
            role=('without-'+pair['patch'],'full')[index%2]
            label='Only '+pair['patch']+' disabled' if index%2==0 else 'ProjectM TV · fix enabled'
            strong,links,images=(list(panel.nodes(tag)) for tag in ('strong','a','img'))
            assert len(strong)==len(links)==len(images)==1
            assert strong[0].text()==label
            original=f"../../images/patches/clarity/{pair['name']}-{role}.png"
            assert links[0].attrs['href']==original
            assert images[0].attrs['src']==(original.removesuffix('.png')+'-crop.png' if index<2 else original)
            assert (images[0].attrs['width'],images[0].attrs['height'])==tuple(map(str,(w,h) if index<2 else (3840,2160)))
            assert all('style' not in node.attrs for node in [panel,*panel.nodes()])
        for role,record in pair['roles'].items():
            assert record['identity_ref']==role
            path=repo/'docs/user-guide/images/patches/clarity'/f"{pair['name']}-{role}.png"
            assert sha(path.read_bytes())==record['asset_sha256']
            image=Image.open(path);assert image.mode=='RGB' and image.size==(3840,2160)
            assert sha(image.tobytes())==record['rgb_sha256']
            closeup=path.with_name(path.stem+'-crop.png')
            assert sha(closeup.read_bytes())==record['crop_sha256']
            crop=Image.open(closeup)
            assert crop.size==(w,h) and crop.mode=='RGB'
            assert crop.tobytes()==image.crop((x,y,x+w,y+h)).tobytes()
            sequences=[]
            for run in record['runs']:
                request=run['request'];result=run['result'];manifest=result['manifest'];cfg=request['config']
                assert cfg==manifest['config']
                assert cfg['width']==3840 and cfg['height']==2160 and cfg['fps']==30 and cfg['seed']==12345
                assert cfg['line_reference_width']==1280 and cfg['line_reference_height']==720
                assert cfg['line_antialiasing'] is True and cfg['feedback_detail']==0
                assert request['identity']==manifest['identity']=={'worker_ref':role}
                assert manifest['status']=='success' and manifest['gl_error_frames']==0
                assert manifest['frames']==cfg['measurement_seconds']*30
                selected=cfg['selected_frames']
                assert selected==sorted(set(selected))
                assert all(type(frame) is int and 0<=frame<manifest['frames'] for frame in selected)
                assert set(result['rgb_sha256'])=={str(frame) for frame in selected}
                states=manifest['readback_states']
                assert len(states)==len(selected)
                assert [state['frame'] for state in states]==selected
                preset=Path(request['preset_path']).name
                assert preset==pair['preset']
                assert sha((repo/'core/src/main/assets/presets'/preset).read_bytes())==pair['inputs']['preset_sha256']
                assert sha((repo/'docs/superpowers/evidence/patch-visual-catalog/audio'/Path(request['pcm_path']).name).read_bytes())==pair['inputs']['pcm_sha256']
                for state in states:
                    for key in ('read_framebuffer','read_buffer','pack_alignment'):
                        assert state['before_'+key]==state['after_'+key]
                sequences.append(result['rgb_sha256'])
                assert result['rgb_sha256'][str(pair['frame'])]==record['rgb_sha256']
            assert len(sequences)==2 and sequences[0]==sequences[1]
    print(f'PASS: {len(gallery)} real-preset pairs; unchanged RGB, independent repeats, controls, source deltas and guide bindings')


if __name__=='__main__':main()
