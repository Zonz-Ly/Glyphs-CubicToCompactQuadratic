# -*- coding: utf-8 -*-
"""Degree <= 3 roots on [0,1], using quadratic knots and bracketed Newton."""
import math


def polynomial_roots_unit(coeff):
    scale=max(map(abs,coeff))
    if not scale:return []
    c=[v/scale for v in coeff]
    while len(c)>1 and abs(c[-1])<1e-14:c.pop()
    def inside(values):
        return sorted(set(max(0.0,min(1.0,v)) for v in values if -1e-12<=v<=1+1e-12))
    if len(c)==1:return []
    if len(c)==2:return inside([-c[0]/c[1]])
    if len(c)==3:
        a,b,d=c[2],c[1],c[0];disc=b*b-4*a*d
        if disc<0:return []
        q=-.5*(b+math.copysign(math.sqrt(disc),b))
        return inside([q/a,d/q] if q else [-b/(2*a)])
    if len(c)!=4:raise ValueError('Only degree <= 3 is used by this fitter')
    d,b,a,h=c
    value=lambda t:((h*t+a)*t+b)*t+d
    derivative=lambda t:(3*h*t+2*a)*t+b
    knots=[0.0]+polynomial_roots_unit([b,2*a,3*h])+[1.0]
    roots=[t for t in knots if abs(value(t))<1e-11]
    for lo,hi in zip(knots,knots[1:]):
        flo,fhi=value(lo),value(hi)
        if flo*fhi>=0:continue
        t=(lo+hi)/2
        for _ in range(26):
            f=value(t)
            if f==0:break
            if flo*f<=0:hi=t
            else:lo=t;flo=f
            der=derivative(t)
            step=f/der if der else float('inf')
            proposal=t-step
            if abs(step)<2e-14 and lo<=proposal<=hi:
                t=proposal;break
            if hi-lo<2e-13:t=(lo+hi)/2;break
            t=proposal if lo<proposal<hi and abs(step)<.8*(hi-lo) else (lo+hi)/2
        else:
            # Difficult nearly multiple roots retain a reliable bracket fallback.
            for _ in range(38):
                t=(lo+hi)/2;f=value(t)
                if flo*f<=0:hi=t
                else:lo=t;flo=f
            t=(lo+hi)/2
        roots.append(t)
    roots.sort();result=[]
    for t in roots:
        if not result or abs(t-result[-1])>1e-9:result.append(t)
    return result
