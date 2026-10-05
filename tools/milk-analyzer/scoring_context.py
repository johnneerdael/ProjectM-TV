"""Retain v1 measurement provenance across the diagnostic-only scorer repair."""
import ast
import hashlib
import json
from pathlib import Path

LEGACY_HASH='892438f1f10f671175d19113c22795a6d7aa547bf6389044dd3f10c50fe76464'
LEGACY_PATH='profiles/scorers/beta-score-v1.py.txt'


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_identity(facts):
    body={k:v for k,v in facts.items() if k!='identity'}
    return facts.get('identity')==hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()


def numerical_program(path):
    tree=ast.parse(path.read_text())
    # Main owns resume/selection bookkeeping. Its declared inputs must separately
    # match exactly; constants, transport and all measurement code are compared.
    tree.body=[n for n in tree.body if not (
        isinstance(n,ast.FunctionDef) and n.name=='main'
        or isinstance(n,ast.ImportFrom) and n.module=='scoring_context')]
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name=='measure':
            for statement in node.body:
                if isinstance(statement,ast.Try):statement.finalbody=[]
    return ast.dump(tree,include_attributes=False)


def compatible_previous(previous,current,source=None):
    source=source or Path(__file__).parent
    archived=source/LEGACY_PATH
    if not valid_identity(previous) or not valid_identity(current):return False
    if previous.get('scorer_sha256')!=LEGACY_HASH or not archived.is_file():return False
    if file_hash(archived)!=LEGACY_HASH or file_hash(source/'beta_score.py')!=current.get('scorer_sha256'):return False
    exempt={'identity','scorer_sha256'}
    if {k:v for k,v in previous.items() if k not in exempt}!={k:v for k,v in current.items() if k not in exempt}:return False
    return numerical_program(archived)==numerical_program(source/'beta_score.py')


def source_for(facts,source=None):
    source=source or Path(__file__).parent
    if facts.get('scorer_sha256')==LEGACY_HASH and file_hash(source/LEGACY_PATH)==LEGACY_HASH:
        return LEGACY_PATH
    if facts.get('scorer_sha256')==file_hash(source/'beta_score.py'):return 'beta_score.py'
    raise ValueError('Unknown scorer source identity')
