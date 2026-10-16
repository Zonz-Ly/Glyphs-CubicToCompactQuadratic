# -*- coding: utf-8 -*-
"""Production geometric fitting; masters share a minimal acceptable control count."""
import math
from concurrent.futures import CancelledError
from quad_fit import single_l2,diagnostics
from geometry_fit import make_context,optimize_one,geometric_bounds,nelder_mead
from search_core import (Context,pack,unpack,pair_seeds,choose_diverse,sample_norms,
                         score_norms,refine_lm,numeric_cache)
from chain_fit import optimize_chain,subdivision_seed
from preferences import validated_settings
from options_fit import adjust_parts,center_parts
from tangent_constraints import TangentConflict

def optimize_pair(p,geometry=None):
    context=Context(p,count=33,reverse_count=17,geometry=geometry)
    seeds=pair_seeds(p,single_l2(p))
    objective=lambda x:score_norms(sample_norms(unpack(p,x),context),2)
    ranked=[(objective(x),x) for x in seeds];results=[]
    for score,x in choose_diverse(ranked,2):
        y,value=refine_lm(p,x,context,iterations=14)
        results.extend([(score,x),(value,y)])
    score,x=min(results,key=lambda r:r[0])
    after,y=nelder_mead(objective,x,step=.004,iterations=45)
    if after<score:score,x=after,y
    fine=Context(p,count=65,reverse_count=25,
                 geometry=context.geometry)
    choices=[x]+[v for _,v in results]
    final=lambda v:score_norms(sample_norms(unpack(p,v),fine),2)
    score,x=min(((final(x),x) for x in choices),key=lambda r:r[0])
    y,value=refine_lm(p,x,fine,iterations=5)
    if value<score:x=y
    return unpack(p,x),fine

def fit(p,policy='auto',tolerance=.5,control_count=2,metrics=False,check_error=True,decision_only=False,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,cancel=None,tangents=None):
    """Fixed-count policies are internal; auto retains the established one/two fit."""
    if policy not in ('single','auto','pair','probe','multiple'):raise ValueError('Unknown policy')
    values=validated_settings(deviation=tolerance,max_controls=control_count)
    tolerance=values['deviation'];control_count=values['max_controls']
    if len(p)!=4 or any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in p):
        raise ValueError('Invalid cubic coordinates')
    origin=p[0];scale=max([abs(z-origin) for z in p]+[1e-9])
    normal=tuple((z-origin)/scale for z in p)
    restore=lambda parts:[tuple(origin+scale*z for z in q) for q in parts]
    cache=numeric_cache();source_cache={};context=None;single_error=None
    while len(cache)>64:cache.pop(next(iter(cache)))
    def prepare(parts):
        return adjust_parts([p],parts,tolerance,center_limit,integer_step,explicit_midpoint,
                            context_factory=lambda curves:Context(curves[0]),cancel=cancel,tangents=tangents)
    def result(parts,error,status,norms=None):
        return dict(parts=parts,error=error,within=error[1]<=tolerance if error is not None else None,
                    angles=diagnostics(p,parts),single_error=single_error,status=status,
                    rms=score_norms(norms)*scale if norms is not None else None,tangents=tangents or (None,None))
    if abs(normal[3]-3*normal[2]+3*normal[1]-normal[0])<1e-11:
        one=single_l2(normal)
        count=2 if policy=='pair' else (control_count if policy=='multiple' else 1)
        if count==1:parts=restore([one])
        elif count==2:
            a=(one[0]+one[1])/2;b=(one[1]+one[2])/2;m=(a+b)/2
            parts=restore([(one[0],a,m),(m,b,one[2])])
        else:parts=restore(unpack(normal,subdivision_seed(normal,[i/count for i in range(count+1)])))
        original_parts=parts;parts=prepare(parts)
        error=(geometric_bounds(p,parts,tolerance,reject_above=tolerance if decision_only else None,
                               source_cache=source_cache) if parts!=original_parts else (0.0,scale*1e-10)) if check_error else None
        single_error=error
        return result(parts,error,'EXACT DEGREE REDUCTION')
    if policy not in ('pair','multiple'):
        key=('one',normal)
        if key not in cache:cache[key]=optimize_one(normal,make_context(normal),maximum=False)
        one=cache[key];parts=prepare(restore([one]))
        single_error=geometric_bounds(p,parts,tolerance,
            reject_above=tolerance if decision_only or policy in ('auto','probe') else None,
            source_cache=source_cache) if check_error else None
        if policy in ('single','probe') or not check_error or single_error[1]<=tolerance:
            norms=sample_norms([tuple((z-origin)/scale for z in q) for q in parts],Context(normal)) if metrics else None
            return result(parts,single_error,'ONE QUADRATIC',norms)
    count=control_count if policy=='multiple' else 2
    key=('chain',normal,count)
    if key not in cache:
        geometry=cache.get(('source',normal))
        cache[key],context=optimize_pair(normal,geometry) if count==2 else optimize_chain(normal,count,geometry)
        cache[('source',normal)]=context.geometry
    parts=prepare(restore(cache[key]))
    error=geometric_bounds(p,parts,tolerance,source_cache=source_cache,
                           reject_above=tolerance if decision_only else None) if check_error else None
    norms=sample_norms([tuple((z-origin)/scale for z in q) for q in parts],context or Context(normal)) if metrics else None
    return result(parts,error,'QUADRATIC CHAIN',norms)

def select_simpler(candidates,layers,margin,complete,measure,cancel=None,ceiling=None):
    """Keep the first smaller count within a fixed margin of the current result."""
    def worst(count,results,limit=None):
        upper=0.0
        for i in range(layers):
            if cancel is not None and cancel():raise CancelledError()
            if i==len(results):results.append(complete(i,count))
            r=results[i]
            if r is None:return float('inf')
            error=r['error']
            if limit is not None and error is not None and error[0]>limit:return float('inf')
            error=measure(i,r,limit)
            if limit is not None and error[0]>limit:return float('inf')
            upper=max(upper,error[1])
            if limit is not None and upper>limit:return upper
        return upper
    current=candidates[-1];cost=worst(len(candidates),current)
    threshold=cost+margin
    limit=min(threshold,ceiling) if ceiling is not None else threshold
    for count,results in enumerate(candidates[:-1],1):
        error=worst(count,results,limit)
        if error<threshold and (ceiling is None or error<=ceiling):return results
    if math.isfinite(cost):return current
    raise TangentConflict()

def fit_corresponding(curves,tolerance=.5,max_controls=2,cancel=None,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,center_tolerance=None,tangents=None,comparison_tolerance=None):
    """Find a passing count or the cap, then prefer a simpler fit within the margin."""
    values=validated_settings(deviation=tolerance,max_controls=max_controls)
    tolerance=values['deviation'];max_controls=values['max_controls'];curves=list(curves)
    center_tolerance=tolerance if center_tolerance is None else center_tolerance
    comparison_tolerance=tolerance if comparison_tolerance is None else validated_settings(comparison_tolerance)['deviation']
    options=dict(integer_step=integer_step,explicit_midpoint=explicit_midpoint,cancel=cancel) if integer_step else {}
    if tangents is not None and len(tangents)!=len(curves):raise TangentConflict()
    def check_cancel():
        if cancel is not None and cancel():raise CancelledError()
    def finish(results):
        if any(r is None for r in results):raise TangentConflict()
        if center_limit:
            for i,(p,r) in enumerate(zip(curves,results)):
                parts=center_parts([p],r['parts'],center_tolerance,center_limit,integer_step,
                                   tangents[i] if tangents is not None else None,cancel)
                if parts!=r['parts']:
                    r['parts']=parts;r['angles']=diagnostics(p,parts)
                    r['error']=geometric_bounds(p,parts,center_tolerance);r['within']=r['error'][1]<=center_tolerance
        return results
    def compute(p,count,check_error,index):
        check_cancel();extra=dict(options)
        if tangents is not None:extra['tangents']=tangents[index]
        try:return fit(p,policy='single' if count==1 else ('pair' if count==2 else 'multiple'),
                   tolerance=tolerance,control_count=count,check_error=check_error,decision_only=True,**extra)
        except TangentConflict:return None
    if not curves:return []
    if max_controls==1:return finish([compute(p,1,False,i) for i,p in enumerate(curves)])
    candidates=[]
    for count in range(1,max_controls+1):
        at_limit=count==max_controls;results=[]
        for i,p in enumerate(curves):
            r=compute(p,count,not at_limit,i);results.append(r)
            if not at_limit and (r is None or not r['within']):break
        candidates.append(results)
        if not at_limit and len(results)==len(curves) and all(r is not None and r['within'] for r in results):break
    source_caches=[{} for _ in curves]
    def measure(i,r,limit):
        if r['error'] is None or not r['within']:
            r['error']=geometric_bounds(curves[i],r['parts'],tolerance,
                source_cache=source_caches[i],reject_above=limit)
            r['within']=r['error'][1]<=tolerance
        return r['error']
    return finish(select_simpler(candidates,len(curves),comparison_tolerance/2,
                                lambda i,count:compute(curves[i],count,False,i),measure,cancel))
