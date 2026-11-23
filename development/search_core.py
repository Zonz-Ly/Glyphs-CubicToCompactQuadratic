# -*- coding: utf-8 -*-
"""Unconstrained geometric fitting, arc-length weights and multiple starts.

No endpoint tangent constraints. Coordinates are normalized before search.
"""
import math
from concurrent.futures import CancelledError
from segment_index import SegmentIndex
from roots_unit import polynomial_roots_interval
from quad_fit import (dot,cubic,quadratic,split,single_l2,pair_l2,pair_basis,
                      solve,diagnostics)
from geometry_fit import (point_segment,nearest_quadratic,flatten,arc_samples,
                          geometric_bounds,nelder_mead,make_context,optimize_one,
                          sampled_objective)


def check_cancelled(cancel):
    """Honor the shared optional predicate at fitting and adjustment boundaries."""
    if cancel is not None and cancel():raise CancelledError()


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
        self.differences=(p[1]-p[0],p[2]-p[1],p[3]-p[2],
                          p[2]-2*p[1]+p[0],p[3]-2*p[2]+p[1])
        self.power_coefficients=(p[0],3*self.differences[0],3*self.differences[3],
                                 p[3]-3*p[2]+3*p[1]-p[0])
        self.constant=all(v==p[0] for v in p)
        self.reverse_count=reverse_count
        if geometry is None:
            self.line,self.times=polyline_parameterization(p)
            self.index=SegmentIndex(self.line)
        else:
            self.line,self.times,self.index=geometry
        self.geometry=(self.line,self.times,self.index)
        chord=p[3]-p[0];length2=dot(chord,chord)
        self.straight=bool(length2 and all(
            (z-p[0]).real*chord.imag==(z-p[0]).imag*chord.real and
            0<=dot(z-p[0],chord)<=length2 for z in p[1:3]))
        lengths=[abs(b-a) for a,b in zip(self.line,self.line[1:])]
        self.samples=[];total=sum(lengths);edge=0;before=0.0
        for i in range(count):
            target=total*i/(count-1)
            while edge<len(lengths)-1 and before+lengths[edge]<target:
                before+=lengths[edge];edge+=1
            local=(target-before)/lengths[edge] if lengths[edge] else 0.0
            t=self.parameter_at(edge,local)
            weight=.5 if i==0 or i==count-1 else 1.0
            self.samples.append((cubic(p,t),weight/(count-1)))

    def parameter_at(self,edge,fraction):
        """Invert chord position, rather than assuming uniform parameter speed."""
        lo=self.times[edge];hi=self.times[edge+1]
        if fraction<=0:return lo
        if fraction>=1:return hi
        chord=self.line[edge+1]-self.line[edge]
        if not abs(chord):return lo+(hi-lo)*fraction
        target=self.line[edge]+fraction*chord
        t=lo+(hi-lo)*fraction
        for _ in range(64):
            f=dot(cubic(self.p,t)-target,chord)
            if f==0:return t
            if f<0:lo=t
            else:hi=t
            derivative=dot(self.tangent(t),chord)
            proposed=t-f/derivative if derivative>0 else float('inf')
            if lo<proposed<hi and abs(proposed-t)<2e-14:return proposed
            proposed=proposed if lo<proposed<hi else (lo+hi)/2
            if proposed==t:return t
            t=proposed
        return t

    def tangent(self,t):
        d0,d1,d2,_,_=self.differences;u=1-t
        return 3*(u*u*d0+2*u*t*d1+t*t*d2)

    def interior(self,t):
        return 1e-7<t<1-1e-7

    def nearest(self,z):
        if self.straight:
            _,index,fraction=self.index.nearest(z)
            t=self.parameter_at(index,fraction)
            return cubic(self.p,t),t
        if self.constant:return self.p[0],0.0
        best,index,part=self.index.nearest(z)
        # Refine the closest polyline location on the original cubic itself.
        a=self.times[max(0,index-1)];b=self.times[min(len(self.times)-1,index+2)]
        t=self.times[index]+part*(self.times[index+1]-self.times[index])
        p=self.p;converged=False;previous=None
        d0,d1,d2,e0,e1=self.differences
        for _ in range(5):
            u=1-t
            pos=cubic(p,t)
            der=3*(u*u*d0+2*u*t*d1+t*t*d2)
            second=6*(u*e0+t*e1)
            denominator=dot(der,der)+dot(pos-z,second)
            if denominator<=1e-15:break
            proposed=max(a,min(b,t-dot(pos-z,der)/denominator))
            if abs(proposed-t)<1e-10:
                converged=(a<proposed<b or proposed in (0.0,1.0))
                previous=t;t=proposed;break
            t=proposed
        candidates=[0.0,1.0,t,self.times[index]+part*(self.times[index+1]-self.times[index])]
        if previous is not None:candidates.append(previous)
        if not converged:
            # Keep every old candidate. Add all stationary parameters if the
            # local Newton solve fails, including nonpositive denominators.
            coefficients=(p[0]-z,)+self.power_coefficients[1:]
            derivative=[i*v for i,v in enumerate(coefficients) if i]
            stationary=[0.0]*6
            for i,v in enumerate(coefficients):
                for j,w in enumerate(derivative):stationary[i+j]+=dot(v,w)
            candidates.extend(polynomial_roots_interval(stationary))
        t=candidates[0];point=cubic(p,t);distance=abs(point-z)
        for value in candidates[1:]:
            candidate=cubic(p,value);measured=abs(candidate-z)
            if measured<distance:distance,point,t=measured,candidate,value
        return point,t


def unpack(p,x):
    controls=[complex(x[i],x[i+1]) for i in range(0,len(x),2)]
    joins=[p[0]]+[(a+b)/2 for a,b in zip(controls,controls[1:])]+[p[3]]
    return [(joins[i],q,joins[i+1]) for i,q in enumerate(controls)]


def pack(parts):
    return [v for q in parts for v in (q[1].real,q[1].imag)]


def unique_vectors(values):
    """Preserve first occurrence and tie order; accept mutable search vectors."""
    seen=set()
    for value in values:
        key=tuple(value)
        if key not in seen:
            seen.add(key);yield value


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


class PreparedParts(list):
    """Quadratic control-hull bounds shared by all forward objective queries."""
    def __init__(self,parts):
        super().__init__(parts)
        self.boxes=[(min(z.real for z in q),max(z.real for z in q),
                     min(z.imag for z in q),max(z.imag for z in q)) for q in self]
        self.margin=max([1.0]+[abs(z) for q in self for z in q])*1e-12


def forward_projection(z,parts):
    if len(parts)==1:return nearest_quadratic(z,parts[0])+(0,)
    if not isinstance(parts,PreparedParts):parts=PreparedParts(parts)
    ranked=sorted((math.hypot(max(b[0]-z.real,0,z.real-b[1]),
                              max(b[2]-z.imag,0,z.imag-b[3])),i)
                  for i,b in enumerate(parts.boxes))
    margin=max(parts.margin,abs(z)*1e-12);best=None
    for bound,i in ranked:
        if best is not None and bound-margin>best[0]:break
        distance,t=nearest_quadratic(z,parts[i])
        if best is None or (distance,i)<(best[0],best[2]):best=distance,t,i
    return best


def reverse_projections(parts,context,reverse_count):
    """Shared geometry only; scoring never constructs tangent/Jacobian rows."""
    for i,q in enumerate(parts):
        for k in range(reverse_count):
            s=k/(reverse_count-1)
            position=quadratic(q,s)
            der=2*((1-s)*(q[1]-q[0])+s*(q[2]-q[1]))
            weight=abs(der)*(.5 if k==0 or k==reverse_count-1 else 1)/(reverse_count-1)
            target,t=context.nearest(position)
            yield i,s,position-target,weight,t


def sample_rows(parts,context,reverse_count=None):
    """Residual/Jacobian rows with balanced, arc-length-aware weights."""
    reverse_count=reverse_count or context.reverse_count
    if len(parts)>1 and not isinstance(parts,PreparedParts):parts=PreparedParts(parts)
    count=len(parts);rows=[];norms=[]
    for z,weight in context.samples:
        distance,s,i=forward_projection(z,parts);q=parts[i]
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
    for i,s,difference,weight,t in reverse_projections(parts,context,reverse_count):
        tangent=context.tangent(t);jac=basis(s,i,count)
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
    if len(parts)>1 and not isinstance(parts,PreparedParts):parts=PreparedParts(parts)
    norms=[]
    for z,weight in context.samples:
        distance=forward_projection(z,parts)[0]
        norms.append((distance,weight*.5))
    reverse=[];length=0.0
    for i,s,difference,weight,t in reverse_projections(parts,context,reverse_count):
        reverse.append((abs(difference),weight));length+=weight
    length=max(length,1e-15)
    norms.extend((d,w/length*.5) for d,w in reverse)
    return norms


def score_norms(norms,power=2):
    if power=='max':return max(d for d,w in norms)
    return sum(w*d**power for d,w in norms)**(1.0/power)


def bounded_score(parts,context,limit,check=None):
    """Exact full RMS, or None only when a candidate cannot beat limit.

    For integer neighbor comparisons only. Nonnegative partial sums are
    guarded for roundoff; completed scores retain built-in sum and term order.
    A rejection is not a score and must never enter the full-score cache.
    """
    if check is not None:check()
    if not math.isfinite(limit):return score_norms(sample_norms(parts,context))
    if len(parts)>1:parts=PreparedParts(parts)
    terms=[];expected_terms=len(context.samples)+len(parts)*context.reverse_count
    def cannot_win():
        if check is not None:check()
        partial=sum(terms)**.5
        guard=4*(expected_terms+4)*2.220446049250313e-16*max(partial,abs(limit),1e-300)
        return partial>=limit+guard
    for i,(z,weight) in enumerate(context.samples,1):
        distance=forward_projection(z,parts)[0]
        terms.append((weight*.5)*distance**2)
        if i%8==0 and cannot_win():return None
    # Reverse weights must be normalized by the complete curve length, even
    # when a later distance query can be skipped.
    prepared=[];length=0.0;reverse_count=context.reverse_count
    for q in parts:
        for k in range(reverse_count):
            s=k/(reverse_count-1)
            position=quadratic(q,s)
            der=2*((1-s)*(q[1]-q[0])+s*(q[2]-q[1]))
            weight=abs(der)*(.5 if k==0 or k==reverse_count-1 else 1)/(reverse_count-1)
            prepared.append((position,weight));length+=weight
    length=max(length,1e-15)
    for i,(position,weight) in enumerate(prepared,1):
        target,t=context.nearest(position)
        distance=abs(position-target)
        terms.append((weight/length*.5)*distance**2)
        if i%4==0 and cannot_win():return None
    return sum(terms)**.5


def normal_equations(rows,dim,power):
    """Assemble the undamped system, visiting only nonzero local derivatives."""
    matrix=[[0.0]*dim for _ in range(dim)];rhs=[0.0]*dim
    largest=max([abs(r) for r,j,w in rows]+[1e-12])
    for r,jac,weight in rows:
        weight*=max(abs(r)/largest,.001)**(power-2)
        active=[(i,v) for i,v in enumerate(jac) if v]
        for i,a in active:
            rhs[i]-=weight*a*r
            for j,b in active:matrix[i][j]+=weight*a*b
    return matrix,rhs


def refine_lm(p,x,context,power=2,iterations=25):
    """Normal-distance Gauss-Newton/LM; accept only improved true objectives."""
    x=list(x);damping=1e-4
    rows,norms=sample_rows(unpack(p,x),context)
    score=score_norms(norms,power)
    system=None
    for _ in range(iterations):
        if system is None:system=normal_equations(rows,len(x),power)
        base,rhs=system;matrix=[row[:] for row in base]
        for i in range(len(x)):matrix[i][i]+=damping*max(matrix[i][i],1e-9)
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
            system=None
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

