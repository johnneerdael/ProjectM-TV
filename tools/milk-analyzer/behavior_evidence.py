"""Fail-closed evidence-record validation, not automatic semantic certification.

Review decisions are trusted workspace artifacts. This checker validates their
binding/provenance; it cannot establish that a mathematical proof is sound or
that its conditions hold at an actual source use. Neither earns token credit yet.
"""
import hashlib
import json
from pathlib import Path
import re


ROLES={'native_source','implementation','domain','verification'}
PROOFS={'analytic','native_differential','exhaustive_profile'}


def statement_digest(certificate):
    statement={key:certificate.get(key) for key in
               ['schema_version','id','semantic_rule','profile','proof_kind','limitations']}
    references=certificate.get('artifacts',[])
    statement['artifacts']=[ref for ref in references if not isinstance(ref,dict) or ref.get('role')!='verification'] if isinstance(references,list) else references
    return hashlib.sha256(json.dumps(statement,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def file_digest(path):
    result=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):result.update(block)
    return result.hexdigest()


def validate_certificate(certificate:dict,*,root:Path,profile:str)->dict:
    reasons=[];root=root.resolve();proof=None
    if certificate.get('schema_version')!=1:reasons.append('unsupported certificate schema')
    for key in ['id','semantic_rule','profile']:
        if not isinstance(certificate.get(key),str) or not certificate[key].strip():reasons.append('missing certificate field: '+key)
    if certificate.get('profile')!=profile:reasons.append('certificate profile mismatch')
    if certificate.get('status')!='verified':reasons.append('certificate is not verified')
    if not isinstance(certificate.get('proof_kind'),str) or certificate['proof_kind'] not in PROOFS:reasons.append('unsupported proof kind')
    if certificate.get('limitations')!=[]:reasons.append('certificate has unresolved limitations')
    artifacts=certificate.get('artifacts',[]);ids=set();roles=set()
    if not isinstance(artifacts,list):artifacts=[];reasons.append('invalid artifact list')
    for ref in artifacts:
        if not isinstance(ref,dict):reasons.append('invalid artifact reference');continue
        name=ref.get('id');role=ref.get('role')
        if not isinstance(role,str) or role not in ROLES:reasons.append('invalid artifact role');continue
        roles.add(role)
        if not isinstance(name,str) or not name:reasons.append('artifact id missing');continue
        if name in ids:reasons.append('duplicate artifact id: '+name)
        ids.add(name)
        path_text=ref.get('path');expected=ref.get('sha256')
        if not isinstance(path_text,str) or not isinstance(expected,str) or not re.fullmatch('[0-9a-f]{64}',expected):
            reasons.append('invalid artifact identity: '+name);continue
        relative=Path(path_text)
        if relative.is_absolute():reasons.append('artifact path is not relative: '+name);continue
        path=(root/relative).resolve()
        if not path.is_relative_to(root):reasons.append('artifact path outside root: '+name);continue
        try:
            actual=file_digest(path)
        except OSError:
            reasons.append('artifact missing/unreadable: '+name);continue
        if actual!=expected:reasons.append('artifact hash mismatch: '+name);continue
        if role=='verification':
            if proof is not None:reasons.append('multiple verification artifacts')
            try:proof=json.loads(path.read_text())
            except (OSError,UnicodeError,json.JSONDecodeError):reasons.append('invalid verification result: '+name)
    if not ROLES.issubset(roles):reasons.append('required artifact roles missing')
    if not isinstance(proof,dict):reasons.append('reviewed verification proof missing')
    else:
        if proof.get('schema_version')!=1 or proof.get('status')!='passed':reasons.append('verification did not pass')
        if proof.get('certificate_statement_sha256')!=statement_digest(certificate):reasons.append('verification statement binding mismatch')
        if proof.get('proof_kind')!=certificate.get('proof_kind') or proof.get('profile')!=profile:reasons.append('verification proof/profile mismatch')
        if proof.get('domain_obligations')!='closed':reasons.append('verification domain obligations not closed')
        checks=proof.get('checks')
        if not isinstance(checks,list) or not checks or not all(isinstance(c,str) and c.strip() for c in checks):
            reasons.append('verification checks missing')
        review=proof.get('review',{})
        if not isinstance(review,dict) or review.get('status')!='accepted' or not isinstance(review.get('reviewer'),str) or not review['reviewer'].strip():
            reasons.append('verification review missing')
    return {'certificate_id':certificate.get('id'),'valid':not reasons,'reasons':reasons,
            'coverage_credit_granted':False,
            'scope':'artifact/proof-record checks; per-use semantics/domain closure still required'}
