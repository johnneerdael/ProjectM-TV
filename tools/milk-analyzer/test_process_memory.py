import os
from pathlib import Path
import process_memory


def test_current_process_measurement_is_positive():
    assert process_memory.process_bytes(os.getpid())>0
    assert process_memory.policy() in {'darwin-physical-footprint-v0','linux-resident-plus-swap-v1'}


def test_owned_group_does_not_measure_unrelated_processes(monkeypatch):
    monkeypatch.setattr(process_memory.subprocess,'check_output',lambda *a,**k:'10 10\n11 10\n12 12\n')
    seen=[]
    def measure(pid):seen.append(pid);return pid*100
    monkeypatch.setattr(process_memory,'process_bytes',measure)
    assert process_memory.group_bytes(10)==2100
    assert seen==[10,11]


def test_limit_boundary_is_explicit():
    assert not process_memory.exceeded(600,600)
    assert process_memory.exceeded(601,600)


def test_monitor_query_is_bounded_and_failure_is_not_zero(monkeypatch):
    import subprocess,pytest
    def hung(*args,**kwargs):
        assert kwargs.get('timeout')==2
        raise subprocess.TimeoutExpired(args[0],2)
    monkeypatch.setattr(process_memory.subprocess,'check_output',hung)
    with pytest.raises(subprocess.TimeoutExpired):process_memory.group_bytes(123)
