"""Extract strict source evidence without rendering a preset or a display field."""
import argparse
import json
from pathlib import Path
import shutil

from forecast import read_source,PRODUCTION_EQUATION_SEED,CORE_2315_EQUATION_RNG_POLICY
from shader_compat import check_shader
from strict_source_features import strict_features


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preset',type=Path,required=True)
    parser.add_argument('--audio',type=Path,required=True)
    parser.add_argument('--binaries',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--profile',choices=['gles300','glsl330'],required=True)
    parser.add_argument('--width',type=int,required=True);parser.add_argument('--height',type=int,required=True)
    parser.add_argument('--mesh-x',type=int,default=48);parser.add_argument('--mesh-y',type=int,default=32)
    parser.add_argument('--equation-seed',type=int,default=PRODUCTION_EQUATION_SEED)
    parser.add_argument('--equation-rng-policy',default=CORE_2315_EQUATION_RNG_POLICY)
    parser.add_argument('--equation-loader-policy',choices=['strict-raw-v1','projectmtv-core-2.2.8-v1'],
                        default='projectmtv-core-2.2.8-v1')
    parser.add_argument('--queries',type=Path)
    parser.add_argument('--validator',type=Path)
    args=parser.parse_args()
    source=read_source(args.preset,reader=args.binaries/'milk-native-reader')
    audio=json.loads(args.audio.read_text())
    validator=args.validator or shutil.which('glslangValidator')
    if validator is None:raise ValueError('offline shader validator required')
    compatibility={}
    for stage,prefix in [('warp','warp_'),('composite','comp_')]:
        code=source.get('sections',{}).get(prefix,{}).get('source','')
        if code:
            compatibility[stage]=check_shader(code,stage=stage,profile=args.profile,
                translator=args.binaries/'milk-shader-translate',validator=Path(validator),
                samplers={'sampler_main':'sampler2D'},texture_sizes=['texsize_main'])
    domain={'profile':args.profile,'width':args.width,'height':args.height,
            'mesh_x':args.mesh_x,'mesh_y':args.mesh_y,'equation_seed':args.equation_seed,
            'equation_rng_policy':args.equation_rng_policy,'equation_loader_policy':args.equation_loader_policy,
            'shader_queries':json.loads(args.queries.read_text()) if args.queries else [{'_uv':[.5,.5]}],
            'max_shader_queries':128}
    record=strict_features(source,audio=audio,binaries=args.binaries,domain=domain,compatibility=compatibility)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    temporary=args.output.with_suffix(args.output.suffix+'.tmp')
    temporary.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n');temporary.replace(args.output)
    print(json.dumps({'basis':record['feature_basis'],'features':len(record['features']),
                      'source_sha256':record['context']['input_hashes']['preset_sha256'],'output':str(args.output)}))


if __name__=='__main__':main()
