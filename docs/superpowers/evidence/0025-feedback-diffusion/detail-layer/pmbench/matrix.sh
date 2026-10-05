#!/bin/bash
ADB=~/Library/Android/sdk/platform-tools/adb; S=192.168.50.104:5555
run() { # label preset engine w h rw rh env
  local out; out=$($ADB -s $S shell "cd /data/local/tmp/pmbench && $8 ./pmbench-$3 presets/p$2.milk textures pcm-480.f32 $4 $5 $6 $7 240 60 2>&1 | grep -E 'mean|detail shader|failed' | tr '\n' ' '")
  echo "$1 p$2 $out"
}
for round in 1 2; do
 for p in 0 1 2 3 4 5; do
  run up4k $p upstream 3840 2160 0 0 ""
  run main4k $p main 3840 2160 1024 768 ""
  run md0_4k $p mdetail-a 3840 2160 1280 720 "PM_DETAIL=0"
  run md1_4k $p mdetail-a 3840 2160 1280 720 "PM_DETAIL=1"
  run up1330 $p upstream 2364 1330 0 0 ""
  run main1330 $p main 2364 1330 1024 768 ""
 done
done
echo MATRIX-DONE
