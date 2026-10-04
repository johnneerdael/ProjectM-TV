"""Separate Fed quadratrail feedback-state dimming from its composite shader."""
import json
import re
from concurrent.futures import ThreadPoolExecutor

from fidelity import image_error
from measure import EVIDENCE, REPO, measure


def main():
    source = REPO / "core/src/main/assets/presets/Fed - quadratrail.milk"
    root = EVIDENCE / "feedback-canvas"
    root.mkdir(exist_ok=True)
    name = "fed-quadratrail-canvas-v1.milk"
    # Replace the existing section, rather than appending duplicate keys.
    original = source.read_text()
    canvas = re.sub(r"^comp_\d+=.*\n?", "", original, flags=re.MULTILINE)
    canvas += "comp_1=`shader_body\ncomp_2=`{\ncomp_3=`ret=GetPixel(uv);\ncomp_4=`}\n"
    assert re.findall(r"^comp_\d+=", canvas, flags=re.MULTILINE) == [
        "comp_1=", "comp_2=", "comp_3=", "comp_4="
    ]
    (root / name).write_text(canvas)
    jobs = [("baseline", 1182, 665, (0, 0))]
    jobs += [(worker, w, h, (1024, 768)) for worker in ["baseline", "reviewed"]
             for w, h in [(2364, 1330), (3840, 2160)]]

    def run(job):
        worker, w, h, reference = job
        result = measure(name, worker, w, h, reference, seconds=12, preset_root=root)
        print(worker, h, result["status"], result.get("luma"), flush=True)
        assert result["status"] == "success", result["diagnostics"]
        return result

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, jobs))
    authored = results[0]
    for result in results:
        result["luma_ratio"] = result["luma"] / authored["luma"]
        result["img_err"] = image_error(result, authored)
    (EVIDENCE / "feedback-canvas-report.json").write_text(
        json.dumps({"protocol": "12s window after 4s warm-up, 30fps, bass-0.30; only composite replaced by direct main read; warp and geometry unchanged", "results": results}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
