# -*- coding: utf-8 -*-
"""Selection, synchronized masters, staged edits and one undo transaction."""
import math
from contextlib import ExitStack
from collections import deque
from builtins import id as _python_id
from fast_fit import fit_corresponding
from merge_fit import fit_run_corresponding
from tangent_constraints import aligned
from i18n import tr
from preferences import validated_settings
try:
    from objc import pyobjc_id as _objc_id
except ImportError:
    _objc_id=None


def object_id(obj):
    """Native pointers survive recreation of Python proxy wrappers."""
    if _objc_id is not None and obj is not None:
        try:return _objc_id(obj)
        except (TypeError,ValueError):pass
    return _python_id(obj)


class ConversionError(RuntimeError):
    pass


def flag(obj,name,default=False):
    value=getattr(obj,name,default)
    return value() if callable(value) else value


def validate_nodes(nodes,closed,offcurve,curve,qcurve,overrides=None):
    overrides=overrides or {};types=[overrides.get(i,n.type) for i,n in enumerate(nodes)]
    ons=[i for i,t in enumerate(types) if t!=offcurve]
    if not ons:return bool(closed) and bool(nodes)
    if not closed and (ons[0]!=0 or ons[-1]!=len(nodes)-1):return False
    pairs=list(zip(ons,ons[1:]))
    if closed:pairs.append((ons[-1],ons[0]+len(nodes)))
    for start,end in pairs:
        count=end-start-1;kind=types[end%len(nodes)]
        if kind==curve:
            if count!=2:return False
        elif kind==qcurve:
            if count<1:return False
        elif count:return False
    return True


def cubic_keys(layer,constants,selected=False):
    offcurve,curve,qcurve=constants;keys=set()
    for pi,path in enumerate(layer.paths):
        nodes=list(path.nodes);n=len(nodes)
        if n<3:continue
        for i in range(n if path.closed else max(0,n-3)):
            part=[nodes[(i+j)%n] for j in range(4)]
            if not (part[0].type!=offcurve and part[1].type==offcurve and
                    part[2].type==offcurve and part[3].type==curve):continue
            if not selected or ((part[0].selected and part[3].selected) or
                                (part[1].selected and part[2].selected)):
                keys.add((pi,i))
    return keys


def layer_for_master(glyph,master_id):
    try:layer=glyph.layers[master_id]
    except (KeyError,TypeError,IndexError):layer=None
    if layer is None:raise ConversionError(tr('missing_master')+str(master_id))
    return layer


def structure(layer):
    shapes=[]
    for shape in layer.shapes:
        if hasattr(shape,'nodes'):
            shapes.append(('path',bool(shape.closed),tuple(n.type for n in shape.nodes),
                           flag(shape,'direction',None)))
        else:shapes.append(('component',str(shape.componentName)))
    anchors=tuple(sorted(a if isinstance(a,str) else str(a.name) for a in layer.anchors))
    return str(layer.compareString()),tuple(shapes),anchors


def layer_glyph(layer):
    parent=getattr(layer,'parent',None)
    if parent is not None and hasattr(parent,'layers'):return parent
    foreground=flag(layer,'foreground',None)
    return getattr(foreground,'parent',None) if foreground is not None else None


def independent_layer(layer):
    return flag(layer,'foreground',None) is not None or not (flag(layer,'isMasterLayer') or flag(layer,'isSpecialLayer'))


def synchronized_layers(font,glyph,sources,constants,independent=False):
    if independent:
        layers=list(sources)
        for layer in layers:
            foreground=flag(layer,'foreground',None)
            attached=(object_id(flag(foreground,'background',None))==object_id(layer) and object_id(layer_glyph(foreground))==object_id(glyph)) if foreground is not None else any(object_id(layer)==object_id(x) for x in glyph.layers)
            if not attached:raise ConversionError(tr('changed_layers'))
    else:
        layers=[layer_for_master(glyph,m.id) for m in font.masters]
        for layer in glyph.layers:
            if flag(layer,'isSpecialLayer') and all(object_id(layer)!=object_id(x) for x in layers):layers.append(layer)
    if not layers:raise ConversionError(tr('no_master'))
    if any(all(object_id(source)!=object_id(x) for x in layers) for source in sources):
        raise ConversionError(tr('changed_layers'))
    if not independent and len(layers)>1 and not bool(glyph.mastersCompatible):
        raise ConversionError(tr('incompatible'))
    expected=structure(layers[0])
    for layer in layers:
        if structure(layer)!=expected:
            raise ConversionError(tr('structure'))
        if any(not validate_nodes(list(p.nodes),bool(p.closed),*constants) for p in layer.paths):
            raise ConversionError(tr('unsupported'))
    return layers


def selected_requests(font,constants):
    requests=[]
    if font.currentTab is None:
        # Font View selection is separate from the Edit View layer selection.
        for glyph in list(font.selection or []):
            requests.append((glyph,layer_for_master(glyph,font.selectedFontMaster.id),True,set()))
    else:
        layers=list(font.selectedLayers or [])
        active=flag(font.currentTab,'activeLayer',None)
        if active is None:
            try:active=flag(font.parent.windowController(),'activeLayer',None)
            except AttributeError:pass
        foreground=flag(active,'foreground',None) if active is not None else None
        if foreground is not None and layers:
            layers=[active if object_id(layer)==object_id(foreground) else layer for layer in layers]
        if not layers:
            # A text insertion cursor can have an active glyph without a range.
            if active is None:
                tab=font.currentTab;visible=list(getattr(tab,'layers',[]) or [])
                cursor=int(getattr(tab,'layersCursor',0))
                active=visible[cursor] if 0<=cursor<len(visible) else None
            if active is not None:layers=[active]
        for layer in layers:
            glyph=layer_glyph(layer)
            if glyph is None or not hasattr(glyph,'layers'):continue
            whole=not bool(list(layer.selection))
            requests.append((glyph,layer,whole,cubic_keys(layer,constants,selected=True)))
    return requests


def prepare_tasks(font,constants):
    initial=selected_requests(font,constants)
    if not initial:return [],[],[]
    registry={};queue=deque()
    def add(glyph,layer,whole,keys):
        independent=independent_layer(layer);name=(glyph.name,object_id(layer) if independent else None)
        if name not in registry:
            registry[name]=dict(glyph=glyph,sources=[],whole=False,keys=set(),revision=0,independent=independent)
        item=registry[name]
        changed=(whole and not item['whole']) or not keys.issubset(item['keys'])
        if all(object_id(layer)!=object_id(x) for x in item['sources']):item['sources'].append(layer);changed=True
        item['whole']|=whole;item['keys'].update(keys)
        if changed:item['revision']+=1;queue.append((name,item['revision']))
    for args in initial:add(*args)
    checked={};invalid=set()
    while queue:
        name,revision=queue.popleft();item=registry[name]
        if revision!=item['revision'] or name in invalid:continue
        try:layers=synchronized_layers(font,item['glyph'],item['sources'],constants,item['independent'])
        except Exception:invalid.add(name);continue
        checked[name]=layers
        # Components remain references. Convert their base glyphs recursively.
        names=set()
        for source in ([] if item['independent'] else item['sources']):
            for comp in source.components:
                if item['whole'] or bool(flag(comp,'selected')):names.add(str(comp.componentName))
        for base_name in sorted(names):
            try:
                base=font.glyphs[base_name]
                if base is None:raise KeyError(base_name)
                add(base,layer_for_master(base,font.selectedFontMaster.id),True,set())
            except Exception:invalid.add(name)
    tasks=[];groups=[];guards=[]
    for name,item in registry.items():
        if name in invalid:continue
        layers=checked[name]
        item['layers']=layers
        item['snapshots']={object_id(l):[(p,tuple(p.nodes),path_state(p)) for p in l.paths] for l in layers}
        item['structure_before']={object_id(l):structure(l) for l in layers}
        guards.append(item)
        keys=cubic_keys(layers[0],constants) if item['whole'] else item['keys']
        if not keys:continue
        # Native hints can reference off-curve nodes. Do not leave dangling refs.
        removed=set()
        for layer in layers:
            for pi,i in keys:
                nodes=list(layer.paths[pi].nodes);n=len(nodes)
                removed.update(object_id(nodes[(i+j)%n]) for j in (1,2))
        hints_bad=any(object_id(getattr(h,key,None)) in removed for l in layers for h in l.hints
                      for key in ('originNode','targetNode','otherNode1','otherNode2'))
        if hints_bad:continue
        item['keys']=keys
        item['selected_sources']={object_id(l) for l in item['sources']} if not item['whole'] else set()
        tasks.append(item)
        groups.extend((item,pi,i) for pi,i in sorted(keys))
    return tasks,groups,guards


def curve_runs(tasks,angle_limit=2.0):
    """Only selected cubics are grouped; native hint targets remain boundaries."""
    groups=[]
    for item in tasks:
        by_path={}
        for pi,i in item['keys']:by_path.setdefault(pi,set()).add(i)
        for pi,starts in sorted(by_path.items()):
            path=item['layers'][0].paths[pi];n=len(path.nodes);closed=bool(path.closed);protected=set()
            for layer in item['layers']:
                references={object_id(getattr(h,key)) for h in layer.hints
                            for key in ('originNode','targetNode','otherNode1','otherNode2')
                            if getattr(h,key,None) is not None}
                protected.update(i for i in starts if object_id(layer.paths[pi].nodes[i]) in references)
            for i in starts:
                previous=(i-3)%n if closed else i-3
                if previous not in starts:continue
                for layer in item['layers']:
                    nodes=layer.paths[pi].nodes
                    point=lambda j:complex(float(nodes[j%n].position.x),float(nodes[j%n].position.y))
                    if not aligned(point(i)-point(i-1),point(i+1)-point(i),angle_limit):protected.add(i);break
            def successor(i):
                next_i=(i+3)%n if closed else i+3
                return next_i if next_i in starts and next_i not in protected else None
            def has_previous(i):
                previous=(i-3)%n if closed else i-3
                return i not in protected and previous in starts
            visited=set()
            for start in sorted(i for i in starts if not has_previous(i))+sorted(starts):
                if start in visited:continue
                indices=[];i=start
                while i is not None and i not in visited:
                    visited.add(i);indices.append(i);i=successor(i)
                groups.append((item,pi,indices,closed and i==start))
    return groups


def line_tangents(layer,pi,indices,constants,angle_limit):
    path=layer.paths[pi];nodes=path.nodes;n=len(nodes);closed=bool(path.closed)
    offcurve,curve,qcurve=constants;start=indices[0];end=(indices[-1]+3)%n
    point=lambda i:complex(float(nodes[i%n].position.x),float(nodes[i%n].position.y))
    left=right=None
    if (closed or start>0) and nodes[(start-1)%n].type!=offcurve and nodes[start].type not in constants:
        direction=point(start)-point(start-1)
        if aligned(point(start+1)-point(start),direction,angle_limit/2):left=(point(start),direction)
    if (closed or end<n-1) and nodes[(end+1)%n].type not in constants:
        direction=point(end)-point(end+1)
        if aligned(point(end-1)-point(end),direction,angle_limit/2):right=(point(end),direction)
    return left,right


def curve_tangents(layer,pi,indices,constants,angle_limit):
    path=layer.paths[pi];nodes=path.nodes;n=len(nodes);closed=bool(path.closed)
    offcurve,curve,qcurve=constants
    point=lambda i:complex(float(nodes[i%n].position.x),float(nodes[i%n].position.y))
    def at_join(i):
        if not closed and (i<3 or i+3>=n):return None
        if not (nodes[i%n].type==curve and nodes[(i-1)%n].type==offcurve and
                nodes[(i-2)%n].type==offcurve and nodes[(i-3)%n].type!=offcurve and
                nodes[(i+1)%n].type==offcurve and nodes[(i+2)%n].type==offcurve and
                nodes[(i+3)%n].type==curve):return None
        incoming=point(i)-point(i-1);outgoing=point(i+1)-point(i)
        if not aligned(incoming,outgoing,angle_limit):return None
        mean=incoming/abs(incoming)+outgoing/abs(outgoing)
        return mean/abs(mean) if abs(mean)>1e-12 else None
    start=indices[0];end=(indices[-1]+3)%n;left=at_join(start);right=at_join(end)
    return ((point(start),left) if left is not None else None,
            (point(end),-right) if right is not None else None)


def path_state(path):
    return bool(path.closed),tuple((object_id(n),n.type,float(n.position.x),float(n.position.y),bool(n.smooth))
                                   for n in path.nodes)


def build_path_plan(path,results,GSNode,make_point,constants,sharp,add_midpoint=False):
    offcurve,curve,qcurve=constants;nodes=list(path.nodes);n=len(nodes)
    edits={};types={};new=[]
    for i,result in sorted(results.items()):
        span=result.get('source_count',1)
        ids=[(i+j)%n for j in range(3*span+1)];controls=[]
        for part_index,q in enumerate(result['parts']):
            node=GSNode();node.position=make_point(float(q[1].real),float(q[1].imag));node.type=offcurve
            controls.append(node);new.append(node)
            if add_midpoint and part_index<len(result['parts'])-1:
                m=q[2] if result.get('integer_coords') else (q[1]+result['parts'][part_index+1][1])/2
                midpoint=GSNode();midpoint.position=make_point(float(m.real),float(m.imag))
                midpoint.type=qcurve;midpoint.smooth=True
                controls.append(midpoint);new.append(midpoint)
        edits[ids[1]]=controls
        for index in ids[2:-1]:edits[index]=[]
        types[ids[-1]]=qcurve
    output=[];mapping={}
    for i,node in enumerate(nodes):
        if i in edits:output.extend(edits[i])
        else:mapping[i]=len(output);output.append(node)
    if not validate_nodes(output,bool(path.closed),*constants,
                          overrides={mapping[i]:kind for i,kind in types.items()}):
        raise ConversionError(tr('invalid_nodes'))
    return dict(path=path,original=nodes,output=output,
                types=[(nodes[i],kind) for i,kind in types.items()],
                sharp=[nodes[i] for i in sharp],new=new,
                removed={object_id(nodes[i]) for i in edits},
                status=[(node,node.type,bool(node.smooth)) for node in nodes])


def commit_plans(font,batches,tasks,constants):
    # Recheck structure and coordinates after asynchronous planning, before writes.
    for item in tasks:
        if object_id(item['glyph'].parent)!=object_id(font):raise ConversionError(tr('left_font'))
        for layer in item['layers']:
            if structure(layer)!=item['structure_before'][object_id(layer)]:
                raise ConversionError(tr('changed_structure')+item['glyph'].name)
            original=item['snapshots'][object_id(layer)];current=list(layer.paths)
            if len(current)!=len(original) or any(object_id(p)!=object_id(old) or path_state(p)!=state
                   for p,(old,retained_nodes,state) in zip(current,original)):
                raise ConversionError(tr('edited')+item['glyph'].name)
        current_layers=synchronized_layers(font,item['glyph'],item['sources'],constants,item['independent'])
        if [object_id(l) for l in current_layers]!=[object_id(l) for l in item['layers']]:
            raise ConversionError(tr('changed_layers'))
    for layer,plans,select_new in batches:
        removed={key for plan in plans for key in plan['removed']}
        if any(object_id(getattr(h,key,None)) in removed for h in layer.hints
               for key in ('originNode','targetNode','otherNode1','otherNode2')):
            raise ConversionError(tr('hint_changed'))
    old_selection={object_id(layer):list(layer.selection) for layer,plans,select_new in batches}
    document=getattr(font,'parent',None)
    manager=document.undoManager() if document is not None else None
    with ExitStack() as stack:
        font.disableUpdateInterface();stack.callback(font.enableUpdateInterface)
        if manager is not None:
            manager.beginUndoGrouping();stack.callback(manager.endUndoGrouping)
        for layer,plans,select_new in batches:
            layer.beginChanges();stack.callback(layer.endChanges)
        try:
            for layer,plans,select_new in batches:
                removed={key for plan in plans for key in plan['removed']}
                selection=[x for x in old_selection[object_id(layer)] if object_id(x) not in removed]
                for plan in plans:
                    for node,kind in plan['types']:node.type=kind
                    for node in plan['sharp']:node.smooth=False
                    plan['path'].nodes=plan['output']
                    if select_new:selection.extend(plan['new'])
                layer.selection=selection
            for item in tasks:
                if not item['independent'] and len(item['layers'])>1 and not bool(item['glyph'].mastersCompatible):
                    raise ConversionError(tr('post_compat')+item['glyph'].name)
        except Exception as original:
            failures=[]
            for layer,plans,select_new in reversed(batches):
                for plan in reversed(plans):
                    try:
                        for node,kind,smooth in plan['status']:node.type=kind;node.smooth=smooth
                        plan['path'].nodes=plan['original']
                    except Exception as exc:failures.append(str(exc))
                try:layer.selection=old_selection[object_id(layer)]
                except Exception as exc:failures.append(str(exc))
            if failures:raise ConversionError(str(original)+tr('rollback')+'；'.join(failures)) from original
            raise


def conversion_steps(font,GSNode,make_point,constants,tolerance=1.0,max_controls=2,
                     active_font=None,add_midpoint=False,preflight=None,fit_runner=None,merge_curves=False,center_limit=0.0,integer_coords=False,angle_limit=2.0,keep_line_tangent=False,keep_curve_tangent=False):
    values=validated_settings(tolerance,max_controls,add_midpoint,merge_curves=merge_curves,center_limit=center_limit,integer_coords=integer_coords,angle_limit=angle_limit,keep_line_tangent=keep_line_tangent,keep_curve_tangent=keep_curve_tangent)
    tolerance=values['deviation'];max_controls=values['max_controls'];add_midpoint=values['add_midpoint'];merge_curves=values['merge_curves']
    upm=float(getattr(font,'upm',1000));font_scale=upm/1000
    if not math.isfinite(upm) or upm<=0:raise ConversionError(tr('invalid_upm'))
    tolerance*=font_scale
    options=dict(center_limit=values['center_limit']*font_scale,integer_step=1.0 if values['integer_coords'] else 0.0,
                 explicit_midpoint=add_midpoint) if values['center_limit'] or values['integer_coords'] else {}
    tasks,groups,guards=prepare_tasks(font,constants)
    groups=curve_runs(tasks,values['angle_limit']) if merge_curves else [(item,pi,[i],False) for item,pi,i in groups]
    total=len(groups);results={};sharp={}
    if not groups:return False
    if preflight is not None:preflight()
    yield dict(done=0,total=total,glyph=tr('preparing'))
    for done,(item,pi,indices,cyclic) in enumerate(groups,1):
        if active_font is not None and object_id(active_font())!=object_id(font):raise ConversionError(tr('changed_font'))
        chains=[]
        for layer in item['layers']:
            nodes=list(layer.paths[pi].nodes);n=len(nodes)
            chains.append(tuple(tuple(complex(float(nodes[(i+j)%n].position.x),float(nodes[(i+j)%n].position.y))
                                      for j in range(4)) for i in indices))
        progress=dict(done=done-1,total=total,glyph=item['glyph'].name)
        extra=dict(options,center_tolerance=tolerance/2)
        if values['keep_line_tangent'] or values['keep_curve_tangent']:
            joins=[]
            for layer in item['layers']:
                pairs=[]
                for i in indices:
                    line=line_tangents(layer,pi,[i],constants,values['angle_limit']) if values['keep_line_tangent'] else (None,None)
                    curve=curve_tangents(layer,pi,[i],constants,values['angle_limit']) if values['keep_curve_tangent'] else (None,None)
                    pairs.append(tuple(a if a is not None else b for a,b in zip(line,curve)))
                joins.append(pairs)
            if len(indices)>1:extra['join_tangents']=joins
            else:extra['tangents']=[pairs[0] for pairs in joins]
        if len(indices)>1:
            if fit_runner is None:blocks=fit_run_corresponding(chains,tolerance,max_controls,cyclic,single_tolerance=tolerance/2,angle_limit=values['angle_limit'],**extra)
            else:blocks=yield from fit_runner(chains,tolerance,max_controls,progress,merge=True,cyclic=cyclic,single_tolerance=tolerance/2,angle_limit=values['angle_limit'],**extra)
        else:
            curves=[chain[0] for chain in chains]
            if fit_runner is None:fits=fit_corresponding(curves,tolerance/2,max_controls,comparison_tolerance=tolerance,**extra)
            else:fits=yield from fit_runner(curves,tolerance/2,max_controls,progress,comparison_tolerance=tolerance,**extra)
            blocks=[dict(start=0,count=1,fits=fits)]
        for block in blocks:
            i=indices[block['start']];span=block['count'];fits=block['fits']
            if len({len(r['parts']) for r in fits})!=1:raise ConversionError(tr('count_mismatch'))
            any_angle=[any(r['angles'][k] is not None and abs(r['angles'][k])>1e-6 and not r.get('tangents',(None,None))[k] for r in fits) for k in (0,1)]
            for layer,r in zip(item['layers'],fits):
                key=(object_id(layer),pi);result=dict(r,source_count=span,integer_coords=values['integer_coords'])
                results.setdefault(key,{})[i]=result
                n=len(layer.paths[pi].nodes)
                sharp.setdefault(key,set()).update((i+(0 if k==0 else 3*span))%n for k in (0,1) if any_angle[k])
        yield dict(done=done,total=total,glyph=item['glyph'].name)
    batches=[]
    for item in tasks:
        for layer in item['layers']:
            plans=[]
            for pi,path in enumerate(layer.paths):
                key=(object_id(layer),pi)
                if key in results:plans.append(build_path_plan(path,results[key],GSNode,make_point,constants,sharp[key],add_midpoint=add_midpoint))
            if plans:batches.append((layer,plans,object_id(layer) in item['selected_sources']))
    if active_font is not None and object_id(active_font())!=object_id(font):raise ConversionError(tr('changed_font'))
    if float(getattr(font,'upm',1000))!=upm:raise ConversionError(tr('changed_upm'))
    if batches:commit_plans(font,batches,guards,constants)
    return bool(batches)


def make_job(tolerance=1.0,max_controls=3,add_midpoint=False,fit_runner=None,merge_curves=True,center_limit=7.0,integer_coords=True,angle_limit=5.0,keep_line_tangent=True,keep_curve_tangent=True):
    from GlyphsApp import Glyphs,GSNode,GSPath,OFFCURVE,CURVE,QCURVE
    from Foundation import NSMakePoint
    from native_probe import native_preflight
    values=validated_settings(tolerance,max_controls,add_midpoint,merge_curves=merge_curves,center_limit=center_limit,integer_coords=integer_coords,angle_limit=angle_limit,keep_line_tangent=keep_line_tangent,keep_curve_tangent=keep_curve_tangent)
    tolerance=values['deviation'];max_controls=values['max_controls'];add_midpoint=values['add_midpoint'];merge_curves=values['merge_curves']
    font=Glyphs.font
    if font is None:raise ConversionError(tr('no_font'))
    constants=(OFFCURVE,CURVE,QCURVE)
    preflight=lambda:native_preflight(GSNode,GSPath,NSMakePoint,constants,add_midpoint=add_midpoint,max_controls=max_controls)
    return conversion_steps(font,GSNode,NSMakePoint,constants,tolerance,max_controls,
                            lambda:Glyphs.font,add_midpoint,preflight,fit_runner,merge_curves,center_limit,integer_coords,angle_limit,keep_line_tangent,keep_curve_tangent)


def show_message(text,title=None):
    from GlyphsApp import Message
    Message(title=title or tr('title'),message=text,OKButton=tr('ok'))

def glyphs_main(tolerance=1.0,max_controls=3,add_midpoint=False,merge_curves=True,center_limit=7.0,integer_coords=True,angle_limit=3.0,keep_line_tangent=True,keep_curve_tangent=True):
    from GlyphsApp import Glyphs
    job=make_job(tolerance,max_controls,add_midpoint,merge_curves=merge_curves,center_limit=center_limit,integer_coords=integer_coords,angle_limit=angle_limit,keep_line_tangent=keep_line_tangent,keep_curve_tangent=keep_curve_tangent)
    while True:
        try:next(job)
        except StopIteration as done:
            if done.value:Glyphs.redraw()
            return done.value
