# -*- coding: utf-8 -*-
import contextlib,io,math,random,sys,unittest
from concurrent.futures import CancelledError
from unittest.mock import patch
from mock_glyphs import *
from preferences import DEFAULT_SETTINGS,PREFERENCE_PREFIX,load_settings,save_settings
from fast_fit import fit,fit_corresponding
from merge_fit import fit_run_corresponding,CompositeContext
from options_fit import grid_point,adjust_parts
from geometry_fit import geometric_bounds,nearest_quadratic
from search_core import Context,sample_norms,score_norms,numeric_cache
from glyphs_adapter import conversion_steps,make_job,ConversionError
from test_merge import elevated,pieces,joined_font,THREE
from test_settings import finish
from test_entrypoints import modules,load,plugin_files

def coordinates(layer):
    return [complex(n.position.x,n.position.y) for n in layer.paths[0].nodes]

class UnitAndLatticeTests(unittest.TestCase):
    def test_new_defaults_and_invalid_center_are_atomic(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        self.assertEqual(load_settings(app)['deviation'],1)
        self.assertEqual(DEFAULT_SETTINGS['center_limit'],7)
        self.assertTrue(DEFAULT_SETTINGS['integer_coords'])
        for x in (-1,float('nan'),float('inf'),'bad'):
            before=dict(app.defaults)
            with self.assertRaises(ValueError):save_settings(app,center_limit=x)
            self.assertEqual(app.defaults,before)

    def test_saved_deviation_is_not_rescaled_or_marked(self):
        for value,want in [(0.05000000074505806,.05),('0.25',.25),('25',25)]:
            app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
            app.defaults[PREFERENCE_PREFIX+'deviation']=value
            self.assertEqual(load_settings(app)['deviation'],want)
            self.assertEqual(load_settings(app)['deviation'],want)
            self.assertNotIn(PREFERENCE_PREFIX+'deviation_unit',app.defaults)

    def test_new_percent_and_center_values_round_trip(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        saved=save_settings(app,deviation=.05,center_limit=.05,integer_coords=True)
        self.assertEqual(load_settings(app),saved)
        self.assertEqual(repr(load_settings(app)['deviation']),'0.05')
        self.assertEqual(repr(load_settings(app)['center_limit']),'0.05')

    def test_upm_invariance_default_fit_and_merge(self):
        for merged in (False,True):
            outputs=[]
            for upm in (1000,2000,2048):
                scale=upm/1000
                chains=[tuple(tuple(z*scale for z in p) for p in THREE)]
                f,g=joined_font(chains);f.upm=upm
                finish(conversion_steps(f,Node,Point,CONSTANTS,merge_curves=merged))
                outputs.append([z/scale for z in coordinates(g.layers[0])])
            for out in outputs[1:]:
                self.assertEqual(len(out),len(outputs[0]))
                for a,b in zip(out,outputs[0]):self.assertLess(abs(a-b),1e-7)

    def test_public_job_keeps_unit_value(self):
        f=Font([glyph()]);f.selectedLayers=[f.glyphs['A'].layers[0]]
        with patch.dict(sys.modules,modules(f)),patch('glyphs_adapter.conversion_steps',return_value='job') as wrapped:
            self.assertEqual(make_job(tolerance=.8,center_limit=2,integer_coords=True),'job')
            self.assertEqual(wrapped.call_args[0][4],.8)
            self.assertEqual(wrapped.call_args[0][-5:],(2,True,5.0,True,True))

    def test_invalid_upm_does_not_touch_font(self):
        for upm in (0,-1000,float('nan'),float('inf')):
            f,g=joined_font();f.upm=upm
            with self.assertRaises(ConversionError):finish(conversion_steps(f,Node,Point,CONSTANTS))
            self.assertEqual(f.events,[])

    def test_upm_change_before_commit_cancels(self):
        f,g=joined_font();f.upm=1000;old=list(g.layers[0].paths[0].nodes)
        job=conversion_steps(f,Node,Point,CONSTANTS);next(job);next(job);f.upm=2000
        with self.assertRaises(ConversionError):finish(job)
        self.assertEqual(g.layers[0].paths[0].nodes,old);self.assertEqual(f.events,[])

    def test_zero_center_and_float_mode_skip_optional_search(self):
        with patch('options_fit.geometric_bounds',side_effect=AssertionError()),patch('options_fit.sample_norms',side_effect=AssertionError()):
            a=fit_corresponding([EXACT],.5,1)
        self.assertEqual(a[0]['parts'][0][1],60+120j)

    def test_center_reaches_middle_preserving_perpendicular_height(self):
        p=elevated((0j,20+5j,100+0j))
        q=fit_corresponding([p],10,1,center_limit=5)[0]['parts'][0]
        self.assertEqual(q[1],50+5j)
        self.assertLessEqual(geometric_bounds(p,[q],10)[1],10)

    def test_center_stops_at_error_threshold(self):
        p=elevated((0j,20+5j,100+0j))
        q=fit_corresponding([p],.5,1,center_limit=6)[0]['parts'][0]
        self.assertGreater(q[1].real,20);self.assertLess(q[1].real,50)
        self.assertEqual(q[1].imag,5)
        self.assertLessEqual(geometric_bounds(p,[q],.5)[1],.5)
        farther=(q[0],q[1]+1,q[2])
        self.assertGreater(geometric_bounds(p,[farther],.5)[0],.5)

    def test_center_above_height_limit_or_already_over_error_is_unchanged(self):
        p=elevated((0j,20+5j,100+0j))
        a=fit_corresponding([p],1,1,center_limit=4)[0]['parts']
        self.assertLess(abs(a[0][1]-(20+5j)),1e-10)
        base=fit_corresponding([HARD],.001,1)[0]['parts']
        moved=fit_corresponding([HARD],.001,1,center_limit=1000)[0]['parts']
        self.assertEqual(base,moved)

    def test_center_rotation_and_translation(self):
        rotation=(3+4j)/5;origin=200-30j
        q=tuple(origin+rotation*z for z in (0j,20+5j,100+0j));p=elevated(q)
        r=fit_corresponding([p],10,1,center_limit=5.000001)[0]['parts'][0]
        self.assertLess(abs(r[1]-(origin+rotation*(50+5j))),1e-8)

    def test_center_multiple_control_result_is_unchanged(self):
        a=fit_corresponding([HARD],.5,2)[0]['parts']
        b=fit_corresponding([HARD],.5,2,center_limit=200)[0]['parts']
        self.assertEqual(a,b)

    def test_center_works_on_merged_single_result(self):
        chain=pieces(elevated((0j,20+5j,100+0j)))
        r=fit_run_corresponding([chain],10,1,center_limit=6)
        self.assertEqual(len(r),1);self.assertEqual(r[0]['count'],3)
        self.assertLess(abs(r[0]['fits'][0]['parts'][0][1]-(50+5j)),1e-5)

    def test_center_integer_preserves_height_and_integer_grid(self):
        p=elevated((0j,20+5j,100+0j))
        q=fit_corresponding([p],.5,1,center_limit=6,integer_step=1)[0]['parts'][0]
        self.assertEqual(q[1],complex(round(q[1].real),5))
        self.assertGreater(q[1].real,20);self.assertLess(q[1].real,50)
        self.assertLessEqual(geometric_bounds(p,[q],.5)[1],.5)

    def test_integer_fit_improves_on_naive_rounding(self):
        a=fit(HARD,policy='single',check_error=False)['parts']
        naive=[(a[0][0],grid_point(a[0][1],1),a[0][2])]
        integer=fit(HARD,policy='single',check_error=False,integer_step=1)['parts']
        scale=max([abs(z) for z in HARD]+[abs(z) for q in a for z in q]);context=Context(tuple(z/scale for z in HARD))
        score=lambda parts:score_norms(sample_norms([tuple(z/scale for z in q) for q in parts],context))
        self.assertNotEqual(integer,naive);self.assertLess(score(integer),score(naive))
        self.assertEqual(integer[0][1],18+109j)

    def test_integer_candidates_are_checked_before_count_acceptance(self):
        p=elevated((0j,20.49+15.49j,100+0j))
        floating=fit_corresponding([p],.001,2)
        with patch('fast_fit.fit',wraps=fit) as searched:
            integer=fit_corresponding([p],.001,3,integer_step=1)
        self.assertEqual(len(floating[0]['parts']),1)
        self.assertEqual({call.kwargs['control_count'] for call in searched.call_args_list},{1,2,3})
        self.assertFalse(integer[0]['within'])

    def test_integer_merge_must_pass_strict_error_at_cap(self):
        chain=pieces(elevated((0j,20.49+15.49j,100+0j)))
        r=fit_run_corresponding([chain],.001,1,integer_step=1)
        self.assertTrue(all(b['count']==1 for b in r))

    def test_integer_explicit_midpoints_match_written_curve(self):
        f,g=joined_font(((PAIR_NEEDED,),));old_start=g.layers[0].paths[0].nodes[0]
        finish(conversion_steps(f,Node,Point,CONSTANTS,integer_coords=True,add_midpoint=True))
        nodes=g.layers[0].paths[0].nodes
        self.assertIs(nodes[0],old_start)
        self.assertTrue(all(z.real.is_integer() and z.imag.is_integer() for z in coordinates(g.layers[0])))
        expected=fit_corresponding([PAIR_NEEDED],.5,2,integer_step=1,explicit_midpoint=True)[0]['parts']
        self.assertEqual(coordinates(g.layers[0]),[expected[0][0],expected[0][1],expected[0][2],expected[1][1],expected[1][2]])

    def test_integer_grid_is_in_original_font_units(self):
        for upm in (1000,2000,2048):
            scale=upm/1000
            p=tuple(z*scale for z in HARD);f,g=joined_font(((p,),));f.upm=upm
            finish(conversion_steps(f,Node,Point,CONSTANTS,integer_coords=True,add_midpoint=True))
            nodes=g.layers[0].paths[0].nodes
            for n in nodes[1:-1]:
                self.assertTrue(n.position.x.is_integer());self.assertTrue(n.position.y.is_integer())
            self.assertEqual(coordinates(g.layers[0])[0],p[0]);self.assertEqual(coordinates(g.layers[0])[-1],p[-1])

    def test_fractional_original_endpoints_are_preserved(self):
        p=tuple(z+.2+.3j for z in HARD);f,g=joined_font(((p,),))
        finish(conversion_steps(f,Node,Point,CONSTANTS,integer_coords=True))
        self.assertEqual(coordinates(g.layers[0])[0],p[0]);self.assertEqual(coordinates(g.layers[0])[-1],p[-1])
        self.assertTrue(all(n.position.x.is_integer() and n.position.y.is_integer() for n in g.layers[0].paths[0].nodes[1:-1]))

    def test_integer_master_count_and_rollback(self):
        f,g=joined_font(((EXACT,),(HARD,)));old=[list(l.paths[0].nodes) for l in g.layers]
        g.layers[1].paths[0].fail_once=True
        with self.assertRaises(RuntimeError):finish(conversion_steps(f,Node,Point,CONSTANTS,integer_coords=True))
        for l,nodes in zip(g.layers,old):self.assertEqual(l.paths[0].nodes,nodes)
        self.assertTrue(g.mastersCompatible)

    def test_options_cancel_before_search(self):
        with self.assertRaises(CancelledError):fit_corresponding([HARD],.5,2,cancel=lambda:True,integer_step=1)
        with self.assertRaises(CancelledError):fit_run_corresponding([THREE],.5,2,cancel=lambda:True,center_limit=3)

    def test_acceptable_curve_still_refines_complete_error_interval(self):
        import inspect
        p=elevated((0j,20+5j,100+0j));q=[(0j,30+5j,100+0j)]
        error=geometric_bounds(p,q,1,accuracy=.0001)
        self.assertLess(error[1],1);self.assertLess(error[1]-error[0],.0001)
        self.assertNotIn('accept_below',inspect.signature(geometric_bounds).parameters)

    def test_composite_box_pruning_matches_all_original_projections(self):
        context=CompositeContext(THREE);rng=random.Random(1015)
        for _ in range(160):
            z=complex(rng.uniform(-50,250),rng.uniform(-50,150))
            all_points=[(abs(point-z),i,point,t) for i,c in enumerate(context.contexts) for point,t in [c.nearest(z)]]
            best=min(all_points,key=lambda r:r[:2])
            self.assertEqual(context.nearest(z),(best[2],(best[1],best[3])))
        with patch.object(context.contexts[-1],'nearest',wraps=context.contexts[-1].nearest) as far:
            context.nearest(0j);self.assertEqual(far.call_count,0)

    def test_combined_upm_center_integer_merge_all_masters(self):
        p=elevated((0j,20+5j,100+0j));chain=pieces(p)
        scale=2.048;scaled=tuple(tuple(z*scale for z in p) for p in chain)
        f,g=joined_font((scaled,scaled));f.upm=2048
        finish(conversion_steps(f,Node,Point,CONSTANTS,tolerance=.5,merge_curves=True,integer_coords=True,center_limit=6))
        self.assertTrue(g.mastersCompatible)
        for layer in g.layers:
            z=coordinates(layer);self.assertEqual(len(z),3)
            self.assertEqual(z[1].real,round(z[1].real));self.assertEqual(z[1].imag,round(z[1].imag))
            source=tuple(tuple(v/scale for v in p) for p in scaled)
            bounds=geometric_bounds(source[0],[tuple(v/scale for v in z)],.5,source_curves=source)
            self.assertLessEqual(bounds[1],.5)

    def test_exact_merged_quadratic_skips_iterative_search(self):
        numeric_cache().clear()
        with patch('merge_fit.refine_lm',side_effect=AssertionError('iterative search')),patch('merge_fit.nelder_mead',side_effect=AssertionError('iterative search')):
            result=fit_run_corresponding([THREE],.001,1)
        self.assertEqual(result[0]['count'],3)
        self.assertLess(result[0]['fits'][0]['error'][1],.001)

    def test_integer_center_with_fractional_endpoint_chord(self):
        q=(0j,10+10j,100.5+50.25j);p=elevated(q)
        result=fit_corresponding([p],10,1,center_limit=20,integer_step=1)[0]['parts'][0]
        shift=result[1]-q[1]
        self.assertGreater(abs(shift),0);self.assertAlmostEqual(shift.real,2*shift.imag)
        self.assertEqual(result[1].real,round(result[1].real));self.assertEqual(result[1].imag,round(result[1].imag))

    def test_combined_options_in_real_background_worker(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor
        chain=pieces(elevated((0j,20+5j,100+0j)));f,g=joined_font((chain,))
        env=modules(f);root,res=plugin_files();threads=[];current=threading.get_ident()
        with patch.dict(sys.modules,env):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                module=load(res/'plugin.py','integer_real_worker');module.ThreadPoolExecutor=ThreadPoolExecutor
                original=module.fit_run_corresponding
                def observed(*args,**kwargs):
                    threads.append(threading.get_ident());return original(*args,**kwargs)
                module.fit_run_corresponding=observed;p=module.ZonzCubicToQuadraticPlugin();p.settings()
                try:
                    runner=p.fit_async([chain],.5,1,{},merge=True,center_limit=6,integer_step=1)
                    result=finish(runner)
                    self.assertEqual(result[0]['count'],3);self.assertEqual(len(threads),1);self.assertNotEqual(threads[0],current)
                    control=result[0]['fits'][0]['parts'][0][1]
                    self.assertEqual(control.real,round(control.real));self.assertEqual(control.imag,5)
                    self.assertEqual(f.events,[])
                finally:p._executor.shutdown(wait=True)

    def test_options_panel_order_alignment_save_and_background(self):
        f,g=joined_font();env=modules(f);app=env['GlyphsApp'].Glyphs
        root,res=plugin_files()
        with patch.dict(sys.modules,env),contextlib.redirect_stdout(io.StringIO()):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                module=load(res/'plugin.py','units_plugin');p=module.ZonzCubicToQuadraticPlugin();p.settings();p.openSettings_(None)
                fields=[p._deviation_field,p._count_field,p._center_field,p._angle_field,p._tangent_check,p._merge_check,p._midpoint_check,p._integer_check]
                frames=[x.calls['initWithFrame_'][0] for x in fields]
                self.assertEqual(len({r[0]+r[2] for r in frames}),1)
                self.assertEqual([r[1] for r in frames],sorted([r[1] for r in frames],reverse=True))
                self.assertEqual(p._deviation_field.stringValue(),'1');self.assertEqual(p._center_field.stringValue(),'7')
                p._deviation_field.setStringValue_('5');p._center_field.setStringValue_('2,5');p._integer_check.setState_(1);[p.changeSetting_(getattr(p,a)) for _,a in module.SETTING_CONTROLS]
                values=engine.load_settings(app);self.assertEqual(values['deviation'],5);self.assertEqual(values['center_limit'],2.5);self.assertTrue(values['integer_coords'])
                with patch.object(module,'make_job',return_value=iter([])) as job:
                    p.convert_(None);self.assertEqual(job.call_args[1]['center_limit'],2.5);self.assertTrue(job.call_args[1]['integer_coords']);p.finish()
                runner=p.fit_async([EXACT],.5,1,{},center_limit=2,integer_step=1)
                result=finish(runner);self.assertEqual(len(result),1);self.assertEqual(result[0]['parts'][0][1],60+120j)

if __name__=='__main__':unittest.main(verbosity=2)
