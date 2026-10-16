# -*- coding: utf-8 -*-
"""Unconstrained geometric fitting, arc-length weights and multiple starts.

No endpoint tangent constraints. Coordinates are normalized before search.
"""
import math
from segment_index import SegmentIndex
from quad_fit import (dot,cubic,quadratic,split,single_l2,pair_l2,pair_basis,
                      solve,diagnostics)
from geometry_fit import (point_segment,nearest_quadratic,flatten,arc_samples,
                          geometric_bounds,nelder_mead,make_context,optimize_one,
                          sampled_objective)


def numeric_cache():
    """Reuse normalized fitting solutions across conversions."""
    import sys,types
    name='_Zonz_compact_quadratic_numeric_cache'
    if name not in sys.modules:
        module=types.ModuleType(name);module.values={};sys.modules[name]=module
    return sys.modules[name].values


def polyline_parameterization(p,tolerance=1e-6):
    stack=[(p,0.0,1.0,0)];points=[p[0]];times=[0.0]
    while stack:
        q,a,b,depth=stack.pop()
        if max(point_segment(z,q[0],q[-1]) for z in q[1:-1])<=tolerance or depth>=20:
            points.append(q[-1]);times.append(b)
        else:
            left,right=split(q);m=(a+b)/2
            stack.append((right,m,b,depth+1));stack.append((left,a,m,depth+1))
    return points,times


class Context:
    def __init__(self,p,count=65,reverse_count=25,geometry=None):
        self.p=p
        self.reverse_count=reverse_count
        if geometry is None:
            self.line,self.times=polyline_parameterization(p)
            self.index=SegmentIndex(self.line)
        else:
            self.line,self.times,self.index=geometry
        self.geometry=(self.line,self.times,self.index)
        lengths=[abs(b-a) for a,b in zip(self.line,self.line[1:])]
        self.samples=[];total=sum(lengths);edge=0;before=0.0
        for i in range(count):
            target=total*i/(count-1)
            while edge<len(lengths)-1 and before+lengths[edge]<target:
                before+=lengths[edge];edge+=1
            local=(target-before)/lengths[edge] if lengths[edge] else 0.0
            t=self.times[edge]+local*(self.times[edge+1]-self.times[edge])
            weight=.5 if i==0 or i==count-1 else 1.0
            self.samples.append((cubic(p,t),weight/(count-1)))

    def tangent(self,t):
        p=self.p;u=1-t
        return 3*(u*u*(p[1]-p[0])+2*u*t*(p[2]-p[1])+t*t*(p[3]-p[2]))

    def interior(self,t):
        return 1e-7<t<1-1e-7

    def nearest(self,z):
        best,index,part=self.index.nearest(z)
        # Refine the closest polyline location on the original cubic itself.
        a=self.times[max(0,index-1)];b=self.times[min(len(self.times)-1,index+2)]
        t=self.times[index]+part*(self.times[index+1]-self.times[index])
        p=self.p
        for _ in range(5):
            u=1-t
            pos=cubic(p,t)
            der=3*(u*u*(p[1]-p[0])+2*u*t*(p[2]-p[1])+t*t*(p[3]-p[2]))
            second=6*(u*(p[2]-2*p[1]+p[0])+t*(p[3]-2*p[2]+p[1]))
            denominator=dot(der,der)+dot(pos-z,second)
            if denominator<=1e-15:break
            proposed=max(a,min(b,t-dot(pos-z,der)/denominator))
            if abs(proposed-t)<1e-10:break
            t=proposed
        candidates=[0.0,1.0,t,self.times[index]+part*(self.times[index+1]-self.times[index])]
        t=min(candidates,key=lambda v:abs(cubic(p,v)-z))
        return cubic(p,t),t


def unpack(p,x):
    controls=[complex(x[i],x[i+1]) for i in range(0,len(x),2)]
    joins=[p[0]]+[(a+b)/2 for a,b in zip(controls,controls[1:])]+[p[3]]
    return [(joins[i],q,joins[i+1]) for i,q in enumerate(controls)]


def pack(parts):
    return [v for q in parts for v in (q[1].real,q[1].imag)]


def basis(s,segment,count):
    if count==1:
        value=2*s*(1-s)
        return [complex(value,0),complex(0,value)]
    if count==2:
        a,b,_,_=pair_basis(s,segment)
        return [complex(a,0),complex(0,a),complex(b,0),complex(0,b)]
    weights=[0.0]*count;u=1-s
    weights[segment]=2*u*s
    if segment>0:
        weights[segment-1]+=u*u/2;weights[segment]+=u*u/2
    if segment<count-1:
        weights[segment]+=s*s/2;weights[segment+1]+=s*s/2
    return [v for w in weights for v in (complex(w,0),complex(0,w))]


def sample_rows(parts,context,reverse_count=None):
    """Residual/Jacobian rows with balanced, arc-length-aware weights."""
    reverse_count=reverse_count or context.reverse_count
    count=len(parts);rows=[];norms=[]
    for z,weight in context.samples:
        candidates=[nearest_quadratic(z,q)+(i,) for i,q in enumerate(parts)]
        distance,s,i=min(candidates,key=lambda v:v[0]);q=parts[i]
        value=quadratic(q,s);der=2*((1-s)*(q[1]-q[0])+s*(q[2]-q[1]))
        jac=basis(s,i,count);difference=value-z
        if abs(der)>1e-12 and 1e-7<s<1-1e-7:
            normal=1j*der/abs(der)
            rows.append((dot(difference,normal),[dot(v,normal) for v in jac],weight*.5))
        else:
            rows.append((difference.real,[v.real for v in jac],weight*.5))
            rows.append((difference.imag,[v.imag for v in jac],weight*.5))
        norms.append((distance,weight*.5))
    reverse=[];length=0.0
    for i,q in enumerate(parts):
        for k in range(reverse_count):
            s=k/(reverse_count-1)
            position=quadratic(q,s)
            der=2*((1-s)*(q[1]-q[0])+s*(q[2]-q[1]))
            weight=abs(der)*(.5 if k==0 or k==reverse_count-1 else 1)/(reverse_count-1)
            target,t=context.nearest(position)
            tangent=context.tangent(t)
            jac=basis(s,i,count);difference=position-target
            reverse.append((difference,tangent,jac,weight,t));length+=weight
    length=max(length,1e-15)
    for difference,tangent,jac,weight,t in reverse:
        weight=weight/length*.5
        if abs(tangent)>1e-12 and context.interior(t):
            normal=1j*tangent/abs(tangent)
            rows.append((dot(difference,normal),[dot(v,normal) for v in jac],weight))
        else:
            rows.append((difference.real,[v.real for v in jac],weight))
            rows.append((difference.imag,[v.imag for v in jac],weight))
        norms.append((abs(difference),weight))
    return rows,norms


def sample_norms(parts,context,reverse_count=None):
    """Identical distance weights to sample_rows; omit unused Jacobians."""
    reverse_count=reverse_count or context.reverse_count
    norms=[]
    for z,weight in context.samples:
        distance=min(nearest_quadratic(z,q)[0] for q in parts)
        norms.append((distance,weight*.5))
    reverse=[];length=0.0
    for q in parts:
        for k in range(reverse_count):
            s=k/(reverse_count-1)
            position=quadratic(q,s)
            der=2*((1-s)*(q[1]-q[0])+s*(q[2]-q[1]))
            weight=abs(der)*(.5 if k==0 or k==reverse_count-1 else 1)/(reverse_count-1)
            target,t=context.nearest(position)
            reverse.append((abs(position-target),weight));length+=weight
    length=max(length,1e-15)
    norms.extend((d,w/length*.5) for d,w in reverse)
    return norms


def score_norms(norms,power=2):
    if power=='max':return max(d for d,w in norms)
    return sum(w*d**power for d,w in norms)**(1.0/power)


def refine_lm(p,x,context,power=2,iterations=25):
    """Normal-distance Gauss-Newton/LM; accept only improved true objectives."""
    x=list(x);damping=1e-4
    rows,norms=sample_rows(unpack(p,x),context)
    score=score_norms(norms,power)
    for _ in range(iterations):
        dim=len(x);matrix=[[0.0]*dim for _ in range(dim)];rhs=[0.0]*dim
        largest=max([abs(r) for r,j,w in rows]+[1e-12])
        for r,jac,weight in rows:
            # Relative IRLS weights avoid tiny fourth-power normal matrices.
            weight*=max(abs(r)/largest,.001)**(power-2)
            for i in range(dim):
                rhs[i]-=weight*jac[i]*r
                for j in range(dim):matrix[i][j]+=weight*jac[i]*jac[j]
        for i in range(dim):matrix[i][i]+=damping*max(matrix[i][i],1e-9)
        try:step=solve(matrix,rhs)
        except ValueError:break
        maximum=max(map(abs,step))
        if maximum<2e-8:break
        if maximum>.2:step=[v*.2/maximum for v in step]
        proposed=[a+b for a,b in zip(x,step)]
        if max(map(abs,proposed))>20:damping*=10;continue
        newrows,newnorms=sample_rows(unpack(p,proposed),context)
        newscore=score_norms(newnorms,power)
        if newscore<score:
            improvement=score-newscore
            x,rows,norms,score=proposed,newrows,newnorms,newscore
            damping=max(1e-9,damping*.3)
            if improvement<1e-10:break
        else:
            damping*=10
            if damping>1e8:break
    return x,score


def pair_seeds(p,one):
    seeds=[pack(pair_l2(p))]
    a=(one[0]+one[1])/2;b=(one[1]+one[2])/2;m=(a+b)/2
    seeds.append(pack([(p[0],a,m),(m,b,p[3])]))
    for t in [.15,.3,.5,.7,.85]:
        left,right=split(p,t)
        # Non-half subdivision is a source of starting positions only.
        # Its fitted controls always use their midpoint as the actual join.
        seeds.append(pack([single_l2(left),single_l2(right)]))
        centre=cubic(p,t);u=1-t
        direction=3*(u*u*(p[1]-p[0])+2*u*t*(p[2]-p[1])+t*t*(p[3]-p[2]))
        if abs(direction)>1e-10:
            span=(abs(centre-p[0])+abs(p[3]-centre))/4
            direction=direction/abs(direction)*span
            seeds.append([centre.real-direction.real,centre.imag-direction.imag,
                          centre.real+direction.real,centre.imag+direction.imag])
    # Diverse midpoint/span combinations avoid starting in the same basin.
    result=[]
    for x in seeds:
        if all(max(abs(a-b) for a,b in zip(x,y))>1e-7 for y in result):result.append(x)
    return result


def choose_diverse(scored,count):
    scored=sorted(scored,key=lambda r:r[0]);chosen=[scored[0]];remaining=scored[1:]
    while remaining and len(chosen)<count:
        # Good score matters, but retain geometrically different starts.
        eligible=remaining[:max(5,count*2)]
        pick=max(eligible,key=lambda r:min(sum((a-b)**2 for a,b in zip(r[1],c[1])) for c in chosen))
        chosen.append(pick);remaining.remove(pick)
    return chosen

