"""Measure the auxiliary compiler inventory on an unchanged saved selection."""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import time

from source_shader_compiler import CompilerTools, analyze_case, sha256, validate_join


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('corpus', type=Path, help='saved sample-selection.json and compatibility directory')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--limit', type=int, default=32)
    parser.add_argument('--reader', type=Path, help='optional exact native source reader for a paired lowering inventory')
    parser.add_argument('--presets', type=Path, help='source assets corresponding to the saved selection')
    parser.add_argument('--naga-worker', type=Path)
    args = parser.parse_args(argv)
    if args.limit < 1 or bool(args.reader) != bool(args.presets):
        parser.error('positive limit and paired --reader/--presets required')
    selection_path = args.corpus/'sample-selection.json'; selection_bytes = selection_path.read_bytes()
    selection = json.loads(selection_bytes)['presets'][:args.limit]
    tools = CompilerTools(naga_worker=args.naga_worker); rows = []; args.output.mkdir(parents=True, exist_ok=True); started = time.perf_counter()
    for preset in selection:
        case_path = args.corpus/'compatibility'/Path(preset['relative_path']).with_suffix('.json')
        case_bytes = case_path.read_bytes(); case = json.loads(case_bytes)
        if case['preset']['sha256'] != preset['sha256']:
            raise ValueError('saved selection preset hash mismatch')
        result = analyze_case(case, tools); validate_join(result, case)
        if case_path.read_bytes() != case_bytes:
            raise ValueError('saved compatibility evidence changed during inspection')
        (args.output/(preset['sha256']+'.json')).write_text(json.dumps(result, indent=2) + '\n')
        source = None
        if args.reader:
            from forecast import read_source
            source = read_source(args.presets/preset['relative_path'], reader=args.reader)
            if source['preset_sha256'] != preset['sha256'] or source['parser_inputs']['engine'] != case['engine'] or source['parser_inputs']['engine_archive_sha256'] != case['engine_archive_sha256']:
                raise ValueError('paired source reader/asset engine hash mismatch')
        for stage, record in result['stages'].items():
            row = {'preset': preset, 'stage': stage, 'status': record['status'], 'seconds': record['seconds'],
                   'source_join': {k: record.get(k) for k in ('authored_source_sha256', 'request_sha256', 'translation_sha256', 'translated_glsl_sha256')}}
            if 'inspection' in record:
                original = record['inspection']['original_summary']; normalized = record['inspection']['normalized_summary']
                row.update(functions=len(original['functions']), calls=sum(len(f['calls']) for f in original['functions']),
                           loops=sum(len(f['loops']) for f in original['functions']), selections=sum(len(f['selections']) for f in original['functions']),
                           conversions=original['conversion_count'], samples=original['sample_count'], resources=len(record['inspection']['resources']),
                           original_instructions=original['instruction_count'], normalized_instructions=normalized['instruction_count'],
                           all_sample_joins=all(n['source'] and n['source']['text'] is not None for f in original['functions'] for n in f['samples']),
                           all_conversion_joins=all(n['source'] and n['source']['text'] is not None for f in original['functions'] for n in f['conversions']),
                           conversion_count_preserved=original['conversion_count']==normalized['conversion_count'],
                           sample_count_preserved=original['sample_count']==normalized['sample_count'])
                if 'naga' in record['inspection']:
                    n=record['inspection']['naga']; row['naga']={k:n.get(k) for k in ('profile','sample_count_preserved','conversion_count_preserved')}
                    row['naga']['status']=n.get('typed_ir',{}).get('status', n.get('status'))
            if source is not None:
                from shader_fields import ShaderFields
                section = source['sections']['comp_' if stage == 'composite' else 'warp_']
                if sha256(section['source']) != case['reports'][stage]['source_sha256']:
                    raise ValueError('paired authored shader hash mismatch')
                lower_started = time.perf_counter()
                model = ShaderFields(stage=stage, frame=0, warp_reads_blur=True,
                                     global_input_policy='projectmtv-implicit-extern-zero-v1', array_initializer_policy='grouped-elements-v1')
                field = model.lower(section['tree'])
                row['paired_lowering'] = {'complete': model.complete, 'unknown': model.unknown, 'root_op': field.op,
                                         'seconds': time.perf_counter()-lower_started,
                                         'scope': 'existing typed graph construction only; no shader execution'}
            rows.append(row)
    if selection_path.read_bytes() != selection_bytes:
        raise ValueError('saved selection changed during inspection')
    summary = {'fixed_presets': len(selection), 'authored_sections': len(rows), 'selection_sha256': sha256(selection_bytes),
               'statuses': dict(Counter(r['status'] for r in rows)), 'wall_seconds': time.perf_counter()-started,
               'sum_stage_seconds': sum(r['seconds'] for r in rows), 'median_seconds': statistics.median(r['seconds'] for r in rows),
               'worst_seconds': max(r['seconds'] for r in rows), 'tools': tools.identities,
               'reader_sha256': sha256(args.reader.read_bytes()) if args.reader else None,
               'paired_lowering_policy': 'frame0; warp_reads_blur=true; native implicit globals; grouped array elements',
               'new_numeric_calculations': 0, 'tighter_numeric_estimates': 0, 'predictions_changed': 0,
               'rows': rows}
    (args.output/'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in {'rows', 'tools'}}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
