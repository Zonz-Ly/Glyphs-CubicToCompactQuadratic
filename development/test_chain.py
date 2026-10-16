# -*- coding: utf-8 -*-
import contextlib,io,math,random,sys,unittest
from unittest.mock import patch
from mock_glyphs import *
from quad_fit import cubic,quadratic
from search_core import unpack,pack,basis,Context,sample_rows,sample_norms
from chain_fit import subdivision_seed,least_squares_seed
from fast_fit import fit,fit_corresponding,numeric_cache
from glyphs_adapter import conversion_steps
from preferences import load_settings,save_settings,validated_settings,PREFERENCE_PREFIX
from test_entrypoints import modules,plugin_files,load
from test_settings import finish

class ChainTests(unittest.TestCase):
    def test_basis_matches_finite_difference(self):
        rng=random.Random(701)
        p=(0j,1+2j,3-1j,4+0j)
        for count in (1,2,3,4,8):
            x=[rng.uniform(-1,1) for _ in range(2*count)]
            for segment in range(count):
                for s in (0,.2,.6,1):
                    analytic=basis(s,segment,count)
                    for dim,value in enumerate(analytic):
                        high=list(x);low=list(x);high[dim]+=1e-6;low[dim]-=1e-6
                        numerical=(quadratic(unpack(p,high)[segment],s)-quadratic(unpack(p,low)[segment],s))/2e-6
                        self.assertLess(abs(numerical-value),5e-10)

    def test_multiple_controls_keep_midpoint_joins_and_tangents(self):
        p=HARD
        for count in (3,4,7):
            parts=unpack(p,subdivision_seed(p,[i/count for i in range(count+1)]))
            self.assertEqual(parts[0][0],p[0]);self.assertEqual(parts[-1][-1],p[3])
            self.assertEqual(len(parts),count)
            for a,b in zip(parts,parts[1:]):
                self.assertEqual(a[2],b[0]);self.assertEqual(a[2],(a[1]+b[1])/2)
                self.assertAlmostEqual(abs((a[2]-a[1])-(b[1]-b[0])),0,places=10)

    def test_exact_quadratic_subdivision_and_lsq_seeds(self):
        q=(0j,60+100j,200+20j)
        p=(q[0],(q[0]+2*q[1])/3,(2*q[1]+q[2])/3,q[2])
        for count in (3,5,9):
            times=[i/count for i in range(count+1)]
            for seed in (subdivision_seed(p,times),least_squares_seed(p,times)):
                parts=unpack(p,seed)
                for i in range(81):
                    t=i/80;segment=min(count-1,int(t*count));s=t*count-segment
                    self.assertLess(abs(quadratic(parts[segment],s)-cubic(p,t)),2e-10)

    def test_multisegment_score_only_equals_rows(self):
        p=tuple(z/220 for z in HARD);context=Context(p,33,17)
        for count in (3,5):
            parts=unpack(p,subdivision_seed(p,[i/count for i in range(count+1)]))
            self.assertEqual(sample_rows(parts,context)[1],sample_norms(parts,context))

    def test_hard_case_adds_controls_until_target_passes(self):
        pair=fit_corresponding([HARD],max_controls=2)[0]
        four=fit_corresponding([HARD],max_controls=4)[0]
        self.assertEqual(len(pair['parts']),1);self.assertFalse(pair['within'])
        self.assertEqual(len(four['parts']),4);self.assertLess(__import__('geometry_fit').geometric_bounds(HARD,four['parts'],.5)[1],.5)
        self.assertIsNotNone(four['error'])

    def test_allowed_maximum_is_not_forced_count(self):
        p=(68+656j,96+410j,256+283j,485+242j)
        with patch('fast_fit.optimize_chain',side_effect=AssertionError('unnecessary chain search')):
            r=fit_corresponding([p],max_controls=32)[0]
        self.assertEqual(len(r['parts']),1);self.assertTrue(r['within'])

    def test_all_masters_share_required_count(self):
        results=fit_corresponding([EXACT,HARD],max_controls=4)
        self.assertEqual([len(r['parts']) for r in results],[4,4])
        self.assertTrue(all(r['error'] is not None for r in results))

    def test_cap_reached_is_applied(self):
        g=glyph(sources=(EXACT,HARD));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        r=finish(conversion_steps(f,Node,Point,CONSTANTS,max_controls=3))
        self.assertTrue(r)
        for l in g.layers:
            self.assertEqual(sum(n.type=='offcurve' for n in l.paths[0].nodes),3)
            self.assertEqual(len(l.paths[0].nodes),5)
        self.assertTrue(g.mastersCompatible)

    def test_multicontrol_explicit_midpoints(self):
        g=glyph(sources=(EXACT,HARD));f=Font([g],2);l=g.layers[1]
        l.selection=l.paths[0].nodes[1:3];f.selectedLayers=[l]
        r=finish(conversion_steps(f,Node,Point,CONSTANTS,max_controls=4,add_midpoint=True))
        for layer in g.layers:
            nodes=layer.paths[0].nodes
            self.assertEqual([n.type for n in nodes],['line','offcurve','qcurve','offcurve','qcurve','offcurve','qcurve'])
            for i in (2,4):
                self.assertTrue(nodes[i].smooth)
                self.assertEqual(nodes[i].position.x,(nodes[i-1].position.x+nodes[i+1].position.x)/2)
                self.assertEqual(nodes[i].position.y,(nodes[i-1].position.y+nodes[i+1].position.y)/2)
        self.assertEqual(len(l.selection),5)
        self.assertEqual(f.undo.groups,1);self.assertTrue(g.mastersCompatible)

    def test_multicontrol_write_failure_rolls_back_all_masters(self):
        g=glyph(sources=(EXACT,HARD));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        old=[list(l.paths[0].nodes) for l in g.layers];g.layers[1].paths[0].fail_once=True
        with self.assertRaisesRegex(RuntimeError,'Injected'):
            finish(conversion_steps(f,Node,Point,CONSTANTS,max_controls=4,add_midpoint=True))
        for layer,original in zip(g.layers,old):self.assertEqual(layer.paths[0].nodes,original)
        self.assertEqual(f.undo.depth,0)

    def test_cap_compares_earlier_counts_without_exceeding_limit(self):
        calls=[];errors={1:8,2:3,3:4,4:2}
        def fake(p,policy='single',control_count=2,**kwargs):
            count=1 if policy in ('probe','single') else (2 if policy=='pair' else control_count)
            calls.append(count);error=errors[count]
            return dict(parts=[(0j,0j,0j)]*count,within=False,error=(error,error))
        def bounds(p,parts,*args,**kwargs):return (errors[len(parts)],)*2
        with patch('fast_fit.fit',fake),patch('fast_fit.geometric_bounds',bounds):
            r=fit_corresponding([HARD,EXACT],max_controls=3)
            self.assertEqual([len(x['parts']) for x in r],[2,2]);self.assertLessEqual(max(calls),3)
            calls.clear();r=fit_corresponding([HARD,EXACT],max_controls=4)
            self.assertEqual([len(x['parts']) for x in r],[4,4]);self.assertLessEqual(max(calls),4)

    def test_maximum_count_validation_is_atomic(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs;load_settings(app)
        for count in (0,-1,'3.5',float('nan'),float('inf'),1.5,True,'bad'):
            old=dict(app.defaults)
            with self.assertRaises(ValueError):save_settings(app,max_controls=count)
            self.assertEqual(app.defaults,old)
        self.assertEqual(validated_settings(max_controls='4')['max_controls'],4)

    def test_current_preferences_use_defaults_for_missing_values(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        app.defaults[PREFERENCE_PREFIX+'add_midpoint']=True
        want=dict(deviation=1,max_controls=3,add_midpoint=True,merge_curves=True,center_limit=7.0,integer_coords=True,angle_limit=5.0,keep_line_tangent=True,keep_curve_tangent=True)
        self.assertEqual(load_settings(app),want);self.assertEqual(load_settings(app),want)
        save_settings(app,deviation=.3,max_controls=5)
        self.assertEqual(load_settings(app),dict(deviation=.3,max_controls=5,add_midpoint=False,merge_curves=False,center_limit=0.0,integer_coords=False,angle_limit=2.0,keep_line_tangent=False,keep_curve_tangent=False))

    def test_compact_panel_system_fonts_and_alignment(self):
        g=glyph(sources=(EXACT,HARD));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        root,res=plugin_files();env=modules(f);app=env['GlyphsApp'].Glyphs;messages=[]
        env['GlyphsApp'].Message=lambda **kw:messages.append(kw)
        with patch.dict(sys.modules,env),contextlib.redirect_stdout(io.StringIO()):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            engine.save_settings(app,deviation=1,max_controls=2,center_limit=0,merge_curves=False,integer_coords=False,angle_limit=2,keep_line_tangent=False)
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','release_panel');p=m.ZonzCubicToQuadraticPlugin();p.settings();p.start();p.openSettings_(None)
                self.assertEqual(p._settings_panel.calls['setTitle_'][0],'转换为精简的二次曲线设置⋯')
                self.assertEqual(len(p._settings_panel.contentView().children),18)
                fields=[p._deviation_field,p._count_field,p._midpoint_check]
                for field in fields:
                    self.assertEqual(field.calls['setFont_'][0].calls['size'],13)
                rights=[field.calls['initWithFrame_'][0][0]+field.calls['initWithFrame_'][0][2] for field in fields]
                self.assertEqual(len(set(rights)),1)
                p._count_field.setStringValue_('4');p._midpoint_check.setState_(1);[p.changeSetting_(getattr(p,a)) for _,a in m.SETTING_CONTROLS]
                p.convert_(None)
                for _ in range(20):
                    if not p._busy:break
                    p.advance_(p._timer)
                self.assertFalse(p._busy);self.assertEqual(messages,[])
                self.assertTrue(all(len(l.paths[0].nodes)==7 for l in g.layers))

    def test_cancel_multicontrol_job_keeps_font(self):
        g=glyph(sources=(EXACT,HARD));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        job=conversion_steps(f,Node,Point,CONSTANTS,max_controls=4);next(job);next(job);job.close()
        self.assertTrue(all(l.paths[0].nodes[-1].type=='curve' for l in g.layers))
        self.assertEqual(f.events,[])

if __name__=='__main__':unittest.main(verbosity=2)
