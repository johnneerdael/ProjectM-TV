"""Rescore one cached source feature record without executing its preset."""
import argparse
import json
from pathlib import Path

from mood_profiles import PROFILES,get_profile
from mood_scoring import score_source_features


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--features',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    choice=parser.add_mutually_exclusive_group()
    choice.add_argument('--profile',choices=sorted(PROFILES))
    choice.add_argument('--profile-file',type=Path)
    parser.add_argument('--age-band',choices=['18–34','35–54','55–69','70+'])
    parser.add_argument('--allow-simulated',action='store_true')
    args=parser.parse_args()
    record=json.loads(args.features.read_text())
    profile=json.loads(args.profile_file.read_text()) if args.profile_file else get_profile(args.profile,age_band=args.age_band)
    result=score_source_features(record,profile=profile,allow_simulated=args.allow_simulated)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    temporary=args.output.with_suffix(args.output.suffix+'.tmp')
    temporary.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    temporary.replace(args.output)
    print(json.dumps({'model':result['model_id'],'profile':result['profile']['id'],
                      'eligible':result['profile']['eligible'],'bands':result['bands'],'output':str(args.output)}))


if __name__=='__main__':main()
