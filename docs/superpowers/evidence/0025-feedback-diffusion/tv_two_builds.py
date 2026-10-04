"""Compare main and the candidate at 1330 without writing release app data.

Both are optimized, debuggable profile builds for run-as configuration. Run only
after the current device benchmark has restored its state and removed its profile.
"""
import argparse
import hashlib
import json
import subprocess
import tv_benchmark as bench

BASELINE="nl.neerdael.projectmtv.diffusionbaseline"
CANDIDATE="nl.neerdael.projectmtv.profile"

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
    parser.add_argument("--device",default="192.168.51.53:5555")
    parser.add_argument("--label",default="am9-main-vs-candidate-1330")
    parser.add_argument("--restore-adb-user",action="store_true")
    args=parser.parse_args()
    bench.DEVICE=args.device;bench.ADB=["adb","-P","5038","-s",args.device]
    bench.TV=bench.EVIDENCE/("tv-"+args.label);bench.TV.mkdir(exist_ok=True)
    bench.prefs=prefs;bench.root=remove_resume
    bench.awake()
    packages=bench.shell(["pm","list","packages"]).splitlines()
    assert all("package:"+p not in packages for p in [BASELINE,CANDIDATE]),"Do not overwrite an existing research package"
    properties={n:bench.shell(["getprop",n]).strip() for n in ["debug.projectmtv.preset","debug.projectmtv.diffusion","debug.projectmtv.kernel"]}
    builds={BASELINE:bench.REPO/"build/diffusion/android-main/app/build/outputs/apk/profile/app-profile.apk",
            CANDIDATE:bench.REPO/"build/diffusion/android/app/build/outputs/apk/profile/app-profile.apk"}
    session={"device":args.device,"main_commit":subprocess.check_output(["git","-C",str(bench.REPO/"build/diffusion/android-main"),"rev-parse","HEAD"],text=True).strip(),
             "apk_sha256":{p:hashlib.sha256(a.read_bytes()).hexdigest() for p,a in builds.items()},
             "properties":properties,"release_data_written":False,"render_height":1330,
             "saved_prefs_source":"settled original release preferences from prior session",
             "condition":"same settings, 60 FPS target; live audio passages vary between runs"}
    # Run with authorized root ADB so settled release prefs can be audited without writing them.
    assert bench.shell(["id","-u"]).strip()=="0","Root ADB is required for the release-preference audit"
    bench.shell(["am","force-stop",bench.RELEASE])
    original=bench.adb("shell",f"cat /data/data/{bench.RELEASE}/shared_prefs/projectm_settings.xml")
    session["release_prefs_sha256"]=hashlib.sha256(original.encode()).hexdigest()
    (bench.TV/"source-settings.xml").write_text(original)
    configured=bench.configured(original,1330)
    (bench.TV/"configured-settings.xml").write_text(configured)
    session["configured_settings_sha256"]=hashlib.sha256(configured.encode()).hexdigest()
    source_root=bench.REPO/"build/diffusion/android"
    native=source_root/"third_party/projectm/src/libprojectM/MilkdropPreset/FeedbackDiffusion.cpp"
    session["candidate_diffusion_cpp_sha256"]=hashlib.sha256(native.read_bytes()).hexdigest()
    session["candidate_patches"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (source_root/"tools/projectm-patches").glob("*.patch")}
    (bench.TV/"session.json").write_text(json.dumps(session,indent=2)+"\n")
    installed=[];rows=[]
    try:
        for package,apk in builds.items():
            bench.adb("install","--no-streaming",str(apk));installed.append(package)
            bench.shell(["pm","grant",package,"android.permission.RECORD_AUDIO"])
        bench.shell(["am","force-stop",bench.RELEASE])
        ordinal=0
        for preset in bench.PRESETS:
            pair=[]
            for package in [BASELINE,CANDIDATE,BASELINE,CANDIDATE]:
                for other in [BASELINE,CANDIDATE]:bench.shell(["am","force-stop",other])
                bench.PROFILE=package;ordinal+=1
                # Main ignores this selector; candidate mode2 uses its normal compensated path.
                row=bench.run(preset,1330,2,ordinal,original,25,60)
                row["build"]="main" if package==BASELINE else "candidate"
                row["package"]=package
                row["apk_sha256"]=session["apk_sha256"][package]
                rows.append(row)
                pair.append(row)
                (bench.TV/"results.json").write_text(json.dumps(rows,indent=2)+"\n")
            audible=[r["audio_mean"]>0 for r in pair]
            assert all(audible) or not any(audible), "Audio state changed between builds; do not aggregate this cohort"
    finally:
        errors=[]
        for name,value in properties.items():
            try:bench.property_value(name,value)
            except Exception as error:errors.append(f"restore {name}: {error}")
        for package in installed:
            try:bench.shell(["am","force-stop",package]);bench.adb("uninstall",package)
            except Exception as error:errors.append(f"remove {package}: {error}")
        try:
            session["properties_restored"]={n:bench.shell(["getprop",n]).strip()==v for n,v in properties.items()}
            final=bench.shell(["pm","list","packages"]).splitlines()
            session["packages_removed"]=all("package:"+p not in final for p in installed)
            final_xml=bench.adb("shell",f"cat /data/data/{bench.RELEASE}/shared_prefs/projectm_settings.xml")
            session["release_prefs_unchanged"]=final_xml==original
        except Exception as error:errors.append(f"verify restoration: {error}")
        session["cleanup_errors"]=errors
        (bench.TV/"restoration.json").write_text(json.dumps(session,indent=2)+"\n")
        assert not errors and session["packages_removed"] and session["release_prefs_unchanged"] and all(session["properties_restored"].values())
        try:bench.awake()
        except RuntimeError:pass
        else:bench.shell(["am","start","-n",bench.RELEASE+bench.ACTIVITY])
        if args.restore_adb_user:bench.adb("unroot")

if __name__=="__main__":main()
