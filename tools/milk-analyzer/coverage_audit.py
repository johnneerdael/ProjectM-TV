#!/usr/bin/env python3
"""Audit original preset source; syntax/lowering are never behavioral proof."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from source_inventory import CODE_KEY,TOKEN,COMMENT,EEL_COMMENT,SUPPORTED_PREFIXES

from shader_fields import ShaderFields


def source_tokens(text: str, *, shader: bool) -> list[str]:
    if shader:
        text = COMMENT.sub(lambda m: m[0] if m[0].startswith('"') else ' ', text)
    else:
        text = EEL_COMMENT.sub(' ', text)
    return TOKEN.findall(text)


def audit_source(raw: bytes, *, cache: dict | None = None, reader_sha: str,
                 equation_loader_policy='strict-raw-v1',shader_profile=None,shader_compatibility=None,
                 random_binding_evidence=None,asset_metadata=None,random_policy_patch_sha256=None) -> dict:
    """Count source once, including omitted code and invalid/unclassified rows.

    Latin-1 provides a lossless byte-to-character mapping for the inventory.
    Native JSON source comparison separately follows its UTF-8 display policy.
    Configuration is counted separately: a scalar assignment is not proof of
    its drawing/runtime effects. No AST node count enters the denominator.
    """
    digest = hashlib.sha256(raw).hexdigest()
    from equation_loading import select_equation
    select_equation(None,'per_frame_',policy=equation_loader_policy)
    valid_cache = (cache is not None and cache.get('preset_sha256') == digest
                   and cache.get('reader_sha256') == reader_sha)
    from equation_loading import constant_q_components
    known_q=constant_q_components(cache,policy=equation_loader_policy) if valid_cache else {}
    from equation_domains import q_uniform_domains
    known_q_domains=q_uniform_domains(cache,policy=equation_loader_policy) if valid_cache else {}
    stage_plan=None
    if shader_profile is not None and valid_cache:
        from stage_resolution import resolve_stages
        stage_plan=resolve_stages(cache,profile=shader_profile,compatibility=shader_compatibility or {})
    groups = defaultdict(list)
    first_keys = set()
    first_values = {}
    for number, line in enumerate(re.split(r'\r\n|\r|\n', raw.decode('latin1')), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(('//', '\\\\')) or re.fullmatch(r'\[[^\]]*\]', stripped):
            continue
        delimiter = re.search('[ =]', line)
        if delimiter is None or delimiter.start() == 0:
            groups['unclassified'].append((number, None, line, False))
            continue
        key = line[:delimiter.start()]
        value = line[delimiter.end():]
        match = CODE_KEY.fullmatch(key)
        unique = key not in first_keys
        first_keys.add(key)
        if unique:first_values[key]=value
        if match:
            prefix, index = match.groups()
            groups[prefix].append((number, index, value.removeprefix('`'), unique))
        else:
            groups['configuration'].append((number, None, line, unique))

    units = []
    stages = defaultdict(Counter)
    calls = defaultdict(Counter)
    unknowns = Counter()
    for prefix, rows in sorted(groups.items()):
        shader = prefix in {'warp_', 'comp_'}
        stage = {'warp_': 'warp', 'comp_': 'composite'}.get(prefix, prefix if
                prefix in {'configuration', 'unclassified'} else 'eel')
        # GetCode consumes first occurrences of keys 1..N, stopping at a gap.
        indexed = {index: (line, value) for line, index, value, unique in rows if unique}
        consumed = []
        if prefix in SUPPORTED_PREFIXES:
            for index in range(1, 100000):
                row = indexed.get(str(index))
                if row is None:
                    break
                consumed.append(row)
        consumed_lines = {line for line, _ in consumed}
        # Match the native reader's actual prefix requests and first-value map.
        # Absence of parsing is not evidence that potentially live code is safe.
        requested=cache.get('requested_code_prefixes',[]) if valid_cache else []
        native_values=cache.get('values',{}) if valid_cache else {}
        native_loader=(isinstance(requested,list) and all(isinstance(p,str) for p in requested) and
                       set(requested)==SUPPORTED_PREFIXES and isinstance(native_values,dict))
        consumed_text='\n'.join(value for _,value in consumed)+'\n' if consumed else ''
        native_section=cache.get('sections',{}).get(prefix,{}) if valid_cache else {}
        display=lambda value:value.encode('latin1').decode('utf8',errors='replace')
        native_source_matches=(native_section.get('source')==display(consumed_text) if consumed
                               else prefix not in cache.get('sections',{}) if valid_cache else False)
        first_values_match=all(native_values.get(key)==display(value) for key,value in first_values.items()
                               if CODE_KEY.fullmatch(key) and CODE_KEY.fullmatch(key)[1]==prefix)
        partitions = [(True, consumed)] if consumed else []
        omitted = [(line, value) for line, _, value, _ in rows if line not in consumed_lines]
        if omitted:
            partitions.append((False, omitted))
        for visited, entries in partitions:
            text = '\n'.join(value for _, value in entries) + '\n'
            tokens = source_tokens(text, shader=shader)
            count = len(tokens)
            section = cache.get('sections', {}).get(prefix, {}) if valid_cache and visited else {}
            expected_source = text.encode('latin1').decode('utf8', errors='replace')
            source_matches = section.get('source') == expected_source
            parsed = (source_matches and section.get('status') == 'parsed' and
                      (shader or section.get('projectm_native_status') == 'parsed'))
            selected=None
            if stage=='eel' and source_matches and 'projectm_native_compile_status' in section:
                selected=select_equation(section,prefix,policy=equation_loader_policy)
                parsed=selected['compile_status']=='accepted' and selected['tree_status']=='parsed'
            lowered = False
            reasons = []
            random_context=None
            if shader and parsed:
                stage_name='warp' if stage=='warp' else 'composite'
                bindings=None
                if stage_plan and stage_plan[stage_name]['kind']=='custom_'+stage_name:
                    requested=shader_compatibility[stage_name]['request']['samplers']
                    # A declared sampler type can make offline compilation pass
                    # without proving TextureManager preserves a random alias.
                    # Source-bound observed aliases may clear this only in their
                    # verified profile; Android and future selections stay separate.
                    random_names={name for name in requested if re.fullmatch(
                        r'sampler_(?:[A-Za-z]{2}_)?rand[0-9]+(?:_[A-Za-z0-9_]+)?',name,re.I)}
                    if not random_names:bindings=requested
                    elif random_binding_evidence is not None and random_policy_patch_sha256 is not None:
                        from random_binding_context import verified_context
                        random_context=verified_context(cache,stage=stage_name,profile=shader_profile,
                            evidence=random_binding_evidence,asset_metadata=asset_metadata or {},
                            policy_patch_sha256=random_policy_patch_sha256)
                        if (random_context is not None and random_names<=random_context['samplers'].keys() and
                                all(requested[name]==random_context['samplers'][name] for name in random_names)):
                            bindings=requested
                        else:random_context=None
                model = ShaderFields(stage='warp' if stage == 'warp' else 'composite',
                                     frame=3, warp_reads_blur=False,known_uniform_components=known_q,
                                     known_uniform_component_domains=known_q_domains,
                                     global_input_policy=section.get('implicit_global_input_policy','strict-v1'),
                                     array_initializer_policy=section.get('array_initializer_policy','legacy-layout-v1'))
                try:
                    model.lower(section['tree'],language_extensions=section.get('language_extensions',[]),native_samplers=bindings)
                    lowered = model.complete
                    reasons = [str(reason) for reason in model.unknown]
                except (KeyError, TypeError, ValueError, RecursionError) as error:
                    reasons = ['lowering audit failed: ' + str(error)]
            unit = {'section': prefix, 'stage': stage,
                    'lines': [line for line, _ in entries], 'source_tokens': count,
                    'source_sha256': hashlib.sha256(text.encode('latin1')).hexdigest(),
                    'loader_numbering_reachable': visited, 'target_parsed': bool(parsed),
                    'lowering_complete': lowered if shader else None,
                    'lowering_unknowns': reasons, 'verified_behavior': None}
            if random_context is not None:unit['random_binding_context']=random_context
            unit['loader_ignored_confirmed']=bool(stage!='configuration' and not visited and native_loader and
                                                  native_source_matches and first_values_match)
            if selected is not None:
                unit['equation_loading']={key:selected[key] for key in ['policy','assembly','compile_status','tree_status']}
                if 'warning' in selected:unit['equation_loading']['warning']=selected['warning']
            if shader and stage_plan and source_matches:
                unit['shader_stage_resolution']=stage_plan['warp' if stage=='warp' else 'composite']
            units.append(unit)
            totals = stages[stage]
            totals['source_tokens'] += count
            totals['units'] += 1
            if visited:
                totals['visited_code_tokens'] += count
            elif stage in {'eel', 'warp', 'composite', 'unclassified'}:
                totals['unvisited_code_tokens'] += count
            if parsed:
                totals['parsed_code_tokens'] += count
            if lowered:
                totals['lowering_complete_tokens'] += count
            # Lexical call names are an inventory, not AST dependency claims.
            for token, following in zip(tokens, tokens[1:]):
                if following == '(' and re.fullmatch(r'[A-Za-z_]\w*', token):
                    calls[stage][token] += 1
            unknowns.update(set(reasons))
    all_tokens = sum(row['source_tokens'] for row in stages.values())
    code_tokens = sum(row['source_tokens'] for name, row in stages.items() if name != 'configuration')
    parsed_tokens = sum(row['parsed_code_tokens'] for row in stages.values())
    return {'preset_sha256': digest, 'cache_identity_matches': bool(valid_cache),
            'source_tokens': all_tokens, 'code_tokens': code_tokens,
            'parsed_code_tokens': parsed_tokens,
            'unvisited_code_tokens': sum(row['unvisited_code_tokens'] for row in stages.values()),
            'parsed_code_token_percent': 100 * parsed_tokens / code_tokens if code_tokens else None,
            'stages': {name: dict(row) for name, row in stages.items()}, 'units': units,
            'lexical_calls': {name: dict(row) for name, row in calls.items()},
            'lowering_unknowns': dict(unknowns),
            'verified_behavior_percent': None,
            'visual_gate': {'eligible': False, 'reason':
                'Per-use execution contexts, numeric domains and behavioral evidence are not yet audited.'}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--presets', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    from equation_loading import POLICIES
    parser.add_argument('--equation-loader-policy',choices=sorted(POLICIES),default='strict-raw-v1')
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    reader_sha = summary['reader_sha256']
    cache_rows = {row['preset']: row for row in summary['rows']}
    paths = sorted(args.presets.glob('*.milk'))
    if not paths:
        parser.error('no .milk presets found')
    stages = defaultdict(Counter)
    calls = defaultdict(Counter)
    unknowns = Counter()
    presets = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    detail_path = args.output.with_suffix('.presets.jsonl')
    with detail_path.open('w') as details:
        for index, path in enumerate(paths, 1):
            row = cache_rows.get(path.name, {})
            cache = None
            if row.get('tree'):
                try:
                    cache = json.loads(Path(row['tree']).read_text())
                except (OSError, json.JSONDecodeError):
                    pass  # Missing/invalid cache is uncovered, never excluded.
            result = audit_source(path.read_bytes(), cache=cache, reader_sha=reader_sha,
                                  equation_loader_policy=args.equation_loader_policy)
            result['preset'] = path.name
            details.write(json.dumps(result, separators=(',', ':')) + '\n')
            for stage, counts in result['stages'].items():
                stages[stage].update(counts)
            for stage, counts in result['lexical_calls'].items():
                calls[stage].update(counts)
            unknowns.update(result['lowering_unknowns'])
            presets.append({key: result[key] for key in ('preset', 'preset_sha256',
                'cache_identity_matches', 'source_tokens', 'code_tokens',
                'parsed_code_tokens', 'unvisited_code_tokens')})
            if index % 1000 == 0:
                print(f'Audited {index}/{len(paths)}', flush=True)
    source_count = sum(row['source_tokens'] for row in presets)
    code_count = sum(row['code_tokens'] for row in presets)
    parsed_count = sum(row['parsed_code_tokens'] for row in presets)
    result = {'schema_version': 1, 'presets': len(paths), 'reader_sha256': reader_sha,
              'equation_loader_policy':args.equation_loader_policy,
              'audit_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'lowering_inputs': {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                  for name in ('shader_fields.py', 'sampling_policy.py','equation_loading.py')},
              'summary_sha256': hashlib.sha256(args.summary.read_bytes()).hexdigest(),
              'corpus_sha256': hashlib.sha256(json.dumps([(row['preset'], row['preset_sha256'])
                                                         for row in presets]).encode()).hexdigest(),
              'cache_identity_mismatches': sum(not row['cache_identity_matches'] for row in presets),
              'denominator': 'Original lexical tokens in numbered code values, configuration assignments '
                  'and unclassified rows; comments/blank lines/section headers excluded. '
                  'No expanded engine headers or optimized AST counts. Disabled source, duplicates, '
                  'numbering gaps and unsupported/unparsed sections retained. '
                  'Tokens weight source volume, not visual influence or semantic complexity.',
              'source_tokens': source_count, 'code_tokens': code_count,
              'parsed_code_tokens': parsed_count,
              'parsed_code_token_percent': 100 * parsed_count / code_count if code_count else None,
              'stages': {name: dict(row) for name, row in stages.items()},
              'lexical_calls': {name: dict(row.most_common()) for name, row in calls.items()},
              'lowering_unknowns': dict(unknowns.most_common()),
              'verified_behavior_percent': None,
              'missing_behavior_evidence': [
                  'source construct to implementation/reference/fixture mapping',
                  'per-use state scope, execution order and engine fallback compatibility',
                  'numeric domains, termination and undefined-operation checks',
                  'explicit materials, shader uniforms, framebuffer/audio starting state',
                  'automatic drawing/warp/blur/composite/feedback chain integration',
                  'native numeric differential or analytic proof under each declared profile'],
              'visual_gate': {'eligible': False, 'reason':
                  'Reference and fixture coverage has not established per-use behavioral coverage.'},
              'details': str(detail_path), 'rows': presets}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                     if key not in {'rows', 'lexical_calls', 'lowering_unknowns'}}, indent=2))


if __name__ == '__main__':
    main()
