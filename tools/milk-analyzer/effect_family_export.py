"""Export static program mechanisms in resumable paired batches, without simulation."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import subprocess

from corpus_store import RunStore,atomic_json,digest,discover,file_hash
from effect_families import analyze_families,POLICY,_IMPORT_MODEL_HASHES as _FAMILY_IMPORT_HASHES
from engine_profiles import CORE_2331_ENGINE
from forecast import model_file_hashes,read_source,_MODEL_IMPORT_HASHES

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_READER=ROOT/'build/preset-corpus/source31/adapters/milk-native-reader'


def loaded_model_hashes():
    models=model_file_hashes()
    if models!=_MODEL_IMPORT_HASHES or models!=_FAMILY_IMPORT_HASHES:
        raise ValueError('static family model changed since import; start a fresh process')
    return models


def export_preset(path,*,reader=DEFAULT_READER,cache=None,profile='gles300',compatibility=None):
    """Return (stable record, cache_hit); the only native operation is parsing."""
    path=Path(path);reader=Path(reader).resolve(strict=True)
    raw=path.read_bytes();source_sha=hashlib.sha256(raw).hexdigest()
    models=loaded_model_hashes()
    identity={'policy':POLICY,'name':path.name,'preset_sha256':source_sha,
              'reader_sha256':file_hash(reader),'model_modules':models,
              'profile':profile,'compatibility':compatibility}
    key=digest(identity)
    cached=None if cache is None else Path(cache)/(key+'.json')
    if cached is not None and cached.is_file():
        saved=json.loads(cached.read_text())
        if saved.get('cache_key')!=key or saved.get('record_sha256')!=digest(saved.get('record')):
            raise ValueError('static family cache record hash mismatch')
        return saved['record'],True
    source=read_source(path,reader=reader)
    if source['preset_sha256']!=source_sha or file_hash(path)!=source_sha:
        raise ValueError('preset changed during static family analysis')
    if source['reader_sha256']!=identity['reader_sha256']:
        raise ValueError('parser changed during static family analysis')
    if source['parser_inputs']['engine']!=CORE_2331_ENGINE:
        raise ValueError('static export requires exact published31 source reader')
    source['numbered_source']=raw.decode('utf-8',errors='replace')
    analysis=analyze_families(source,profile=profile,compatibility=compatibility)
    if model_file_hashes()!=models or file_hash(reader)!=identity['reader_sha256'] or file_hash(path)!=source_sha:
        raise ValueError('static family model/parser/preset changed during analysis')
    record={'schema_version':1,'export_kind':'preset-effect-families','status':'computed',
            'preset':{'name':path.name,'sha256':source_sha},'analysis':analysis,
            'uses_rendered_reference':False,'appearance_accuracy_verified':False,
            'provenance':{'reader_sha256':identity['reader_sha256'],
                          'engine':source['parser_inputs']['engine'],
                          'engine_archive_sha256':source['parser_inputs']['engine_archive_sha256'],
                          'model_modules':models},'cache_key':key}
    if cached is not None:
        atomic_json(cached,{'cache_key':key,'record':record,'record_sha256':digest(record)})
    return record,False


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',nargs='?',type=Path,default=ROOT/'core/src/main/assets/presets')
    parser.add_argument('--reader',type=Path,default=DEFAULT_READER)
    parser.add_argument('--output',type=Path,default=Path.home()/'Downloads/ProjectM-TV-static-effect-families')
    parser.add_argument('--cache',type=Path)
    parser.add_argument('--profile',choices=('gles300','glsl330'),default='gles300')
    parser.add_argument('--batch-size',type=int,default=100)
    args=parser.parse_args(argv)
    try:
        reader=args.reader.resolve(strict=True)
        if args.source.is_file():
            if args.source.suffix.lower()!='.milk':raise ValueError('MilkDrop source file required')
            cases=[{'relative_path':args.source.name,'name':args.source.name,
                    'path':str(args.source.resolve()),'sha256':file_hash(args.source)}]
        else:cases=discover(args.source)
        identity={'export_kind':'preset-effect-families','policy':POLICY,
                  'reader_sha256':file_hash(reader),'model_modules':loaded_model_hashes(),
                  'profile':args.profile,'source_engine':CORE_2331_ENGINE,
                  'simulation':False,'AI_involved':False}
        cache=args.cache or args.output/'cache'
        with RunStore(args.output,identity,cases,batch_size=args.batch_size) as store:
            pending=store.pending()
            print(json.dumps({'event':'ready','presets':len(cases),'pending':len(pending),
                              'simulation':False,'AI_involved':False,'output':str(args.output)}),flush=True)
            for case in pending:
                if model_file_hashes()!=identity['model_modules'] or file_hash(reader)!=identity['reader_sha256']:
                    raise ValueError('static analysis identity changed; start a new run after edits finish')
                started=time.perf_counter();hit=False
                try:
                    result,hit=export_preset(case['path'],reader=reader,cache=cache,profile=args.profile)
                except Exception as error:
                    result={'export_kind':'preset-effect-families',
                            'status':'timeout' if isinstance(error,subprocess.TimeoutExpired) else 'error','analysis':None,
                            'error_type':type(error).__name__,'error':str(error),
                            'uses_rendered_reference':False,'appearance_accuracy_verified':False}
                store.complete(case,result)
                print(json.dumps({'event':'preset_completed','preset':case['name'],'status':result['status'],
                                  'cache_hit':hit,'elapsed_seconds':round(time.perf_counter()-started,6),
                                  'counts':store.counts()}),flush=True)
            store.flush(partial=True)
            print(json.dumps({'event':'finished','counts':store.counts(),'simulation':False}),flush=True)
            return 1 if any(store.counts().get(status,0) for status in ('error','timeout')) else 0
    except (ValueError,OSError,RuntimeError) as error:
        print('Static family export stopped: '+str(error),file=sys.stderr)
        return 2


if __name__=='__main__':raise SystemExit(main())
