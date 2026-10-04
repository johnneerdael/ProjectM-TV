import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import run

class HostTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.work=Path(self.temp.name)
        raw=b"\x01\x02\x03\x04\x05\x06"
        (self.work/"frame-0000.rgb").write_bytes(raw)
        (self.work/"frame-0001.rgb").write_bytes(raw)
        sha=hashlib.sha256(raw).hexdigest()
        self.job={"schema_version":2,"job_id":"job","protocol_sha256":"protocol","preset_filename":"exact.milk",
                  "preset_sha256":"source","width":2,"height":1,"fps":30,"seed":12345,
                  "warmup_frames":0,"measurement_frames":2,"capture_mode":"selected","capture_frames":[0,1],
                  "expected_core_sha256":"core","retain_native_frames":True}
        self.result={"schema_version":2,"job_id":"job","protocol_sha256":"protocol","status":"success",
                     "rendered_frames":2,"capture_mode":"selected","capture_frames":[0,1],"core_sha256":"core",
                     "width":2,"height":1,"fps":30,"seed":12345,"eligible_count":1,
                     "requested_preset_sha256":"source",
                     "selected_files":[{"frame":i,"path":f"frame-{i:04d}.rgb","bytes":6,"sha256":sha} for i in range(2)]}
        self.frames=[{"frame":i,"preset_filename":"exact.milk","change_counter":1,"sha256":sha,"captured":True,"pcm_bytes":1470} for i in range(2)]
        trace=self.work/"frames.jsonl";trace.write_text("".join(json.dumps(row)+"\n" for row in self.frames))
        self.result["frames_metadata_sha256"]=run.file_hash(trace)
    def tearDown(self):self.temp.cleanup()
    def test_shipping_frame_selections_cover_short_and_long_windows(self):
        self.assertEqual(run.frame_picks(120),[120,150,180,210,239])
        self.assertEqual(run.frame_picks(360),[120,150,180,210,239,300,390,479])
    def test_job_key_separates_roles_modes_repeats_and_source_protocol(self):
        record={"path":"x.milk","sha256":"x"}
        keys=[run.job_key("p",record,"baseline","selected",1),run.job_key("p",record,"candidate","selected",1),
              run.job_key("p",record,"baseline","full",1),run.job_key("p",record,"baseline","selected",2),
              run.job_key("q",record,"baseline","selected",1),run.job_key("p",dict(record,sha256="changed"),"baseline","selected",1)]
        self.assertEqual(len(set(keys)),6)
    def test_adjacent_motion_pairs_include_short_and_long_windows(self):
        self.assertEqual(run.capture_indices(360),[120,121,150,151,180,181,210,211,238,239,300,301,390,391,478,479])

    def test_cached_rows_require_payload_and_retained_file_integrity(self):
        path=self.work/"row.json"
        value={"key":"key","protocol_sha256":"protocol","status":"success",
               "retained_files":[{"path":"frame-0000.rgb","sha256":run.file_hash(self.work/"frame-0000.rgb")}]}
        run.save_row(path,value)
        self.assertIsNotNone(run.read_cached(path,"key","protocol"))
        self.assertIsNone(run.read_cached(path,"key","other"))
        (self.work/"frame-0000.rgb").write_bytes(b"corrupt")
        self.assertIsNone(run.read_cached(path,"key","protocol"))

    def test_failed_apk_result_is_terminal_failed(self):
        self.result["status"]="failed";self.result["error"]="requested preset rejected"
        self.assertEqual(run.validate_result(self.job,self.result,[],self.work),"failed")

    def test_gzipped_trace_preserves_every_uncompressed_byte(self):
        path=self.work/"frames.jsonl"
        raw=b'{"frame":0,"preset_filename":"exact.milk"}\n{"frame":1,"preset_filename":"exact.milk"}\n'
        path.write_bytes(raw)
        metadata=run.compress_trace(path)
        self.assertFalse(path.exists())
        self.assertEqual(metadata["uncompressed_sha256"],hashlib.sha256(raw).hexdigest())
        self.assertEqual(metadata["uncompressed_bytes"],len(raw))
        self.assertEqual(metadata["compressed_sha256"],run.file_hash(self.work/"frames.jsonl.gz"))
        self.assertEqual([row["frame"] for row in run.read_frames(self.work)], [0,1])

    def make_repeat_rows(self):
        rows=[]
        raw=b"lossless thumbnail evidence";sha=hashlib.sha256(raw).hexdigest()
        for repeat in (1,2):
            key=f"repeat-{repeat}";directory=self.work/"jobs"/key/"output";directory.mkdir(parents=True)
            (directory/"thumb.png").write_bytes(raw)
            row={"key":key,"protocol_sha256":"protocol","status":"success",
                 "selected_native_sha256":{"120":"native"},
                 "result":{"selected_files":[{"frame":120,"thumbnail_path":"thumb.png","thumbnail_sha256":sha}]},
                 "retained_files":[{"path":"output/thumb.png","sha256":sha}]}
            run.save_row(directory.parent/"row.json",row);rows.append(row)
        return rows

    def test_repeat_png_hardlink_requires_two_verified_identical_files(self):
        first,second=self.make_repeat_rows()
        result=run.deduplicate_repeat_pngs(first,second,self.work)
        self.assertEqual(result["unique_thumbnail_files"],1)
        self.assertTrue((self.work/"jobs/repeat-1/output/thumb.png").samefile(self.work/"jobs/repeat-2/output/thumb.png"))
        self.assertIsNotNone(run.read_cached(self.work/"jobs/repeat-2/row.json","repeat-2","protocol"))

    def test_changed_repeat_png_is_rejected_before_linking(self):
        first,second=self.make_repeat_rows()
        (self.work/"jobs/repeat-2/output/thumb.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError,"checksum"):
            run.deduplicate_repeat_pngs(first,second,self.work)
        self.assertFalse((self.work/"jobs/repeat-1/output/thumb.png").samefile(self.work/"jobs/repeat-2/output/thumb.png"))

    def test_missing_repeat_png_is_explicit(self):
        first,second=self.make_repeat_rows()
        (self.work/"jobs/repeat-1/output/thumb.png").unlink()
        with self.assertRaisesRegex(ValueError,"missing"):
            run.deduplicate_repeat_pngs(first,second,self.work)

    def test_repeated_thumbnail_path_and_rerun_do_not_double_count(self):
        first,second=self.make_repeat_rows()
        first["result"]["selected_files"].append(dict(first["result"]["selected_files"][0],frame=121))
        second["result"]["selected_files"].append(dict(second["result"]["selected_files"][0],frame=121))
        one=run.deduplicate_repeat_pngs(first,second,self.work)
        before=(self.work/"jobs/repeat-2/row.json").read_bytes()
        two=run.deduplicate_repeat_pngs(first,second,self.work)
        self.assertEqual(one,two)
        self.assertEqual(one["unique_thumbnail_files"],1)
        self.assertEqual(before,(self.work/"jobs/repeat-2/row.json").read_bytes())

    def test_shared_observer_requires_same_private_instrumentation_and_harness(self):
        first={"backend_identity":{"instrumentation_sha256":"shared","harness_sources_sha256":{"x.cpp":"same"}}}
        second={"backend_identity":{"instrumentation_sha256":"different","harness_sources_sha256":{"x.cpp":"same"}}}
        with self.assertRaisesRegex(ValueError,"instrumentation|observer"):
            run.validate_observer_pair(first,second)
        second["backend_identity"]["instrumentation_sha256"]="shared"
        run.validate_observer_pair(first,second)
        second["backend_identity"]["harness_sources_sha256"]["x.cpp"]="changed"
        with self.assertRaisesRegex(ValueError,"harness|observer"):
            run.validate_observer_pair(first,second)

    def test_producer_trace_hash_mismatch_is_rejected(self):
        self.result["frames_metadata_sha256"]="wrong"
        with self.assertRaisesRegex(ValueError,"trace|metadata"):
            run.validate_result(self.job,self.result,self.frames,self.work)

    def test_pcm_block_length_is_required_every_frame(self):
        self.frames[1].pop("pcm_bytes")
        with self.assertRaisesRegex(ValueError,"PCM"):
            run.validate_result(self.job,self.result,self.frames,self.work)

    def test_thumbnail_wrong_ihdr_dimensions_is_rejected(self):
        import struct
        raw=b"\x89PNG\r\n\x1a\n"+struct.pack(">I",13)+b"IHDR"+struct.pack(">II",128,72)+b"header"
        (self.work/"thumb.png").write_bytes(raw)
        sample=self.result["selected_files"][0]
        sample.update(thumbnail_path="thumb.png",thumbnail_sha256=run.file_hash(self.work/"thumb.png"),thumbnail_bytes=len(raw))
        with self.assertRaisesRegex(ValueError,"dimensions|256"):
            run.validate_result(self.job,self.result,self.frames,self.work)

    def test_private_transport_tar_rejects_escaping_and_symlink_members(self):
        import io,tarfile
        for name,kind in (("../escape.txt",tarfile.REGTYPE),("link",tarfile.SYMTYPE)):
            archive=self.work/("bad-"+str(len(name))+".tar")
            with tarfile.open(archive,"w") as out:
                item=tarfile.TarInfo(name);item.type=kind
                if kind==tarfile.REGTYPE:item.size=3;out.addfile(item,io.BytesIO(b"bad"))
                else:item.linkname="../outside";out.addfile(item)
            with self.assertRaisesRegex(ValueError,"unsafe|link|escape"):
                run.extract_owned_tar(archive,self.work/"extracted")

    def test_private_transport_tar_preserves_job_file_bytes(self):
        import io,tarfile
        archive=self.work/"job.tar";raw=b"native-byte-evidence"
        with tarfile.open(archive,"w") as out:
            item=tarfile.TarInfo("./output/frame-0120.rgb");item.size=len(raw);out.addfile(item,io.BytesIO(raw))
        run.extract_owned_tar(archive,self.work/"extracted")
        self.assertEqual((self.work/"extracted/output/frame-0120.rgb").read_bytes(),raw)

    def test_job_stages_private_input_and_app_created_external_output(self):
        protocol={"sha256":"p","pcm":{"480":{"sha256":"audio"}},"roles":{"baseline":{"core_sha256":"core"}}}
        job=run.make_job(protocol,{"path":"x.milk","sha256":"source"},"baseline","selected",1,360)
        self.assertTrue(job["pcm_uint8_path"].startswith("/data/user/0/"+run.PACKAGE+"/files/jobs/"))
        self.assertTrue(job["output_directory"].startswith("/sdcard/Android/data/"+run.PACKAGE+"/files/jobs/"))

    def test_pre_engine_failure_does_not_require_unavailable_runtime_core_hash(self):
        self.result["status"]="failed";self.result["error"]="PCM checksum mismatch"
        self.result.pop("core_sha256")
        self.assertEqual(run.validate_result(self.job,self.result,[],self.work),"failed")

    def test_verified_success_survives_cleanup_failure_with_warning(self):
        from unittest.mock import patch
        result={"status":"success","native_verified":True}
        with patch.object(run,"adb",side_effect=RuntimeError("owned remote cleanup denied")):
            run.cleanup_verified_job("192.168.51.53:5555","files/jobs/"+"a"*64,"/sdcard/Android/data/"+run.PACKAGE+"/files/jobs/"+"a"*64,result)
        self.assertEqual(result["status"],"success")
        self.assertTrue(result["native_verified"])
        self.assertEqual(len(result["cleanup_warning"]),2)

    def test_other_device_is_rejected(self):
        with self.assertRaises(ValueError):run.validate_device("192.168.51.36:5555")
    def test_allowed_ip_serials_are_accepted(self):
        self.assertEqual(run.validate_device("192.168.51.53:5555"),"192.168.51.53:5555")
    def test_selected_native_files_validate_against_trace_hashes(self):
        self.assertEqual(run.validate_result(self.job,self.result,self.frames,self.work),"success")
    def test_wrong_current_preset_is_explicit(self):
        self.frames[1]["preset_filename"]="fallback.milk"
        self.assertEqual(run.validate_result(self.job,self.result,self.frames,self.work),"incorrect_current_preset")
    def test_truncated_native_sample_is_rejected(self):
        (self.work/"frame-0001.rgb").write_bytes(b"short")
        with self.assertRaisesRegex(ValueError,"bytes|checksum"):run.validate_result(self.job,self.result,self.frames,self.work)
    def test_selected_result_cannot_claim_full_stream_hash(self):
        self.result["sha256_all_frames"]="invented"
        with self.assertRaisesRegex(ValueError,"full|coverage"):run.validate_result(self.job,self.result,self.frames,self.work)
    def test_wrong_runtime_core_library_is_rejected(self):
        self.result["core_sha256"]="othercore"
        with self.assertRaisesRegex(ValueError,"core|provenance"):run.validate_result(self.job,self.result,self.frames,self.work)
    def test_missing_or_duplicate_frame_names_are_rejected(self):
        self.frames[1]["frame"]=0
        with self.assertRaisesRegex(ValueError,"frame|trace"):run.validate_result(self.job,self.result,self.frames,self.work)

if __name__=="__main__":unittest.main()
