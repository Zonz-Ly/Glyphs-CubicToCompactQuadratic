# -*- coding: utf-8 -*-
import ast,contextlib,io,math,plistlib,string,sys,unittest
from pathlib import Path as FilePath
from types import SimpleNamespace
from unittest.mock import patch
from mock_glyphs import *
from fast_fit import fit_corresponding
from glyphs_adapter import conversion_steps,build_path_plan,commit_plans,validate_nodes
from preferences import DEFAULT_SETTINGS,PREFERENCE_PREFIX,load_settings,save_settings,validated_settings
from i18n import TRANSLATIONS,tr
from quad_fit import quadratic
from test_entrypoints import modules,plugin_files,load

def finish(job):
    while True:
        try:next(job)
        except StopIteration as done:return done.value

class VersionOneTests(unittest.TestCase):
    def test_defaults_and_atomic_invalid_save(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        self.assertEqual(load_settings(app),DEFAULT_SETTINGS)
        for value in ('',0,-1,float('nan'),float('inf'),'bad'):
            before=dict(app.defaults)
            with self.assertRaises(ValueError):save_settings(app,deviation=value)
            self.assertEqual(app.defaults,before)
        saved=save_settings(app,deviation=.25,max_controls=1,add_midpoint=True)
        self.assertEqual(load_settings(app),saved)
        self.assertEqual(DEFAULT_SETTINGS['deviation'],1)

    def test_corrupt_stored_settings_fall_back(self):
        app=modules(Font([glyph()]))['GlyphsApp'].Glyphs
        app.defaults[PREFERENCE_PREFIX+'deviation']='nan'
        self.assertEqual(load_settings(app),DEFAULT_SETTINGS)

    def test_all_translations_and_placeholders(self):
        formatter=string.Formatter()
        expected={'en','zh-Hans','zh-Hant','ja','ko','de','fr','es','it','pt','ru'}
        for key,variants in TRANSLATIONS.items():
            self.assertEqual(set(variants),expected,key)
            fields={f for _,f,_,_ in formatter.parse(variants['en']) if f}
            for lang,text in variants.items():
                self.assertTrue(text.strip(),key+lang)
                self.assertEqual({f for _,f,_,_ in formatter.parse(text) if f},fields,key+lang)
                tr(key,language=lang,**{f:3 for f in fields})
        self.assertEqual(tr('title',language='zh-Hant-TW'),'轉換為精簡的二次曲線')
        self.assertEqual(tr('title',language='zh_TW'),'轉換為精簡的二次曲線')
        self.assertEqual(tr('title',language='unknown'),TRANSLATIONS['title']['en'])

    def test_runtime_language_uses_glyphs_locale(self):
        env=modules(Font([glyph()]))
        app=env['GlyphsApp'].Glyphs
        def localize(values):
            for lang in app.defaults['AppleLanguages']:
                while True:
                    if lang in values:return values[lang]
                    if '-' not in lang:break
                    lang=lang.rsplit('-',1)[0]
            return values['en']
        app.localize=localize
        with patch.dict(sys.modules,env):
            for lang in ('zh-Hant-TW','zh-CN','ja-JP','ko-KR','de-DE','fr-FR','es-ES','it-IT','pt-BR','ru-RU'):
                app.defaults['AppleLanguages']=[lang]
                self.assertEqual(tr('title'),tr('title',language=lang))

    def test_only_one_skips_every_pair_search(self):
        with patch('fast_fit.optimize_pair',side_effect=AssertionError('pair search was called')):
            results=fit_corresponding([EXACT,PAIR_NEEDED],tolerance=.5,max_controls=1)
        self.assertEqual([len(r['parts']) for r in results],[1,1])
        self.assertIsNone(results[1]['error'])

    def test_one_only_over_target_is_applied_in_all_masters(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        r=finish(conversion_steps(f,Node,Point,CONSTANTS,max_controls=1,add_midpoint=True))
        self.assertTrue(r)
        self.assertTrue(all([n.type for n in l.paths[0].nodes]==['line','offcurve','qcurve'] for l in g.layers))
        self.assertTrue(g.mastersCompatible)

    def test_explicit_midpoint_keeps_coordinates_and_selection(self):
        for explicit in (False,True):
            g=glyph(sources=(EXACT,PAIR_NEEDED));f=Font([g],2);l=g.layers[1]
            l.selection=l.paths[0].nodes[1:3];f.selectedLayers=[l]
            r=finish(conversion_steps(f,Node,Point,CONSTANTS,add_midpoint=explicit))
            for layer in g.layers:
                nodes=layer.paths[0].nodes
                expected=['line','offcurve','qcurve','offcurve','qcurve'] if explicit else ['line','offcurve','offcurve','qcurve']
                self.assertEqual([n.type for n in nodes],expected)
                if explicit:
                    midpoint=nodes[2]
                    self.assertTrue(midpoint.smooth)
                    self.assertEqual(midpoint.position.x,(nodes[1].position.x+nodes[3].position.x)/2)
                    self.assertEqual(midpoint.position.y,(nodes[1].position.y+nodes[3].position.y)/2)
            self.assertEqual(len(l.selection),3 if explicit else 2)
            self.assertTrue(r);self.assertEqual(f.undo.groups,1)
            self.assertTrue(g.mastersCompatible)

    def test_explicit_and_implicit_fit_are_same_curve(self):
        results=fit_corresponding([PAIR_NEEDED],tolerance=.5)
        original=path(PAIR_NEEDED)
        implicit=build_path_plan(original,{0:results[0]},Node,Point,CONSTANTS,set())
        explicit=build_path_plan(original,{0:results[0]},Node,Point,CONSTANTS,set(),add_midpoint=True)
        a=implicit['output'];b=explicit['output']
        z=lambda n:complex(n.position.x,n.position.y)
        self.assertEqual([z(n) for n in a],[z(n) for n in b if n is not b[2]])
        parts=results[0]['parts']
        explicit_parts=[tuple(z(n) for n in b[:3]),tuple(z(n) for n in b[2:])]
        for q,r in zip(parts,explicit_parts):
            for i in range(101):self.assertLess(abs(quadratic(q,i/100)-quadratic(r,i/100)),1e-12)

    def test_closed_wrap_explicit_midpoint(self):
        p=path(PAIR_NEEDED);p.closed=True;p.nodes=p.nodes[1:]+p.nodes[:1]
        # The original source cubic crosses node zero.
        result=fit_corresponding([PAIR_NEEDED],tolerance=.5)[0]
        plan=build_path_plan(p,{3:result},Node,Point,CONSTANTS,set(),add_midpoint=True)
        overrides={plan['output'].index(n):t for n,t in plan['types']}
        self.assertTrue(validate_nodes(plan['output'],True,*CONSTANTS,overrides=overrides))
        self.assertEqual(sum(n.type==CONSTANTS[2] for n in plan['new']),1)

    def test_explicit_write_failure_restores_every_master(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        originals=[list(l.paths[0].nodes) for l in g.layers]
        g.layers[1].paths[0].fail_once=True
        with self.assertRaisesRegex(RuntimeError,'Injected'):
            finish(conversion_steps(f,Node,Point,CONSTANTS,add_midpoint=True))
        for layer,old in zip(g.layers,originals):
            self.assertEqual(layer.paths[0].nodes,old)
            self.assertEqual(layer.paths[0].nodes[-1].type,'curve')
        self.assertEqual(f.undo.depth,0)

    def test_invalid_job_settings_do_not_touch_font(self):
        g=glyph();f=Font([g]);f.selectedLayers=[g.layers[0]]
        with self.assertRaises(ValueError):finish(conversion_steps(f,Node,Point,CONSTANTS,tolerance=0))
        self.assertEqual(f.events,[])

    def test_settings_panel_autosaves_and_retains_values_after_reopening(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        root,res=plugin_files();env=modules(f);app=env['GlyphsApp'].Glyphs
        with patch.dict(sys.modules,env):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','quad_plugin_settings');p=m.ZonzCubicToQuadraticPlugin()
                p.settings();p.start();p.openSettings_(None)
                self.assertEqual(p._deviation_field.stringValue(),'1')
                self.assertEqual(p._count_field.stringValue(),'3')
                p._deviation_field.setStringValue_('0,25');p.changeSetting_(p._deviation_field)
                self.assertEqual(engine.load_settings(app)['deviation'],.25)
                p._deviation_field.setStringValue_('nan');before=dict(app.defaults)
                p.changeSetting_(p._deviation_field);self.assertEqual(app.defaults,before)
                p.controlTextDidEndEditing_(SimpleNamespace(object=lambda:p._deviation_field))
                self.assertEqual(p._deviation_field.stringValue(),'0.25')
                p._count_field.setStringValue_('1');p.changeSetting_(p._count_field)
                p._settings_panel.close();p.openSettings_(None)
                self.assertEqual(p._deviation_field.stringValue(),'0.25')
                fresh=m.ZonzCubicToQuadraticPlugin();fresh.settings();fresh.openSettings_(None)
                self.assertEqual(fresh._count_field.stringValue(),'1')
                fresh.convert_(None)
                while fresh._busy:fresh.advance_(fresh._timer)
                self.assertTrue(all(len(l.paths[0].nodes)==3 for l in g.layers))

    def test_plugin_saved_explicit_midpoint_native_probe(self):
        g=glyph(sources=(EXACT,PAIR_NEEDED));f=Font([g],2);f.selectedLayers=[g.layers[0]]
        root,res=plugin_files();env=modules(f);app=env['GlyphsApp'].Glyphs
        with patch.dict(sys.modules,env),contextlib.redirect_stdout(io.StringIO()):
            engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
            with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                m=load(res/'plugin.py','quad_plugin_explicit');p=m.ZonzCubicToQuadraticPlugin()
                p.settings();engine.save_settings(app,deviation=1,max_controls=2,center_limit=0,merge_curves=False,integer_coords=False,angle_limit=2,keep_line_tangent=False,add_midpoint=True)
                p.convert_(None)
                for _ in range(20):
                    if not p._busy:break
                    p.advance_(p._timer)
                self.assertFalse(p._busy)
        self.assertTrue(all([n.type for n in l.paths[0].nodes]==['line','offcurve','qcurve','offcurve','qcurve'] for l in g.layers))

    def test_metadata_author_version_and_entry_class(self):
        root,res=plugin_files()
        info=plistlib.loads((root/'CubicToCompactQuadratic.glyphsPlugin/Contents/Info.plist').read_bytes())
        self.assertEqual(info['CFBundleShortVersionString'],'1.0')
        self.assertEqual(info['NSPrincipalClass'],'ZonzCubicToQuadraticPlugin')
        self.assertEqual(info['CFBundleIdentifier'],'com.Zonz.CubicToQuadratic')
        self.assertIn('Zonz',info['NSHumanReadableCopyright'])
        for p in [root/'CubicToCompactQuadratic.py',res/'plugin.py',res/'Zonz_quad_engine.py']:
            ast.parse(p.read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main(verbosity=2)
