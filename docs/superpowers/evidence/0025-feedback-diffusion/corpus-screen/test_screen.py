import tempfile
import unittest
from pathlib import Path
import numpy as np
import screen

class ScreenTests(unittest.TestCase):
 def test_engine_first_key_and_case_are_preserved(self):
  text="bTexWrap=1\nbTexWrap=0\nbtexwrap=0\n fDecay=.5\nfDecay=.95\n"
  self.assertEqual(screen.first_keys(text),{"bTexWrap":"1","btexwrap":"0","fDecay":".95"})

 def test_dark_comparison_is_finite_and_not_an_exact_ratio(self):
  auth={"luma":0.0,"centre_rgb":[0,0,0]};run={"luma":.00001,"centre_rgb":[0,0,0]}
  value=screen.compare_metrics(run,auth,0.001)
  self.assertIsNone(value["luma_ratio"])
  self.assertTrue(value["dark_authored"])
  self.assertAlmostEqual(value["regularized_luma_ratio"],1.01)

 def test_sparse_manifest_must_match_actual_capture_count(self):
  manifest={"frames":480,"captured_frames":8,"capture_frame_indices":[120,150,180,210,239,300,390,479]}
  self.assertTrue(screen.valid_sparse_manifest(manifest,480,manifest["capture_frame_indices"],8))
  self.assertFalse(screen.valid_sparse_manifest(manifest,480,manifest["capture_frame_indices"],7))

 def test_sample_collector_ignores_uncaptured_frames(self):
  cfg=screen.Config(width=2,height=2,fps=30,warmup_seconds=4,measurement_seconds=12)
  collector=screen.Samples(cfg,[120,150],(2,2))
  collector.observe(np.zeros((2,2,3),np.uint8),119)
  collector.observe(np.full((2,2,3),255,np.uint8),120)
  collector.observe(np.full((2,2,3),128,np.uint8),150)
  result=collector.summary([120,150])
  self.assertAlmostEqual(result["luma"],(1+128/255)/2,places=6)
  self.assertEqual(sorted(collector.frames),[120,150])

 def test_store_resume_rejects_mixed_manifest(self):
  with tempfile.TemporaryDirectory() as directory:
   store=screen.Store(Path(directory),{"worker":"frozen-a"})
   store.put("job",{"status":"success","frames":8})
   self.assertEqual(store.get("job")["frames"],8)
   store.close()
   again=screen.Store(Path(directory),{"worker":"frozen-a"})
   self.assertEqual(again.get("job")["status"],"success")
   again.close()
   with self.assertRaises(ValueError):screen.Store(Path(directory),{"worker":"different"})

 def test_native_code_stops_at_first_missing_number(self):
  keys=screen.first_keys("warp_1=`shader_body\nwarp_3=`ignored\nwarp_1=`duplicate\n")
  self.assertEqual(screen.get_code(keys,"warp"),"shader_body")

 def test_hashes_have_consistent_json_keys_for_repeat_resume(self):
  import json
  cfg=screen.Config(width=2,height=2,fps=30,warmup_seconds=4,measurement_seconds=12)
  a=screen.Samples(cfg,[120],(2,2));a.observe(np.zeros((2,2,3),np.uint8),120)
  normalized={str(k):v for k,v in a.hashes.items()}
  self.assertEqual(json.loads(json.dumps(normalized)),normalized)
  self.assertEqual(len(screen.profile_plan()),7)

 def test_reference_change_invalidates_previous_comparisons(self):
  with tempfile.TemporaryDirectory() as directory:
   store=screen.Store(Path(directory),{"worker":"a"})
   store.put("candidate",{"reference_job_key":"auth","comparisons":{"4":{"img_err":.1}}})
   store.invalidate_reference("auth")
   row=store.get("candidate")
   self.assertNotIn("comparisons",row)
   self.assertFalse(row["comparison_eligible"])
   store.close()

if __name__=="__main__":unittest.main()
