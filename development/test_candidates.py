# -*- coding: utf-8 -*-
import unittest
from concurrent.futures import CancelledError
from unittest.mock import patch
from mock_glyphs import *
from test_merge import joined_font,THREE
from test_settings import finish
from preferences import PREFERENCE_PREFIX,load_settings,save_settings
from test_entrypoints import modules
from glyphs_adapter import conversion_steps
from fast_fit import fit,fit_corresponding
from geometry_fit import geometric_bounds
from i18n import tr

class CandidateTests(unittest.TestCase):
    def test_upm_scales_only_limits_preserving_raw_snapshot(self):
        source=tuple(z*2 for z in PAIR_NEEDED);f,g=joined_font(((source,),));f.upm=2000;calls=[]
        def runner(curves,tolerance,max_controls,progress,**options):
            calls.append((curves,tolerance,max_controls,options))
            if False:yield
            return fit_corresponding(curves,tolerance,max_controls,**options)
        finish(conversion_steps(f,Node,Point,CONSTANTS,tolerance=.5,fit_runner=runner,center_limit=5,integer_coords=True))
        curves,tolerance,maximum,options=calls[0]
        self.assertEqual(curves,[source]);self.assertEqual(tolerance,.5)
        self.assertEqual(options['center_limit'],10);self.assertEqual(options['integer_step'],1)
        direct=fit_corresponding([source],.5,2,center_limit=10,center_tolerance=.5,integer_step=1)
        written=[complex(n.position.x,n.position.y) for n in g.layers[0].paths[0].nodes if n.type=='offcurve']
        self.assertEqual(written,[q[1] for q in direct[0]['parts']])

    def test_upm_merge_receives_original_chain_and_scaled_limits(self):
        scale=2.048;chain=tuple(tuple(z*scale for z in p) for p in THREE)
        f,g=joined_font((chain,));f.upm=2048;calls=[]
        from merge_fit import fit_run_corresponding
        def runner(chains,tolerance,max_controls,progress,merge=False,cyclic=False,**options):
            calls.append((chains,tolerance,merge,options))
            if False:yield
            return fit_run_corresponding(chains,tolerance,max_controls,cyclic,**options)
        finish(conversion_steps(f,Node,Point,CONSTANTS,merge_curves=True,fit_runner=runner,center_limit=3))
        chains,tolerance,merge,options=calls[0]
        self.assertEqual(chains,[chain]);self.assertTrue(merge)
        self.assertEqual(tolerance,scale);self.assertEqual(options['center_limit'],3*scale)

    def test_saved_value_ignores_retired_unit_marker(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        for marker in (None,1,2):
            app.defaults[PREFERENCE_PREFIX+'deviation_unit']=marker
            app.defaults[PREFERENCE_PREFIX+'deviation']='0.25'
            self.assertEqual(load_settings(app)['deviation'],.25)
        app.defaults.pop(PREFERENCE_PREFIX+'deviation_unit')
        save_settings(app,deviation=25)
        self.assertNotIn(PREFERENCE_PREFIX+'deviation_unit',app.defaults)

    def test_chinese_prefers_seat_character(self):
        self.assertEqual(tr('integer_coords',language='zh-Hans'),'以整数座标转换')
        self.assertEqual(tr('integer_coords',language='zh-Hant'),'以整數座標轉換')

    def test_real_single_can_beat_higher_count_at_cap(self):
        one=fit(HARD,policy='single',check_error=False)['parts']
        two=fit(HARD,policy='pair',check_error=False)['parts']
        a=geometric_bounds(HARD,one,.5);b=geometric_bounds(HARD,two,.5)
        self.assertLess(a[1],b[0])
        chosen=fit_corresponding([HARD],.5,2)[0]
        self.assertEqual(chosen['parts'],one);self.assertFalse(chosen['within'])

    def test_cap_comparison_uses_worst_master_and_completes_only_once(self):
        a=(0j,0j,0j,0j);b=(1j,1j,1j,1j);calls=[]
        errors={(0j,1):5,(1j,1):5,(0j,2):2,(1j,2):9}
        def fake(p,policy,control_count,check_error,**options):
            count=control_count;calls.append((p[0],count));error=errors[p[0],count]
            return dict(parts=[(p[0],0j,p[3])]*count,error=(error,error) if check_error else None,within=False)
        def bounds(p,parts,*args,**options):return (errors[p[0],len(parts)],)*2
        with patch('fast_fit.fit',fake),patch('fast_fit.geometric_bounds',bounds):r=fit_corresponding([a,b],.01,2)
        self.assertEqual([len(x['parts']) for x in r],[1,1])
        self.assertEqual(len(calls),len(set(calls)));self.assertEqual({n for _,n in calls},{1,2})

    def test_comparison_tie_prefers_fewer_controls(self):
        def fake(p,control_count,**options):return dict(parts=[(0j,0j,0j)]*control_count,error=(3,3),within=False)
        with patch('fast_fit.fit',fake),patch('fast_fit.geometric_bounds',return_value=(3,3)):
            r=fit_corresponding([HARD,EXACT],.5,4)
        self.assertEqual([len(x['parts']) for x in r],[1,1])

    def test_comparison_cancellation_stops_before_font_writes(self):
        f,g=joined_font(((HARD,),));old=list(g.layers[0].paths[0].nodes);cancelled=[False]
        def bounds(p,parts,*args,**options):cancelled[0]=True;return (3,3)
        def fake(p,control_count,**options):return dict(parts=[(0j,0j,0j)]*control_count,error=(3,3),within=False)
        with patch('fast_fit.fit',fake),patch('fast_fit.geometric_bounds',bounds):
            with self.assertRaises(CancelledError):fit_corresponding([HARD],.5,2,cancel=lambda:cancelled[0])
        self.assertEqual(g.layers[0].paths[0].nodes,old);self.assertEqual(f.events,[])

if __name__=='__main__':unittest.main(verbosity=2)
