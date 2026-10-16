# -*- coding: utf-8 -*-
"""Fit adjacent cubic pieces jointly, then partition without losing selected data."""
import math
from concurrent.futures import CancelledError
from quad_fit import cubic,quadratic,single_l2,solve,diagnostics,intersection
from geometry_fit import geometric_bounds,nelder_mead,nearest_quadratic
from search_core import Context,basis,pack,unpack,sample_norms,score_norms,refine_lm,numeric_cache
from chain_fit import subdivision_seed
from fast_fit import fit_corresponding,select_simpler
from preferences import validated_settings
from options_fit import adjust_parts,center_parts
from tangent_constraints import smooth_join,TangentConflict

class CompositeContext:
    def __init__(self,curves,count=65,reverse_count=25,geometry=None):
        self.curves=curves;self.p=(curves[0][0],curves[0][1],curves[-1][2],curves[-1][3])
        self.reverse_count=reverse_count
        self.boxes=[(min(z.real for z in p),max(z.real for z in p),min(z.imag for z in p),max(z.imag for z in p)) for p in curves]
        self.box_allowance=max([1.0]+[abs(z) for p in curves for z in p])*1e-12
        if geometry is None:
            contexts=[Context(p,2,reverse_count) for p in curves];line=[];edges=[]
            for i,context in enumerate(contexts):
                line.extend(context.line if not line else context.line[1:])
                edges.extend((i,j) for j in range(len(context.line)-1))
            self.geometry=(contexts,line,edges)
        else:self.geometry=geometry
        self.contexts,self.line,self.edges=self.geometry
        self.prune_source=sum(len(c.line) for c in self.contexts)>32
        lengths=[abs(b-a) for a,b in zip(self.line,self.line[1:])]
        total=sum(lengths);edge=0;before=0.0;self.samples=[]
        for i in range(count):
            target=total*i/(count-1)
            while edge<len(lengths)-1 and before+lengths[edge]<target:before+=lengths[edge];edge+=1
            local=(target-before)/lengths[edge] if lengths[edge] else 0.0
            piece,j=self.edges[edge];context=self.contexts[piece]
            t=context.times[j]+local*(context.times[j+1]-context.times[j])
            weight=(.5 if i in (0,count-1) else 1.0)/(count-1)
            self.samples.append((cubic(curves[piece],t),weight))

    def nearest(self,z):
        if not self.prune_source:
            candidates=[(abs(point-z),i,point,t) for i,c in enumerate(self.contexts) for point,t in [c.nearest(z)]]
            best=min(candidates,key=lambda r:r[:2]);return best[2],(best[1],best[3])
        lower=lambda b:math.hypot(max(b[0]-z.real,0,z.real-b[1]),max(b[2]-z.imag,0,z.imag-b[3]))
        ranked=sorted((lower(box),i) for i,box in enumerate(self.boxes));best=None
        for bound,i in ranked:
            if best is not None and bound-self.box_allowance>best[0]:continue
            point,t=self.contexts[i].nearest(z);candidate=(abs(point-z),i,point,t)
            if best is None or candidate[:2]<best[:2]:best=candidate
        return best[2],(best[1],best[3])

    def tangent(self,t):
        return self.contexts[t[0]].tangent(t[1])

    def interior(self,t):
        return self.contexts[t[0]].interior(t[1])

def composite_seed(context,count):
    matrix=[[0.0]*count for _ in range(count)];rhs=[0j]*count
    for index,(z,weight) in enumerate(context.samples):
        t=index/(len(context.samples)-1);segment=min(count-1,int(t*count));s=t*count-segment;u=1-s
        coefficients=[v.real for v in basis(s,segment,count)[::2]]
        target=z
        if segment==0:target-=u*u*context.p[0]
        if segment==count-1:target-=s*s*context.p[3]
        active=[(i,v) for i,v in enumerate(coefficients) if v]
        for i,a in active:
            rhs[i]+=weight*a*target
            for j,b in active:matrix[i][j]+=weight*a*b
    real=solve(matrix,[z.real for z in rhs]);imag=solve(matrix,[z.imag for z in rhs])
    return [v for a,b in zip(real,imag) for v in (a,b)]

def optimize_composite(curves,count,geometry=None):
    if count==1:
        proxy=(curves[0][0],curves[0][1],curves[-1][2],curves[-1][3]);exact=intersection(proxy)
        allowance=max([1.0]+[abs(z) for p in curves for z in p])*1.01e-10
        if exact is not None and single_quadratic_bound(curves,exact)<=allowance:return [exact],geometry
    context=CompositeContext(curves,max(65,16*len(curves)+1,12*count+1),17,geometry)
    p=context.p;seeds=[subdivision_seed(p,[i/count for i in range(count+1)])]
    try:seeds.append(composite_seed(context,count))
    except ValueError:pass
    if count==len(curves):seeds.append(pack([single_l2(p) for p in curves]))
    objective=lambda x:score_norms(sample_norms(unpack(p,x),context))
    candidates=sorted(((objective(x),x) for x in seeds),key=lambda r:r[0])
    for _,x in candidates[:2]:
        y,value=refine_lm(p,x,context,iterations=14);candidates.append((value,y))
    score,x=min(candidates,key=lambda r:r[0])
    if count==1:
        after,y=nelder_mead(objective,x,step=.004,iterations=100)
        if after<score:x=y
    fine=CompositeContext(curves,max(97,20*len(curves)+1,16*count+1),25,context.geometry)
    final=lambda x:score_norms(sample_norms(unpack(p,x),fine))
    score,x=min(((final(v),v) for v in [x]+[y for _,y in candidates]),key=lambda r:r[0])
    y,value=refine_lm(p,x,fine,iterations=5)
    if value<score:x=y
    return unpack(p,x),fine.geometry

def single_quadratic_bound(curves,q):
    """A monotone parameter correspondence gives a conservative control-hull bound."""
    times=[0.0]+[nearest_quadratic(p[3],q)[1] for p in curves[:-1]]+[1.0]
    if any(b<a for a,b in zip(times,times[1:])):return float('inf')
    upper=0.0
    for p,a,b in zip(curves,times,times[1:]):
        start=quadratic(q,a);end=quadratic(q,b)
        control=start+(b-a)*((1-a)*(q[1]-q[0])+a*(q[2]-q[1]))
        elevated=(start,(start+2*control)/3,(2*control+end)/3,end)
        upper=max(upper,max(abs(x-y) for x,y in zip(p,elevated)))
    return upper+max([1.0]+[abs(z) for p in curves for z in p]+list(map(abs,q)))*1e-10

def fit_merged_count(curves,count,tolerance,geometries,bounds_cache,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,cancel=None,tangents=None,center_tolerance=None):
    origin=curves[0][0];scale=max([abs(z-origin) for p in curves for z in p]+[1e-9])
    normal=tuple(tuple((z-origin)/scale for z in p) for p in curves)
    cache=numeric_cache();key=('merged',normal,count)
    if key not in cache:
        cache[key],geometries[normal]=optimize_composite(normal,count,geometries.get(normal))
        while len(cache)>64:cache.pop(next(iter(cache)))
    parts=[tuple(origin+scale*z for z in q) for q in cache[key]]
    parts=adjust_parts(curves,parts,tolerance,0.0,integer_step,explicit_midpoint,
                       context_factory=CompositeContext,cancel=cancel,tangents=tangents)
    if center_limit:
        parts=center_parts(curves,parts,tolerance if center_tolerance is None else center_tolerance,
                           center_limit,integer_step,tangents,cancel)
    proxy=(curves[0][0],curves[0][1],curves[-1][2],curves[-1][3])
    bound=single_quadratic_bound(curves,parts[0]) if count==1 else float('inf')
    error=(0.0,bound) if bound<=tolerance else geometric_bounds(
        proxy,parts,tolerance,accuracy=min(max(.002,tolerance*.02),tolerance*.1),
        reject_above=tolerance,source_cache=bounds_cache,source_curves=curves)
    return dict(parts=parts,error=error,within=error[1]<=tolerance,angles=diagnostics(proxy,parts),tangents=tangents or (None,None))

def try_merged_corresponding(chains,tolerance,max_controls,cancel=None,tangents=None,**options):
    geometries={};bounds_cache={};candidates=[]
    def compute(i,count):
        if cancel is not None and cancel():raise CancelledError()
        extra=dict(options)
        if tangents is not None:extra['tangents']=tangents[i]
        try:return fit_merged_count(chains[i],count,tolerance,geometries,bounds_cache,cancel=cancel,**extra)
        except TangentConflict:return None
    def measure(i,r,limit):
        if r['error'] is None or not r['within']:
            curves=chains[i];proxy=(curves[0][0],curves[0][1],curves[-1][2],curves[-1][3])
            r['error']=geometric_bounds(proxy,r['parts'],tolerance,
                accuracy=min(max(.002,tolerance*.02),tolerance*.1),reject_above=limit,
                source_cache=bounds_cache,source_curves=curves)
            r['within']=r['error'][1]<=tolerance
        return r['error']
    for count in range(1,max_controls+1):
        results=[]
        for i in range(len(chains)):
            r=compute(i,count);results.append(r)
            if r is None or not r['within']:break
        candidates.append(results)
        if len(results)==len(chains) and all(r is not None and r['within'] for r in results):
            return select_simpler(candidates,len(chains),tolerance/2,compute,measure,cancel,ceiling=tolerance)
    return None

def fit_run_corresponding(chains,tolerance=.5,max_controls=2,cyclic=False,cancel=None,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,single_tolerance=None,angle_limit=2.0,tangents=None,center_tolerance=None,join_tangents=None):
    """Whole first; failed runs choose a complete, non-overlapping partition."""
    settings=validated_settings(tolerance,max_controls,angle_limit=angle_limit);tolerance=settings['deviation'];max_controls=settings['max_controls'];angle_limit=settings['angle_limit']
    chains=tuple(tuple(map(tuple,chain)) for chain in chains)
    if not chains:raise ValueError('Invalid corresponding curve runs')
    length=len(chains[0])
    if any(len(chain)!=length for chain in chains) or not length:raise ValueError('Invalid corresponding curve runs')
    if any(len(p)!=4 or any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in p) for chain in chains for p in chain):raise ValueError('Invalid cubic coordinates')
    if any(a[3]!=b[0] for chain in chains for a,b in zip(chain,chain[1:])):raise ValueError('Non-contiguous cubic run')
    if cyclic and any(chain[-1][3]!=chain[0][0] for chain in chains):raise ValueError('Non-closed cubic run')
    options=dict(center_limit=center_limit,integer_step=integer_step,explicit_midpoint=explicit_midpoint) if center_limit or integer_step else {}
    single_tolerance=tolerance if single_tolerance is None else single_tolerance
    center_tolerance=tolerance if center_tolerance is None else center_tolerance
    candidates={}
    def candidate(start,count):
        if cancel is not None and cancel():raise CancelledError()
        key=(start%length,count)
        if key not in candidates:
            boundary_tangents=[(pair[0] if start%length==0 else None,pair[1] if (start+count)%length==0 else None) for pair in tangents] if tangents is not None else None
            if join_tangents is not None:
                boundary_tangents=[(pairs[start%length][0],pairs[(start+count-1)%length][1]) for pairs in join_tangents]
            extra=dict(options)
            if boundary_tangents is not None:extra['tangents']=boundary_tangents
            if count==1:
                candidates[key]=fit_corresponding([chain[start%length] for chain in chains],single_tolerance,max_controls,cancel,center_tolerance=center_tolerance,comparison_tolerance=tolerance,**extra)
            else:
                subset=[tuple(chain[(start+i)%length] for i in range(count)) for chain in chains]
                smooth=all(smooth_join(a,b,angle_limit) for chain in subset for a,b in zip(chain,chain[1:]))
                candidates[key]=try_merged_corresponding(subset,tolerance,max_controls,cancel,center_tolerance=center_tolerance,**extra) if smooth else None
        return candidates[key]
    if length==1:return [dict(start=0,count=1,fits=candidate(0,1))]
    whole=candidate(0,length)
    if whole is not None:return [dict(start=0,count=length,fits=whole)]
    def partition(rotation):
        best=[None]*(length+1);best[length]=((0,0.0,0),[])
        for offset in range(length-1,-1,-1):
            choices=[]
            for count in range(length-offset,0,-1):
                fits=candidate(rotation+offset,count)
                if fits is None:continue
                tail,blocks=best[offset+count]
                error=max(r['error'][1] for r in fits) if count>1 else 0.0
                cost=(tail[0]+1,max(error,tail[1]),tail[2]+len(fits[0]['parts']))
                block=dict(start=(rotation+offset)%length,count=count,fits=fits)
                choices.append((cost,[block]+blocks))
            best[offset]=min(choices,key=lambda r:r[0])
        return best[0]
    return min((partition(i) for i in range(length if cyclic else 1)),key=lambda r:r[0])[1]
