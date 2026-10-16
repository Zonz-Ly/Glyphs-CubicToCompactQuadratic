# -*- coding: utf-8 -*-
import sys,unittest
from unittest.mock import patch
from fast_fit import fit_corresponding
from merge_fit import try_merged_corresponding,fit_run_corresponding
from tangent_constraints import TangentConflict
from mock_glyphs import HARD,EXACT,Font,glyph
from test_merge import THREE
from test_entrypoints import modules,plugin_files,load,NSString
from i18n import TRANSLATIONS,tr

class SimplificationTests(unittest.TestCase):
    def choose(self,errors,tolerance=1,maximum=5,comparison_tolerance=None):
        curves=[(complex(i),)*4 for i in range(len(next(iter(errors.values()))))];calls=[]
        def fake(p,control_count,check_error,**kw):
            count=control_count;calls.append((int(p[0].real),count));error=errors[count][int(p[0].real)]
            return dict(parts=[(p[0],0j,p[-1])]*count,error=(error,error) if check_error else None,
                        within=error<=tolerance if check_error else None)
        def bounds(p,parts,*args,**kw):return (errors[len(parts)][int(p[0].real)],)*2
        with patch('fast_fit.fit',fake),patch('fast_fit.geometric_bounds',bounds):
            result=fit_corresponding(curves,tolerance,maximum,comparison_tolerance=comparison_tolerance)
        self.assertEqual(len(calls),len(set(calls)))
        return [len(r['parts']) for r in result],calls

    def test_first_passing_multi_result_compares_before_cap(self):
        counts,calls=self.choose({1:[1.35],2:[1.1],3:[.9]})
        self.assertEqual(counts,[1]);self.assertEqual(max(n for _,n in calls),3)

    def test_first_eligible_count_wins(self):
        counts,calls=self.choose({1:[2],2:[1.3],3:[.9]})
        self.assertEqual(counts,[2])

    def test_equal_to_reference_plus_margin_is_not_eligible(self):
        counts,calls=self.choose({1:[1.5],2:[2],3:[1]})
        self.assertEqual(counts,[3])

    def test_cap_prefers_fewest_eligible_over_lowest_error(self):
        counts,calls=self.choose({1:[2.4],2:[1.8],3:[2]},tolerance=.1,maximum=3,comparison_tolerance=1)
        self.assertEqual(counts,[1])

    def test_reference_stays_fixed_at_original_current_result(self):
        counts,calls=self.choose({1:[2.5],2:[2],3:[1.5],4:[1.1]},tolerance=1.2)
        self.assertEqual(counts,[3])

    def test_worst_master_is_compared_and_missing_fits_are_reused(self):
        counts,calls=self.choose({1:[1.2,1.8],2:[1.1,1.3],3:[.6,.9]})
        self.assertEqual(counts,[2,2]);self.assertIn((1,1),calls);self.assertIn((1,2),calls)

    def test_rejected_coarse_bounds_are_refined_for_comparison(self):
        def fake(p,control_count,check_error,**kw):
            error=(1.1,99) if control_count==1 else (.8,.8)
            return dict(parts=[(0j,0j,0j)]*control_count,error=error,within=control_count==2)
        with patch('fast_fit.fit',fake),patch('fast_fit.geometric_bounds',return_value=(1.1,1.2)) as bounds:
            result=fit_corresponding([HARD],1,4)
        self.assertEqual(len(result[0]['parts']),1);self.assertEqual(bounds.call_count,1)

    def test_impossible_smaller_counts_do_not_relax_constraints(self):
        def fake(p,control_count,**kw):
            if control_count<3:raise TangentConflict()
            return dict(parts=[(0j,0j,0j)]*3,error=(.5,.5),within=True)
        with patch('fast_fit.fit',fake):result=fit_corresponding([HARD,EXACT],1,5)
        self.assertEqual([len(r['parts']) for r in result],[3,3])

    def test_merged_simplification_preserves_full_tolerance_gate(self):
        calls=[]
        def fake(curves,count,tolerance,*args,**kw):
            calls.append(count);error=1.2 if count==1 else .9
            return dict(parts=[(0j,0j,0j)]*count,error=(error,error),within=error<=tolerance)
        with patch('merge_fit.fit_merged_count',fake):result=try_merged_corresponding([THREE],1,4)
        self.assertEqual(len(result[0]['parts']),2);self.assertEqual(calls,[1,2])

    def test_unmerged_fallback_uses_full_outline_tolerance_for_comparison(self):
        with patch('merge_fit.fit_corresponding',return_value=[]) as fit:
            fit_run_corresponding([(HARD,)],1.6,4,single_tolerance=.8)
        self.assertEqual(fit.call_args[0][1],.8)
        self.assertEqual(fit.call_args[1]['comparison_tolerance'],1.6)

    def test_all_languages_fit_single_line_labels_and_smaller_fields(self):
        root,res=plugin_files()
        for language in TRANSLATIONS['title']:
            with self.subTest(language=language):
                env=modules(Font([glyph()]));env['GlyphsApp'].Glyphs.localize=lambda texts:texts[language]
                with patch.dict(sys.modules,env):
                    engine=load(res/'Zonz_quad_engine.py','Zonz_quad_engine')
                    with patch.dict(sys.modules,{'Zonz_quad_engine':engine}):
                        m=load(res/'plugin.py','sizing_'+language.replace('-','_'))
                        p=m.ZonzCubicToQuadraticPlugin();p.settings();p.openSettings_(None)
                children=p._settings_panel.contentView().children
                for i in range(0,16,2):
                    label,control=children[i:i+2]
                    text=label.calls['setStringValue_'][0];frame=label.calls['initWithFrame_'][0]
                    needed=NSString(text).sizeWithAttributes_({}).width
                    self.assertGreaterEqual(frame[2]-needed,8)
                    self.assertFalse(label.calls['setWraps_'][0])
                    self.assertTrue(label.calls['setUsesSingleLineMode_'][0])
                    box=control.calls['initWithFrame_'][0]
                    self.assertGreaterEqual(box[0]-(frame[0]+frame[2]),12)
                    if i<8:self.assertEqual(box[2:],(22,22))

    def test_setting_labels_drop_units_and_chinese_particle(self):
        for key in ('deviation','center_limit','angle_limit'):
            self.assertTrue(all('(' not in s and '（' not in s for s in TRANSLATIONS[key].values()))
        self.assertEqual(tr('center_limit',language='zh-Hans'),'尝试居中贴线控制点范围')
        self.assertEqual(tr('center_limit',language='zh-Hant'),'嘗試居中貼線控制點範圍')

if __name__=='__main__':unittest.main(verbosity=2)
