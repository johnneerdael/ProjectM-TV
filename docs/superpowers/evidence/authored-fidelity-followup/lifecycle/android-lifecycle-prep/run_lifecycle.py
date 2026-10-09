#!/usr/bin/env python3
"""Owned user0/5640 transport for the separate lifecycle protocol; no install/build."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import tarfile
import tempfile
import uuid
import zipfile
from verify_lifecycle import PROTOCOL, ROOT, require, sha, verify

spec=importlib.util.spec_from_file_location("corpus_transport",ROOT/"tools/core-corpus/run_corpus.py")
corpus=importlib.util.module_from_spec(spec)
spec.loader.exec_module(corpus)
DEVICE="emulator-5640"
USER=0
PACKAGE="nl.neerdael.projectmtv.corpuslifecycle"
HERE=Path(__file__).resolve().parent

def write(path,value):
    path.write_text(json.dumps(value,sort_keys=True,separators=(",",":"))+"\n")

def check_binding(binding):
    require(binding["protocol"] == PROTOCOL and binding["package"] == PACKAGE, "Wrong binding protocol/package")
    require(binding["ownedSerial"] == DEVICE and binding["androidUser"] == USER, "Wrong owned device/user")
    require(sha(binding["apk"]) == binding["apk_sha256"] and sha(binding["aar"]) == binding["aar_sha256"], "Frozen artifact changed")
    require(sha(binding["pcm"]) == binding["pcm_sha256"], "Frozen PCM changed")
    for name,value in binding["worker_source_sha256"].items():
        require(sha(HERE/name) == value,"Frozen worker source changed: "+name)
    for name,key in (("verify_lifecycle.py","verifier_sha256"),("run_lifecycle.py","controller_sha256"),("bind_lifecycle.py","binder_sha256")):
        require(sha(HERE/name) == binding[key],"Frozen lifecycle helper changed: "+name)
    with zipfile.ZipFile(binding["apk"]) as apk:
        require(hashlib.sha256(apk.read("lib/arm64-v8a/libprojectmtv.so")).hexdigest() == binding["apk_native_sha256"], "Actual core bytes changed")
        require(hashlib.sha256(apk.read("assets/presets.idx")).hexdigest() == binding["apk_index_sha256"], "APK index changed")
        for name,value in binding["fixtures_sha256"].items():
            require(hashlib.sha256(apk.read("assets/presets/"+name)).hexdigest() == value,"APK fixture changed")

def run(args):
    binding=json.loads(args.binding.read_text())
    check_binding(binding)
    require(args.preset in ("audit followup uv default-feedback.milk", "audit followup uv custom-feedback.milk"), "Initialized UV lifecycle protocol requires a feedback fixture")
    require(args.preset in binding["fixtures_sha256"], "Preset is not a bound fixture")
    require(0 < args.reduced_width < args.width and 0 < args.reduced_height < args.height, "Reduced dimensions must shrink")
    require(args.width*args.height*4 <= 2147483647, "Unbounded capture")
    require(not args.output.exists(), "Use a fresh lifecycle output directory")
    adb=corpus.Adb(DEVICE,args.adb_port)
    with corpus.session_lock(DEVICE,args.adb_port):
        user=adb.shell("am","get-current-user")
        require(re.fullmatch(r"[0-9]+",user) is not None and int(user) == USER,"Current user must be confirmed numeric0")
        require(adb.shell("getprop","ro.build.fingerprint") == binding["fingerprint"],"Frozen device fingerprint changed")
        require(adb.shell("getprop","ro.build.version.sdk") == "34", "Owned lifecycle device must be API34")
        corpus.require_awake(adb)
        packages=adb.shell("pm","list","packages","--user",USER,PACKAGE).splitlines()
        require(all(re.fullmatch(r"package:[A-Za-z0-9_.]+",line) for line in packages) and "package:"+PACKAGE in packages,"Private lifecycle worker missing for user0")
        # Prove the installed APK bytes before any instrumentation. This worker must be one base APK.
        installed=adb.shell("pm","path","--user",USER,PACKAGE).splitlines()
        require(len(installed) == 1 and installed[0].startswith("package:/"),"Expected one installed base APK")
        require(hashlib.sha256(adb.call("exec-out","cat",installed[0][8:]).stdout).hexdigest() == binding["apk_sha256"],"Installed APK differs from frozen private APK")
        args.output.mkdir(parents=True)
        key="lifecycle-"+uuid.uuid4().hex
        private=f"/data/user/{USER}/{PACKAGE}/files/lifecycle/{key}"
        staging="/data/local/tmp/"+key
        request=dict(protocol=PROTOCOL,androidUser=USER,ownedSerial=DEVICE,binding=binding,
            preset=args.preset,seed=12345,instrumented=True,referenceWidth=0,referenceHeight=0,
            width=args.width,height=args.height,reducedWidth=args.reduced_width,reducedHeight=args.reduced_height,
            expectedPresetCount=binding["apk_preset_count"],pcmPath=private+"/audio.u8",outputDir=private+"/output")
        write(args.output/"request.json",request)
        prior=adb.shell("getprop","debug.projectmtv.preset")
        log_process=None
        verified=False
        try:
            adb.shell("am","force-stop","--user",USER,PACKAGE)
            adb.shell("mkdir","-p",staging)
            adb.shell("run-as",PACKAGE,"--user",USER,"mkdir","-p",private)
            for name,path in (("request.json",args.output/"request.json"),("audio.u8",Path(binding["pcm"]))):
                adb.call("push",path,staging+"/"+name)
                adb.shell("run-as",PACKAGE,"--user",USER,"cp",staging+"/"+name,private+"/"+name)
            adb.shell("setprop","debug.projectmtv.preset",corpus.preset_prefix(args.preset))
            # Do not clear the shared device log buffer. Record the protocol launch timestamp.
            with (args.output/"native-logcat.txt").open("wb") as logs:
                log_process=subprocess.Popen(adb.prefix+["logcat","-T","1","-v","epoch","projectM-Native:V","CoreCorpus:V","*:S"],stdout=logs,stderr=subprocess.STDOUT)
                result=adb.call("shell",corpus.remote_command(["am","instrument","--user",USER,"-w","-e","job",private+"/request.json",PACKAGE+"/nl.neerdael.projectmtv.corpus.CorpusInstrumentation"]),timeout=600)
                (args.output/"instrumentation.log").write_bytes(result.stdout)
                log_process.terminate()
                log_process.wait(timeout=10)
                log_process=None
            archive=adb.call("exec-out","run-as",PACKAGE,"--user",USER,"tar","-cf","-","-C",private,"output",timeout=120).stdout
            with tempfile.TemporaryDirectory(dir=args.output) as temporary:
                tarpath=Path(temporary)/"output.tar";tarpath.write_bytes(archive)
                with tarfile.open(tarpath) as stream:
                    stream.extractall(temporary,filter="data")
                for path in (Path(temporary)/"output").iterdir():
                    require(path.is_file(),"Unexpected worker output subtree")
                    path.replace(args.output/path.name)
            manifest=verify(args.output,binding)
            # Gate only structural lifecycle safety here. RGB comparison is scoped to matching generations/protocols.
            write(args.output/"verified.json",dict(protocol=PROTOCOL,status="ok",binding_sha256=sha(args.binding),
                request_sha256=sha(args.output/"request.json"),manifest_sha256=sha(args.output/"manifest.json"),
                cross_generation_pixel_agreement=False,cost_run=False,
                limitation="pbuffer production JNI lifecycle; no Activity/Home/audio-reattachment or physical TV qualification"))
            verified=True
            return manifest
        finally:
            if log_process is not None:
                log_process.terminate();log_process.wait(timeout=10)
            adb.shell("setprop","debug.projectmtv.preset",prior)
            adb.shell("am","force-stop","--user",USER,PACKAGE)
            # Retain failed private output for diagnosis; successful jobs are already pulled and verified.
            adb.shell("rm","-rf",staging)
            if verified:
                adb.shell("run-as",PACKAGE,"--user",USER,"rm","-rf",private)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--binding",type=Path,required=True)
    parser.add_argument("--preset",required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--adb-port",type=int,default=5037)
    parser.add_argument("--width",type=int,default=1280)
    parser.add_argument("--height",type=int,default=720)
    parser.add_argument("--reduced-width",type=int,default=960)
    parser.add_argument("--reduced-height",type=int,default=540)
    run(parser.parse_args())
