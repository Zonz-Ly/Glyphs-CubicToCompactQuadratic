"""Small reproducible review cases; not a whole-font or native Glyphs benchmark."""
import argparse
import importlib
import json
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import time


def encode(value):
    if isinstance(value,complex):return [value.real,value.imag]
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v) for v in value]
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--revision',help='Revision label for an exported source tree without .git')
    args=parser.parse_args();sys.path.insert(0,str(args.repo.resolve()/'development'))
    ff=importlib.import_module('fast_fit');gf=importlib.import_module('geometry_fit')
    sc=importlib.import_module('search_core');mf=importlib.import_module('merge_fit')
    rng=random.Random(509);queries=[]
    for _ in range(30):
        q=tuple(complex(rng.uniform(-2,2),rng.uniform(-2,2)) for _ in range(3))
        for _ in range(65):queries.append((complex(rng.uniform(-3,3),rng.uniform(-3,3)),q))
    p=(0j,30+120j,180+10j,220+0j)
    symmetric=(0j,100j,100+100j,100+0j)
    simple=(0j,33+66j,66.5+67j,100+0j)
    rays=((simple[0],simple[1]-simple[0]),(simple[3],simple[2]-simple[3]))
    parts=sc.unpack(p,[0,40,100,100,210,20])
    curves=tuple((complex(i),complex(i+.3,1),complex(i+.7,1),complex(i+1)) for i in range(32))
    context=mf.CompositeContext(curves)
    points=[complex(rng.uniform(-1,33),rng.uniform(-1,2)) for _ in range(100)]
    def cold(fn):
        def run():
            ff.numeric_cache().clear()
            if hasattr(gf,'quadratic_coefficients'):gf.quadratic_coefficients.cache_clear()
            return fn()
        return run
    cases={
        'nearest_1950':(lambda:[gf.nearest_quadratic(z,q) for z,q in queries],7),
        'symmetric_single':(cold(lambda:ff.fit(symmetric,policy='single')),7),
        'unique_tangents':(cold(lambda:ff.fit(simple,policy='single',tangents=rays)),7),
        'simple_float':(cold(lambda:ff.fit(simple,policy='single')),7),
        'simple_integer':(cold(lambda:ff.fit(simple,policy='single',integer_step=1)),7),
        'corresponding_integer':(cold(lambda:ff.fit_corresponding([p],tolerance=.5,max_controls=3,integer_step=1)),5),
        'bounds_three_parts':(lambda:gf.geometric_bounds(p,parts,.5),7),
        'nearest_32_curves':(lambda:[context.nearest(z) for z in points],7),
    }
    report=dict(python=sys.version,platform=platform.platform(),
                commit=args.revision or subprocess.check_output(['git','-C',str(args.repo),'rev-parse','HEAD'],text=True).strip(),cases={})
    for name,(fn,repeats) in cases.items():
        times=[]
        for _ in range(repeats):
            start=time.perf_counter();result=fn();times.append(time.perf_counter()-start)
        report['cases'][name]=dict(median_seconds=statistics.median(times),runs_seconds=times,result=encode(result))
        print(name,report['cases'][name]['median_seconds'],flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
