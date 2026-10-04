# Engine fallbacks (macOS desktop GL) before/after, plus a GLES 3.00 compile of each authored translation.
import os, re, subprocess, collections, json
from concurrent.futures import ThreadPoolExecutor
SP = os.path.dirname(os.path.abspath(__file__))
def load(name):
    d = os.path.join(SP, name)
    index = dict(l.rstrip('\n').split('\t', 1) for l in open(os.path.join(d, 'index.tsv')))
    shaders = {}
    for f in os.listdir(d):
        m = re.match(r'(\d+)_(warp|composite)_(\d+)\.hlsl$', f)
        if m:
            key = (index[m.group(1)], m.group(2))
            shaders.setdefault(key, set()).add(int(m.group(3)))
    return d, index, shaders
def gles(dirname, translator):
    d = os.path.join(SP, dirname); out = d + '-glsl'; os.makedirs(out, exist_ok=True)
    files = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith('_0.hlsl'))
    r = subprocess.run([os.path.join(SP, translator), out], input='\n'.join(files) + '\n', capture_output=True, text=True)
    status = dict(m.groups() for m in re.finditer(r'^@@(\S+)\t(\w+)$', r.stdout, re.M))
    def check(base):
        if status.get(base) != 'OK': return base, status.get(base, 'MISSING')
        p = subprocess.run(['glslangValidator', '-S', 'frag', os.path.join(out, base + '.frag')], capture_output=True, text=True)
        return base, 'COMPILES' if p.returncode == 0 else 'REJECTED'
    with ThreadPoolExecutor(12) as ex:
        res = dict(ex.map(check, [os.path.basename(f)[:-5] for f in files]))
    index = dict(l.rstrip('\n').split('\t', 1) for l in open(os.path.join(d, 'index.tsv')))
    return {(index[b.split('_')[0]], b.split('_')[1]): s for b, s in res.items()}
_, _, base = load('dump-base'); _, _, final = load('dump-final')
fb_base = {k for k, v in base.items() if 1 in v}; fb_final = {k for k, v in final.items() if 1 in v}
print('engine (desktop GL) authored shaders', len(base), len(final))
print('fallbacks base', len(fb_base), 'final', len(fb_final))
print('fixed', len(fb_base - fb_final), 'newly falling back', len(fb_final - fb_base))
for k in sorted(fb_final - fb_base): print('  REGRESSION', k)
print('missing in final', len(set(base) - set(final)), 'missing in base', len(set(final) - set(base)))
gb = gles('dump-base', 'translate-old'); gf = gles('dump-final', 'translate-t1')
print('GLES base', collections.Counter(gb.values())); print('GLES final', collections.Counter(gf.values()))
worse = [(k, gb.get(k), gf[k]) for k in gf if gb.get(k) == 'COMPILES' and gf[k] != 'COMPILES']
better = [(k, gb.get(k), gf[k]) for k in gf if gb.get(k) != 'COMPILES' and gf[k] == 'COMPILES']
print('GLES newly compiling', len(better), 'GLES newly failing', len(worse))
for k in worse: print('  GLES REGRESSION', k)
json.dump({'fixed_engine': sorted(map(list, fb_base - fb_final)), 'better': [list(k) for k, _, _ in better],
           'gles_base': {f'{a}|{b}': v for (a, b), v in gb.items()}, 'gles_final': {f'{a}|{b}': v for (a, b), v in gf.items()}},
          open(os.path.join(SP, 'compare_dumps.json'), 'w'))
