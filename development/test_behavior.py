# -*- coding: utf-8 -*-
import contextlib,io,struct,sys,unittest
from types import SimpleNamespace
from unittest.mock import patch
from mock_glyphs import *
from preferences import DEFAULT_SETTINGS,PREFERENCE_PREFIX,save_settings,load_settings,validated_settings
from fast_fit import fit_corresponding,numeric_cache
from glyphs_adapter import conversion_steps
from test_entrypoints import modules,load,plugin_files
from test_settings import finish

class BehaviorTests(unittest.TestCase):
    def test_unbounded_positive_integers_saved_as_text(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        for count in (33,1024,10**25,10**100):
            values=save_settings(app,max_controls=count)
            self.assertEqual(values['max_controls'],count)
            self.assertEqual(app.defaults[PREFERENCE_PREFIX+'max_controls'],str(count))
            self.assertEqual(load_settings(app)['max_controls'],count)

    def test_extreme_limit_does_not_allocate_that_count(self):
        p=(68+656j,96+410j,256+283j,485+242j)
        with patch('fast_fit.optimize_chain',side_effect=AssertionError('unused large limit')):
            results=fit_corresponding([p],max_controls=10**100)
        self.assertEqual(len(results[0]['parts']),1)

    def test_cap_one_omits_continuous_error_checks(self):
        numeric_cache().clear()
        with patch('fast_fit.geometric_bounds',side_effect=AssertionError('unneeded final check')):
            results=fit_corresponding([HARD,EXACT],max_controls=1)
        self.assertEqual([len(r['parts']) for r in results],[1,1])
        self.assertTrue(all(r['error'] is None for r in results))

    def test_cap_two_compares_both_counts(self):
        import fast_fit
        numeric_cache().clear();calls=[];original=fast_fit.geometric_bounds
        def checked(p,parts,*args,**kw):
            calls.append(len(parts));return original(p,parts,*args,**kw)
        with patch('fast_fit.geometric_bounds',checked):fit_corresponding([HARD,EXACT],max_controls=2)
        self.assertEqual(set(calls),{1,2});self.assertLessEqual(max(calls),2)

    def test_failed_master_skips_remaining_error_checks(self):
        import fast_fit
        calls=[];original=fast_fit.fit
        def watched(p,*args,**kw):
            calls.append((kw.get('policy'),kw.get('check_error',True)))
            return original(p,*args,**kw)
        with patch('fast_fit.fit',watched):fit_corresponding([HARD,EXACT],max_controls=4)
        self.assertIn(('multiple',False),calls)
        # Rejecting a count defers all unused matching-master work.
        self.assertEqual(calls[:3],[('single',True),('pair',True),('multiple',True)])
        self.assertEqual(calls[3:],[('multiple',False),('multiple',False)])

    def test_success_before_cap_stops_immediately(self):
        calls=[]
        def fake(p,policy='probe',control_count=2,**kw):
            count=1 if policy in ('probe','single') else (2 if policy=='pair' else control_count)
            calls.append(count)
            return dict(parts=[(0j,0j,0j)]*count,within=count==3,error=(0,0))
        with patch('fast_fit.fit',fake):
            results=fit_corresponding([HARD,EXACT],max_controls=10**50)
        self.assertEqual([len(r['parts']) for r in results],[3,3])
        self.assertEqual(calls,[1,2,3,3])

    def test_geometry_reused_across_control_counts(self):
        import fast_fit
        numeric_cache().clear();seen=[];original=fast_fit.optimize_chain
        def watched(p,count,geometry=None):
            seen.append(geometry);return original(p,count,geometry)
        with patch('fast_fit.optimize_chain',watched):fit_corresponding([HARD],max_controls=4)
        self.assertEqual(len(seen),2);self.assertIsNotNone(seen[0])
        self.assertIs(seen[0][0],seen[1][0]);self.assertIs(seen[0][2],seen[1][2])

    def test_decimal_storage_survives_float32_preferences(self):
        class Float32Dict(dict):
            def __setitem__(self,key,value):
                if isinstance(value,float):value=struct.unpack('f',struct.pack('f',value))[0]
                super().__setitem__(key,value)
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        app.defaults=Float32Dict(app.defaults)
        for value in ('0.05','0.00000123','0.123456789123'):
            save_settings(app,deviation=value)
            self.assertEqual(float(app.defaults[PREFERENCE_PREFIX+'deviation']),float(value))
            self.assertEqual(repr(load_settings(app)['deviation']),repr(float(value)))
            if value=='0.05':self.assertEqual(app.defaults[PREFERENCE_PREFIX+'deviation'],'0.05')

    def test_old_binary32_decimal_is_recovered(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        app.defaults[PREFERENCE_PREFIX+'deviation']=0.05000000074505806
        self.assertEqual(repr(load_settings(app)['deviation']),'0.05')

    def test_no_selection_does_not_call_preflight_or_write(self):
        f=Font([glyph()],edit=False)
        with patch('glyphs_adapter.fit_corresponding',side_effect=AssertionError('no selected input')):
            report=finish(conversion_steps(f,Node,Point,CONSTANTS,preflight=lambda:(_ for _ in ()).throw(AssertionError('preflight'))))
        self.assertFalse(report);self.assertEqual(f.events,[])

    def test_selected_glyph_without_cubics_is_empty(self):
        g=glyph();g.layers[0].paths=[];f=Font([g],edit=False);f.selection=[g]
        report=finish(conversion_steps(f,Node,Point,CONSTANTS))
        self.assertFalse(report);self.assertEqual(f.events,[])

    def plugin(self,font,env=None,name='behavior_plugin'):
        root,res=plugin_files();env=env or modules(font)
        engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
        return root,res,env,engine

    def test_option_menu_alternate_and_shortcuts(self):
        f=Font([glyph()]);root,res,env,engine=self.plugin(f)
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','alternate_menu');p=m.ZonzCubicToQuadraticPlugin();p.settings();p.start()
        normal,alternate=env['GlyphsApp'].Glyphs.menu[7]
        self.assertEqual(normal.calls['initWithTitle_action_keyEquivalent_'][2],'2')
        self.assertEqual(normal.calls['setKeyEquivalentModifierMask_'],(9,))
        self.assertEqual(alternate.calls['initWithTitle_action_keyEquivalent_'][2],'2')
        self.assertEqual(alternate.calls['setKeyEquivalentModifierMask_'],(11,))
        self.assertEqual(alternate.calls['setAlternate_'],(True,))

    def test_short_job_never_opens_progress(self):
        g=glyph();f=Font([g]);f.selectedLayers=[g.layers[0]]
        root,res,env,engine=self.plugin(f)
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','short_progress');p=m.ZonzCubicToQuadraticPlugin();p.settings()
            with patch.object(m.time,'monotonic',return_value=0),patch.object(p,'open_progress') as opened:
                p.convert_(None)
                while p._busy:p.advance_(p._timer)
            self.assertEqual(opened.call_count,0)
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'qcurve')

    def test_progress_opens_only_after_one_second(self):
        gs=[glyph(x) for x in ('A','B','C')]
        f=Font(gs,edit=False);f.selection=gs
        root,res,env,engine=self.plugin(f);clock=[0.0]
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','delayed_progress');p=m.ZonzCubicToQuadraticPlugin();p.settings()
            with patch.object(m.time,'monotonic',side_effect=lambda:clock[0]):
                p.convert_(None);p.advance_(p._timer);self.assertIsNone(p._panel)
                clock[0]=.99;p.advance_(p._timer);self.assertIsNone(p._panel)
                clock[0]=1.0;p.advance_(p._timer);self.assertIsNotNone(p._panel)
                panel=p._panel;p.advance_(p._timer)
                self.assertFalse(p._busy);self.assertTrue(panel.closed)

    def test_delayed_cancel_keeps_all_glyphs(self):
        gs=[glyph(x) for x in ('A','B','C')];f=Font(gs,edit=False);f.selection=gs
        root,res,env,engine=self.plugin(f);clock=[0.0]
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','delayed_cancel');p=m.ZonzCubicToQuadraticPlugin();p.settings()
            with patch.object(m.time,'monotonic',side_effect=lambda:clock[0]):
                p.convert_(None);p.advance_(p._timer);clock[0]=1.1;p.advance_(p._timer)
                self.assertIsNotNone(p._panel);p.cancel_(None)
        self.assertTrue(all(g.layers[0].paths[0].nodes[-1].type=='curve' for g in gs))
        self.assertEqual(f.events,[])

    def test_plugin_empty_finishes_silently_without_progress_or_redraw(self):
        f=Font([glyph()],edit=False);root,res,env,engine=self.plugin(f);messages=[];redraws=[]
        env['GlyphsApp'].Message=lambda **kw:messages.append(kw)
        env['GlyphsApp'].Glyphs.redraw=lambda:redraws.append(True)
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','silent_empty');p=m.ZonzCubicToQuadraticPlugin();p.settings()
            with patch.object(p,'open_progress') as progress:
                p.convert_(None);p.advance_(p._timer)
            self.assertEqual(progress.call_count,0);self.assertFalse(p._busy)
        self.assertEqual(messages,[]);self.assertEqual(redraws,[])

    def test_plugin_success_finishes_silently_and_redraws_once(self):
        g=glyph();f=Font([g]);f.selectedLayers=[g.layers[0]]
        root,res,env,engine=self.plugin(f);messages=[];redraws=[]
        env['GlyphsApp'].Message=lambda **kw:messages.append(kw)
        env['GlyphsApp'].Glyphs.redraw=lambda:redraws.append(True)
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','silent_success');p=m.ZonzCubicToQuadraticPlugin();p.settings();p.convert_(None)
            while p._busy:p.advance_(p._timer)
        self.assertEqual(messages,[]);self.assertEqual(redraws,[True])
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'qcurve')

    def test_plugin_failure_still_shows_error_and_preserves_data(self):
        g=glyph();f=Font([g]);f.selectedLayers=[g.layers[0]]
        root,res,env,engine=self.plugin(f);messages=[];redraws=[]
        env['GlyphsApp'].Message=lambda **kw:messages.append(kw)
        env['GlyphsApp'].Glyphs.redraw=lambda:redraws.append(True)
        def failed_job(**kw):
            yield dict(done=0,total=1,glyph='A')
            raise RuntimeError('conversion failed')
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','silent_failure');p=m.ZonzCubicToQuadraticPlugin();p.settings()
            with patch.object(m,'make_job',failed_job),contextlib.redirect_stderr(io.StringIO()):
                p.convert_(None)
                while p._busy:p.advance_(p._timer)
        self.assertEqual(len(messages),1);self.assertIn('conversion failed',str(messages))
        self.assertEqual(redraws,[]);self.assertEqual(f.events,[])
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve')

    def test_long_single_job_shows_progress_without_native_worker_edits(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor
        g=glyph(sources=(HARD,));f=Font([g]);f.selectedLayers=[g.layers[0]]
        root,res,env,engine=self.plugin(f);started=threading.Event();release=threading.Event();clock=[0.0]
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','real_async_progress');m.ThreadPoolExecutor=ThreadPoolExecutor
            original=m.fit_corresponding;worker_ids=[]
            def slow(*args,**kwargs):
                worker_ids.append(threading.get_ident());started.set();release.wait(5)
                return original(*args,**kwargs)
            m.fit_corresponding=slow;p=m.ZonzCubicToQuadraticPlugin();p.settings()
            try:
                with patch.object(m.time,'monotonic',side_effect=lambda:clock[0]):
                    p.convert_(None);p.advance_(p._timer);p.advance_(p._timer)
                    self.assertTrue(started.wait(2));self.assertIsNone(p._panel)
                    self.assertEqual(f.events,[]);clock[0]=1.1;p.advance_(p._timer)
                    self.assertIsNotNone(p._panel);self.assertEqual(f.events,[])
                    self.assertNotEqual(worker_ids[0],threading.get_ident())
                    release.set();p._executor.submit(lambda:None).result(10)
                    while p._busy:p.advance_(p._timer)
                self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'qcurve')
            finally:release.set();p._executor.shutdown(wait=True)

    def test_cancel_is_checked_before_numerical_work(self):
        from concurrent.futures import CancelledError
        with patch('fast_fit.fit',side_effect=AssertionError('cancelled task must not fit')):
            with self.assertRaises(CancelledError):
                fit_corresponding([HARD],max_controls=10**100,cancel=lambda:True)

    def test_cancel_worker_does_not_edit_glyph_after_completion(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor
        from concurrent.futures import CancelledError
        g=glyph(sources=(HARD,));f=Font([g]);f.selectedLayers=[g.layers[0]]
        root,res,env,engine=self.plugin(f);started=threading.Event();release=threading.Event()
        with patch.dict(sys.modules,env),patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
            m=load(res/'plugin.py','real_async_cancel');m.ThreadPoolExecutor=ThreadPoolExecutor
            def slow(*args,**kwargs):
                started.set();release.wait(5)
                if kwargs['cancel']():raise CancelledError()
                return engine.fit_corresponding(*args,**kwargs)
            m.fit_corresponding=slow;p=m.ZonzCubicToQuadraticPlugin();p.settings()
            try:
                p.convert_(None);p.advance_(p._timer);p.advance_(p._timer)
                self.assertTrue(started.wait(2));p.cancel_(None);release.set()
                p._executor.submit(lambda:None).result(10)
                self.assertFalse(p._busy);self.assertEqual(f.events,[])
                self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve')
            finally:release.set();p._executor.shutdown(wait=True)

if __name__=='__main__':unittest.main(verbosity=2)

