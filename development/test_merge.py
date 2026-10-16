# -*- coding: utf-8 -*-
import contextlib,io,sys,unittest
from types import SimpleNamespace
from unittest.mock import patch
from mock_glyphs import *
from quad_fit import split,quadratic,cubic
from geometry_fit import geometric_bounds,nearest_quadratic
from merge_fit import CompositeContext,fit_run_corresponding
from glyphs_adapter import conversion_steps,curve_runs,prepare_tasks,validate_nodes
from preferences import DEFAULT_SETTINGS,load_settings
from test_settings import finish
from test_entrypoints import modules,load,plugin_files

def elevated(q):
    return (q[0],(q[0]+2*q[1])/3,(2*q[1]+q[2])/3,q[2])
def line(a,b):
    return a,a+(b-a)/3,a+2*(b-a)/3,b
def pieces(p):
    a,rest=split(p,.3);b,c=split(rest,.6);return a,b,c
QUADRATIC=elevated((0j,60+100j,200+20j))
THREE=pieces(QUADRATIC)
def joined_path(curves,closed=False,rotation=0):
    p=Path();p.closed=closed
    nodes=[node(curves[0][0],'curve' if closed else 'line')]
    for q in curves:
        nodes.extend([node(q[1],'offcurve'),node(q[2],'offcurve'),node(q[3],'curve')])
    if closed:nodes.pop()
    p.nodes=nodes[rotation:]+nodes[:rotation]
    return p
def joined_font(chains=(THREE,),closed=False,rotation=0):
    g=Glyph('A',[Layer([joined_path(chain,closed,rotation)],'m'+str(i)) for i,chain in enumerate(chains)])
    f=Font([g],len(chains));f.selectedLayers=[g.layers[0]]
    return f,g
def convert(f,**kw):
    return finish(conversion_steps(f,Node,Point,CONSTANTS,**kw))
def signature(f):
    return [[(n.type,n.position.x,n.position.y) for n in l.paths[0].nodes] for l in f.glyphs['A'].layers]

class MergeTests(unittest.TestCase):
    def test_setting_default_on_and_persistent(self):
        f,g=joined_font();app=modules(f)['GlyphsApp'].Glyphs
        self.assertTrue(DEFAULT_SETTINGS['merge_curves'])
        self.assertTrue(load_settings(app)['merge_curves'])

    def test_disabled_keeps_original_join_objects_and_results(self):
        a,ga=joined_font();b,gb=joined_font()
        joins=[ga.layers[0].paths[0].nodes[i] for i in (3,6)]
        convert(a);convert(b,merge_curves=False)
        self.assertEqual(signature(a),signature(b))
        self.assertTrue(all(n in ga.layers[0].paths[0].nodes for n in joins))

    def test_exact_three_piece_quadratic_merges_to_one(self):
        f,g=joined_font();p=g.layers[0].paths[0];start,end=p.nodes[0],p.nodes[-1];joins=p.nodes[3],p.nodes[6]
        r=convert(f,merge_curves=True,tolerance=.05,max_controls=1)
        self.assertEqual([n.type for n in p.nodes],['line','offcurve','qcurve'])
        self.assertIs(p.nodes[0],start);self.assertIs(p.nodes[-1],end)
        self.assertTrue(all(n not in p.nodes for n in joins))
        self.assertTrue(r);self.assertEqual(f.undo.groups,1)
        fitted=tuple(complex(n.position.x,n.position.y) for n in p.nodes)
        for source in THREE:
            for i in range(101):self.assertLess(nearest_quadratic(cubic(source,i/100),fitted)[0],.05)

    def test_first_pair_merge_and_last_single_fallback(self):
        chain=THREE[:2]+(line(THREE[1][3],300+200j),)
        r=fit_run_corresponding([chain],.05,1)
        self.assertEqual([(b['start'],b['count']) for b in r],[(0,2),(2,1)])

    def test_first_single_and_last_pair_merge(self):
        chain=(line(-100-100j,THREE[0][0]),)+THREE[:2]
        r=fit_run_corresponding([chain],.05,1)
        self.assertEqual([(b['start'],b['count']) for b in r],[(0,1),(1,2)])

    def test_overlapping_pair_candidates_compared_once(self):
        calls=[];chain=(line(0j,100+0j),line(100+0j,200+0j),line(200+0j,300+0j))
        def candidate(chains,tolerance,max_controls,cancel,**options):
            start=int(chains[0][0][0].real/100);count=len(chains[0]);calls.append((start,count))
            if count==3:return None
            error=.2 if start==0 else .1
            return [dict(parts=[(chains[0][0][0],150+0j,chains[0][-1][-1])],error=(error,error),within=True,angles=(0,0))]
        with patch('merge_fit.try_merged_corresponding',candidate):
            r=fit_run_corresponding([chain],.5,1)
        self.assertEqual([(b['start'],b['count']) for b in r],[(0,1),(1,2)])
        self.assertEqual(calls.count((0,2)),1);self.assertEqual(calls.count((1,2)),1)

    def test_rejected_pair_retains_join_and_normal_cap_behavior(self):
        chain=(line(0j,100j),line(100j,100+100j));f,g=joined_font((chain,))
        p=g.layers[0].paths[0];join=p.nodes[3]
        convert(f,merge_curves=True,tolerance=.05,max_controls=1)
        self.assertIn(join,p.nodes);self.assertEqual(len(p.nodes),5)

    def test_merged_bounds_check_at_control_limit(self):
        bad=dict(parts=[(0j,50j,100+100j)],error=(2,2),within=False,angles=(0,0))
        with patch('merge_fit.fit_merged_count',return_value=bad) as checked:
            r=fit_run_corresponding([THREE[:2]],.05,1)
        self.assertEqual(checked.call_count,1)
        self.assertEqual([b['count'] for b in r],[1,1])

    def test_compound_continuous_bounds_cover_join(self):
        chain=(line(0j,100j),line(100j,100+100j))
        fitted=[(0j,50+50j,100+100j)]
        lo,hi=geometric_bounds((0j,0j,100+100j,100+100j),fitted,.05,source_curves=chain)
        self.assertGreater(lo,70.70);self.assertLess(hi,70.72)

    def test_master_partition_must_pass_every_layer(self):
        other=THREE[:2]+(line(THREE[1][3],300+200j),)
        f,g=joined_font((THREE,other));old=[(l.paths[0].nodes[3],l.paths[0].nodes[6]) for l in g.layers]
        convert(f,merge_curves=True,tolerance=.05,max_controls=1)
        for l,(removed,retained) in zip(g.layers,old):
            self.assertNotIn(removed,l.paths[0].nodes);self.assertIn(retained,l.paths[0].nodes)
            self.assertEqual(len(l.paths[0].nodes),5)
        self.assertTrue(g.mastersCompatible)

    def test_unselected_neighbour_is_not_merged(self):
        f,g=joined_font();p=g.layers[0].paths[0];last=p.nodes[6]
        g.layers[0].selection=[p.nodes[i] for i in (1,2,4,5)]
        convert(f,merge_curves=True,tolerance=.05,max_controls=1)
        self.assertIn(last,p.nodes);self.assertEqual([n.type for n in p.nodes][-3:],['offcurve','offcurve','curve'])
        self.assertEqual(len(p.nodes),6)

    def test_straight_segment_separates_runs(self):
        f,g=joined_font();p=g.layers[0].paths[0];p.nodes=p.nodes[:4]+[node(300+20j,'line')]+[node(310+80j,'offcurve'),node(380+80j,'offcurve'),node(400+20j,'curve')]
        tasks,*_=prepare_tasks(f,CONSTANTS);groups=curve_runs(tasks)
        self.assertEqual([indices for _,_,indices,_ in groups],[[0],[4]])
        convert(f,merge_curves=True);self.assertTrue(any(n.type=='line' and n.position.x==300 for n in p.nodes))

    def test_hint_target_between_cubics_is_preserved(self):
        f,g=joined_font();p=g.layers[0].paths[0];protected=p.nodes[3]
        g.layers[0].hints=[SimpleNamespace(originNode=protected)]
        convert(f,merge_curves=True,tolerance=.05,max_controls=1)
        self.assertIn(protected,p.nodes);self.assertIs(g.layers[0].hints[0].originNode,protected)

    def test_closed_full_run_and_rotated_start(self):
        q0=(0j,40+80j,80j);q1=(80j,-40+80j,0j);chain=(elevated(q0),elevated(q1))
        for rotation in (0,1,2):
            f,g=joined_font((chain,),True,rotation)
            convert(f,merge_curves=True,tolerance=.05,max_controls=2)
            p=g.layers[0].paths[0]
            self.assertEqual(len(p.nodes),3);self.assertEqual(sum(n.type=='qcurve' for n in p.nodes),1)
            self.assertTrue(validate_nodes(p.nodes,True,*CONSTANTS))

    def test_closed_wrap_partition_is_considered(self):
        chain=(line(0j,100+100j),line(100+100j,200+0j),line(200+0j,0j))
        def candidate(chains,tolerance,max_controls,cancel,**options):
            points=[p[0].real for p in chains[0]]
            if points!=[200,0]:return None
            return [dict(parts=[(200+0j,50+20j,100+100j)],error=(.01,.02),within=True,angles=(0,0))]
        with patch('merge_fit.try_merged_corresponding',candidate):
            r=fit_run_corresponding([chain],.5,1,cyclic=True,angle_limit=180)
        self.assertEqual({(b['start'],b['count']) for b in r},{(2,2),(1,1)})

    def test_midpoint_option_applies_to_new_fitted_controls(self):
        chain=(elevated((0j,40+80j,80j)),elevated((80j,-40+80j,0j)))
        f,g=joined_font((chain,),True)
        old=g.layers[0].paths[0].nodes[3]
        convert(f,merge_curves=True,add_midpoint=True,tolerance=.05,max_controls=2)
        nodes=g.layers[0].paths[0].nodes
        self.assertNotIn(old,nodes);self.assertEqual(len(nodes),4)
        self.assertEqual(sum(n.type=='qcurve' for n in nodes),2)

    def test_merge_write_failure_rolls_back_old_anchors(self):
        f,g=joined_font((THREE,THREE));old=[list(l.paths[0].nodes) for l in g.layers]
        g.layers[1].paths[0].fail_once=True
        with self.assertRaisesRegex(RuntimeError,'Injected'):
            convert(f,merge_curves=True,tolerance=.05,max_controls=1)
        for l,nodes in zip(g.layers,old):self.assertEqual(l.paths[0].nodes,nodes)
        self.assertEqual(f.undo.depth,0)

    def test_async_merge_setting_entry_and_selection(self):
        f,g=joined_font();root,res=plugin_files();env=modules(f)
        with patch.dict(sys.modules,env),contextlib.redirect_stdout(io.StringIO()):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','merge_ui');p=m.ZonzCubicToQuadraticPlugin();p.settings();p.openSettings_(None)
                self.assertEqual(p._merge_check.state(),1)
                mid=p._midpoint_check.calls['initWithFrame_'][0];merge=p._merge_check.calls['initWithFrame_'][0]
                self.assertGreater(merge[1],mid[1])
                p._merge_check.setState_(1);p._count_field.setStringValue_('1');p._deviation_field.setStringValue_('0.05')
                [p.changeSetting_(getattr(p,a)) for _,a in m.SETTING_CONTROLS];p.convert_(None)
                while p._busy:p.advance_(p._timer)
        self.assertEqual(len(g.layers[0].paths[0].nodes),3)

    def test_cancelled_candidate_does_not_optimize(self):
        from concurrent.futures import CancelledError
        with patch('merge_fit.fit_merged_count',side_effect=AssertionError('should not fit')):
            with self.assertRaises(CancelledError):
                fit_run_corresponding([THREE],cancel=lambda:True)

    def test_composite_nearest_and_tangents_at_piece_boundaries(self):
        context=CompositeContext(THREE,count=65)
        for i,p in enumerate(THREE):
            for t in (0,.3,.7,1):
                z=cubic(p,t);got,where=context.nearest(z)
                self.assertLess(abs(got-z),1e-5)
                self.assertTrue(all(map(__import__('math').isfinite,(context.tangent(where).real,context.tangent(where).imag))))

    def test_actual_closed_wrap_pair_replaces_original_start_anchor(self):
        left,right=split(QUADRATIC,.4)
        chain=(right,line(right[3],left[0]),left)
        f,g=joined_font((chain,tuple(tuple(2*z for z in p) for p in chain)),True)
        old=[l.paths[0].nodes[0] for l in g.layers]
        convert(f,merge_curves=True,tolerance=.05,max_controls=1)
        for l,removed in zip(g.layers,old):
            self.assertNotIn(removed,l.paths[0].nodes)
            self.assertEqual(len(l.paths[0].nodes),4)
            self.assertTrue(validate_nodes(l.paths[0].nodes,True,*CONSTANTS))
        self.assertTrue(g.mastersCompatible)

    def test_real_background_merge_cancellation_does_not_remove_nodes(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor
        from concurrent.futures import CancelledError
        f,g=joined_font();old=list(g.layers[0].paths[0].nodes)
        root,res=plugin_files();env=modules(f);started=threading.Event();release=threading.Event()
        with patch.dict(sys.modules,env):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','merge_real_cancel');m.ThreadPoolExecutor=ThreadPoolExecutor
                original=m.fit_run_corresponding
                def slow(*args,**kwargs):
                    started.set();release.wait(5)
                    return original(*args,**kwargs)
                m.fit_run_corresponding=slow;p=m.ZonzCubicToQuadraticPlugin();p.settings()
                engine.save_settings(env['GlyphsApp'].Glyphs,merge_curves=True)
                try:
                    p.convert_(None);p.advance_(p._timer);p.advance_(p._timer)
                    self.assertTrue(started.wait(2));p.cancel_(None);release.set()
                    p._executor.submit(lambda:None).result(10)
                    self.assertEqual(g.layers[0].paths[0].nodes,old);self.assertEqual(f.events,[])
                finally:release.set();p._executor.shutdown(wait=True)

    def test_strict_small_tolerance_does_not_use_fixed_error_floor(self):
        r=fit_run_corresponding([THREE],tolerance=.001,max_controls=1)
        self.assertEqual([block['count'] for block in r],[3])
        self.assertLessEqual(r[0]['fits'][0]['error'][1],.001)

    def test_invalid_compound_coordinates_rejected(self):
        for chains in ([],[[]],[[tuple([0j]*3)]],[[tuple([0j,0j,complex(float('nan'),0),0j])]]):
            with self.assertRaises(ValueError):fit_run_corresponding(chains)

    def test_control_hull_acceptance_bound_is_conservative(self):
        import random,math
        from merge_fit import single_quadratic_bound
        rng=random.Random(1007);q=(0j,60+100j,200+20j)
        for _ in range(20):
            source=[list(p) for p in THREE]
            for p in source:
                for j in (1,2):p[j]+=complex(rng.uniform(-.1,.1),rng.uniform(-.1,.1))
            source=tuple(map(tuple,source));bound=single_quadratic_bound(source,q)
            self.assertTrue(math.isfinite(bound))
            for p in source:
                for i in range(81):
                    self.assertLessEqual(nearest_quadratic(cubic(p,i/80),q)[0],bound+1e-10)

    def test_control_hull_shortcut_rejects_nonmonotone_correspondence(self):
        from merge_fit import single_quadratic_bound
        chain=(line(0j,80+0j),line(80+0j,20+0j),line(20+0j,100+0j))
        self.assertEqual(single_quadratic_bound(chain,(0j,50+0j,100+0j)),float('inf'))

if __name__=='__main__':unittest.main(verbosity=2)



