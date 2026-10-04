"""Conserve original source-token ownership with physical byte provenance."""
from bisect import bisect_right
from collections import defaultdict
import argparse
import hashlib
import json
import re
from pathlib import Path


def check_ownership(tokens,units,source_size):
    ids=[token['id'] for token in tokens]
    owners=[token for unit in units for token in unit['token_ids']]
    if len(ids)!=len(set(ids)) or len(owners)!=len(set(owners)) or set(ids)!=set(owners):
        raise ValueError('token ownership is not exhaustive and disjoint')
    spans=sorted(span for token in tokens for span in token['spans']);previous=0
    for start,end in spans:
        if not 0<=start<end<=source_size or start<previous:raise ValueError('source token byte spans overlap or exceed source')
        previous=end

CODE_KEY = re.compile(r'^(per_frame_init_|per_frame_|per_pixel_|warp_|comp_|'
                      r'(?:wave|shape)_\d+_(?:init|per_frame|per_point))(\d+)$')
TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|[A-Za-z_]\w*|'
                   r'(?:0[xX][0-9a-fA-F]+|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)[fFuU]?|'
                   r'\+\+|--|&&|\|\||==|!=|<=|>=|[+*/%&|^<>-]=|\S')
COMMENT = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?(?:\*/|$)')
EEL_COMMENT = re.compile(r'//[^\n]*|\\\\[^\n]*')
SUPPORTED_PREFIXES = {'per_frame_init_', 'per_frame_', 'per_pixel_', 'warp_', 'comp_'}
SUPPORTED_PREFIXES.update(f'{kind}_{index}_{phase}' for kind in ('wave', 'shape')
                         for index in range(4) for phase in ('init', 'per_frame', 'per_point')
                         if kind == 'wave' or phase != 'per_point')


def mask_comments(text,*,shader):
    if shader:
        return COMMENT.sub(lambda m:m[0] if m[0].startswith('"') else ' '*len(m[0]),text)
    return EEL_COMMENT.sub(lambda m:' '*len(m[0]),text)


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def inventory_source(raw:bytes)->dict:
    source_sha=hashlib.sha256(raw).hexdigest();groups=defaultdict(list);first_keys=set()
    # Restrict line separators to the native CR/LF grammar; other control bytes
    # remain source rather than silently changing physical line provenance.
    for line_number,match in enumerate(re.finditer(r'[^\r\n]*(?:\r\n|\r|\n|$)',raw.decode('latin1')),1):
        physical=match[0]
        if not physical:continue
        line=physical.rstrip('\r\n');position=match.start();stripped=line.strip()
        if not stripped or stripped.startswith(('//','\\\\')) or re.fullmatch(r'\[[^\]]*\]',stripped):continue
        delimiter=re.search('[ =]',line)
        if delimiter is None or delimiter.start()==0:
            prefix='unclassified';index=None;text=line;start=position;unique=False
        else:
            key=line[:delimiter.start()];value=line[delimiter.end():];code=CODE_KEY.fullmatch(key)
            unique=key not in first_keys;first_keys.add(key)
            if code:
                prefix,index=code.groups();start=position+delimiter.end();text=value
                if text.startswith('`'):text=text[1:];start+=1
            else:prefix='configuration';index=None;text=line;start=position
        groups[prefix].append({'line':line_number,'index':index,'text':text,'start':start,'unique':unique})
    units=[];tokens=[]
    for prefix,rows in sorted(groups.items()):
        stage={'warp_':'warp','comp_':'composite'}.get(prefix,prefix if prefix in {'configuration','unclassified'} else 'eel')
        indexed={r['index']:r for r in rows if r['unique']};consumed=[]
        if prefix in SUPPORTED_PREFIXES:
            for index in range(1,100000):
                row=indexed.get(str(index))
                if row is None:break
                consumed.append(row)
        reached={r['line'] for r in consumed};omitted=[r for r in rows if r['line'] not in reached]
        for reachable,entries in [(True,consumed),(False,omitted)]:
            if not entries:continue
            text='';segments=[]
            for row in entries:
                begin=len(text);text+=row['text']+'\n'
                segments.append((begin,begin+len(row['text']),row['start'],row['line']))
            starts=[r[0] for r in segments];unit_tokens=[]
            for match in TOKEN.finditer(mask_comments(text,shader=stage in {'warp','composite'})):
                spans=[];first_line=None;cursor=max(0,bisect_right(starts,match.start())-1)
                while cursor<len(segments) and segments[cursor][0]<match.end():
                    begin,end,original,line=segments[cursor];lo=max(begin,match.start());hi=min(end,match.end())
                    if lo<hi:
                        spans.append([original+lo-begin,original+hi-begin])
                        if first_line is None:first_line=line
                    cursor+=1
                if not spans:raise ValueError('token has no original source bytes')
                token_id=digest([source_sha,spans])
                unit_tokens.append(token_id)
                tokens.append({'id':token_id,'text':text[match.start():match.end()],
                               'spans':spans,'line':first_line,'section':prefix,'stage':stage,
                               'loader_numbering_reachable':reachable})
            unit_id=digest([source_sha,prefix,reachable,unit_tokens])
            units.append({'id':unit_id,'section':prefix,'stage':stage,'source':text,
                          'source_sha256':hashlib.sha256(text.encode('latin1')).hexdigest(),
                          'lines':[r['line'] for r in entries],'loader_numbering_reachable':reachable,
                          'token_ids':unit_tokens})
    result={'schema_version':1,'preset_sha256':source_sha,'source_bytes':len(raw),
            'tokens':tokens,'units':units,'code_tokens':sum(t['stage']!='configuration' for t in tokens),
            'configuration_tokens':sum(t['stage']=='configuration' for t in tokens)}
    check_ownership(tokens,units,len(raw))
    result['inventory_sha256']=digest(result)
    return result


def validate_inventory(raw:bytes,inventory:dict)->None:
    expected=inventory_source(raw)
    if inventory!=expected:raise ValueError('source inventory/ownership does not match original bytes')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--presets',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();paths=sorted(args.presets.glob('*.milk'))
    if not paths:parser.error('no .milk files found')
    rows=[];stages=defaultdict(int)
    for count,path in enumerate(paths,1):
        inventory=inventory_source(path.read_bytes())
        for token in inventory['tokens']:stages[token['stage']]+=1
        rows.append({'preset':path.name,'preset_sha256':inventory['preset_sha256'],
                     'inventory_sha256':inventory['inventory_sha256'],'code_tokens':inventory['code_tokens'],
                     'configuration_tokens':inventory['configuration_tokens'],'units':len(inventory['units']),
                     'ownership_complete':True})
        if count%1000==0:print(f'Owned {count}/{len(paths)} presets',flush=True)
    result={'schema_version':1,'presets':len(rows),'ownership_complete':True,
            'code_tokens':sum(row['code_tokens'] for row in rows),
            'configuration_tokens':sum(row['configuration_tokens'] for row in rows),
            'stages':dict(stages),'corpus_sha256':hashlib.sha256(json.dumps([(row['preset'],row['preset_sha256']) for row in rows]).encode()).hexdigest(),
            'inventory_implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'verified_behavior_percent':None,'coverage_credit_granted':False,
            'token_storage':'byte spans/IDs regenerated deterministically from source; per-file inventory digests committed',
            'rows':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='rows'},indent=2))


if __name__=='__main__':main()
