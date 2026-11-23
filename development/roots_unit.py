# -*- coding: utf-8 -*-
"""Degree <= 3 roots on [0,1], using quadratic knots and bracketed Newton."""
import math


def polynomial_roots_interval(coeff):
    """Isolate real stationary roots on [0,1] for cubic-distance fallback.

    Derivative roots partition the polynomial into monotone intervals. This
    degree-five fallback supplements failed cubic projection refinement; the
    existing degree-three quadratic projection solver below is unchanged.
    """
    coeff=list(coeff)
    while len(coeff)>1 and coeff[-1]==0:coeff.pop()
    scale=max(map(abs,coeff))
    if not scale or len(coeff)==1:return []
    coeff=[v/scale for v in coeff]
    if len(coeff)==2:
        t=-coeff[0]/coeff[1]
        return [t] if 0<=t<=1 else []
    def value(t):
        result=coeff[-1]
        for c in reversed(coeff[:-1]):result=result*t+c
        return result
    critical=polynomial_roots_interval([i*c for i,c in enumerate(coeff) if i])
    knots=sorted(set([0.0,1.0]+critical));values=[value(t) for t in knots]
    roots=[t for t,v in zip(knots,values) if abs(v)<1e-13]
    for lo,hi,flo,fhi in zip(knots,knots[1:],values,values[1:]):
        if flo*fhi>=0:continue
        for _ in range(64):
            t=(lo+hi)/2
            if t==lo or t==hi:break
            f=value(t)
            if f==0:lo=hi=t;break
            if flo*f<=0:hi=t
            else:lo=t;flo=f
        roots.append((lo+hi)/2)
    return sorted(set(roots))


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
