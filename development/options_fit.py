# -*- coding: utf-8 -*-
"""Optional tangent/lattice fitting and separately accepted one-control centering."""
import math
from concurrent.futures import CancelledError
from quad_fit import dot
from geometry_fit import geometric_bounds
from search_core import sample_norms,score_norms
from tangent_constraints import (TangentConflict,project_controls,optimize_constrained,
                                 primitive_direction,on_ray)

def grid_point(z,step):return complex(round(z.real/step)*step,round(z.imag/step)*step)

def control_parts(start,end,controls,step=0.0,explicit=False):
    joins=[start]+[(a+b)/2 for a,b in zip(controls,controls[1:])]+[end]
    if step and explicit:joins[1:-1]=[grid_point(z,step) for z in joins[1:-1]]
    return [(joins[i],q,joins[i+1]) for i,q in enumerate(controls)]

def center_parts(curves,parts,tolerance,center_limit,integer_step=0.0,tangents=None,cancel=None):
    if not center_limit or len(parts)!=1:return parts
    def check():
        if cancel is not None and cancel():raise CancelledError()
    check();start,q,end=parts[0];chord=end-start
    if abs(chord)<1e-12:return parts
    direction=chord/abs(chord);middle=(start+end)/2
    offset=dot(q-middle,direction);signed_height=dot(q-start,1j*direction);height=abs(signed_height)
    if height>center_limit+max(1.0,height,center_limit)*1e-12 or abs(offset)<1e-9:return parts
    target=q-direction*offset;cache={};tangents=tangents or (None,None)
    def acceptable(control):
        check()
        if any(not on_ray(control,ray,integer_step) for ray in tangents):return False
        bounds=geometric_bounds(curves[0],[(start,control,end)],tolerance,
            accuracy=min(max(.002,tolerance*.02),tolerance*.1),reject_above=tolerance,
            source_cache=cache,source_curves=curves if len(curves)>1 else None)
        return bounds[1]<=tolerance
    if not acceptable(q):return parts
    if acceptable(target):desired=target
    else:
        low=0.0;high=1.0
        for _ in range(26):
            if (high-low)*abs(offset)<1e-6:break
            mid=(low+high)/2
            if acceptable(q+(target-q)*mid):low=mid
            else:high=mid
        desired=q+(target-q)*low
    if not integer_step:return [(start,desired,end)]
    candidates={q}
    # Include exact-height lattice motion where it exists, plus nearby quantized motion.
    try:
        move=primitive_direction(chord,integer_step)
        k=round(dot(desired-q,move)/abs(move)**2)
        candidates.update(grid_point(q+j*move,integer_step) for j in (k-1,k,k+1))
    except TangentConflict:pass
    for fraction in (1.0,.9,.75,.5,.25,0.0):
        base=grid_point(q+(desired-q)*fraction,integer_step)
        candidates.update(base+complex(x,y)*integer_step for x in (-1,0,1) for y in (-1,0,1))
    quantum=integer_step/math.sqrt(2)+1e-9
    def key(z):return (abs(dot(z-middle,direction)),abs(dot(z-start,1j*direction)-signed_height),abs(z-desired),z.real,z.imag)
    for z in sorted(candidates,key=key):
        if abs(dot(z-middle,direction))>=abs(offset)-1e-9:continue
        new_height=dot(z-start,1j*direction)
        if abs(new_height-signed_height)>quantum or new_height*signed_height<-1e-12:continue
        if acceptable(z):return [(start,z,end)]
    return parts

def adjust_parts(curves,parts,tolerance,center_limit=0.0,integer_step=0.0,explicit=False,context_factory=None,cancel=None,tangents=None):
    constrained=bool(tangents and any(tangents))
    if not integer_step and not constrained:return center_parts(curves,parts,tolerance,center_limit,cancel=cancel)
    def check():
        if cancel is not None and cancel():raise CancelledError()
    check();start,end=parts[0][0],parts[-1][-1];origin=start
    scale=max([abs(z-origin) for p in curves for z in p]+[abs(z-origin) for q in parts for z in q]+[1e-9])
    normal=tuple(tuple((z-origin)/scale for z in p) for p in curves);context=context_factory(normal);memo={}
    def objective(values):
        key=tuple(values)
        if key not in memo:
            proposed=control_parts(start,end,values,integer_step,explicit)
            normalized=[tuple((z-origin)/scale for z in q) for q in proposed]
            memo[key]=score_norms(sample_norms(normalized,context))
        return memo[key]
    controls=[q[1] for q in parts]
    if constrained:
        try:controls=optimize_constrained(controls,tangents,origin,scale,objective,check)
        except TangentConflict:
            if not integer_step:raise
            controls=project_controls(controls,tangents,integer_step)
    if integer_step:
        controls=[grid_point(z,integer_step) for z in controls]
        controls=project_controls(controls,tangents,integer_step);score=objective(controls)
        for _ in range(16):
            changed=False
            for i in range(len(controls)):
                check();best=controls;best_score=score
                directions=[complex(x,y)*integer_step for x,y in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))]
                for delta in directions:
                    candidate=list(controls);candidate[i]=grid_point(candidate[i]+delta,integer_step)
                    try:candidate=project_controls(candidate,tangents,integer_step)
                    except TangentConflict:continue
                    value=objective(candidate)
                    if value<best_score-1e-13:best_score=value;best=candidate
                if best!=controls:controls=best;score=best_score;changed=True
            if not changed:break
    parts=control_parts(start,end,controls,integer_step,explicit)
    return center_parts(curves,parts,tolerance,center_limit,integer_step,tangents,cancel)
