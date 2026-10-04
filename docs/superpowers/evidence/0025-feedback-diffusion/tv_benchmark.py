"""Authorized AM6 measurements. Never wake remotely; always restore initial state.

The release app remains installed and its preferences remain untouched. At 2160 an
isolated profile/off build supplies the baseline because release is capped at 1330.
Live Milkbeat audio is recorded as a limitation; do not mix silence/music samples.
"""
import argparse
import hashlib
import json
import re
import shlex
import subprocess
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
DEVICE = "192.168.50.80:5555"
PROFILE = "nl.neerdael.projectmtv.profile"
RELEASE = "nl.neerdael.projectmtv"
ACTIVITY = "/com.example.projectm.visualizer.MainActivity"
ADB = ["adb", "-P", "5038", "-s", DEVICE]
PRESETS = [
    "Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk",
    "$$$ Royal - Mashup (191).milk",
    "$$$ Royal - Mashup (103).milk",
    "TonyMilkdrop - I Like Cartoon --- Isosceles edit.milk",
    "fat cancer tour meant t nz+.milk",
    "Flexi - alien complex 03.milk",
]

def adb(*args):
    return subprocess.check_output(ADB + list(args), text=True)

def shell(args):
    return adb("shell", shlex.join(args))

def root(command):
    if shell(["id","-u"]).strip()=="0":
        return adb("shell",command)
    return shell(["su", "-c", command])

def awake():
    text = shell(["dumpsys", "power"])
    display_on = "Display Power: state=ON" in text
    if not display_on:
        display_on=bool(re.search(r"DisplayDeviceInfo\{.*state ON",shell(["dumpsys","display"])))
    if "mWakefulness=Awake" not in text or not display_on:
        raise RuntimeError("Device asleep or display off; stopping without waking it")

def property_value(name, value):
    shell(["setprop", name, value])

def gpu_sample(elapsed):
    utilization=int(shell(["cat","/sys/class/mpgpu/utilization"]).strip())
    result=subprocess.run(ADB+["shell","cat","/sys/class/mpgpu/cur_freq"],capture_output=True,text=True)
    frequency=int(result.stdout.strip()) if result.returncode==0 else None
    return {"elapsed_s":elapsed,"utilization":utilization,"frequency":frequency}

def configured(xml, height):
    tree = ET.fromstring(xml)
    # The final app distinguishes Native (-1) from legacy saved numeric 2160, which stays capped.
    saved_height = -1 if height > 1330 else height
    values = {"render_height":("int",str(saved_height)),"frame_rate_cap":("int","60"),
              "frame_rate_reset_30":("boolean","true"),
              "memory_limit":("boolean","false"),"blank_detection_v3":("boolean","false"),
              "skip_slow_presets":("boolean","false"),"beat_cuts":("boolean","false"),
              "track_info":("boolean","false"),"track_access_explained":("boolean","true"),
              "auto_change_enabled":("boolean","false"),"auto_update":("boolean","false")}
    for child in list(tree):
        if child.get("name") in values: tree.remove(child)
    for name,(tag,value) in values.items(): ET.SubElement(tree,tag,name=name,value=value)
    return ET.tostring(tree,encoding="unicode")

def prefs(xml):
    temporary = REPO / "build/diffusion/tv-prefs.xml"
    temporary.write_text(xml)
    adb("push", str(temporary), "/data/local/tmp/projectmtv-diffusion-prefs.xml")
    root(f"mkdir -p /data/data/{PROFILE}/shared_prefs")
    root(f"cat /data/local/tmp/projectmtv-diffusion-prefs.xml > /data/data/{PROFILE}/shared_prefs/projectm_settings.xml")
    root(f"chown -R $(stat -c %u /data/data/{PROFILE}):$(stat -c %g /data/data/{PROFILE}) /data/data/{PROFILE}/shared_prefs")

def run(preset,height,mode,ordinal,original_xml,warmup,window):
    awake()
    shell(["am","force-stop",PROFILE])
    prefs(configured(original_xml,height))
    # Resume state takes priority over preset pin. Remove only the experimental app's files.
    root(f"rm -f /data/data/{PROFILE}/files/resume_preset.txt")
    # Full filename avoids matching another preset with the same stem (fat cancer ... asect).
    property_value("debug.projectmtv.preset",preset)
    property_value("debug.projectmtv.diffusion",str(mode))
    log = TV / f"run-{ordinal:03d}-{height}-{mode}.log"
    log.parent.mkdir(parents=True,exist_ok=True)
    samples, lines, gpu = [], [], []
    current_pid=None
    process = subprocess.Popen(ADB+["logcat","-v","epoch","-T","1","VisualizerRenderer:I","projectM-Native:I","MainActivity:I","*:S"],
                               stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    start = time.monotonic()
    def consume():
        nonlocal current_pid
        for line in process.stdout:
            elapsed=time.monotonic()-start
            lines.append({"elapsed_s":elapsed,"line":line.rstrip()})
            pid_match=re.match(r"\s*[\d.]+\s+(\d+)\s+\d+\s+[A-Z]",line)
            if f"BENCHMARK preset='{preset}'" in line and pid_match:
                current_pid=pid_match[1]
            match=re.search(r"STATS fps=([\d.]+) surface=(\d+)x(\d+) audio=([\d.]+)",line)
            if match and pid_match and pid_match[1]==current_pid and warmup <= elapsed <= warmup+window:
                samples.append({"elapsed_s":elapsed,"fps":float(match[1]),"width":int(match[2]),
                                "height":int(match[3]),"audio":float(match[4])})
    reader=threading.Thread(target=consume,daemon=True);reader.start()
    try:
        shell(["am","start","-S","-n",PROFILE+ACTIVITY])
        start = time.monotonic()  # Exclude launch time from the full 25-second warm-up.
        while time.monotonic()-start < warmup+window:
            awake()
            top = shell(["dumpsys", "activity", "activities"])
            resumed = [line for line in top.splitlines() if "ResumedActivity:" in line]
            if not resumed or not all(PROFILE+ACTIVITY in line for line in resumed):
                raise RuntimeError("Benchmark lost foreground; sample invalid: " + str(resumed))
            if time.monotonic()-start >= warmup:
                sample=gpu_sample(time.monotonic()-start)
                if sample is not None: gpu.append(sample)
            time.sleep(1)
    finally:
        process.terminate();process.wait(timeout=10);reader.join(timeout=5);process.stdout.close()
        log.write_text("\n".join(json.dumps(line) for line in lines)+"\n")
    assert len(samples)>=9, f"missing stats: {log}"
    assert all(s["height"]==height for s in samples), f"wrong render height: {samples}"
    assert current_pid is not None, f"wrong pinned preset: {log}"
    loads=[line["line"] for line in lines if "LOAD preset=" in line["line"] and
           re.match(r"\s*[\d.]+\s+(\d+)\s+\d+\s+[A-Z]",line["line"])[1]==current_pid]
    assert loads and all(f"LOAD preset='{preset}'" in line for line in loads), f"preset changed during pinned run: {log}"
    result={"preset":preset,"height":height,"mode":mode,"ordinal":ordinal,"samples":samples,"gpu":gpu,
            "fps_mean":sum(s["fps"] for s in samples)/len(samples),"fps_min":min(s["fps"] for s in samples),
            "fps_max":max(s["fps"] for s in samples),"audio_mean":sum(s["audio"] for s in samples)/len(samples),
            "gpu_mean":sum(s["utilization"] for s in gpu)/len(gpu) if gpu else None,"log":str(log),
            "condition":"nonzero PCM recorded; live audio passages vary" if any(s["audio"]>0 for s in samples) else "silence recorded in this run",
            "warmup_s":warmup,"window_s":window}
    (log.with_suffix(".json")).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ["samples","gpu","log"]}),flush=True)
    return result

def main():
    global TV, DEVICE, ADB
    parser=argparse.ArgumentParser()
    parser.add_argument("--device",default=DEVICE)
    parser.add_argument("--restore-adb-user",action="store_true")
    parser.add_argument("--limit",type=int,default=6)
    parser.add_argument("--skip",type=int,default=0)
    parser.add_argument("--reuse-owned-profile",action="store_true")
    parser.add_argument("--label",default=time.strftime("%Y%m%d-%H%M%S"))
    parser.add_argument("--kernel",default="9",choices=["9","9z","5","5h","4","3"])
    parser.add_argument("--heights",default="1330,2160")
    parser.add_argument("--modes",default="0,1,0,2")
    parser.add_argument("--warmup",type=int,default=25)
    parser.add_argument("--window",type=int,default=60)
    args=parser.parse_args()
    DEVICE=args.device
    ADB=["adb","-P","5038","-s",DEVICE]
    TV = EVIDENCE / ("tv-" + args.label)
    TV.mkdir(parents=True,exist_ok=True)
    awake()
    packages=shell(["pm","list","packages"]).splitlines()
    existing = "package:"+PROFILE in packages
    assert not existing or args.reuse_owned_profile,"Existing profile app requires a separate backup; do not overwrite"
    properties={name:shell(["getprop",name]).strip() for name in ["debug.projectmtv.preset","debug.projectmtv.diffusion","debug.projectmtv.kernel"]}
    # Stop first: onPause remembers Auto's last level. Capture the settled preferences.
    shell(["am","force-stop",RELEASE])
    original_xml=root(f"cat /data/data/{RELEASE}/shared_prefs/projectm_settings.xml")
    (REPO/"build/diffusion/release-prefs-original.xml").write_text(original_xml)
    apk=REPO/"build/diffusion/android/app/build/outputs/apk/profile/app-profile.apk"
    if existing:
        installed_path=shell(["pm","path",PROFILE]).strip().split(":",1)[1]
        installed_hash=shell(["sha256sum",installed_path]).split()[0]
        assert installed_hash==hashlib.sha256(apk.read_bytes()).hexdigest(),"Existing profile is not this task's APK"
    session={"device":DEVICE,"properties":properties,"kernel":args.kernel,"release_prefs_sha256":hashlib.sha256(original_xml.encode()).hexdigest(),
             "apk_sha256":hashlib.sha256(apk.read_bytes()).hexdigest(),"installed_profile_initially":False,
             "model":shell(["getprop","ro.product.model"]).strip(),"display":shell(["dumpsys","display"]),
             "media_before":shell(["dumpsys","media_session"])}
    (TV/"session.json").write_text(json.dumps(session,indent=2)+"\n")
    installed=False
    try:
        if not existing: adb("install","--no-streaming","-r",str(apk))
        installed=True
        property_value("debug.projectmtv.kernel",args.kernel)
        shell(["pm","grant",PROFILE,"android.permission.RECORD_AUDIO"])
        shell(["am","force-stop",RELEASE])
        ordinal=0
        for preset in PRESETS[args.skip:args.limit]:
            for height in map(int,args.heights.split(",")):
                for mode in map(int,args.modes.split(",")):
                    ordinal+=1
                    run(preset,height,mode,ordinal,original_xml,args.warmup,args.window)
    finally:
        for name,value in properties.items():property_value(name,value)
        if installed:
            shell(["am","force-stop",PROFILE]);adb("uninstall",PROFILE)
        shell(["rm","-f","/data/local/tmp/projectmtv-diffusion-prefs.xml"])
        # Release preferences were never modified; prove that before returning its foreground.
        final_xml=root(f"cat /data/data/{RELEASE}/shared_prefs/projectm_settings.xml")
        session["release_prefs_unchanged"]=final_xml==original_xml
        session["properties_restored"]={name:shell(["getprop",name]).strip()==value for name,value in properties.items()}
        session["profile_removed"]="package:"+PROFILE not in shell(["pm","list","packages"]).splitlines()
        (TV/"restoration.json").write_text(json.dumps(session,indent=2)+"\n")
        assert session["release_prefs_unchanged"],"Release prefs changed externally; do not overwrite another actor's changes"
        try:awake()
        except RuntimeError:pass
        else:shell(["am","start","-n",RELEASE+ACTIVITY])
        if args.restore_adb_user:adb("unroot")

if __name__=="__main__":main()
