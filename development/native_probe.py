from i18n import tr

def native_preflight(GSNode, GSPath, make_point, constants, add_midpoint=False, max_controls=2):
    """Exercise actual NSPoint, node and native quadratic drawing APIs."""
    offcurve, curve, qcurve = constants
    probe = GSPath()
    probe.closed = False
    nodes = []
    for xy, kind in [((0,0), 'line'), ((40,80), offcurve), ((100,0), qcurve)]:
        node = GSNode()
        node.position = make_point(float(xy[0]), float(xy[1]))
        node.type = kind
        nodes.append(node)
    probe.nodes = nodes
    actual = list(probe.nodes)
    if len(actual) != 3 or actual[-1].type != qcurve:
        raise RuntimeError(tr('native'))
    # NSBezierPath.bounds is tight geometric bounds, not controlPointBounds.
    rect = probe.bezierPath.bounds()
    values = (rect.origin.x, rect.origin.y, rect.size.width, rect.size.height)
    if max(abs(float(a)-b) for a,b in zip(values,(0.0,0.0,100.0,40.0))) > 1e-5:
        raise RuntimeError(tr('native')+' ' + repr(values))
    implicit = GSPath()
    implicit.closed = False
    nodes = []
    for xy, kind in [((0,0),'line'), ((0,100),offcurve),
                     ((100,100),offcurve), ((100,0),qcurve)]:
        node = GSNode()
        node.position = make_point(float(xy[0]),float(xy[1]))
        node.type = kind
        nodes.append(node)
    implicit.nodes = nodes
    if len(implicit.nodes) != 4 or sum(n.type != offcurve for n in implicit.nodes) != 2:
        raise RuntimeError(tr('native'))
    rect = implicit.bezierPath.bounds()
    values = (rect.origin.x,rect.origin.y,rect.size.width,rect.size.height)
    if max(abs(float(a)-b) for a,b in zip(values,(0,0,100,100))) > 1e-5:
        raise RuntimeError(tr('native')+' ' + repr(values))



    if add_midpoint:
        explicit=GSPath();explicit.closed=False;nodes=[]
        for xy,kind in [((0,0),'line'),((0,100),offcurve),((50,100),qcurve),
                        ((100,100),offcurve),((100,0),qcurve)]:
            node=GSNode();node.position=make_point(float(xy[0]),float(xy[1]))
            node.type=kind;nodes.append(node)
        nodes[2].smooth=True;explicit.nodes=nodes
        rect=explicit.bezierPath.bounds()
        values=(rect.origin.x,rect.origin.y,rect.size.width,rect.size.height)
        if len(explicit.nodes)!=5 or max(abs(float(a)-b) for a,b in zip(values,(0,0,100,100)))>1e-5:
            raise RuntimeError(tr('native')+' '+repr(values))

    if max_controls>2:
        count=3
        chain=GSPath();chain.closed=False;nodes=[]
        points=[(0.0,'line')]+[(100.0*(i+.5)/count,offcurve) for i in range(count)]+[(100.0,qcurve)]
        for x,kind in points:
            node=GSNode();node.position=make_point(x,0.0);node.type=kind;nodes.append(node)
        chain.nodes=nodes;rect=chain.bezierPath.bounds()
        values=(rect.origin.x,rect.origin.y,rect.size.width,rect.size.height)
        if len(chain.nodes)!=count+2 or max(abs(float(a)-b) for a,b in zip(values,(0,0,100,0)))>1e-5:
            raise RuntimeError(tr('native')+' '+repr(values))
