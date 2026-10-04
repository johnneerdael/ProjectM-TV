import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest


class BehaviorEvidenceTest(unittest.TestCase):
    def setup_files(self,root):
        references=[]
        for name,kind in [('native.cpp','native_source'),('model.py','implementation'),
                          ('domain.json','domain'),('checks.json','verification')]:
            path=root/name;path.write_text(json.dumps({'kind':kind}))
            references.append({'id':kind,'role':kind,'path':name,
                               'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        return {'schema_version':1,'id':'test-certificate','status':'verified',
                'semantic_rule':'finite scalar addition in the declared context',
                'profile':'test-profile','proof_kind':'analytic','artifacts':references,
                'limitations':[]}

    def validate(self,certificate,root):
        return importlib.import_module('behavior_evidence').validate_certificate(certificate,root=root,profile='test-profile')

    def test_verified_label_without_reviewed_proof_is_not_a_certificate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);cert=self.setup_files(root)
            self.assertFalse(self.validate(cert,root)['valid'])

    def reviewed(self,cert,root):
        module=importlib.import_module('behavior_evidence')
        proof={'schema_version':1,'certificate_statement_sha256':module.statement_digest(cert),
               'status':'passed','proof_kind':'analytic','profile':'test-profile',
               'review':{'status':'accepted','reviewer':'fixture-review'},'checks':['known addition identity'],
               'domain_obligations':'closed'}
        path=root/'checks.json';path.write_text(json.dumps(proof))
        cert['artifacts'][-1]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()

    def test_artifact_mutation_invalidates_reviewed_certificate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);cert=self.setup_files(root);self.reviewed(cert,root)
            self.assertTrue(self.validate(cert,root)['valid'])
            (root/'model.py').write_text('changed behavior')
            result=self.validate(cert,root)
            self.assertFalse(result['valid'])
            self.assertIn('artifact hash mismatch: implementation',result['reasons'])

    def test_semantic_statement_change_invalidates_proof_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);cert=self.setup_files(root);self.reviewed(cert,root)
            cert['semantic_rule']='different claim'
            self.assertFalse(self.validate(cert,root)['valid'])

    def test_wrong_profile_missing_artifact_and_conditional_status_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);cert=self.setup_files(root);self.reviewed(cert,root)
            cert['profile']='another-profile'
            self.assertFalse(self.validate(cert,root)['valid'])
            cert['profile']='test-profile';cert['status']='conditional'
            self.assertFalse(self.validate(cert,root)['valid'])
            cert['status']='verified';(root/'native.cpp').unlink()
            self.assertFalse(self.validate(cert,root)['valid'])

    def test_duplicate_artifact_ids_and_paths_outside_root_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);cert=self.setup_files(root);self.reviewed(cert,root)
            cert['artifacts'].append(dict(cert['artifacts'][0]))
            self.assertFalse(self.validate(cert,root)['valid'])
            cert['artifacts'].pop();cert['artifacts'][0]['path']='../other.cpp'
            self.assertFalse(self.validate(cert,root)['valid'])

    def test_malformed_role_and_unclosed_domain_do_not_crash_or_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);cert=self.setup_files(root);self.reviewed(cert,root)
            cert['artifacts'][0]['role']=[]
            self.assertFalse(self.validate(cert,root)['valid'])
            cert['artifacts'][0]['role']='native_source';self.reviewed(cert,root)
            proof=json.loads((root/'checks.json').read_text());proof['domain_obligations']='conditional'
            (root/'checks.json').write_text(json.dumps(proof))
            cert['artifacts'][-1]['sha256']=hashlib.sha256((root/'checks.json').read_bytes()).hexdigest()
            self.assertFalse(self.validate(cert,root)['valid'])


if __name__=='__main__':unittest.main()
