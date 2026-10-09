"""Read only this runner's owned process groups; include compressed/swap memory."""
import ctypes
import errno
from pathlib import Path
import subprocess
import sys


class _DarwinUsage(ctypes.Structure):
    # macOS SDK sys/resource.h rusage_info_v0 (RUSAGE_INFO_V0=0).
    _fields_=[('uuid',ctypes.c_uint8*16)]+[(name,ctypes.c_uint64) for name in
        ('user_time','system_time','pkg_idle_wkups','interrupt_wkups','pageins',
         'wired_size','resident_size','phys_footprint','start_time','exit_time')]


_POLICY={'darwin':'darwin-physical-footprint-v0','linux':'linux-resident-plus-swap-v1'}


def policy():
    key='linux' if sys.platform.startswith('linux') else sys.platform
    if key not in _POLICY:raise ValueError('worker memory monitoring requires macOS or Linux')
    return _POLICY[key]


def process_bytes(pid):
    if sys.platform=='darwin':
        lib=ctypes.CDLL('/usr/lib/libproc.dylib',use_errno=True)
        call=lib.proc_pid_rusage;call.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_void_p];call.restype=ctypes.c_int
        value=_DarwinUsage()
        if call(pid,0,ctypes.byref(value)):
            error=ctypes.get_errno()
            if error==errno.ESRCH:return 0
            raise OSError(error,'cannot read owned worker footprint',pid)
        return value.phys_footprint
    if sys.platform.startswith('linux'):
        try:text=Path('/proc',str(pid),'status').read_text()
        except FileNotFoundError:return 0
        fields={line.split(':',1)[0]:line.split(':',1)[1].split() for line in text.splitlines() if ':' in line}
        return sum(int(fields.get(name,['0'])[0])*1024 for name in ('VmRSS','VmSwap'))
    policy()


def group_bytes(pgid):
    listing=subprocess.check_output(['ps','-axo','pid=,pgid='],text=True,timeout=2)
    pids=[int(row.split()[0]) for row in listing.splitlines()
          if len(row.split())==2 and int(row.split()[1])==pgid]
    return sum(process_bytes(pid) for pid in pids)


def exceeded(footprint,limit):return footprint>limit
