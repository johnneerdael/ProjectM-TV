"""Source34 slot contracts retain exact parser/translator attribution."""
import copy
from pathlib import Path

from engine_profiles import CORE_2331_ENGINE,CORE_2334_ENGINE
from random_binding_contract import native_contract,recognized,verified_contract
from test_core2331_binding_contract import inputs31

SOURCE34=Path(__file__).resolve().parents[2]/'build/preset-corpus/source34/production-engine'


def test_source34_native_contract_uses_declared_identity():
    contract=native_contract(SOURCE34,identity=CORE_2334_ENGINE)
    assert contract['engine']==CORE_2334_ENGINE
    assert recognized(contract)
    assert native_contract(SOURCE34,identity={**CORE_2334_ENGINE,'patches_sha256':'0'*64}) is None


def test_matching_source34_pair_accepts_conditional_typing():
    source,compatibility=inputs31()
    contract=native_contract(SOURCE34,identity=CORE_2334_ENGINE)
    source['parser_inputs']['engine']=copy.deepcopy(CORE_2334_ENGINE)
    source['parser_inputs']['random_binding_contract']=contract
    compatibility['translation']['engine']=copy.deepcopy(CORE_2334_ENGINE)
    compatibility['translation']['random_binding_contract']=copy.deepcopy(contract)
    result=verified_contract(source,stage='composite',profile='gles300',compatibility=compatibility)
    assert result and result['engine']==CORE_2334_ENGINE
    assert result['native_driver_verified'] is False
    compatibility['translation']['engine']=copy.deepcopy(CORE_2331_ENGINE)
    assert verified_contract(source,stage='composite',profile='gles300',compatibility=compatibility) is None
