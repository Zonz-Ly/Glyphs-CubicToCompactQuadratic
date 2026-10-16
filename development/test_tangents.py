# -*- coding: utf-8 -*-
import contextlib,io,math,sys,unittest
from unittest.mock import patch
from mock_glyphs import *
from test_merge import elevated,pieces,joined_font,line
from test_settings import finish
from test_entrypoints import modules,plugin_files,load
from preferences import DEFAULT_SETTINGS,load_settings,save_settings,PREFERENCE_PREFIX
from glyphs_adapter import conversion_steps,prepare_tasks,curve_runs,line_tangents
from fast_fit import fit_corresponding
from merge_fit import fit_run_corresponding
from geometry_fit import geometric_bounds
from tangent_constraints import aligned,smooth_join,cross2,on_ray,project_controls,TangentConflict
from options_fit import grid_point
from quad_fit import quadratic
from i18n import tr

def straight_font(p=(0j,20+.1j,80+80j,100+100j),reverse=False,masters=1):
    previous=-100+0j;following=200+200j
    if reverse:p=tuple(reversed(p));previous,following=following,previous
    paths=[]
    for i in range(masters):
        path=Path();path.nodes=[node(previous,'line'),node(p[0],'line'),node(p[1],'offcurve'),node(p[2],'offcurve'),node(p[3],'curve'),node(following,'line')]
        path.nodes[1].smooth=True;path.nodes[4].smooth=True;paths.append(Layer([path],'m'+str(i)))
    g=Glyph('A',paths);f=Font([g],masters);f.selectedLayers=[g.layers[0]];return f,g

def bend(degrees):
    direction=complex(math.cos(math.radians(degrees)),math.sin(math.radians(degrees)))
    return ((0j,30j,90+0j,100+0j),(100+0j,100+10*direction,170+20j,200+0j))

def converted_controls(layer):return [complex(n.position.x,n.position.y) for n in layer.paths[0].nodes if n.type=='offcurve']

class TangentRevisionTests(unittest.TestCase):
    def test_defaults_names_and_no_percent(self):
        self.assertEqual(DEFAULT_SETTINGS['deviation'],1)
        self.assertEqual(DEFAULT_SETTINGS['angle_limit'],5)
        self.assertTrue(DEFAULT_SETTINGS['keep_line_tangent'])
        self.assertEqual(tr('merge_curves',language='zh-Hans'),'尝试合并平滑连接的曲线')
        self.assertEqual(tr('keep_line_tangent',language='zh-Hans'),'维持平滑的直线连接处')
        self.assertNotIn('%',tr('deviation',language='zh-Hans'))

    def test_angle_validation_atomic_and_persisted(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs;load_settings(app)
        for value in (-1,181,float('nan'),float('inf'),'bad'):
            before=dict(app.defaults)
            with self.assertRaises(ValueError):save_settings(app,angle_limit=value)
            self.assertEqual(app.defaults,before)
        for value in (0,2.5,180):
            settings=save_settings(app,angle_limit=value,keep_line_tangent=True)
            self.assertEqual(load_settings(app),settings)

    def test_ordinary_half_merge_full_center_half_at_upm2000(self):
        f,g=joined_font(((EXACT,),));f.upm=2000;calls=[]
        def runner(curves,tolerance,max_controls,progress,**options):
            calls.append((tolerance,options))
            if False:yield
            return fit_corresponding(curves,tolerance,max_controls,**options)
        finish(conversion_steps(f,Node,Point,CONSTANTS,tolerance=.8,center_limit=3,fit_runner=runner))
        self.assertEqual(calls[0][0],.8);self.assertEqual(calls[0][1]['center_tolerance'],.8)
        self.assertEqual(calls[0][1]['comparison_tolerance'],1.6)
        self.assertEqual(calls[0][1]['center_limit'],6)
        chain=pieces(elevated((0j,20+5j,100+0j)));f,g=joined_font((chain,));f.upm=2000;calls=[]
        def merged(chains,tolerance,max_controls,progress,**options):
            options.pop('merge');cyclic=options.pop('cyclic');calls.append((tolerance,dict(options)))
            if False:yield
            return fit_run_corresponding(chains,tolerance,max_controls,cyclic,**options)
        finish(conversion_steps(f,Node,Point,CONSTANTS,tolerance=.8,merge_curves=True,fit_runner=merged))
        self.assertEqual(calls[0][0],1.6);self.assertEqual(calls[0][1]['single_tolerance'],.8)

    def test_center_uses_full_threshold_after_half_count_decision(self):
        p=elevated((0j,20+5j,100+0j))
        r=fit_corresponding([p],.4,2,center_limit=6,center_tolerance=.8)[0]
        self.assertEqual(len(r['parts']),1)
        bound=geometric_bounds(p,r['parts'],.8)
        self.assertLessEqual(bound[1],.8);self.assertGreater(bound[0],.4)

    def test_coprime_slanted_integer_chord_now_centers(self):
        q=(0j,15+8j,101+37j);p=elevated(q)
        r=fit_corresponding([p],.4,1,center_limit=5,center_tolerance=.8,integer_step=1)[0]
        control=r['parts'][0][1];direction=q[2]/abs(q[2]);middle=q[2]/2
        project=lambda z:abs(((z-middle)*direction.conjugate()).real)
        self.assertLess(project(control),project(q[1])*.5)
        self.assertEqual(control,grid_point(control,1))
        self.assertLessEqual(abs(cross2(control-q[1],direction)),1/math.sqrt(2)+1e-8)
        self.assertLessEqual(geometric_bounds(p,r['parts'],.8)[1],.8)

    def test_integer_center_has_no_unchecked_rounding(self):
        q=(0j,15+8j,101+37j);p=elevated(q)
        result=fit_corresponding([p],.1,1,center_limit=5,center_tolerance=.1,integer_step=1)[0]
        self.assertLessEqual(geometric_bounds(p,result['parts'],.1)[1],.1)
        self.assertEqual(result['parts'][0][1],grid_point(result['parts'][0][1],1))

    def test_angle_uses_oriented_travel_not_outward_handle_angle(self):
        self.assertTrue(aligned(1+0j,1+0j,0))
        self.assertFalse(aligned(1+0j,-1+0j,2))
        self.assertFalse(aligned(0j,1+0j,180))
        self.assertTrue(smooth_join(*bend(1.99),2));self.assertFalse(smooth_join(*bend(2.01),2))

    def test_corner_rejected_before_any_merge_optimization(self):
        for degrees in (2.01,90,179):
            with patch('merge_fit.try_merged_corresponding',side_effect=AssertionError('corner must not be fitted')):
                result=fit_run_corresponding([bend(degrees)],1000,1,angle_limit=2)
            self.assertEqual([b['count'] for b in result],[1,1])

    def test_small_angle_can_merge_and_custom_tolerance_controls_gate(self):
        for degrees,limit,expected in [(1.99,2,[2]),(2.01,2,[1,1]),(3,4,[2])]:
            result=fit_run_corresponding([bend(degrees)],1000,1,angle_limit=limit)
            self.assertEqual([b['count'] for b in result],expected)

    def test_any_master_corner_keeps_join_everywhere(self):
        f,g=joined_font((bend(1),bend(3)));joins=[l.paths[0].nodes[3] for l in g.layers]
        report=finish(conversion_steps(f,Node,Point,CONSTANTS,tolerance=1000,merge_curves=True))
        for layer,join in zip(g.layers,joins):self.assertIn(join,layer.paths[0].nodes)
        self.assertTrue(g.mastersCompatible)

    def test_native_grouping_splits_corner_before_background(self):
        f,g=joined_font((bend(90),));tasks,*_=prepare_tasks(f,CONSTANTS)
        groups=curve_runs(tasks,2)
        self.assertEqual([len(group[2]) for group in groups],[1,1])

    def test_degenerate_join_handle_is_kept(self):
        chain=list(bend(0));chain[1]=tuple([chain[1][0],chain[1][0],chain[1][2],chain[1][3]])
        result=fit_run_corresponding([chain],1000,1,angle_limit=180)
        self.assertEqual([b['count'] for b in result],[1,1])

    def test_line_gate_is_half_angle_tolerance(self):
        f,g=straight_font();layer=g.layers[0]
        self.assertIsNotNone(line_tangents(layer,0,[1],CONSTANTS,2)[0])
        self.assertIsNone(line_tangents(layer,0,[1],CONSTANTS,.4)[0])
        self.assertIsNotNone(line_tangents(layer,0,[1],CONSTANTS,2)[1])

    def test_line_uses_exactly_half_connection_angle(self):
        for degrees,expected in ((.999,True),(1.001,False)):
            control=20+20*math.tan(math.radians(degrees))*1j
            f,g=straight_font((0j,control,80+80j,100+100j))
            ray=line_tangents(g.layers[0],0,[1],CONSTANTS,2)[0]
            self.assertEqual(ray is not None,expected)

    def test_line_tangent_both_directions_float_and_integer(self):
        for reverse in (False,True):
            for integer in (False,True):
                f,g=straight_font(reverse=reverse);layer=g.layers[0];original=list(layer.paths[0].nodes)
                rays=line_tangents(layer,0,[1],CONSTANTS,2)
                finish(conversion_steps(f,Node,Point,CONSTANTS,keep_line_tangent=True,integer_coords=integer))
                controls=converted_controls(layer)
                self.assertTrue(on_ray(controls[0],rays[0]));self.assertTrue(on_ray(controls[-1],rays[1]))
                if integer:self.assertTrue(all(z==grid_point(z,1) for z in controls))
                self.assertIs(layer.paths[0].nodes[0],original[0]);self.assertIs(layer.paths[0].nodes[-1],original[-1])
                self.assertEqual(complex(original[1].position.x,original[1].position.y),rays[0][0])

    def test_line_tangent_survives_master_sync_and_explicit_midpoints(self):
        f,g=straight_font(masters=2)
        finish(conversion_steps(f,Node,Point,CONSTANTS,keep_line_tangent=True,integer_coords=True,add_midpoint=True))
        self.assertTrue(g.mastersCompatible)
        for layer in g.layers:
            controls=converted_controls(layer)
            self.assertAlmostEqual(controls[0].imag,0);self.assertAlmostEqual(controls[-1].real-controls[-1].imag,0)
            self.assertTrue(all(n.position.x.is_integer() and n.position.y.is_integer() for n in layer.paths[0].nodes))

    def test_line_tangent_works_at_closed_path_wrap(self):
        f,g=straight_font();path=g.layers[0].paths[0];path.closed=True;path.nodes=path.nodes[2:]+path.nodes[:2]
        finish(conversion_steps(f,Node,Point,CONSTANTS,keep_line_tangent=True))
        controls=converted_controls(g.layers[0]);self.assertTrue(any(abs(z.imag)<1e-7 for z in controls));self.assertTrue(any(abs(z.real-z.imag)<1e-7 for z in controls))

    def test_one_control_intersection_allows_quantized_tangent(self):
        rays=((0j,1+0j),(100+100j,-80-100j))
        self.assertEqual(project_controls([19+2j],rays),[20+0j])
        self.assertEqual(project_controls([19+2j],rays,1),[20+0j])
        conflict=((0j,1+0j),(100+100j,-79.7-100j))
        control=project_controls([20+0j],conflict,1)[0]
        self.assertEqual(control,20+0j)
        self.assertTrue(all(on_ray(control,ray,1) for ray in conflict))
        self.assertFalse(on_ray(control,conflict[1]))

    def test_impossible_cap_does_not_modify_font(self):
        f,g=straight_font();old=list(g.layers[0].paths[0].nodes)
        with self.assertRaises(TangentConflict):finish(conversion_steps(f,Node,Point,CONSTANTS,keep_line_tangent=True,max_controls=1))
        self.assertEqual(g.layers[0].paths[0].nodes,old);self.assertEqual(f.events,[])

    def test_constraint_write_failure_restores_all_masters(self):
        f,g=straight_font(masters=2);old=[list(l.paths[0].nodes) for l in g.layers];g.layers[1].paths[0].fail_once=True
        with self.assertRaises(RuntimeError):finish(conversion_steps(f,Node,Point,CONSTANTS,keep_line_tangent=True))
        for layer,nodes in zip(g.layers,old):self.assertEqual(layer.paths[0].nodes,nodes)
        self.assertEqual(f.undo.depth,0)

    def test_merged_run_preserves_outer_line_rays_in_all_masters(self):
        q=(0j,50+0j,100+100j);source=pieces(elevated(q));layers=[]
        for index,scale in enumerate((1,2)):
            path=Path();nodes=[node(-100*scale+0j,'line'),node(0j,'line')]
            for cubic in source:
                nodes.extend([node(cubic[1]*scale,'offcurve'),node(cubic[2]*scale,'offcurve'),node(cubic[3]*scale,'curve')])
            nodes.append(node((200+300j)*scale,'line'));path.nodes=nodes;layers.append(Layer([path],'m'+str(index)))
        g=Glyph('A',layers);f=Font([g],2);f.selectedLayers=[layers[0]];joins=[layer.paths[0].nodes[4] for layer in layers]
        finish(conversion_steps(f,Node,Point,CONSTANTS,merge_curves=True,keep_line_tangent=True,integer_coords=True,center_limit=100))
        self.assertTrue(g.mastersCompatible)
        for layer,scale,join in zip(layers,(1,2),joins):
            self.assertNotIn(join,layer.paths[0].nodes)
            self.assertEqual(converted_controls(layer),[50*scale+0j])

    def test_large_control_must_still_be_on_exact_line(self):
        self.assertFalse(on_ray(300000000+1j,(0j,1+0j)))
        self.assertTrue(on_ray(300000000+0j,(0j,1+0j)))

    def test_new_constraints_run_in_real_worker_and_cancel_without_writes(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor
        f,g=straight_font();old=list(g.layers[0].paths[0].nodes);env=modules(f);root,res=plugin_files()
        started=threading.Event();release=threading.Event()
        with patch.dict(sys.modules,env):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','tangent_worker');m.ThreadPoolExecutor=ThreadPoolExecutor
                original=m.fit_corresponding
                def slow(*args,**kwargs):started.set();release.wait(5);return original(*args,**kwargs)
                m.fit_corresponding=slow;p=m.ZonzCubicToQuadraticPlugin();p.settings()
                engine.save_settings(env['GlyphsApp'].Glyphs,keep_line_tangent=True,integer_coords=True,center_limit=100)
                try:
                    p.convert_(None);p.advance_(p._timer);p.advance_(p._timer)
                    self.assertTrue(started.wait(2));p.cancel_(None);release.set()
                    p._executor.submit(lambda:None).result(10)
                    self.assertEqual(g.layers[0].paths[0].nodes,old);self.assertEqual(f.events,[])
                finally:release.set();p._executor.shutdown(wait=True)

    def test_panel_order_new_values_and_localized_names(self):
        f,g=straight_font();env=modules(f);root,res=plugin_files()
        with patch.dict(sys.modules,env),contextlib.redirect_stdout(io.StringIO()):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','tangent_ui');p=m.ZonzCubicToQuadraticPlugin();p.settings();p.openSettings_(None)
                fields=[p._deviation_field,p._count_field,p._center_field,p._angle_field,p._tangent_check,p._curve_tangent_check,p._merge_check,p._midpoint_check,p._integer_check]
                frames=[field.calls['initWithFrame_'][0] for field in fields]
                self.assertEqual([r[1] for r in frames],sorted([r[1] for r in frames],reverse=True))
                self.assertEqual(len({r[0]+r[2] for r in frames}),1)
                width=p._settings_panel.calls['initWithContentRect_styleMask_backing_defer_'][0][2]
                self.assertTrue(all(r[0]+r[2]==width-22 for r in frames))
                labels=[child for child in p._settings_panel.children if 'setStringValue_' in child.calls and child not in fields]
                self.assertTrue(labels)
                self.assertTrue(all(child.calls['initWithFrame_'][0][0]==22 for child in labels))
                self.assertEqual(p._deviation_field.stringValue(),'1');self.assertEqual(p._angle_field.stringValue(),'5');self.assertEqual(p._tangent_check.state(),1)
                p._angle_field.setStringValue_('3,5');p._tangent_check.setState_(1);[p.changeSetting_(getattr(p,a)) for _,a in m.SETTING_CONTROLS]
                values=engine.load_settings(env['GlyphsApp'].Glyphs);self.assertEqual(values['angle_limit'],3.5);self.assertTrue(values['keep_line_tangent'])

    def test_integer_tangent_uses_intersected_square_not_distance_band(self):
        self.assertTrue(on_ray(1+0j,(0j,1+1j),1))
        self.assertFalse(on_ray(1+.01j,(0j,1-1j),1))
        self.assertTrue(on_ray(5+521j,(5+462j,1+462j),1))
        self.assertFalse(on_ray(5+461j,(5+462j,1+462j),1))
        self.assertFalse(on_ray(300000000+1j,(0j,1+0j),1))

    def test_fractional_ray_origin_can_use_intersected_integer_cells(self):
        ray=(.2+.2j,1+462j)
        control=project_controls([.3+59j],(ray,None),1)[0]
        self.assertEqual(control,59j)
        self.assertTrue(on_ray(control,ray,1))
        self.assertLess(abs(control-(.3+59j)),1)

    def test_parallel_integer_rays_can_share_a_grid_cell(self):
        rays=((0j,1+0j),(10+.4j,-1+0j))
        with self.assertRaises(TangentConflict):project_controls([5+0j],rays)
        self.assertEqual(project_controls([5+0j],rays,1),[5+0j])
        disjoint=((0j,1+0j),(10+1.1j,-1+0j))
        with self.assertRaises(TangentConflict):project_controls([5+0j],disjoint,1)

    def test_complete_reported_path_with_integer_tangent_no_long_control(self):
        source=(5+462j,5+509j,3+538j,564j)
        f,g=straight_font(source)
        path=g.layers[0].paths[0];path.nodes=path.nodes[:-1];path.nodes[0].position=Point(4,0)
        finish(conversion_steps(f,Node,Point,CONSTANTS,tolerance=1,max_controls=3,
            center_limit=5,angle_limit=5,keep_line_tangent=True,merge_curves=True,integer_coords=True))
        control=converted_controls(g.layers[0])[0]
        self.assertLess(abs(control-source[0]),110)
        self.assertEqual(control,grid_point(control,1))
        self.assertTrue(on_ray(control,(source[0],1+462j),1))
        q=(source[0],control,source[-1])
        self.assertLessEqual(geometric_bounds(source,[q],.5)[1],.5)
        self.assertTrue(all(462<=quadratic(q,k/100).imag<=564 for k in range(101)))

    def test_grid_tangent_fit_survives_reflection_rotation_and_reversal(self):
        source=(5+462j,5+509j,3+538j,564j)
        for factor in (1,-1,1j,-1j):
            for reverse in (False,True):
                p=tuple(z*factor for z in source)
                ray=(p[0],(1+462j)*factor)
                if reverse:p=tuple(reversed(p))
                tangents=(None,ray) if reverse else (ray,None)
                r=fit_corresponding([p],.5,3,integer_step=1,center_limit=5,
                    center_tolerance=.5,comparison_tolerance=1,tangents=[tangents])[0]
                controls=[q[1] for q in r['parts']]
                self.assertTrue(on_ray(controls[-1] if reverse else controls[0],ray,1))
                self.assertTrue(all(z==grid_point(z,1) for z in controls))
                self.assertLessEqual(geometric_bounds(p,r['parts'],.5)[1],.5)

if __name__=='__main__':unittest.main(verbosity=2)
