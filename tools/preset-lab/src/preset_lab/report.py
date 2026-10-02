from pathlib import Path
from html import escape
import shutil

from .identity import load_json


def write_report(fingerprints: list, decisions: list, destination: Path) -> Path:
    destination.mkdir(parents=True,exist_ok=True)
    catalog=load_json(Path(__file__).parent/"profiles/genres.json")["genres"]
    labels={g["id"]:g["label"] for g in catalog}
    tables=[]
    for genre in catalog:
        rows=[d for d in decisions if d.genre_id==genre["id"]]
        if not rows: continue
        body=[]
        for row in rows:
            state={"predicted":"Predicted","music-tested":"Music-tested","reviewed":"Reviewed"}[row.evidence_state]
            count=row.contributions.get("music_test_count",0)
            body.append(f'<tr><td>{escape(row.preset.path)}</td><td>{row.score:.3f}</td>'
                        f'<td>{row.music_fit:.3f}</td><td>{row.audience_fit:.3f}</td>'
                        f'<td>{state} · {count} checks</td><td>{"Suggested" if row.included else "Excluded"}</td></tr>')
        tables.append(f'<section id="{escape(genre["id"])}"><h2>{escape(genre["label"])}</h2>'
                      '<div class="table-scroll"><table><thead><tr><th>Preset</th><th>Fit</th><th>Music</th>'
                      '<th>Audience</th><th>Evidence</th><th>Decision</th></tr></thead><tbody>'
                      +''.join(body)+'</tbody></table></div></section>')
    previews=[]
    for index,fp in enumerate(fingerprints):
        source=fp.evidence.get("preview_path")
        if source and Path(source).is_file():
            filename=f"preview-{index}.mp4"
            shutil.copyfile(source,destination/filename)
            poster=""
            image=fp.evidence.get("poster_path")
            if image and Path(image).is_file():
                poster_name=f"poster-{index}.png"
                shutil.copyfile(image,destination/poster_name)
                poster=f' poster="{poster_name}"'
            previews.append(f'<article><h3>{escape(fp.preset.path)}</h3>'
                            f'<video controls preload="metadata" src="{filename}"{poster}></video>'
                            '<p class="muted">Synthetic bass probe preview. Genre music checks are separate.</p></article>')
    tested=sum(d.evidence_state in ("music-tested","reviewed") for d in decisions)
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preset Lab — genre suggestions</title><style>
:root{--ink:#192e30;--muted:#556769;--paper:#faf9f5;--accent:#006f6b;--rule:#d7ddda}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:1180px;margin:auto;padding:48px 32px}header{border-bottom:2px solid var(--ink);padding-bottom:28px}
.eyebrow{letter-spacing:.12em;font-size:12px;text-transform:uppercase;color:var(--accent)}h1{font:48px/1.1 Georgia,serif;margin:10px 0 18px}
h2{font:30px/1.2 Georgia,serif;margin:0 0 18px}h3{font-size:16px;font-weight:600;margin:0 0 12px}p{max-width:820px}.muted{color:var(--muted);font-size:14px}
nav{display:flex;flex-wrap:wrap;gap:8px 20px;margin:24px 0 40px}a{color:var(--accent);text-underline-offset:4px}a:hover{color:var(--ink)}a:focus-visible{outline:2px solid var(--accent);outline-offset:4px}
section{margin:36px 0}.table-scroll{overflow:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:14px}th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);border-bottom:2px solid var(--rule)}td,th{padding:12px 10px}td{border-bottom:1px solid var(--rule)}td:first-child{width:45%;overflow-wrap:anywhere}tbody tr:hover{background:#edf4f0}
.previews{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:28px}.previews h3{min-height:3.1em}video{width:100%;background:#111;aspect-ratio:16/9}footer{border-top:1px solid var(--rule);padding-top:24px;margin-top:48px}
@media(max-width:650px){main{padding:28px 18px}h1{font-size:36px}td,th{padding:10px 8px}}
</style><main><header><span class="eyebrow">ProjectM Preset Lab</span><h1>Genre suggestions</h1>
<p><strong>Provisional results.</strong> Scores combine measured response with editable visual and home-viewing preferences. They are preference-fit scores, not match probabilities.</p>
<p class="muted">Predicted uses cached synthetic fingerprints and music descriptors. Music-tested adds observed rendering against a supplied recording and a matched control. Subjective suitability remains open to review; inventory counts do not establish it.</p>'''
    html+=f'<p class="muted">{len(fingerprints)} preset fingerprints · {tested} music-tested or reviewed genre/preset decisions</p></header>'
    html+='<nav aria-label="Genres">'+''.join(f'<a href="#{escape(g["id"])}">{escape(g["label"])}</a>' for g in catalog)+'</nav>'
    if previews:
        html+='<section><h2>Look at the measured presets</h2><div class="previews">'+''.join(previews)+'</div></section>'
    html+=''.join(tables)
    html+='<footer><h2>Adjust and reuse</h2><p>Edit the genre or audience JSON profile, then run <code>preset-lab match</code>. Matching reuses saved measurements and launches no render workers. Optional include/exclude feedback is keyed by preset content hash and genre.</p></footer></main></html>'
    path=destination/"index.html"
    path.write_text(html,encoding="utf-8")
    return path
