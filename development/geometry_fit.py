# -*- coding: utf-8 -*-
"""Geometric fitting with implicit quadratic joins; pure Python 3.

Optimization uses a sampled objective. Acceptance uses bidirectional
polyline Hausdorff bounds plus certified Bezier flattening bounds.
"""
import math
from roots_unit import polynomial_roots_unit
import heapq
from segment_index import IndexedLine
from quad_fit import (dot, cubic, quadratic, split, single_l2, single_weighted,
                      pair_l2, intersection, diagnostics, tangent)


def point_segment(z, a, b):
    v = b-a
    length2 = dot(v,v)
    if not length2:
        return abs(z-a)
    t = max(0.0,min(1.0,dot(z-a,v)/length2))
    return abs(z-a-t*v)


def nearest_polyline(z, line):
    if hasattr(line,'segment_index'):
        d,i,t=line.segment_index.nearest(z)
        return d,i
    best, index = float('inf'), 0
    for i in range(len(line)-1):
        d = point_segment(z,line[i],line[i+1])
        if d < best:
            best,index = d,i
    return best,index


def flatten(points, tolerance):
    """Polyline within tolerance in Hausdorff distance (exact arithmetic).

    Convex-hull distance to the finite chord bounds curve-to-chord error;
    continuous projection between endpoints bounds chord-to-curve error.
    """
    out = [points[0]]
    stack = [(tuple(points),0)]
    worst = 0.0
    while stack:
        p,depth = stack.pop()
        flatness = max(point_segment(v,p[0],p[-1]) for v in p[1:-1])
        if flatness <= tolerance or depth >= 24:
            out.append(p[-1]);worst = max(worst,flatness)
            continue
        levels=[p]
        while len(levels[-1])>1:
            levels.append(tuple((a+b)/2 for a,b in zip(levels[-1],levels[-1][1:])))
        a = tuple(row[0] for row in levels)
        b = tuple(row[-1] for row in reversed(levels))
        stack.append((b,depth+1));stack.append((a,depth+1))
    return IndexedLine(out),worst


def arc_samples(line, count):
    lengths=[abs(b-a) for a,b in zip(line,line[1:])]
    total=sum(lengths)
    if not total:
        return [line[0]]*count
    result=[];edge=0;before=0.0
    for i in range(count):
        target=total*i/(count-1)
        while edge<len(lengths)-1 and before+lengths[edge]<target:
            before+=lengths[edge];edge+=1
        t=(target-before)/lengths[edge] if lengths[edge] else 0.0
        result.append(line[edge]+min(1.0,max(0.0,t))*(line[edge+1]-line[edge]))
    return result


def nearest_quadratic(z,q):
    a=q[0]-z;b=2*(q[1]-q[0]);c=q[0]-2*q[1]+q[2]
    coeff=(dot(a,b),dot(b,b)+2*dot(a,c),3*dot(b,c),2*dot(c,c))
    candidates=[0.0,1.0]+polynomial_roots_unit(coeff)
    t=min(candidates,key=lambda t:abs(a+b*t+c*t*t))
    return abs(a+b*t+c*t*t),t


def geometric_bounds(p,parts,tolerance=1.0,accuracy=None,reject_above=None,source_cache=None,source_curves=None):
    """Conservative continuous bidirectional Hausdorff interval.

    Max iterations/depth only leave a looser upper bound, never an assumed
    sampled guarantee. Includes a scale-related floating point allowance.
    """
    accuracy=accuracy if accuracy is not None else max(.002,tolerance*.02)
    delta=accuracy/8.0
    bounds_points=tuple(p) if source_curves is None else tuple(z for q in source_curves for z in q)
    key=(tuple(p) if source_curves is None else tuple(map(tuple,source_curves)),delta)
    if source_cache is not None and key in source_cache:
        original,ea=source_cache[key]
    else:
        if source_curves is None:original,ea=flatten(p,delta)
        else:
            points=[];ea=0.0
            for curve in source_curves:
                line,error=flatten(curve,delta);points.extend(line if not points else line[1:]);ea=max(ea,error)
            original=IndexedLine(points)
        if source_cache is not None:
            if len(source_cache)>=8:source_cache.pop(next(iter(source_cache)))
            source_cache[key]=(original,ea)
    fitted=[];eb=0.0
    for q in parts:
        line,e=flatten(q,delta)
        fitted.extend(line if not fitted else line[1:]);eb=max(eb,e)
    fitted=IndexedLine(fitted)
    allowance=max([1.0]+list(map(abs,bounds_points))+[abs(v) for q in parts for v in q])*1e-10
    hull_upper=max([abs(v-p[0]) for v in bounds_points]+[abs(v-p[0]) for q in parts for v in q])+allowance
    heap=[];lower=0.0;serial=0
    def record(a,b,da,db,ia,ib,target,depth):
        nonlocal lower,serial
        lower=max(lower,da,db)
        candidates={ia,ib}
        upper=min(max(point_segment(a,target[j],target[j+1]),
                      point_segment(b,target[j],target[j+1])) for j in candidates)
        upper=min(upper,(da+db+abs(b-a))/2.0)
        heapq.heappush(heap,(-upper,serial,a,b,da,db,ia,ib,target,depth));serial+=1
    for source,target in ((original,fitted),(fitted,original)):
        distances=[]
        for z in source:
            d,i=nearest_polyline(z,target);distances.append((d,i))
            lower=max(lower,d)
            if reject_above is not None and lower-ea-eb-allowance>reject_above:
                return lower-ea-eb-allowance,hull_upper
        for i,(a,b) in enumerate(zip(source,source[1:])):
            da,ia=distances[i];db,ib=distances[i+1]
            record(a,b,da,db,ia,ib,target,0)
    for _ in range(10000):
        if reject_above is not None and lower-ea-eb-allowance>reject_above:
            break
        if not heap or -heap[0][0]-lower<=accuracy/2.0:
            break
        item=heapq.heappop(heap)
        neg,ix,a,b,da,db,ia,ib,target,depth=item
        if depth>=24:
            heapq.heappush(heap,item);break
        m=(a+b)/2;dm,im=nearest_polyline(m,target)
        record(a,m,da,dm,ia,im,target,depth+1)
        record(m,b,dm,db,im,ib,target,depth+1)
    allowance=max([1.0]+list(map(abs,bounds_points))+[abs(v) for q in parts for v in q])*1e-10
    return max(0.0,lower-ea-eb-allowance),max(lower,-heap[0][0] if heap else lower)+ea+eb+allowance


def nelder_mead(objective,initial,step=.025,iterations=180):
    """Small derivative-free local optimizer; no global-optimum claim."""
    dim=len(initial)
    vertices=[list(initial)]
    for i in range(dim):
        v=list(initial);v[i]+=step;vertices.append(v)
    scored=[(objective(v),v) for v in vertices]
    for _ in range(iterations):
        scored.sort(key=lambda r:r[0])
        if max(abs(a-b) for _,v in scored[1:] for a,b in zip(v,scored[0][1]))<2e-6:
            break
        centre=[sum(v[i] for _,v in scored[:-1])/dim for i in range(dim)]
        worst=scored[-1][1]
        reflected=[2*a-b for a,b in zip(centre,worst)];fr=objective(reflected)
        if fr<scored[0][0]:
            expanded=[3*a-2*b for a,b in zip(centre,worst)];fe=objective(expanded)
            scored[-1]=(fe,expanded) if fe<fr else (fr,reflected)
        elif fr<scored[-2][0]:
            scored[-1]=(fr,reflected)
        else:
            outside=fr<scored[-1][0]
            contracted=[(a+b)/2 for a,b in zip(centre,reflected if outside else worst)]
            fc=objective(contracted)
            if fc<(fr if outside else scored[-1][0]):scored[-1]=(fc,contracted)
            else:
                best=scored[0][1]
                scored=[scored[0]]+[(objective(v2),v2) for _,v in scored[1:]
                    for v2 in [[(a+b)/2 for a,b in zip(best,v)]]]
    return min(scored,key=lambda r:r[0])


def make_context(p,flatness=2e-5):
    line,_=flatten(p,flatness)
    return line,arc_samples(line,41)


def sampled_objective(parts,context,maximum=True):
    line,samples=context
    forward=[min(nearest_quadratic(z,q)[0] for q in parts) for z in samples]
    reverse=[]
    for q in parts:
        for i in range(25):reverse.append(nearest_polyline(quadratic(q,i/24.0),line)[0])
    if maximum:return max(forward+reverse)
    return sum(d*d for d in forward)/len(forward)+sum(d*d for d in reverse)/len(reverse)


def optimize_one(p,context,maximum=True):
    seeds=[single_l2(p)[1],single_weighted(p)[1]]
    q=intersection(p)
    if q is not None and abs(q[1]-p[0])<25:seeds.append(q[1])
    # Pick the best sampled starts; preserve the unmodified candidates too.
    ranked=sorted(seeds,key=lambda z:sampled_objective([(p[0],z,p[3])],context,maximum))
    best=[]
    for q in ranked[:2]:
        objective=lambda xy:sampled_objective([(p[0],complex(*xy),p[3])],context,maximum)
        score,xy=nelder_mead(objective,[q.real,q.imag],iterations=140)
        best.append((score,(p[0],complex(*xy),p[3])))
    for q in ranked:best.append((sampled_objective([(p[0],q,p[3])],context,maximum),(p[0],q,p[3])))
    return min(best,key=lambda r:r[0])[1]


