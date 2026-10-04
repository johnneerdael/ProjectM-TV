import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import checkpoint
import run

class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.work=Path(self.temp.name)
        self.record={"path":"x.milk","sha256":"source","bytes":1}
        self.protocol={"sha256":"protocol","config":{"measurement_frames":360},"roles":{"baseline":{"core_sha256":"core"}}}
        self.inventory={"presets":[self.record]}
        self.key=run.job_key("protocol",self.record,"baseline","selected",1,360)
        self.directory=self.work/"jobs"/self.key;self.directory.mkdir(parents=True)
        self.row={"key":self.key,"protocol_sha256":"protocol","preset":self.record,"role":"baseline",
                  "capture_mode":"selected","repeat":1,"measurement_frames":360,"status":"failed",
                  "error":"APK crashed before engine", "retained_files":[]}
        run.save_row(self.directory/"row.json",self.row)
    def tearDown(self):self.temp.cleanup()
    def test_shared_checkout_rejects_second_dataset_writer(self):
        import subprocess
        repository=self.work/"shared-backup"
        subprocess.run(["git","init","-b",checkpoint.BRANCH,str(repository)],check=True,capture_output=True)
        with checkpoint.backup_writer_lock(repository):
            with self.assertRaisesRegex(RuntimeError,"another.*writer"):
                with checkpoint.backup_writer_lock(repository):
                    self.fail("second writer entered the shared checkout")

    def test_writer_lock_releases_and_different_checkouts_can_overlap(self):
        import subprocess
        first=self.work/"first-backup";second=self.work/"second-backup"
        for repository in (first,second):
            subprocess.run(["git","init","-b",checkpoint.BRANCH,str(repository)],check=True,capture_output=True)
        with checkpoint.backup_writer_lock(first):
            with checkpoint.backup_writer_lock(second):
                pass
        with checkpoint.backup_writer_lock(first):
            pass
    def test_checkpoint_normalizes_relative_dataset_before_snapshotting(self):
        import subprocess
        from types import SimpleNamespace
        from unittest.mock import patch
        repository=self.work/"relative-backup"
        subprocess.run(["git","init","-b",checkpoint.BRANCH,str(repository)],check=True,capture_output=True)
        args=SimpleNamespace(backup=repository,work=Path("relative-dataset"))
        expected=args.work.resolve()
        with patch.object(checkpoint,"_checkpoint_cycle",return_value={}) as cycle:
            checkpoint.checkpoint_cycle(args,{})
        self.assertEqual(cycle.call_args.args[0].work,expected)
    def test_explicit_failed_terminal_job_remains_checkpointable(self):
        result=checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)
        self.assertEqual(result["key"],self.key);self.assertEqual(result["status"],"failed")
    def save_failed_producer(self, result):
        packet={"schema_version":2,"job_id":self.key,"protocol_sha256":"protocol",
                "preset_filename":"x.milk","preset_sha256":"source",
                "expected_core_sha256":"core","capture_mode":"selected",
                "measurement_frames":360,"warmup_frames":120}
        run.atomic(self.directory/"job.json",packet)
        run.atomic(self.directory/"output/result.json",result)
        row=dict(self.row,result=result,retained_files=[
            {"path":"job.json","sha256":run.file_hash(self.directory/"job.json")},
            {"path":"output/result.json","sha256":run.file_hash(self.directory/"output/result.json")}])
        run.save_row(self.directory/"row.json",row)

    def test_failed_producer_wrong_identity_cannot_be_checkpointed_after_rehash(self):
        base={"schema_version":2,"job_id":self.key,"protocol_sha256":"protocol","status":"failed",
              "error":"load failed","core_sha256":"core","requested_preset_sha256":"source"}
        for field in ["job_id","protocol_sha256","core_sha256","requested_preset_sha256","status"]:
            with self.subTest(field=field):
                self.save_failed_producer(dict(base,**{field:"other"}))
                with self.assertRaisesRegex(ValueError,"producer|provenance|status"):
                    checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)

    def test_failed_row_cannot_hide_or_rewrite_retained_producer(self):
        base={"schema_version":2,"job_id":self.key,"protocol_sha256":"protocol","status":"failed","error":"load failed"}
        for remove in (False,True):
            with self.subTest(remove=remove):
                self.save_failed_producer(base)
                path=self.directory/"row.json";row=json.loads(path.read_text());row.pop("payload_sha256")
                if remove:row.pop("result")
                else:row["result"]["error"]="rewritten"
                run.save_row(path,row)
                with self.assertRaisesRegex(ValueError,"producer|result"):
                    checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)

    def test_pre_engine_failure_without_runtime_fields_remains_checkpointable(self):
        self.save_failed_producer({"schema_version":2,"job_id":self.key,"protocol_sha256":"protocol",
                                   "status":"failed","error":"PCM checksum mismatch before init"})
        result=checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)
        self.assertEqual(result["status"],"failed")
    def test_missing_result_path_cannot_hide_available_wrong_producer(self):
        self.save_failed_producer({"schema_version":2,"job_id":"wrong","protocol_sha256":"protocol",
                                   "status":"failed","error":"load failed"})
        path=self.directory/"row.json";row=json.loads(path.read_text());row.pop("payload_sha256");row.pop("result")
        row["result_path"]="missing/result.json";run.save_row(path,row)
        with self.assertRaisesRegex(ValueError,"producer|result"):
            checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)

    def test_snapshot_finds_actual_v2_runner_without_retagging_v1(self):
        import run_v2
        with tempfile.TemporaryDirectory(dir=checkpoint.ROOT/"build") as name:
            work=Path(name)
            run.atomic(work/"protocol.json",{})
            run.atomic(work/"inventory.json",{})
            protocol={"pcm":{},"roles":{},"runner_sha256":run.file_hash(Path(run_v2.__file__))}
            try:files=checkpoint.snapshot_files(work,protocol)
            except ValueError:files=[]
        self.assertIn(str(Path(run_v2.__file__)),[item["source"] for item in files])
    def test_partial_job_without_terminal_row_is_not_covered(self):
        (self.directory/"row.json").unlink()
        self.assertIsNone(checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key))
    def test_corrupt_terminal_payload_rejected(self):
        value=json.loads((self.directory/"row.json").read_text());value["role"]="candidate"
        (self.directory/"row.json").write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError,"checksum|provenance"):
            checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)
    def test_missing_declared_file_rejected(self):
        self.row["retained_files"]=[{"path":"missing.log","sha256":"a"*64}]
        run.save_row(self.directory/"row.json",self.row)
        with self.assertRaisesRegex(ValueError,"missing|checksum"):
            checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)
    def test_wrong_role_key_provenance_rejected(self):
        self.row["role"]="other";run.save_row(self.directory/"row.json",self.row)
        with self.assertRaisesRegex(ValueError,"provenance|role"):
            checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)
    def test_repeat_shared_blob_stores_one_payload_and_two_aliases(self):
        one=self.work/"first.png";two=self.work/"second.png";one.write_bytes(b"samePNG");two.write_bytes(b"samePNG")
        files=[{"source":str(one),"path":"jobs/first.png"},{"source":str(two),"path":"jobs/second.png"}]
        result=checkpoint.plan_payloads(files,set())
        self.assertEqual(len(result["payloads"]),1)
        self.assertEqual(len(result["files"]),2)
        self.assertEqual(result["files"][0]["chunks"],result["files"][1]["chunks"])
    def test_resume_uses_existing_shared_payload_without_duplicate(self):
        path=self.work/"x.png";path.write_bytes(b"data")
        sha=hashlib.sha256(b"data").hexdigest()
        result=checkpoint.plan_payloads([{"source":str(path),"path":"x.png"}],{sha})
        self.assertEqual(result["payloads"],{})
        self.assertEqual(result["files"][0]["chunks"][0]["sha256"],sha)
    def test_chunk_alias_restore_reconstructs_exact_large_file(self):
        import subprocess
        from unittest.mock import patch
        repository=self.work/"repo";repository.mkdir()
        subprocess.run(["git","init","-b",checkpoint.BRANCH,str(repository)],check=True,capture_output=True)
        for key,value in (("user.name","Checkpoint test"),("user.email","checkpoint@example.invalid")):
            subprocess.run(["git","-C",str(repository),"config",key,value],check=True,capture_output=True)
        source=self.work/"large.apk";source.write_bytes(b"0123456789abcdef012345")
        with patch.object(checkpoint,"CHUNK_SIZE",8):
            plan=checkpoint.plan_payloads([{"source":str(source),"path":"build/core.apk"}],set())
        self.assertGreater(len(plan["files"][0]["chunks"]),1)
        checkpoint.write_archive(repository,"protocol",0,plan["payloads"],plan["files"],[])
        target=self.work/"restored"
        checkpoint.restore_files(repository,"protocol",target)
        self.assertEqual((target/"build/core.apk").read_bytes(),source.read_bytes())
        checkpoint.restore_files(repository,"protocol",target)
        (target/"build/core.apk").write_bytes(b"newer")
        with self.assertRaisesRegex(ValueError,"overwrite"):
            checkpoint.restore_files(repository,"protocol",target)

    def test_real_git_failed_push_then_retry_does_not_acknowledge_old_head(self):
        import subprocess
        repository=self.work/"repo";repository.mkdir();remote=self.work/"origin.git"
        def command(*args):
            return subprocess.run(["git",*args],check=True,capture_output=True,text=True).stdout.strip()
        command("init","--bare",str(remote));command("-C",str(repository),"init","-b",checkpoint.BRANCH)
        command("-C",str(repository),"config","user.name","Checkpoint test")
        command("-C",str(repository),"config","user.email","checkpoint@example.invalid")
        (repository/"x").write_text("first");command("-C",str(repository),"add","x");command("-C",str(repository),"commit","-m","first")
        command("-C",str(repository),"remote","add","origin",str(remote));first=checkpoint.push(repository)
        (repository/"x").write_text("second");command("-C",str(repository),"commit","-am","second")
        second=command("-C",str(repository),"rev-parse","HEAD")
        command("-C",str(repository),"remote","set-url","origin",str(self.work/"missing.git"))
        with self.assertRaisesRegex(RuntimeError,"retry"):
            checkpoint.push(repository)
        self.assertEqual(command("--git-dir",str(remote),"rev-parse","refs/heads/"+checkpoint.BRANCH),first)
        command("-C",str(repository),"remote","set-url","origin",str(remote))
        self.assertEqual(checkpoint.push(repository),second)

    def test_protocol_partition_reuses_blob_without_retagging_old_evidence(self):
        import subprocess
        repository=self.work/"repo";repository.mkdir()
        subprocess.run(["git","init","-b",checkpoint.BRANCH,str(repository)],check=True,capture_output=True)
        for key,value in (("user.name","Checkpoint test"),("user.email","checkpoint@example.invalid")):
            subprocess.run(["git","-C",str(repository),"config",key,value],check=True,capture_output=True)
        source=self.work/"shared.png";source.write_bytes(b"samePNG")
        first=checkpoint.plan_payloads([{"source":str(source),"path":"old/frame.png"}],set())
        checkpoint.write_archive(repository,"old-protocol",0,first["payloads"],first["files"],[])
        known,_,_,_=checkpoint.load_archives(repository,"new-protocol",{})
        second=checkpoint.plan_payloads([{"source":str(source),"path":"new/frame.png"}],known)
        self.assertEqual(second["payloads"],{})
        checkpoint.write_archive(repository,"new-protocol",0,{},second["files"],[])
        checkpoint.restore_files(repository,"new-protocol",self.work/"new-restore")
        self.assertEqual((self.work/"new-restore/new/frame.png").read_bytes(),b"samePNG")

    def test_final_checkpoint_wakes_only_for_matching_complete_baseline(self):
        state={"protocol_sha256":"protocol","complete_baseline_remote_coverage":False}
        path=self.work/"baseline-completion-index.json"
        self.assertFalse(checkpoint.final_checkpoint_ready(self.work,state))
        path.write_text(json.dumps({"protocol_sha256":"other","complete_coverage":True,"terminal_presets":9606}))
        self.assertFalse(checkpoint.final_checkpoint_ready(self.work,state))
        path.write_text(json.dumps({"protocol_sha256":"protocol","complete_coverage":True,"terminal_presets":9606}))
        self.assertTrue(checkpoint.final_checkpoint_ready(self.work,state))
        self.assertFalse(checkpoint.final_checkpoint_ready(self.work,dict(state,complete_baseline_remote_coverage=True)))

    def test_cross_job_batches_keep_all_keys_and_deduplicate_shared_payloads(self):
        from unittest.mock import patch
        units=[]
        for i in range(20):
            path=self.work/f"file-{i}.png";path.write_bytes(b"same" if i<2 else bytes([i])*5)
            units.append({"files":[{"source":str(path),"path":f"jobs/{i}/frame.png"}],"jobs":[{"key":str(i)}]})
        with patch.object(checkpoint,"BATCH_LIMIT",12),patch.object(checkpoint,"CHUNK_SIZE",8):
            batches=list(checkpoint.coalesce_units(units,set(),{}))
        self.assertLess(len(batches),20)
        keys=[job["key"] for batch in batches for job in batch["jobs"]]
        self.assertEqual(set(keys),{str(i) for i in range(20)});self.assertEqual(len(keys),20)
        blobs=[sha for batch in batches for sha in batch["payloads"]]
        self.assertEqual(len(blobs),len(set(blobs)))
        for batch in batches:self.assertLessEqual(sum(p["bytes"] for p in batch["payloads"].values()),12)

    def test_remote_push_failure_cannot_advance_acknowledgement(self):
        self.assertFalse(checkpoint.remote_acknowledged("new","old"))
        self.assertFalse(checkpoint.remote_acknowledged("new",None))
        self.assertTrue(checkpoint.remote_acknowledged("new","new"))

if __name__=="__main__":unittest.main()
