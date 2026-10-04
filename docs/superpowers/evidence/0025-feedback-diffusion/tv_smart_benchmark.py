"""Authorized non-root Smart TV Pro runs; results are separate from the AM6.

Use a research-only debuggable profile APK for run-as preferences. Release app
data is never written. SurfaceHolder.setFixedSize selects the physical render
buffer independently of the Android UI override; verify every STATS height.
"""
import argparse
import hashlib
import json
import re
import subprocess
import time
import tv_benchmark as bench

def awake():
    power=bench.shell(["dumpsys","power"])
    display=bench.shell(["dumpsys","display"])
    if "mWakefulness=Awake" not in power or not re.search(r"DisplayDeviceInfo\{.*state ON",display):
        raise RuntimeError("TV asleep/display off; stopping without waking it")

def prefs(xml):
    bench.adb("shell","run-as",bench.PROFILE,"mkdir","-p","shared_prefs")
    subprocess.run(bench.ADB+["shell","run-as",bench.PROFILE,"sh","-c",
                             "'cat > shared_prefs/projectm_settings.xml'"],
                   input=xml,text=True,check=True,capture_output=True)

def remove_resume(command):
    assert command==f"rm -f /data/data/{bench.PROFILE}/files/resume_preset.txt"
    return bench.adb("shell","run-as",bench.PROFILE,"rm","-f","files/resume_preset.txt")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--device",default="192.168.50.101:42547")
    parser.add_argument("--label",default="smart-pro-"+time.strftime("%Y%m%d-%H%M%S"))
    parser.add_argument("--skip",type=int,default=0)
    parser.add_argument("--limit",type=int,default=6)
    parser.add_argument("--heights",default="1330,2160")
    args=parser.parse_args()
    bench.DEVICE=args.device
    bench.ADB=["adb","-P","5038","-s",args.device]
    bench.TV=bench.EVIDENCE/("tv-"+args.label)
    bench.TV.mkdir(parents=True,exist_ok=True)
    bench.awake=awake
    bench.prefs=prefs
    bench.root=remove_resume
    # AM6's sysfs interface is unavailable on this TV; FPS and audio still sampled.
    bench.gpu_sample=lambda elapsed:None
    awake()
    assert "package:"+bench.PROFILE not in bench.shell(["pm","list","packages"]).splitlines(),"Existing profile app must not be overwritten"
    wm=bench.shell(["wm","size"])
    properties={n:bench.shell(["getprop",n]).strip() for n in ["debug.projectmtv.preset","debug.projectmtv.diffusion","debug.projectmtv.kernel"]}
    apk=bench.REPO/"build/diffusion/android/app/build/outputs/apk/profile/app-profile.apk"
    session={"device":args.device,"model":bench.shell(["getprop","ro.product.model"]).strip(),
             "platform":bench.shell(["getprop","ro.board.platform"]).strip(),"display_before":wm,
             "properties":properties,"apk_sha256":hashlib.sha256(apk.read_bytes()).hexdigest(),
             "release_data_written":False,"debuggable_profile":True,
             "media_before":bench.shell(["dumpsys","media_session"])}
    (bench.TV/"session.json").write_text(json.dumps(session,indent=2)+"\n")
    installed=False
    try:
        bench.adb("install","--no-streaming",str(apk));installed=True
        bench.adb("shell","run-as",bench.PROFILE,"id")
        bench.shell(["pm","grant",bench.PROFILE,"android.permission.RECORD_AUDIO"])
        bench.shell(["am","force-stop",bench.RELEASE])
        ordinal=0
        for preset in bench.PRESETS[args.skip:args.limit]:
            for height in map(int,args.heights.split(",")):
                for mode in [0,2,0,2]:
                    ordinal+=1
                    bench.run(preset,height,mode,ordinal,"<map/>",25,60)
    finally:
        for name,value in properties.items():bench.property_value(name,value)
        if installed:
            bench.shell(["am","force-stop",bench.PROFILE]);bench.adb("uninstall",bench.PROFILE)
        session["properties_restored"]={n:bench.shell(["getprop",n]).strip()==v for n,v in properties.items()}
        session["display_restored"]=bench.shell(["wm","size"])==wm
        session["profile_removed"]="package:"+bench.PROFILE not in bench.shell(["pm","list","packages"]).splitlines()
        (bench.TV/"restoration.json").write_text(json.dumps(session,indent=2)+"\n")
        assert session["display_restored"] and all(session["properties_restored"].values())
        try:awake()
        except RuntimeError:pass
        else:bench.shell(["am","start","-n",bench.RELEASE+bench.ACTIVITY])

if __name__=="__main__":main()
