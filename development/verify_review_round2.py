"""Check exact arithmetic preservation against a local correctness-only commit."""
import argparse
import json
from pathlib import Path
import random
import subprocess


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',default='e679495')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();repo=Path(__file__).resolve().parent.parent
    import geometry_fit as gf,search_core as sc,roots_unit as ru
    def load(name):
        source=subprocess.check_output(['git','show',args.reference+':development/'+name+'.py'],cwd=repo,text=True)
        env={'__name__':'reference_'+name};exec(compile(source,'reference_'+name,'exec'),env);return env
    old_roots=load('roots_unit');old_geometry=load('geometry_fit');old_search=load('search_core')
    # The old geometry's roots import is replaced with its original solver, so
    # nearest-quadratic comparisons do not assume the new solver is equivalent.
    old_geometry['polynomial_roots_unit']=old_roots['polynomial_roots_unit']
    old_search['nearest_quadratic']=old_geometry['nearest_quadratic']
    old_search['polynomial_roots_interval']=old_roots['polynomial_roots_interval']
    rng=random.Random(20261123);counts={}
    cases=[[0,0,0,0],[0,-1,1],[-.125,.75,-1.5,1],[0,-1,0,1]]
    cases += [[rng.uniform(-1,1)*10**rng.randint(-10,10) for _ in range(4)] for _ in range(50000)]
    for coeff in cases:assert ru.polynomial_roots_unit(coeff)==old_roots['polynomial_roots_unit'](coeff),coeff
    counts['root_lists_exact']=len(cases)
    for _ in range(10000):
        q=tuple(complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(3))
        z=complex(rng.uniform(-1,1),rng.uniform(-1,1))
        assert gf.nearest_quadratic(z,q)==old_geometry['nearest_quadratic'](z,q)
    counts['quadratic_queries_exact']=10000
    queries=0
    for _ in range(12):
        p=tuple(complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(4))
        context=sc.Context(p);reference=old_search['Context'](p)
        assert context.samples==reference.samples
        for _ in range(100):
            z=complex(rng.uniform(-1,1),rng.uniform(-1,1))
            assert context.nearest(z)==reference.nearest(z),(p,z)
            queries+=1
    counts['source_queries_exact']=queries;counts['source_sample_batches_exact']=12
    flattened=0
    for _ in range(100):
        for degree in (2,3,4):
            p=tuple(complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(degree+1))
            assert gf.flatten_points(p,1e-4)==old_geometry['flatten_points'](p,1e-4)
            flattened+=1
    counts['flattened_points_and_bounds_exact']=flattened
    report=dict(reference_commit=subprocess.check_output(['git','rev-parse',args.reference],cwd=repo,text=True).strip(),checks=counts,all_exact=True)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
