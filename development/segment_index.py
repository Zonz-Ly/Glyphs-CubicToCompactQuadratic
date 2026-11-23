# -*- coding: utf-8 -*-
"""Exact nearest-segment queries, accelerated by a small AABB tree."""
import math
import heapq


class BoxIndex:
    """Visit curve control-hull boxes by increasing distance lower bound."""
    def __init__(self,boxes):
        self.boxes=tuple(boxes)
        def build(ids):
            box=(min(boxes[i][0] for i in ids),max(boxes[i][1] for i in ids),
                 min(boxes[i][2] for i in ids),max(boxes[i][3] for i in ids))
            if len(ids)<=4:return box,ids,None
            axis=0 if box[1]-box[0]>=box[3]-box[2] else 2
            ids.sort(key=lambda i:boxes[i][axis]+boxes[i][axis+1])
            middle=len(ids)//2
            return box,build(ids[:middle]),build(ids[middle:])
        self.root=build(list(range(len(boxes)))) if boxes else None

    def ordered(self,z):
        if self.root is None:return
        def lower(box):
            return math.hypot(max(box[0]-z.real,0,z.real-box[1]),
                              max(box[2]-z.imag,0,z.imag-box[3]))
        serial=0;heap=[(lower(self.root[0]),0,serial,self.root)]
        while heap:
            bound,kind,index,node=heapq.heappop(heap)
            if kind:
                yield bound,index
            elif node[2] is None:
                for i in node[1]:heapq.heappush(heap,(lower(self.boxes[i]),1,i,None))
            else:
                for child in node[1:]:
                    serial+=1;heapq.heappush(heap,(lower(child[0]),0,serial,child))


class SegmentIndex:
    def __init__(self, line):
        self.edges=[]
        for a,b in zip(line,line[1:]):
            v=b-a;den=v.real*v.real+v.imag*v.imag
            self.edges.append((a,v,1.0/den if den else 0.0))
        def build(ids):
            xs=[x for i in ids for x in (line[i].real,line[i+1].real)]
            ys=[y for i in ids for y in (line[i].imag,line[i+1].imag)]
            box=(min(xs),min(ys),max(xs),max(ys))
            if len(ids)<=6:return (box,ids,None)
            axis=0 if box[2]-box[0]>=box[3]-box[1] else 1
            ids.sort(key=lambda i:(line[i].real+line[i+1].real) if axis==0
                     else (line[i].imag+line[i+1].imag))
            mid=len(ids)//2
            return (box,build(ids[:mid]),build(ids[mid:]))
        self.root=build(list(range(len(self.edges)))) if self.edges else None

    def nearest(self,z):
        if self.root is None:return float('inf'),0,0.0
        x,y=z.real,z.imag;best=float('inf');index=0;local=0.0
        def lower(node):
            a,b,c,d=node[0]
            dx=a-x if x<a else (x-c if x>c else 0.0)
            dy=b-y if y<b else (y-d if y>d else 0.0)
            return dx*dx+dy*dy
        stack=[(0.0,self.root)]
        while stack:
            bound,node=stack.pop()
            if bound>best:continue
            if node[2] is None:
                for i in node[1]:
                    a,v,inverse=self.edges[i]
                    dx=x-a.real;dy=y-a.imag
                    t=(dx*v.real+dy*v.imag)*inverse
                    t=0.0 if t<0 else (1.0 if t>1 else t)
                    dx-=t*v.real;dy-=t*v.imag;d=dx*dx+dy*dy
                    if d<best or (d==best and i<index):best,index,local=d,i,t
            else:
                left,right=node[1:];a,b=lower(left),lower(right)
                if a<b:stack.extend(((b,right),(a,left)))
                else:stack.extend(((a,left),(b,right)))
        return math.sqrt(best),index,local


class IndexedLine(list):
    def __init__(self,values):
        super().__init__(values)
        self.segment_index=SegmentIndex(self)
