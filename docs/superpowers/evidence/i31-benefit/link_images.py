"""Link selected-frame observers against the already-built benchmark libraries."""
from pathlib import Path
import shlex
import subprocess

root = Path(__file__).resolve().parent
for role in ('with-0019', 'without-0019'):
    output = root / role / 'native-build'
    commands = subprocess.check_output(['ninja', '-C', str(output), '-t', 'commands',
                                        'preset-lab-worker'], text=True).splitlines()
    line = next(line for line in commands if ' -c ' + str(root / 'harness/worker.cpp') in line)
    compile_args = shlex.split(line)
    obj = root / role / 'image-worker.o'
    for flag, value in (('-c', str(root / 'image-harness/worker.cpp')), ('-o', str(obj)),
                        ('-MT', str(obj)), ('-MF', str(obj) + '.d')):
        compile_args[compile_args.index(flag) + 1] = value
    subprocess.run(compile_args, cwd=output, check=True, capture_output=True)
    line = commands[-1]
    if not line.startswith(': && ') or not line.endswith(' && :'):
        raise ValueError('Unexpected CMake linker recipe')
    link = shlex.split(line[5:-5])
    link[link.index('CMakeFiles/preset-lab-worker.dir/worker.cpp.o')] = str(obj)
    link[link.index('-o') + 1] = str(root / role / 'image-worker')
    subprocess.run(link, cwd=output, check=True, capture_output=True)
