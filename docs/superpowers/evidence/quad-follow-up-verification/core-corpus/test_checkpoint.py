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
    def test_explicit_failed_terminal_job_remains_checkpointable(self):
        result=checkpoint.verify_job(self.work,self.protocol,self.inventory,self.key)
        self.assertEqual(result["key"],self.key);self.assertEqual(result["status"],"failed")
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

    def test_remote_push_failure_cannot_advance_acknowledgement(self):
        self.assertFalse(checkpoint.remote_acknowledged("new","old"))
        self.assertFalse(checkpoint.remote_acknowledged("new",None))
        self.assertTrue(checkpoint.remote_acknowledged("new","new"))

if __name__=="__main__":unittest.main()
