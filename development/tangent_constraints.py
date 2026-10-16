# -*- coding: utf-8 -*-
"""Oriented tangent gates with exact or grid-cell endpoint ray constraints."""
import math
from fractions import Fraction
from quad_fit import dot
from geometry_fit import nelder_mead
from i18n import tr

class TangentConflict(ValueError):
    def __init__(self):super().__init__(tr('tangent_conflict'))

def cross2(a,b):return a.real*b.imag-a.imag*b.real

def aligned(a,b,degrees):
    if abs(a)<1e-12 or abs(b)<1e-12:return False
    return abs(math.degrees(math.atan2(cross2(a,b),dot(a,b))))<=degrees+1e-9

def smooth_join(a,b,degrees):return aligned(a[3]-a[2],b[1]-b[0],degrees)

def primitive_direction(direction,step):
    x=direction.real/step;y=direction.imag/step
    fx=Fraction(x).limit_denominator(1000000);fy=Fraction(y).limit_denominator(1000000)
    denominator=fx.denominator*fy.denominator//math.gcd(fx.denominator,fy.denominator)
    ix=fx.numerator*(denominator//fx.denominator);iy=fy.numerator*(denominator//fy.denominator)
    divisor=math.gcd(ix,iy)
    if not divisor:raise TangentConflict()
    move=complex(ix//divisor,iy//divisor)*step
    if abs(cross2(move,direction))>1e-9*abs(move)*abs(direction):raise TangentConflict()
    return move

def on_ray(z,ray,step=0.0):
    if ray is None:return True
    a,d=ray;distance=z-a;length=abs(d)
    if not length:return False
    if not step:return dot(distance,d)/length>1e-10 and abs(cross2(distance,d))/length<=1e-7
    if dot(distance,d)/length<=1e-10:return False
    low=0.0;high=float('inf');half=step/2+step*1e-9
    for offset,direction in ((distance.real,d.real/length),(distance.imag,d.imag/length)):
        if abs(direction)<1e-15:
            if abs(offset)>half:return False
        else:
            bounds=sorted(((offset-half)/direction,(offset+half)/direction))
            low=max(low,bounds[0]);high=min(high,bounds[1])
    return high>=low

def lattice_ray(z,ray,step):
    a,d=ray;unit=d/abs(d)
    base=z if on_ray(z,ray,step) else a+unit*max(step/2,dot(z-a,unit))
    base=complex(round(base.real/step)*step,round(base.imag/step)*step)
    candidates=[base+complex(x,y)*step for x in (-1,0,1) for y in (-1,0,1)]
    candidates=[p for p in candidates if on_ray(p,ray,step)]
    if not candidates:raise TangentConflict()
    return min(candidates,key=lambda p:(abs(p-z),abs(cross2(p-a,unit)),p.real,p.imag))

def project_controls(controls,tangents=None,step=0.0):
    if not tangents or not any(tangents):return list(controls)
    result=list(controls);left,right=tangents
    if step:
        if len(result)==1 and left is not None and right is not None:
            z=result[0];bases=[z,lattice_ray(z,left,step),lattice_ray(z,right,step)]
            try:bases.extend(project_controls(result,tangents))
            except TangentConflict:pass
            candidates={complex(round(b.real/step)+x,round(b.imag/step)+y)*step
                        for b in bases for x in (-1,0,1) for y in (-1,0,1)}
            valid=[p for p in candidates if on_ray(p,left,step) and on_ray(p,right,step)]
            if not valid:raise TangentConflict()
            return [min(valid,key=lambda p:(abs(p-z),p.real,p.imag))]
        for index,ray in ((0,left),(len(result)-1,right)):
            if ray is not None:result[index]=lattice_ray(result[index],ray,step)
        return result
    if len(result)==1 and left is not None and right is not None:
        a,u=left;b,v=right;den=cross2(u,v)
        if abs(den)>1e-12*abs(u)*abs(v):
            z=a+u*(cross2(b-a,v)/den)
            if not on_ray(z,left) or not on_ray(z,right):raise TangentConflict()
            return [z]
        if abs(cross2(b-a,u))>1e-8*max(1.0,abs(u)):raise TangentConflict()
        unit=u/abs(u);low=1e-10;bound=dot(b-a,unit)
        if dot(u,v)<0:high=bound-1e-10
        else:low=max(low,bound+1e-10);high=float('inf')
        if low>high:raise TangentConflict()
        z=a+unit*max(low,min(high,dot(result[0]-a,unit)))
        if not on_ray(z,right):raise TangentConflict()
        return [z]
    for index,ray in ((0,left),(len(result)-1,right)):
        if ray is None:continue
        a,d=ray;unit=d/abs(d)
        result[index]=a+unit*max(1e-9,dot(result[index]-a,unit))
    return result

def optimize_constrained(controls,tangents,origin,scale,objective,cancel):
    controls=project_controls(controls,tangents)
    if len(controls)==1 and all(tangents):return controls
    rays={i:r for i,r in ((0,tangents[0]),(len(controls)-1,tangents[1])) if r is not None}
    initial=[]
    for i,z in enumerate(controls):
        if i in rays:
            a,d=rays[i];initial.append(dot(z-a,d/abs(d))/scale)
        else:initial.extend(((z-origin).real/scale,(z-origin).imag/scale))
    def decode(values):
        result=[];k=0
        for i in range(len(controls)):
            if i in rays:
                a,d=rays[i];result.append(a+d/abs(d)*max(1e-10,values[k])*scale);k+=1
            else:result.append(origin+complex(values[k],values[k+1])*scale);k+=2
        return result
    def score(values):cancel();return objective(decode(values))
    before=score(initial);after,values=nelder_mead(score,initial,step=.015,iterations=120)
    return decode(values) if after<before else controls
