# -*- coding: utf-8 -*-
import math,sys,unittest
from unittest.mock import patch
from mock_glyphs import Node,Point,CONSTANTS
from test_merge import joined_font,THREE
from test_tangents import bend
from test_settings import finish
from test_entrypoints import modules,plugin_files,load
from glyphs_adapter import conversion_steps,curve_tangents
from tangent_constraints import on_ray,aligned
from preferences import DEFAULT_SETTINGS,load_settings,save_settings
from merge_fit import fit_run_corresponding

class CurveJoinTests(unittest.TestCase):
    def convert(self,font,**options):
        return finish(conversion_steps(font,Node,Point,CONSTANTS,tolerance=1,max_controls=3,
            angle_limit=5,keep_curve_tangent=True,**options))

    def controls_at(self,path,anchor):
        nodes=list(path.nodes);i=nodes.index(anchor);n=len(nodes)
        return tuple(complex(nodes[(i+offset)%n].position.x,nodes[(i+offset)%n].position.y) for offset in (-1,1))

    def test_average_uses_directions_without_weighting_handle_length(self):
        chain=bend(4);f,g=joined_font((chain,));rays=curve_tangents(g.layers[0],0,[0],CONSTANTS,5)
        outgoing=curve_tangents(g.layers[0],0,[3],CONSTANTS,5)[0]
        self.assertTrue(aligned(-rays[1][1],outgoing[1],1e-7))
        self.assertAlmostEqual(outgoing[1].imag/outgoing[1].real,math.tan(math.radians(2)))
        self.assertIsNone(curve_tangents(g.layers[0],0,[0],CONSTANTS,3)[1])

    def test_disabled_merge_preserves_average_tangent_float_and_integer(self):
        for integer in (False,True):
            f,g=joined_font((bend(4),));layer=g.layers[0];anchor=layer.paths[0].nodes[3]
            incoming=curve_tangents(layer,0,[0],CONSTANTS,5)[1]
            outgoing=curve_tangents(layer,0,[3],CONSTANTS,5)[0]
            self.convert(f,merge_curves=False,integer_coords=integer)
            left,right=self.controls_at(layer.paths[0],anchor)
            self.assertTrue(on_ray(left,incoming,int(integer)))
            self.assertTrue(on_ray(right,outgoing,int(integer)))
            self.assertEqual(len([n for n in layer.paths[0].nodes if n.type=='qcurve']),2)

    def test_failed_merge_keeps_internal_boundary_constraints(self):
        f,g=joined_font((bend(4),));layer=g.layers[0];anchor=layer.paths[0].nodes[3]
        incoming=curve_tangents(layer,0,[0],CONSTANTS,5)[1]
        outgoing=curve_tangents(layer,0,[3],CONSTANTS,5)[0]
        with patch('merge_fit.try_merged_corresponding',return_value=None) as attempt:
            self.convert(f,merge_curves=True,integer_coords=True)
        self.assertTrue(attempt.called)
        left,right=self.controls_at(layer.paths[0],anchor)
        self.assertTrue(on_ray(left,incoming,1));self.assertTrue(on_ray(right,outgoing,1))

    def test_partial_merge_passes_only_surviving_boundary_rays(self):
        f,g=joined_font();layer=g.layers[0]
        pairs=[curve_tangents(layer,0,[i],CONSTANTS,5) for i in (0,3,6)]
        seen=[]
        def merged(chains,tolerance,max_controls,cancel=None,**options):
            seen.append((len(chains[0]),options['tangents']))
            return None
        with patch('merge_fit.try_merged_corresponding',side_effect=merged):
            blocks=fit_run_corresponding([THREE],1,3,join_tangents=[pairs])
        self.assertEqual([b['count'] for b in blocks],[1,1,1])
        self.assertIn((2,[(pairs[0][0],pairs[1][1])]),seen)
        self.assertIn((2,[(pairs[1][0],pairs[2][1])]),seen)
        for i,block in enumerate(blocks):self.assertEqual(block['fits'][0]['tangents'],pairs[i])

    def test_successful_merge_removes_join_without_internal_constraints(self):
        f,g=joined_font();old=g.layers[0].paths[0].nodes[3]
        self.convert(f,merge_curves=True)
        self.assertNotIn(old,g.layers[0].paths[0].nodes)
        self.assertEqual(len(g.layers[0].paths[0].nodes),3)

    def test_selection_preserves_unconverted_neighbor(self):
        f,g=joined_font((bend(4),));layer=g.layers[0];anchor=layer.paths[0].nodes[3]
        original=list(layer.paths[0].nodes[4:]);position=[(n.position.x,n.position.y,n.type) for n in original]
        layer.selection=layer.paths[0].nodes[1:3]
        ray=curve_tangents(layer,0,[0],CONSTANTS,5)[1]
        self.convert(f,merge_curves=False,integer_coords=True)
        left,right=self.controls_at(layer.paths[0],anchor)
        self.assertTrue(on_ray(left,ray,1))
        self.assertEqual([(n.position.x,n.position.y,n.type) for n in original],position)
        self.assertEqual(anchor.type,'qcurve');self.assertEqual(layer.paths[0].nodes[-1].type,'curve')

    def test_corner_and_zero_handles_do_not_gain_constraints(self):
        for chain in (bend(30),((0j,30j,100+0j,100+0j),bend(0)[1])):
            f,g=joined_font((chain,))
            self.assertIsNone(curve_tangents(g.layers[0],0,[0],CONSTANTS,5)[1])
            self.assertIsNone(curve_tangents(g.layers[0],0,[3],CONSTANTS,5)[0])

    def test_closed_path_wrap_uses_original_mean_tangent(self):
        chain=((0j,30+0j,100+30j,100+0j),(100+0j,100-30j,-30+0j,0j))
        f,g=joined_font((chain,),closed=True,rotation=3);layer=g.layers[0]
        anchors=[layer.paths[0].nodes[i] for i in (0,3)]
        rays=[curve_tangents(layer,0,[i],CONSTANTS,5) for i in (0,3)]
        self.convert(f,merge_curves=False,integer_coords=True)
        for anchor,pair in zip(anchors,rays):
            left,right=self.controls_at(layer.paths[0],anchor)
            self.assertTrue(on_ray(right,pair[0],1))
            self.assertTrue(on_ray(left,(pair[0][0],-pair[0][1]),1))

    def test_master_sync_retains_join_rays_with_explicit_integer_midpoints(self):
        chain=bend(4);other=tuple(tuple(z*2 for z in p) for p in chain)
        f,g=joined_font((chain,other));anchors=[l.paths[0].nodes[3] for l in g.layers]
        pairs=[(curve_tangents(l,0,[0],CONSTANTS,5)[1],curve_tangents(l,0,[3],CONSTANTS,5)[0]) for l in g.layers]
        self.convert(f,merge_curves=False,integer_coords=True,add_midpoint=True)
        self.assertTrue(g.mastersCompatible)
        for layer,anchor,pair in zip(g.layers,anchors,pairs):
            left,right=self.controls_at(layer.paths[0],anchor)
            self.assertTrue(on_ray(left,pair[0],1));self.assertTrue(on_ray(right,pair[1],1))

    def test_new_setting_defaults_and_public_job_forwarding(self):
        self.assertTrue(DEFAULT_SETTINGS['keep_curve_tangent'])
        f,g=joined_font((bend(4),));env=modules(f);root,res=plugin_files()
        with patch.dict(sys.modules,env):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            self.assertTrue(engine.load_settings(env['GlyphsApp'].Glyphs)['keep_curve_tangent'])
            with patch.object(engine,'conversion_steps',return_value=None) as convert:
                engine.make_job(keep_curve_tangent=False)
                self.assertFalse(convert.call_args[0][-1])
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','curve_join_setting');p=m.ZonzCubicToQuadraticPlugin();p.settings();p.openSettings_(None)
                keys=[key for key,attribute in m.SETTING_CONTROLS]
                self.assertEqual(keys[keys.index('keep_line_tangent')+1],'keep_curve_tangent')
                self.assertEqual(p._curve_tangent_check.state(),1)
                p._curve_tangent_check.setState_(0);p.changeSetting_(p._curve_tangent_check)
                self.assertFalse(engine.load_settings(env['GlyphsApp'].Glyphs)['keep_curve_tangent'])
                with patch.object(m,'make_job',return_value=(value for value in ())) as job:
                    p.convert_(None)
                    self.assertFalse(job.call_args[1]['keep_curve_tangent'])
                    p.cancel_(None)

if __name__=='__main__':unittest.main(verbosity=2)
