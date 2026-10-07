import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common
import prepare_worker
import run_sample


class FrozenSampleTests(unittest.TestCase):
    def test_ranking_is_order_independent_and_uses_exact_utf8_names(self):
        records = [{"filename": name, "asset_sha256": "a" * 64}
                   for name in ("A.milk", "a.milk", "é.milk", common.MIDGIT)]
        selected, _ = common.select(records, count=2)
        reversed_selected, _ = common.select(list(reversed(records)), count=2)
        self.assertEqual(selected, reversed_selected)
        for row in selected:
            self.assertEqual(row["selection_rank_sha256"], hashlib.sha256(
                b"12345\0" + row["filename"].encode("utf-8")).hexdigest())

    def test_actual_catalog_selects_100_without_feature_filtering(self):
        records = common.catalog()
        random, regression = common.select(records)
        self.assertEqual(len(records), 9606)
        self.assertEqual(len(random), 100)
        self.assertEqual(len({row["filename"] for row in random}), 100)
        self.assertIn(common.MIDGIT, {row["filename"] for row in random + regression})

    def test_frame_order_dimensions_and_content_integrity_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame-hashes.jsonl"
            rows = [{"frame": frame, "width": 2, "height": 2, "rgbSha256": str(frame) * 64}
                    for frame in range(2)]
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            manifest = {"frameHashCount": 2, "frameHashesSha256": common.file_sha(path)}
            request = {"frameLimit": 2, "width": 2, "height": 2}
            self.assertEqual(common.frame_hashes(directory, manifest, request), ["0" * 64, "1" * 64])
            rows[1]["frame"] = 0
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            manifest["frameHashesSha256"] = common.file_sha(path)
            with self.assertRaisesRegex(ValueError, "Frame order"):
                common.frame_hashes(directory, manifest, request)
            path.write_text("tampered")
            with self.assertRaisesRegex(ValueError, "modified"):
                common.frame_hashes(directory, manifest, request)

    def test_missing_repeat_or_one_pixel_hash_difference_cannot_be_equal(self):
        self.assertEqual(common.first_difference(["a", "b"], ["a", "c"]), 1)
        self.assertIsNone(common.first_difference(["a", "b"], ["a", "b"]))
        with self.assertRaises(ValueError):
            common.first_difference(["a"], ["a", "b"])

    def test_release_without_49_is_rejected_before_artifact_use(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "release.json"
            path.write_text(json.dumps({"schema": "projectmtv-verified-release-v1", "status": "verified",
                "release_tag": "old", "source_commit": "a" * 40, "engine_commit": "b" * 40,
                "aar_path": "missing.aar", "aar_sha256": "c" * 64, "ordered_patches": [], "includes_prs": [44]}))
            with self.assertRaisesRegex(ValueError, "PR #49"):
                common.release_manifest(path)

    def test_regression_union_keeps_required_names_and_rejects_changed_hash(self):
        records = [{"filename": common.MIDGIT, "asset_sha256": "a" * 64},
                   {"filename": "issue.milk", "asset_sha256": "b" * 64}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "regressions.json"
            data = {"schema": "projectmtv-regression-presets-v1", "completeness": "all_original_patch_regression_presets",
                    "source_inventory_sha256": "c" * 64,
                    "presets": [{"filename": "issue.milk", "asset_sha256": "b" * 64, "reasons": ["0049 exact witness"]}]}
            path.write_text(json.dumps(data))
            _, selected = common.regression_inventory(path, records)
            self.assertEqual({row["filename"] for row in selected}, {"issue.milk", common.MIDGIT})
            data["presets"][0]["asset_sha256"] = "d" * 64
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "modified regression"):
                common.regression_inventory(path, records)

    def test_seed_reset_must_follow_environment_assignment(self):
        prefix = "Java_nl_neerdael_projectmtv_corpus_LabBridge_initialize {"
        suffix = "} Java_nl_neerdael_projectmtv_corpus_LabBridge_setFrameClock"
        body = 'setenv("PRESET_LAB_SEED", configured, 1); lab::ResetShaderRandom();'
        self.assertTrue(common.bridge_is_reset_after_seed(prefix + body + suffix))
        self.assertFalse(common.bridge_is_reset_after_seed(prefix + 'lab::ResetShaderRandom(); setenv("PRESET_LAB_SEED", configured, 1);' + suffix))

    def test_source_and_shipping_harness_modes_have_distinct_bridge_guards(self):
        original = (common.ROOT / "tools/core-corpus/android-worker/app/src/main/java/nl/neerdael/projectmtv/corpus/CorpusInstrumentation.java").read_text()
        source = prepare_worker.extend_harness(original)
        shipping = prepare_worker.extend_harness(original, fixed_seed=False)
        self.assertIn('if (!instrumented) throw', source)
        self.assertIn('if (instrumented) throw', shipping)
        self.assertIn("frameHashes.writeFrame(frame, rgba)", source)
        self.assertIn("frame < frameLimit", source)
        self.assertIn("EveryFrameHashes.captures", source)
        self.assertNotIn("frame == CAPTURES[nextCapture]", source)

    def test_job_denominator_is_full_union_with_two_repeats_per_source(self):
        protocol = {"presets": [{"filename": name, "asset_sha256": "a" * 64} for name in ("a.milk", "b.milk")],
                    "profiles": {"1080p": {}}, "frames": 480}
        source, shipping = list(run_sample.jobs(protocol)), list(run_sample.jobs(protocol, shipping=True))
        self.assertEqual(len(source), 8)
        self.assertEqual(len(shipping), 2)
        self.assertEqual(len({row["key"] for row in source + shipping}), 10)

    def test_final_protocol_cannot_shorten_frames_or_drop_regressions(self):
        first = {"filename": "random.milk", "asset_sha256": "a" * 64}
        second = {"filename": "required.milk", "asset_sha256": "b" * 64}
        selected = {"random_presets": [first], "additional_regressions": [second]}
        protocol = {"schema": common.SCHEMA, "mode": "final", "seed": 12345, "fps": 30,
                    "clock": "frame/30.0", "repeats": [0, 1], "backend": "android-gpu-emulator",
                    "frames": 480, "profiles": {"1080p": common.PROFILES["1080p"]},
                    "can_satisfy_random_completion_gate": True, "presets": [first, second]}
        protocol.update(run_sample.proof_contract(selected))
        run_sample.validate_protocol(protocol, selected)
        protocol["frames"] = 60
        with self.assertRaisesRegex(ValueError, "all 480"):
            run_sample.validate_protocol(protocol, selected)
        protocol["frames"] = 480
        protocol["presets"] = [first]
        with self.assertRaisesRegex(ValueError, "every frozen"):
            run_sample.validate_protocol(protocol, selected)
        protocol.update(mode="explore", frames=60, can_satisfy_random_completion_gate=False)
        run_sample.validate_protocol(protocol, selected)
        protocol["presets"] = [second]
        with self.assertRaisesRegex(ValueError, "cherry-pick"):
            run_sample.validate_protocol(protocol, selected)

    def test_positive_proof_cannot_drop_frames_repeats_or_representatives(self):
        selected = {"random_presets": [{"filename": name, "asset_sha256": "a" * 64}
                                      for name in ("first.milk", "second.milk", "third.milk")],
                    "additional_regressions": []}
        protocol = {"schema": common.SCHEMA, "mode": "final", "seed": 12345, "fps": 30,
                    "clock": "frame/30.0", "repeats": [0, 1], "backend": "android-gpu-emulator",
                    "frames": 480, "profiles": {"1080p": common.PROFILES["1080p"]},
                    "can_satisfy_random_completion_gate": True, "presets": selected["random_presets"],
                    **run_sample.proof_contract(selected)}
        for key, value in (("positive_proof_frames", []), ("positive_proof_frames", [120]),
                           ("positive_proof_repeats", [0]), ("positive_proof_presets", ["first.milk"])):
            with self.subTest(key=key, value=value):
                changed = dict(protocol, **{key: value})
                with self.assertRaisesRegex(ValueError, "positive image proof"):
                    run_sample.validate_protocol(changed, selected)

    def test_real_regression_inventory_union_is_preserved(self):
        path = HERE.parent / "patch-regressions/regression-presets.json"
        data, records = common.regression_inventory(path, common.catalog())
        self.assertEqual(len(records), 351)
        self.assertEqual(len(data["missing_external_witnesses"]), 0)
        self.assertEqual(len(data["unresolved_name_aliases"]), 1)
        random, _ = common.select(common.catalog())
        self.assertEqual(len({row["filename"] for row in records + random}), 447)

    def test_original_q2160_trigger_profiles_cover_exact_nine_asset_set(self):
        path = HERE.parent / "patch-regressions/regression-presets.json"
        _, records = common.regression_inventory(path, common.catalog())
        evidence = json.loads((HERE / "q2160-profile-evidence.json").read_text())
        self.assertEqual(len(evidence["presets"]), 9)
        self.assertEqual({row["filename"] for row in evidence["presets"]}, {
            "$$$ Royal - Mashup (191).milk",
            "A Remixed Digital Echasketch  Again 2 martin - no religion  + disco Fruits Machine + Raron + mstress + 8.milk",
            "Hexcollie - Virtual LSD (martin shader) newborns of satan.milk",
            "LuxXx - Growing Alien Organs i.milk",
            "fed - glowing 5 - fingers rmx nz+.milk",
            "fed - glowing 5 - fingers rmx.milk",
            "shifter - mosaique simple - foobar2000 nz+ covet that which is sacred.milk",
            "suksma - mood rings for masochist alien deities - portentous anskeptising.milk",
            "suksma - negative infinity for not flinching - couldn't not.milk",
        })
        profiles = common.named_profile_extensions({"named_regressions": records})
        for row in evidence["presets"]:
            self.assertIn("native4k", profiles[row["filename"]]["profiles"])
        lux = profiles["LuxXx - Growing Alien Organs i.milk"]
        self.assertEqual(lux["profiles"], ["native4k"])
        self.assertIsNone(evidence["original_profile"]["native_trails_integer"])


class ManifestContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.work = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.job = {"key": "job", "preset": "example.milk", "preset_sha256": "a" * 64,
                    "profile": "1080p", "role": "baseline", "repeat": 0, "artifact_scope": "bundled"}
        self.protocol = {"frames": 480, "profiles": {"1080p": common.PROFILES["1080p"]},
                         "backend": "android-gpu-emulator", "pcm_sha256": "b" * 64,
                         "workers": {"baseline": {"package": "owned", "abi": "arm64-v8a"}},
                         "positive_proof_frames": [120, 479]}
        self.gl = {"glVendor": "Google", "glRenderer": "Apple M4 Pro", "glVersion": "OpenGL ES 3.0",
                   "glShadingLanguageVersion": "OpenGL ES GLSL ES 3.00"}
        self.manifest = {"pcmSha256": "b" * 64, "applicationId": "owned",
                         "nativeTrailsStatus": "Standard inactive (render 1080p)",
                         "device": {"fingerprint": "frozen", "sdk": 34, "abis": ["arm64-v8a"]},
                         "frameHashesSha256": "trace", **self.gl}
        common.write(self.work / "device-state.json", {"fingerprint": "frozen", "sdk": 34, "user_id": 0})
        common.write(self.work / "gl-state.json", self.gl)
        for name, captures in (("fresh", None), ("cached", None), ("positive", [120, 479]), ("divergence", [0])):
            directory = self.work / name
            directory.mkdir()
            common.write(directory / "request.json", dict(run_sample.request(self.protocol, self.job, captures),
                                                          pcmPath="private/audio.u8", outputDir="private/output"))

    def test_complete_contract_accepts_every_render_path(self):
        for name, captures in (("fresh", None), ("cached", None), ("positive", [120, 479]), ("divergence", [0])):
            with self.subTest(path=name), mock.patch.object(run_sample, "verify", return_value=self.manifest):
                result = run_sample.verify_render_contract(self.work / name, self.work, self.protocol, self.job,
                                                           captures, bind_gl=name == "fresh")
                self.assertEqual(result, self.manifest)

    def test_pcm_device_abi_driver_and_profile_mismatches_fail_in_every_path(self):
        mutations = [
            ("pcm missing", lambda item: item.pop("pcmSha256")),
            ("pcm changed", lambda item: item.update(pcmSha256="c" * 64)),
            ("fingerprint", lambda item: item["device"].update(fingerprint="other")),
            ("sdk", lambda item: item["device"].update(sdk=35)),
            ("abi", lambda item: item["device"].update(abis=["armeabi-v7a"])),
            ("software", lambda item: item.update(glRenderer="SwiftShader")),
            ("vendor", lambda item: item.update(glVendor="other")),
            ("renderer", lambda item: item.update(glRenderer="Other GPU")),
            ("version", lambda item: item.update(glVersion="OpenGL ES 3.2")),
            ("glsl", lambda item: item.update(glShadingLanguageVersion="OpenGL ES GLSL ES 3.20")),
            ("missing gl", lambda item: item.pop("glVersion")),
            ("profile", lambda item: item.update(nativeTrailsStatus="Medium 1280×720")),
        ]
        for name, captures in (("fresh", None), ("cached", None), ("positive", [120, 479]), ("divergence", [0])):
            for label, mutate in mutations:
                with self.subTest(path=name, mutation=label):
                    changed = json.loads(json.dumps(self.manifest))
                    mutate(changed)
                    with mock.patch.object(run_sample, "verify", return_value=changed):
                        with self.assertRaises(ValueError):
                            run_sample.verify_render_contract(self.work / name, self.work, self.protocol, self.job,
                                                               captures, bind_gl=name == "fresh")

    def test_changed_capture_policy_is_rejected(self):
        path = self.work / "positive/request.json"
        record = json.loads(path.read_text())
        record["captureFrames"] = []
        common.write(path, record)
        with self.assertRaisesRegex(ValueError, "render request|Render request"):
            run_sample.verify_render_contract(path.parent, self.work, self.protocol, self.job, [120, 479])


class JavaFrameHashTests(unittest.TestCase):
    def test_top_down_rgb_alpha_exclusion_repetition_and_gl_error(self):
        javac = Path("/opt/homebrew/opt/openjdk@21/bin/javac")
        java = Path("/opt/homebrew/opt/openjdk@21/bin/java")
        if not javac.is_file():
            self.skipTest("JDK 21 is unavailable for the private Java helper control")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = {
                "android/opengl/GLES30.java": '''package android.opengl;
import java.nio.ByteBuffer;
public class GLES30 {
 public static int error=0;
 public static final int GL_PACK_ALIGNMENT=1,GL_RGBA=2,GL_UNSIGNED_BYTE=3,GL_NO_ERROR=0;
 public static void glPixelStorei(int a,int b) {}
 public static void glReadPixels(int a,int b,int c,int d,int e,int f,ByteBuffer buffer) {
  buffer.put(new byte[]{1,2,3,44,5,6,7,88,9,10,11,99,13,14,15,33});
 }
 public static int glGetError() { int value=error;error=0;return value; }
}''',
                "org/json/JSONArray.java": "package org.json; public class JSONArray { public int length(){return 0;} public int getInt(int i){return 0;} }",
                "org/json/JSONObject.java": "package org.json; public class JSONObject { public JSONArray optJSONArray(String key){return null;} }",
                "nl/neerdael/projectmtv/corpus/Control.java": '''package nl.neerdael.projectmtv.corpus;
import java.io.File;import java.nio.ByteBuffer;import android.opengl.GLES30;
public class Control { public static void main(String[] args)throws Exception {
 try(EveryFrameHashes hashes=new EveryFrameHashes(new File(args[0]),2,2)) {
  ByteBuffer buffer=ByteBuffer.allocateDirect(16);
  hashes.writeFrame(0,buffer);hashes.writeFrame(1,buffer);
  GLES30.error=1282;
  try { hashes.writeFrame(2,buffer);throw new AssertionError("GL error ignored"); }
  catch(IllegalStateException expected) {}
 }
} }''',
            }
            for name, text in sources.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            helper = root / "nl/neerdael/projectmtv/corpus/EveryFrameHashes.java"
            shutil.copyfile(HERE / "harness/EveryFrameHashes.java", helper)
            subprocess.run([str(javac), "-d", str(root / "classes")] + [str(path) for path in root.rglob("*.java")],
                           capture_output=True, text=True, check=True)
            output = root / "frame-hashes.jsonl"
            subprocess.run([str(java), "-cp", str(root / "classes"), "nl.neerdael.projectmtv.corpus.Control", str(output)],
                           capture_output=True, text=True, check=True)
            rows = [json.loads(line) for line in output.read_text().splitlines()]
            wanted = hashlib.sha256(bytes([9,10,11,13,14,15,1,2,3,5,6,7])).hexdigest()
            self.assertEqual(len(rows), 2)
            self.assertEqual([row["rgbSha256"] for row in rows], [wanted, wanted])


if __name__ == "__main__":
    unittest.main()
