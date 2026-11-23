# -*- coding: utf-8 -*-
"""Geometric fitting of quadratic chains with implicit, smooth midpoint joins."""
import bisect
from quad_fit import split,single_l2,cubic,solve
from search_core import Context,pack,unpack,basis,sample_norms,score_norms,refine_lm,unique_vectors

def subdivision_seed(p,times):
    remaining=p;before=0.0;parts=[]
    for end in times[1:-1]:
        left,remaining=split(remaining,(end-before)/(1-before))
        parts.append(single_l2(left));before=end
    parts.append(single_l2(remaining))
    return pack(parts)

def least_squares_seed(p,times):
    """Fit control positions together; endpoints stay fixed."""
    count=len(times)-1;matrix=[[0.0]*count for _ in range(count)];rhs=[0j]*count
    for segment in range(count):
        for j in range(9):
            s=j/8;u=1-s;t=times[segment]*(1-s)+times[segment+1]*s
            weights=[v.real for v in basis(s,segment,count)[::2]]
            target=cubic(p,t)
            if segment==0:target-=u*u*p[0]
            if segment==count-1:target-=s*s*p[3]
            weight=(times[segment+1]-times[segment])*(.5 if j in (0,8) else 1)
            for a,wa in enumerate(weights):
                rhs[a]+=weight*wa*target
                for b,wb in enumerate(weights):matrix[a][b]+=weight*wa*wb
    real=solve(matrix,[z.real for z in rhs]);imag=solve(matrix,[z.imag for z in rhs])
    return [v for a,b in zip(real,imag) for v in (a,b)]

def arc_times(context,count,legacy=False):
    """Arc-length knots; keep the old mapping only to retain old searches."""
    lengths=[abs(b-a) for a,b in zip(context.line,context.line[1:])]
    cumulative=[0.0]
    for length in lengths:cumulative.append(cumulative[-1]+length)
    if cumulative[-1]<1e-15:return [i/count for i in range(count+1)]
    times=[0.0]
    for j in range(1,count):
        target=cumulative[-1]*j/count
        i=min(len(lengths)-1,bisect.bisect_right(cumulative,target)-1)
        local=(target-cumulative[i])/lengths[i] if lengths[i] else 0
        times.append(context.times[i]+local*(context.times[i+1]-context.times[i]) if legacy
                     else context.parameter_at(i,local))
    return times+[1.0]

def optimize_chain(p,count,geometry=None):
    """Retain the complete old search and additionally refine corrected arc knots."""
    context=Context(p,count=max(65,12*count+1),reverse_count=17,geometry=geometry)
    uniform=[i/count for i in range(count+1)];by_arc=arc_times(context,count,legacy=True)
    seeds=[subdivision_seed(p,uniform),subdivision_seed(p,by_arc)]
    try:seeds.append(least_squares_seed(p,uniform))
    except ValueError:pass
    objective=lambda x:score_norms(sample_norms(unpack(p,x),context))
    candidates=sorted((objective(x),x) for x in seeds)
    searched=list(unique_vectors([x for _,x in candidates[:2]]))
    for x in searched:
        y,score=refine_lm(p,x,context,iterations=14)
        candidates.append((score,y))
    fine=Context(p,count=max(97,16*count+1),reverse_count=25,geometry=context.geometry)
    final=lambda x:score_norms(sample_norms(unpack(p,x),fine))
    score,best=min(((final(x),x) for x in unique_vectors([x for _,x in candidates])),key=lambda r:r[0])
    improved,value=refine_lm(p,best,fine,iterations=5)
    if value<score:best=improved;score=value
    # Adding a new seed before ranking/fine refinement could displace a search
    # that used to win. Finish the old path first and retain its final result.
    corrected=subdivision_seed(p,arc_times(context,count))
    if tuple(corrected) not in {tuple(x) for x in searched}:
        alternative,value=refine_lm(p,corrected,context,iterations=14)
        extra_score,extra=min(((final(x),x) for x in unique_vectors([corrected,alternative])),key=lambda r:r[0])
        improved,value=refine_lm(p,extra,fine,iterations=5)
        if value<extra_score:extra=improved;extra_score=value
        if extra_score<score:best=extra
    return unpack(p,best),fine
