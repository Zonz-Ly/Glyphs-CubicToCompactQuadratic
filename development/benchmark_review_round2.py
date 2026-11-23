"""Alternate complete fits against the correctness-only version, without pruning accuracy."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

CASES=('integer_3','pair_float','single_float','symmetric_integer','multiple_3_float','merged_unique')
MODULES=('quad_fit','search_core','segment_index','chain_fit','geometry_fit','roots_unit',
         'options_fit','fast_fit','preferences','merge_fit','tangent_constraints')


def encode(value):
    if isinstance(value,complex):return [value.real,value.imag]
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v) for v in value]
    return value


def worker(args):
    sys.path.insert(0,str(args.repo/'development'))
    import fast_fit as ff,geometry_fit as gf,search_core as sc,merge_fit as mf
    from quad_fit import split
    p=(0j,30+120j,180+10j,220+0j)
    merged=(0j,33+53j,67+53j,100+0j)
    rays=((merged[0],merged[1]-merged[0]),(merged[3],merged[2]-merged[3]))
    cases={
        'integer_3':lambda:ff.fit_corresponding([p],.5,3,integer_step=1),
        'pair_float':lambda:ff.fit(p,policy='pair',tolerance=.5),
        'single_float':lambda:ff.fit(p,policy='single',tolerance=.5),
        'symmetric_integer':lambda:ff.fit_corresponding([(0j,100j,100+100j,100+0j)],.5,3,integer_step=1),
        'multiple_3_float':lambda:ff.fit(p,policy='multiple',control_count=3,tolerance=.5),
        'merged_unique':lambda:mf.fit_merged_count(split(merged),1,1.,{}, {},tangents=rays),
    }
    def clear():ff.numeric_cache().clear();gf.quadratic_coefficients.cache_clear()
    run=cases[args.case];clear();start=time.perf_counter();result=run();elapsed=time.perf_counter()-start
    output=dict(seconds=elapsed,result=encode(result))
    if args.count:
        count=[0];original=gf.nearest_quadratic
        def nearest(*values):count[0]+=1;return original(*values)
        gf.nearest_quadratic=sc.nearest_quadratic=mf.nearest_quadratic=nearest
        clear();assert run()==result
        output['quadratic_queries']=count[0]
    print(json.dumps(output))


def main():
    repo=Path(__file__).resolve().parent.parent
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker',action='store_true');parser.add_argument('--count',action='store_true')
    parser.add_argument('--repo',type=Path,default=repo);parser.add_argument('--case',choices=CASES)
    parser.add_argument('--reference-dir',type=Path);parser.add_argument('--reference-commit',default='e679495')
    parser.add_argument('--repeats',type=int,default=5);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.worker:worker(args);return
    if args.reference_dir is None or args.output is None:parser.error('--reference-dir and --output are required')
    reference=subprocess.check_output(['git','rev-parse',args.reference_commit],cwd=repo,text=True).strip()
    for name in MODULES:
        expected=subprocess.check_output(['git','show',reference+':development/'+name+'.py'],cwd=repo)
        assert (args.reference_dir/'development'/(name+'.py')).read_bytes()==expected,name
    report=dict(python=sys.version,platform=platform.platform(),reference_commit=reference,
                source_sha256={name:hashlib.sha256((repo/'development'/(name+'.py')).read_bytes()).hexdigest() for name in MODULES},
                method='Alternating isolated processes; cold numerical/coefficient caches; timing excludes imports and query counting',cases={})
    for case in CASES:
        seconds={'corrected':[],'optimized':[]};outputs={};counts={}
        for repeat in range(args.repeats):
            order=('corrected','optimized') if repeat%2==0 else ('optimized','corrected')
            for mode in order:
                root=args.reference_dir if mode=='corrected' else repo
                cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'--worker','--repo',str(root),'--case',case]
                if repeat==0 and case=='integer_3':cmd.append('--count')
                row=json.loads(subprocess.check_output(cmd,text=True))
                seconds[mode].append(row['seconds'])
                if mode in outputs:assert row['result']==outputs[mode],(case,mode,'nondeterministic')
                outputs[mode]=row['result']
                if 'quadratic_queries' in row:counts[mode]=row['quadratic_queries']
            assert outputs['corrected']==outputs['optimized'],(case,'different complete output')
        medians={mode:statistics.median(values) for mode,values in seconds.items()}
        report['cases'][case]=dict(median_seconds=medians,raw_seconds=seconds,
                                  speedup=medians['corrected']/medians['optimized'],output_exact_equal=True,
                                  quadratic_queries=counts,result=outputs['optimized'])
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
        print(case,medians,flush=True)


if __name__=='__main__':main()
