# -*- coding: utf-8 -*-
import sys,unittest
from types import SimpleNamespace
from unittest.mock import patch
from mock_glyphs import *
from glyphs_adapter import conversion_steps,ConversionError
from fast_fit import fit_corresponding
from geometry_fit import geometric_bounds
from quad_fit import quadratic
from test_settings import finish
from test_entrypoints import modules,plugin_files,load

SOURCE=(5+0j,5+47j,3+76j,0+102j)
BAD=(5+0j,6+462j,0+102j)

def convert(font,**options):return finish(conversion_steps(font,Node,Point,CONSTANTS,**options))
def snapshot(layer):return [[(n.type,n.position.x,n.position.y,n.smooth) for n in p.nodes] for p in layer.paths]
def backup(g,name='backup',curves=(EXACT,)):
    layer=Layer([path(p) for p in curves],name);layer.isMasterLayer=False;layer.parent=g;g.layers.values.append(layer)
    return layer

def background(foreground):
    layer=Layer([path(EXACT)],foreground.layerId);layer.isMasterLayer=False
    layer.foreground=foreground;layer.parent=foreground;foreground.background=layer
    return layer

class LayerScopeAndSvgTests(unittest.TestCase):
    def test_selected_backup_is_independent_of_incompatible_masters(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));g.override=False;b=backup(g)
        f=Font([g],2);f.selectedLayers=[b];old=[snapshot(l) for l in g.layers if l is not b]
        self.assertTrue(convert(f));self.assertEqual(b.paths[0].nodes[-1].type,'qcurve')
        self.assertEqual([snapshot(l) for l in g.layers if l is not b],old)

    def test_selected_background_preserves_its_foreground_and_other_masters(self):
        g=glyph(sources=(EXACT,EXACT));foreground=g.layers[0];b=background(foreground)
        f=Font([g],2);f.selectedLayers=[b];old=[snapshot(l) for l in g.layers]
        self.assertTrue(convert(f));self.assertEqual(b.paths[0].nodes[-1].type,'qcurve')
        self.assertEqual([snapshot(l) for l in g.layers],old)

    def test_active_background_replaces_foreground_from_selected_layers(self):
        g=glyph();b=background(g.layers[0]);f=Font([g]);f.selectedLayers=[g.layers[0]]
        f.currentTab=SimpleNamespace(activeLayer=lambda:b)
        self.assertTrue(convert(f));self.assertEqual(b.paths[0].nodes[-1].type,'qcurve')
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve')

    def test_background_with_glyph_parent_and_cursor_only(self):
        g=glyph();b=background(g.layers[0]);b.parent=g;f=Font([g])
        f.currentTab=SimpleNamespace(activeLayer=lambda:b)
        self.assertTrue(convert(f));self.assertEqual(b.paths[0].nodes[-1].type,'qcurve')

    def test_selected_nodes_in_backup_only_convert_that_segment(self):
        g=glyph();b=backup(g,curves=(EXACT,PAIR_NEEDED));b.selection=b.paths[0].nodes[1:3]
        f=Font([g]);f.selectedLayers=[b];self.assertTrue(convert(f))
        self.assertEqual(b.paths[0].nodes[-1].type,'qcurve');self.assertEqual(b.paths[1].nodes[-1].type,'curve')
        self.assertEqual(len(b.selection),1)

    def test_two_backups_with_different_topology_do_not_share_keys(self):
        g=glyph();a=backup(g,'first');b=backup(g,'second',(EXACT,PAIR_NEEDED));f=Font([g]);f.selectedLayers=[a,b]
        self.assertTrue(convert(f));self.assertEqual(len(a.paths),1);self.assertEqual(len(b.paths),2)
        self.assertTrue(all(p.nodes[-1].type=='qcurve' for l in (a,b) for p in l.paths))
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve')

    def test_foreground_and_backup_selection_can_coexist(self):
        g=glyph(sources=(EXACT,EXACT));b=backup(g,curves=(EXACT,EXACT));f=Font([g],2)
        f.selectedLayers=[g.layers[0],b];self.assertTrue(convert(f))
        self.assertTrue(all(p.nodes[-1].type=='qcurve' for l in g.layers for p in l.paths))

    def test_removing_backup_while_processing_cancels_without_writes(self):
        g=glyph();b=backup(g);f=Font([g]);f.selectedLayers=[b];old=snapshot(b)
        job=conversion_steps(f,Node,Point,CONSTANTS);next(job);next(job);g.layers.values.remove(b)
        with self.assertRaises(ConversionError):next(job)
        self.assertEqual(snapshot(b),old);self.assertEqual(f.events,[])

    def test_replacing_background_while_processing_cancels(self):
        g=glyph();foreground=g.layers[0];b=background(foreground);f=Font([g]);f.selectedLayers=[b];old=snapshot(b)
        job=conversion_steps(f,Node,Point,CONSTANTS);next(job);next(job);background(foreground)
        with self.assertRaises(ConversionError):next(job)
        self.assertEqual(snapshot(b),old);self.assertEqual(f.events,[])

    def test_backup_components_do_not_change_exporting_base_glyph(self):
        base=glyph('base');g=glyph();b=backup(g);b.components=[Component('base')]
        f=Font([g,base]);f.selectedLayers=[b];self.assertTrue(convert(f))
        self.assertEqual(base.layers[0].paths[0].nodes[-1].type,'curve')
        self.assertEqual(b.components[0].componentName,'base')

    def test_given_bad_quadratic_is_far_outside_tolerance(self):
        lower,upper=geometric_bounds(SOURCE,[BAD],.5)
        self.assertGreater(lower,157.7);self.assertLess(upper,157.8)
        t=462/(2*462-102)
        self.assertGreater(quadratic(BAD,t).imag,259)

    def test_given_source_is_fitted_without_overshoot_under_release_defaults(self):
        g=glyph(sources=(SOURCE,));f=Font([g]);f.selectedLayers=[g.layers[0]]
        root,res=plugin_files();env=modules(f)
        with patch.dict(sys.modules,env):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine');engine.glyphs_main()
        nodes=g.layers[0].paths[0].nodes
        self.assertEqual(len(nodes),3)
        q=tuple(complex(n.position.x,n.position.y) for n in nodes)
        self.assertEqual(q[0],SOURCE[0]);self.assertEqual(q[-1],SOURCE[-1])
        self.assertEqual(q[1],5+51j)
        self.assertLessEqual(geometric_bounds(SOURCE,[q],.5)[1],.5)
        self.assertTrue(all(0<=quadratic(q,i/100).imag<=102 for i in range(101)))

    def test_svg_regression_survives_direction_reflection_and_rotation(self):
        for reverse in (False,True):
            for factor in (1,-1,1j,-1j):
                for conjugate in (False,True):
                    p=tuple((z.conjugate() if conjugate else z)*factor for z in SOURCE)
                    if reverse:p=tuple(reversed(p))
                    r=fit_corresponding([p],.5,3,integer_step=1,center_limit=5,center_tolerance=.5,comparison_tolerance=1)[0]
                    self.assertLessEqual(geometric_bounds(p,r['parts'],.5)[1],.5)
                    self.assertLess(max(abs(z-p[0]) for q in r['parts'] for z in q),110)

    def test_numeric_fields_use_right_alignment(self):
        env=modules(Font([glyph()]));root,res=plugin_files()
        with patch.dict(sys.modules,env):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','right_aligned');p=m.ZonzCubicToQuadraticPlugin();p.settings();p.openSettings_(None)
                for field in (p._deviation_field,p._count_field,p._center_field,p._angle_field):
                    self.assertEqual(field.calls['setAlignment_'],(m.NSTextAlignmentRight,))

if __name__=='__main__':unittest.main(verbosity=2)
