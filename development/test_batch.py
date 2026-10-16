import unittest
from types import SimpleNamespace
from mock_glyphs import *
from glyphs_adapter import conversion_steps,ConversionError,validate_nodes

def steps(font):return conversion_steps(font,Node,Point,CONSTANTS)
def run(font):
    job=steps(font)
    while True:
        try:next(job)
        except StopIteration as done:return done.value

class BatchTests(unittest.TestCase):
    def test_native_identity_is_independent_of_python_wrapper(self):
        from unittest.mock import patch
        import glyphs_adapter as adapter
        a,b=SimpleNamespace(pointer=222),SimpleNamespace(pointer=222)
        with patch.object(adapter,'_objc_id',lambda obj:obj.pointer):
            self.assertEqual(adapter.object_id(a),adapter.object_id(b))
        self.assertNotEqual(id(a),id(b))

    def test_no_selection_converts_whole_glyph(self):
        g=glyph();l=g.layers[0];second=path(EXACT);second.parent=l;l.paths.append(second)
        f=Font([g]);f.selectedLayers=[l]
        ends=[(p.nodes[0],p.nodes[-1]) for p in l.paths]
        r=run(f)
        self.assertTrue(r)
        for p,(a,b) in zip(l.paths,ends):
            self.assertEqual([n.type for n in p.nodes],['line','offcurve','qcurve'])
            self.assertIs(p.nodes[0],a);self.assertIs(p.nodes[-1],b)
        self.assertEqual(l.selection,[]);self.assertEqual(f.undo.depth,0);self.assertEqual(f.undo.groups,1)

    def test_edit_cursor_with_no_selected_layer_uses_only_active_glyph(self):
        a,b=glyph('A'),glyph('B');f=Font([a,b])
        f.currentTab=SimpleNamespace(layers=[a.layers[0],b.layers[0]],layersCursor=1)
        r=run(f)
        self.assertTrue(r)
        self.assertEqual(a.layers[0].paths[0].nodes[-1].type,'curve')
        self.assertEqual(b.layers[0].paths[0].nodes[-1].type,'qcurve')

    def test_node_selection_restricts_curves(self):
        g=glyph();l=g.layers[0];p=l.paths[0];other=path(EXACT);other.parent=l;l.paths.append(other)
        l.selection=p.nodes[1:3];f=Font([g]);f.selectedLayers=[l]
        r=run(f)
        self.assertTrue(r);self.assertEqual(other.nodes[-1].type,'curve')
        self.assertEqual(l.selection,[p.nodes[1]])

    def test_font_view_multiple_glyphs_ignores_node_selection(self):
        a,b,c=[glyph(n) for n in 'ABC'];f=Font([a,b,c],edit=False);f.selection=[a,b]
        a.layers[0].selection=[a.layers[0].paths[0].nodes[0]]
        f.selectedLayers=[c.layers[0]]
        r=run(f)
        self.assertTrue(r)
        self.assertEqual(a.layers[0].paths[0].nodes[-1].type,'qcurve')
        self.assertEqual(b.layers[0].paths[0].nodes[-1].type,'qcurve')
        self.assertEqual(c.layers[0].paths[0].nodes[-1].type,'curve')

    def test_any_master_requires_pair_every_master_gets_pair(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));f=Font([g],masters=2);f.selectedLayers=[g.layers[0]]
        r=run(f)
        self.assertTrue(r)
        for l in g.layers:
            p=l.paths[0];self.assertEqual([n.type for n in p.nodes],['line','offcurve','offcurve','qcurve'])
            self.assertEqual(sum(n.type!='offcurve' for n in p.nodes),2)
        self.assertTrue(g.mastersCompatible);self.assertEqual(f.undo.groups,1)

    def test_all_masters_single_with_variable_instance(self):
        g=glyph(sources=(EXACT,tuple(z*2 for z in EXACT)));f=Font([g],2)
        f.instances=[SimpleNamespace(type=1)];f.selectedLayers=[g.layers[0]]
        r=run(f);self.assertTrue(r)
        self.assertTrue(all(len(l.paths[0].nodes)==3 for l in g.layers))

    def test_selection_in_second_master_maps_to_first_master(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));l=g.layers[1]
        l.selection=l.paths[0].nodes[1:3];f=Font([g],2);f.selectedLayers=[l]
        run(f)
        self.assertTrue(all(p.nodes[-1].type=='qcurve' for layer in g.layers for p in layer.paths))
        self.assertEqual(g.layers[0].selection,[]);self.assertEqual(len(l.selection),2)

    def test_incompatible_master_no_partial_changes(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));g.layers[1].paths.append(path(EXACT))
        f=Font([g],2);f.selectedLayers=[g.layers[0]];r=run(f)
        self.assertFalse(r)
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve');self.assertEqual(f.events,[])

    def test_extra_anchor_mismatch_despite_native_compatible_flag(self):
        g=glyph(sources=(EXACT,EXACT));g.override=True
        g.layers[1].anchors=[SimpleNamespace(name='top')]
        f=Font([g],2);f.selectedLayers=[g.layers[0]]
        self.assertFalse(run(f));self.assertEqual(len(g.layers[0].paths[0].nodes),4)

    def test_special_layer_synchronized_backup_unchanged(self):
        g=glyph(sources=(EXACT,EXACT));brace=Layer([path(EXACT)],'brace',True)
        backup=Layer([path(PAIR_NEEDED)],'backup');backup.isMasterLayer=False
        for l in (brace,backup):l.parent=g;g.layers.values.append(l)
        f=Font([g],2);f.selectedLayers=[g.layers[0]];r=run(f)
        self.assertTrue(r);self.assertEqual(len(brace.paths[0].nodes),3)
        self.assertEqual(backup.paths[0].nodes[-1].type,'curve')

    def test_different_special_topology_skips_glyph(self):
        g=glyph();special=Layer([path(EXACT),path(EXACT)],'bracket',True)
        special.parent=g;g.layers.values.append(special);f=Font([g]);f.selectedLayers=[g.layers[0]]
        self.assertFalse(run(f));self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve')

    def test_recursive_components_keep_references(self):
        base=glyph('base');middle=Glyph('middle',[Layer()]);outer=Glyph('outer',[Layer()])
        middle.layers[0].components=[Component('base')];outer.layers[0].components=[Component('middle')]
        f=Font([base,middle,outer],edit=False);f.selection=[outer]
        comp=outer.layers[0].components[0];r=run(f)
        self.assertEqual(base.layers[0].paths[0].nodes[-1].type,'qcurve')
        self.assertIs(outer.layers[0].components[0],comp)
        self.assertTrue(r)

    def test_component_reference_changed_during_preparation_aborts(self):
        a,b=glyph('baseA'),glyph('baseB');outer=Glyph('outer',[Layer()])
        comp=Component('baseA');outer.layers[0].components=[comp]
        f=Font([a,b,outer],edit=False);f.selection=[outer]
        job=steps(f);next(job);comp.componentName='baseB'
        with self.assertRaisesRegex(ConversionError,'structure changed'):
            while True:next(job)
        self.assertEqual(a.layers[0].paths[0].nodes[-1].type,'curve');self.assertEqual(f.events,[])

    def test_selected_component_is_supported(self):
        base=glyph('base');g=Glyph('A',[Layer()]);comp=Component('base',True)
        g.layers[0].components=[comp];g.layers[0].selection=[comp]
        f=Font([base,g]);f.selectedLayers=[g.layers[0]]
        self.assertTrue(run(f))

    def test_hint_reference_to_removed_handle_skips(self):
        g=glyph();l=g.layers[0];l.hints=[SimpleNamespace(originNode=l.paths[0].nodes[1])]
        f=Font([g]);f.selectedLayers=[l]
        self.assertFalse(run(f));self.assertEqual(l.paths[0].nodes[-1].type,'curve')

    def test_transaction_rollback_all_masters(self):
        g=glyph(sources=(EXACT,EXACT));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        originals=[list(l.paths[0].nodes) for l in g.layers]
        g.layers[1].paths[0].fail_once=True
        with self.assertRaisesRegex(RuntimeError,'Injected'):run(f)
        for l,old in zip(g.layers,originals):
            self.assertEqual(l.paths[0].nodes,old);self.assertEqual(l.paths[0].nodes[-1].type,'curve')
            self.assertEqual(l.depth,0)
        self.assertEqual(f.undo.depth,0);self.assertEqual(f.events,['stop','start'])

    def test_cancel_before_commit_changes_nothing(self):
        g=glyph();f=Font([g]);f.selectedLayers=[g.layers[0]]
        job=steps(f);next(job);next(job);job.close()
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve');self.assertEqual(f.events,[])

    def test_edit_during_preparation_aborts(self):
        g=glyph();f=Font([g]);f.selectedLayers=[g.layers[0]];job=steps(f);next(job)
        g.layers[0].paths[0].nodes[1].position=Point(45,85)
        with self.assertRaisesRegex(ConversionError,'Path edited'):
            while True:next(job)
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve');self.assertEqual(f.events,[])

    def test_switch_font_while_preparing_aborts(self):
        g=glyph();f=Font([g]);f.selectedLayers=[g.layers[0]];active=[f]
        job=conversion_steps(f,Node,Point,CONSTANTS,active_font=lambda:active[0]);next(job)
        active[0]=None
        with self.assertRaisesRegex(ConversionError,'active font changed'):next(job)
        self.assertEqual(f.events,[])

    def test_closed_curve_across_start_index(self):
        g=glyph();l=g.layers[0];p=l.paths[0]
        p.closed=True;p.nodes=[node(0j,'curve'),node(80+120j,'offcurve'),node(-80+120j,'offcurve')]
        p.nodes=p.nodes[1:]+p.nodes[:1]
        f=Font([g]);f.selectedLayers=[l];run(f)
        self.assertTrue(validate_nodes(p.nodes,True,*CONSTANTS))
        self.assertEqual(sum(n.type!='offcurve' for n in p.nodes),1)

    def test_no_font_view_selection_does_not_touch_font(self):
        g=glyph();f=Font([g],edit=False)
        self.assertFalse(run(f))
        self.assertEqual(g.layers[0].paths[0].nodes[-1].type,'curve')

    def test_incomplete_node_selection_does_not_become_whole_glyph(self):
        g=glyph();l=g.layers[0];l.selection=[l.paths[0].nodes[0]]
        f=Font([g]);f.selectedLayers=[l]
        self.assertFalse(run(f));self.assertEqual(l.paths[0].nodes[-1].type,'curve')

if __name__=='__main__':unittest.main(verbosity=2)
