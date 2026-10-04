"""Fake Android 9/14 shell for diagnostics tests; never contacts a device."""

import json
import os
from pathlib import Path
import sys


args = sys.argv[1:]
if args[:1] == ["-s"]:
    args = args[2:]
with Path(os.environ["DIAGNOSTICS_TEST_CALLS"]).open("a") as trace:
    trace.write(json.dumps(args) + "\n")
state_path = Path(os.environ["DIAGNOSTICS_TEST_STATE"])
state = json.loads(state_path.read_text())
failure = os.environ.get("DIAGNOSTICS_TEST_FAILURE", "")
package = "nl.neerdael.projectmtv"
listener = package + "/com.example.projectm.visualizer.TrackListenerService"
changed = False

if args == ["get-state"]:
    print("device")
elif args[:2] == ["logcat", "-v"]:
    print(f"10-05 12:00:00.000 100 100 I ActivityManager: Start proc 202:{package}/u0a123 for service")
    print(f"10-05 12:00:00.001 100 100 I ActivityManager: Start proc 309:{package}/u10a123 for activity")
    print("10-05 12:00:01.000 410 410 I VisualizerRenderer: STATS fps=30.0 surface=1920x1080 audio=0.1")
elif args[:1] == ["shell"]:
    command = args[1:]
    if command == ["am", "get-current-user"]:
        if failure == "user-error":
            print("permission denied", file=sys.stderr)
            sys.exit(1)
        if failure == "user-malformed":
            print("Error: no current user")
        elif failure == "user-whitespace":
            print(" 10 ")
        elif failure == "user-negative":
            print("-1")
        elif failure != "user-empty":
            print("10\r")
    elif command[:1] == ["ps"]:
        if failure == "ps-error" or (failure == "ps-after-stop" and state["pid"] == 0):
            print("ps: unavailable", file=sys.stderr)
            sys.exit(1)
        if failure == "ps-malformed":
            print("USER PID NAME\nu10_a123 309 " + package)
        elif failure != "ps-empty":
            print("UID PID NAME")
            if failure == "ps-bad-row":
                print("u10_a123 309 " + package)
            print("10123 202 " + package)  # Another user's listener keeps its app running.
            print("1010123 999 " + package + ":worker")  # Exact process name matters too.
            if state["pid"]:
                print(f'1010123 {state["pid"]} {package}')
            if failure == "ps-ambiguous":
                print("1010123 102 " + package)
    elif command[:1] == ["pidof"]:  # Reproduce the old cross-user lookup.
        print("202" + (f' {state["pid"]}' if state["pid"] else ""))
    elif command[:2] == ["am", "force-stop"]:
        state["pid"] = 0
        changed = True
    elif command[:2] == ["am", "start"]:
        state["starts"] += 1
        state["pid"] = 309 if state["starts"] == 1 else 410
        changed = True
        print("Status: ok\nTotalTime: 123")
        launch_state = os.environ.get("DIAGNOSTICS_TEST_LAUNCH_STATE", "COLD")
        if launch_state:
            print("LaunchState: " + launch_state)
    elif command[:1] == ["settings"]:
        print(listener if state["listener"] else "null")
    elif command[:2] == ["cmd", "notification"]:
        state["listener"] = command[2] == "allow_listener"
        changed = True
    elif command[:2] == ["getprop", "ro.product.model"]:
        print("Fake TV")
    elif command[:2] == ["dumpsys", "package"]:
        print("versionName=1.0-test")
    elif command[:1] == ["top"]:
        print(f'410 {package}')

if changed:
    state_path.write_text(json.dumps(state))
