"""Durable per-name results and atomic, incremental paired preset archives."""
import fcntl
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import zipfile
import tempfile


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def file_hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(value,indent=2,allow_nan=False)+'\n'
    temporary=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,
                prefix=path.name+'.',suffix='.tmp',delete=False) as stream:
            temporary=Path(stream.name);stream.write(payload)
        temporary.replace(path)
    finally:
        if temporary is not None:temporary.unlink(missing_ok=True)


def discover(directory):
    root=Path(directory).resolve(strict=True);cases=[];outputs=set()
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.suffix.lower()!='.milk':continue
        if path.is_symlink():raise ValueError('symlinked preset input: '+str(path))
        name=path.relative_to(root).as_posix();output=Path(name).with_suffix('.json').as_posix().casefold()
        if output in outputs:raise ValueError('colliding result names: '+name)
        outputs.add(output);cases.append({'relative_path':name,'name':path.name,'sha256':file_hash(path),'path':str(path)})
    if not cases:raise ValueError('no .milk presets found')
    return cases


class RunStore:
    def __init__(self,output,identity,cases,*,batch_size=100):
        if type(batch_size) is not int or batch_size<1:raise ValueError('positive batch size required')
        self.output=Path(output);self.output.mkdir(parents=True,exist_ok=True)
        self.lock=(self.output/'run.lock').open('a+');self.db=None
        try:
            try:fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as error:raise RuntimeError('corpus task already running') from error
            self.batch_size=batch_size;self.cases={c['relative_path']:c for c in cases}
            self.manifest={'schema_version':1,'configuration':identity,'presets':[
                {k:c[k] for k in ('relative_path','name','sha256')} for c in cases],'batch_size':batch_size}
            self.identity=digest(self.manifest);path=self.output/'run-manifest.json'
            if path.exists():
                if json.loads(path.read_text())!=self.manifest:raise ValueError('run identity changed; use a new output directory')
            else:atomic_json(path,self.manifest)
            self.db=sqlite3.connect(self.output/'progress.sqlite');self.db.execute('PRAGMA journal_mode=WAL')
            self.db.execute('CREATE TABLE IF NOT EXISTS results(name TEXT PRIMARY KEY,file TEXT,sha TEXT,status TEXT,completed REAL,batch INTEGER)')
            self.db.execute('CREATE TABLE IF NOT EXISTS archives(number INTEGER PRIMARY KEY,file TEXT,sha TEXT)');self.db.commit()
            self._recover_results();self._recover_archives()
        except BaseException:self.close();raise

    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def close(self):
        if self.db is not None:self.db.close();self.db=None
        if self.lock is not None:self.lock.close();self.lock=None

    def _record_result(self,case,path,status):
        self.db.execute('INSERT INTO results(name,file,sha,status,completed) VALUES(?,?,?,?,?)',
            (case['relative_path'],path.relative_to(self.output).as_posix(),file_hash(path),status,time.time()));self.db.commit()

    def _recover_results(self):
        known=set()
        for name,file,sha in self.db.execute('SELECT name,file,sha FROM results').fetchall():
            if name not in self.cases:raise ValueError('result outside inventory')
            path=self.output/file
            if not path.is_file() or file_hash(path)!=sha:raise ValueError('saved result hash differs: '+name)
            known.add(name)
        for name,case in self.cases.items():
            path=self.output/'results'/Path(name).with_suffix('.json')
            if name in known or not path.exists():continue
            data=json.loads(path.read_text())
            if data.get('run_identity')!=self.identity or data.get('preset',{}).get('sha256')!=case['sha256']:
                raise ValueError('orphan result identity differs: '+name)
            self._record_result(case,path,data['status'])

    def pending(self):
        done={r[0] for r in self.db.execute('SELECT name FROM results')}
        return [case for name,case in self.cases.items() if name not in done]

    def counts(self):return {status:n for status,n in self.db.execute('SELECT status,count(*) FROM results GROUP BY status')}

    def complete(self,case,result):
        if file_hash(case['path'])!=case['sha256']:raise ValueError('preset input changed: '+case['relative_path'])
        status=result.get('status')
        if status not in {'computed','unsupported','error','timeout'}:raise ValueError('terminal result status required')
        path=self.output/'results'/Path(case['relative_path']).with_suffix('.json')
        atomic_json(path,{**result,'run_identity':self.identity,'preset':{k:case[k] for k in ('relative_path','name','sha256')}})
        self._record_result(case,path,status);self.flush()

    def _record_archive(self,number,path,manifest):
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO archives VALUES(?,?,?)',(number,path.name,file_hash(path)))
            for row in manifest['results']:
                self.db.execute('UPDATE results SET batch=? WHERE name=?',(number,row['preset']['relative_path']))

    def _recover_archives(self):
        known={n:(file,sha) for n,file,sha in self.db.execute('SELECT number,file,sha FROM archives')}
        for _,(file,sha) in known.items():
            path=self.output/file
            if not path.is_file() or file_hash(path)!=sha:raise ValueError('archive hash differs: '+file)
        for path in sorted(self.output.glob('batch-*.zip')):
            with zipfile.ZipFile(path) as z:
                manifest=json.loads(z.read('batch-manifest.json'))
                if manifest['run_identity']!=self.identity:raise ValueError('archive identity differs')
                number=manifest['batch_number']
                for row in manifest['results']:
                    name=row['preset']['relative_path'];case=self.cases.get(name)
                    if case is None or case['sha256']!=row['preset']['sha256']:raise ValueError('archive preset differs')
                    if hashlib.sha256(z.read(row['result_file'])).hexdigest()!=row['result_sha256'] or hashlib.sha256(z.read('presets/'+name)).hexdigest()!=case['sha256']:
                        raise ValueError('archive member hash differs')
                    stored=self.db.execute('SELECT sha,batch FROM results WHERE name=?',(name,)).fetchone()
                    if stored is None or stored[0]!=row['result_sha256'] or stored[1] not in (None,number):raise ValueError('archive index differs')
                if number not in known:self._record_archive(number,path,manifest)

    def flush(self,*,partial=False):
        last=None
        while True:
            rows=self.db.execute('SELECT name,file,sha,status FROM results WHERE batch IS NULL ORDER BY completed,name LIMIT ?',
                                 (self.batch_size,)).fetchall()
            if not rows or (len(rows)<self.batch_size and not partial):return last
            number=self.db.execute('SELECT COALESCE(MAX(number),0)+1 FROM archives').fetchone()[0]
            path=self.output/f'batch-{number:06d}.zip'
            if path.exists():raise ValueError('sealed archive already exists')
            manifest={'schema_version':1,'run_identity':self.identity,'batch_number':number,'completed_count':len(rows),
                      'partial':len(rows)<self.batch_size,'results':[]}
            temporary=path.with_suffix('.zip.tmp')
            try:
                with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                    for name,file,sha,status in rows:
                        case=self.cases[name];source=Path(case['path']).read_bytes();result=(self.output/file).read_bytes()
                        if hashlib.sha256(source).hexdigest()!=case['sha256']:raise ValueError('preset input changed: '+name)
                        if hashlib.sha256(result).hexdigest()!=sha:raise ValueError('result hash changed: '+name)
                        member='results/'+Path(name).with_suffix('.json').as_posix()
                        z.writestr(member,result);z.writestr('presets/'+name,source)
                        manifest['results'].append({'preset':{k:case[k] for k in ('relative_path','name','sha256')},
                            'result_file':member,'result_sha256':sha,'status':status})
                    z.writestr('batch-manifest.json',json.dumps(manifest,indent=2,allow_nan=False)+'\n')
                with zipfile.ZipFile(temporary) as z:
                    if z.testzip() is not None:raise ValueError('archive CRC verification failed')
                temporary.replace(path)
            except BaseException:temporary.unlink(missing_ok=True);raise
            self._record_archive(number,path,manifest);last=path
            print(json.dumps({'event':'archive_ready','path':str(path),'completed':len(rows)},ensure_ascii=False),flush=True)
