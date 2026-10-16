"""Small API mock; includes native node constructors and NSPoint checks."""
from types import SimpleNamespace

CONSTANTS=('offcurve','curve','qcurve')
class Point:
    def __init__(self,x,y):self.x,self.y=float(x),float(y)
class Node:
    def __init__(self):
        self._position=Point(0,0);self.type='line';self.smooth=False;self.parent=None
        self.name='';self.userData={}
    @property
    def position(self):return self._position
    @position.setter
    def position(self,p):
        if not isinstance(p,Point):raise TypeError('NSPoint expected')
        self._position=p
    @property
    def selected(self):
        return self.parent is not None and self.parent.parent is not None and self in self.parent.parent.selection
class Path:
    def __init__(self):self._nodes=[];self.closed=False;self.parent=None;self.fail_once=False
    @property
    def nodes(self):return self._nodes
    @nodes.setter
    def nodes(self,value):
        if self.fail_once:self.fail_once=False;raise RuntimeError('Injected write failure')
        for n in self._nodes:n.parent=None
        self._nodes=list(value)
        for n in self._nodes:n.parent=self
    @property
    def bezierPath(self):
        parts=[];start=complex(self.nodes[0].position.x,self.nodes[0].position.y);controls=[]
        for n in self.nodes[1:]:
            z=complex(n.position.x,n.position.y)
            if n.type=='offcurve':controls.append(z);continue
            for i,q in enumerate(controls):
                finish=(q+controls[i+1])/2 if i<len(controls)-1 else z
                parts.append((start,q,finish));start=finish
            controls=[]
        xs=[];ys=[]
        for a,q,b in parts:
            xs.extend((a.real,b.real));ys.extend((a.imag,b.imag))
            for axis,out in [('real',xs),('imag',ys)]:
                aa,qq,bb=(getattr(v,axis) for v in (a,q,b));den=aa-2*qq+bb
                if den:
                    t=(aa-qq)/den
                    if 0<t<1:out.append((1-t)**2*aa+2*t*(1-t)*qq+t*t*bb)
        r=SimpleNamespace(origin=Point(min(xs),min(ys)),
            size=SimpleNamespace(width=max(xs)-min(xs),height=max(ys)-min(ys)))
        return SimpleNamespace(bounds=lambda:r)
class Layer:
    def __init__(self,paths=(),layer_id='m0',special=False):
        self.paths=list(paths);self.components=[];self.anchors=[];self.hints=[]
        self.parent=None;self.selection=[];self.depth=0;self.groups=0
        self.layerId=layer_id;self.associatedMasterId='m0';self.name=layer_id
        self.isMasterLayer=not special;self.isSpecialLayer=special
        for p in self.paths:p.parent=self
    @property
    def shapes(self):return self.paths+self.components
    def compareString(self):
        return repr([(bool(p.closed),[n.type for n in p.nodes]) for p in self.paths])+repr([c.componentName for c in self.components])
    def beginChanges(self):self.depth+=1;self.groups+=1
    def endChanges(self):self.depth-=1
class Layers:
    def __init__(self,layers):self.values=list(layers)
    def __iter__(self):return iter(self.values)
    def __getitem__(self,key):
        if isinstance(key,int):return self.values[key]
        return next((l for l in self.values if l.layerId==key),None)
class Glyph:
    def __init__(self,name,layers):
        self.name=name;self.layers=Layers(layers);self.parent=None;self.override=None
        for l in layers:l.parent=self
    @property
    def mastersCompatible(self):
        if self.override is not None:return self.override
        from glyphs_adapter import structure
        relevant=[l for l in self.layers if l.isMasterLayer or l.isSpecialLayer]
        return len({structure(l) for l in relevant})<=1
class Undo:
    def __init__(self):self.depth=0;self.groups=0
    def beginUndoGrouping(self):self.depth+=1;self.groups+=1
    def endUndoGrouping(self):self.depth-=1
class Font:
    def __init__(self,glyphs,masters=1,edit=True):
        self.glyphs={g.name:g for g in glyphs};self.masters=[SimpleNamespace(id='m'+str(i)) for i in range(masters)]
        self.selectedFontMaster=self.masters[0];self.selection=[];self.selectedLayers=[]
        self.currentTab=object() if edit else None;self.instances=[];self.events=[]
        self.undo=Undo();self.parent=SimpleNamespace(undoManager=lambda:self.undo)
        for g in glyphs:g.parent=self
    def disableUpdateInterface(self):self.events.append('stop')
    def enableUpdateInterface(self):self.events.append('start')
class Component:
    def __init__(self,name,selected=False):self.componentName=name;self.selected=selected

def node(z,kind):
    n=Node();n.type=kind;n.position=Point(z.real,z.imag);return n
def path(p):
    result=Path();result.nodes=[node(z,t) for z,t in zip(p,('line','offcurve','offcurve','curve'))]
    return result
EXACT=(0j,40+80j,280/3+80j,160+0j)
HARD=(0j,30+120j,180+10j,220+0j)
PAIR_NEEDED=(0j,30+130j,180+40j,220+0j)
def glyph(name='A',sources=(EXACT,)):
    return Glyph(name,[Layer([path(p)],'m'+str(i)) for i,p in enumerate(sources)])
