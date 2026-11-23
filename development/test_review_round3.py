"""Third review regressions; preserve every existing fitting search."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from chain_fit import arc_times
from search_core import Context
from quad_fit import cubic
from fast_fit import fit

class NewRegressions(unittest.TestCase):
    def test_arc_length_seed_uses_chord_parameter_inversion(self):
        p=(0j,.01+0j,.02+0j,1+0j)
        times=arc_times(Context(p),3)
        for i,t in enumerate(times):
            self.assertLess(abs(cubic(p,t)-i/3),1e-12)

    def test_auto_degree_reduction_retries_two_controls_after_tangent_conflict(self):
        q=(0j,50+.1j,100+0j)
        p=(q[0],(q[0]+2*q[1])/3,(2*q[1]+q[2])/3,q[2])
        rays=((0j,1+.001j),(100+0j,-1-.001j))
        pair=fit(p,policy='pair',tangents=rays)
        self.assertTrue(pair['within'])
        automatic=fit(p,policy='auto',tangents=rays)
        self.assertEqual(len(automatic['parts']),2)
        self.assertTrue(automatic['within'])



class ArcSeedQualityTests(unittest.TestCase):
    def test_arc_knots_track_geometry_under_transforms_and_reversal(self):
        for scale in (1+0j,1024j):
            for reverse in (False,True):
                p=tuple(2-3j+scale*z for z in (0j,.01+0j,.02+0j,1+0j))
                if reverse:p=p[::-1]
                context=Context(p)
                for count in (2,3,7):
                    times=arc_times(context,count)
                    self.assertEqual((times[0],times[-1]),(0,1))
                    for i,t in enumerate(times):
                        self.assertLess(abs(cubic(p,t)-(p[0]+(p[3]-p[0])*i/count)),abs(scale)*1e-11)

    def test_degenerate_curve_keeps_uniform_knots(self):
        self.assertEqual(arc_times(Context((2+3j,)*4),3),[0,1/3,2/3,1])

    def test_legacy_fine_refinement_cannot_be_displaced_by_new_seed(self):
        import chain_fit as cf
        coarse={0:.2,2:.3,3:.01,10:.1,13:.001}
        fine={0:.2,2:.3,3:.015,10:.04,13:.02,20:.005,23:.01}
        calls=[]
        def context(p,count,**kwargs):return SimpleNamespace(count=count,geometry=None)
        def knots(c,count,legacy=False):return [0,1/3,2/3,1] if legacy else [0,.2,.7,1]
        def seed(p,times):return [0] if times[1]==1/3 else [3]
        def refine(p,x,c,iterations):
            calls.append((x[0],iterations))
            if iterations==14:return ([10],.1) if x==[0] else ([13],.001)
            return ([20],.005) if x==[10] else ([23],.01)
        with patch.object(cf,'Context',side_effect=context),patch.object(cf,'arc_times',side_effect=knots), \
             patch.object(cf,'subdivision_seed',side_effect=seed),patch.object(cf,'least_squares_seed',return_value=[2]), \
             patch.object(cf,'unpack',side_effect=lambda p,x:x),patch.object(cf,'score_norms',side_effect=lambda x:x), \
             patch.object(cf,'sample_norms',side_effect=lambda x,c:(fine if c.count==97 else coarse)[x[0]]), \
             patch.object(cf,'refine_lm',side_effect=refine):
            parts,unused=cf.optimize_chain((0j,)*4,3)
        self.assertEqual(parts,[20])
        self.assertEqual(calls,[(0,14),(10,5),(3,14),(3,5)])


class ExactAutoFallbackTests(unittest.TestCase):
    def curve(self):
        q=(0j,50+.1j,100+0j)
        return q[0],(q[0]+2*q[1])/3,(2*q[1]+q[2])/3,q[2]

    def test_fixed_single_still_reports_conflict(self):
        from tangent_constraints import TangentConflict
        rays=((0j,1+.001j),(100+0j,-1-.001j))
        with self.assertRaises(TangentConflict):fit(self.curve(),policy='single',tangents=rays)

    def test_auto_pair_matches_explicit_pair_without_generic_search(self):
        import fast_fit as ff
        p=self.curve();rays=((0j,1+.001j),(100+0j,-1-.001j))
        expected=fit(p,policy='pair',tangents=rays)
        with patch.object(ff,'optimize_pair',side_effect=AssertionError('exact degree reduction available')):
            got=fit(p,policy='auto',tangents=rays)
        self.assertEqual(got['parts'],expected['parts']);self.assertEqual(got['error'],expected['error'])

    def test_auto_retries_after_single_fails_continuous_validation(self):
        import fast_fit as ff
        original=ff.adjust_parts
        def prepare(curves,parts,*args,**kwargs):
            return [(parts[0][0],50+100j,parts[0][2])] if len(parts)==1 else original(curves,parts,*args,**kwargs)
        with patch.object(ff,'adjust_parts',side_effect=prepare):got=fit(self.curve(),policy='auto')
        self.assertEqual(len(got['parts']),2);self.assertTrue(got['within'])
        self.assertGreater(got['single_error'][0],.5)

    def test_auto_only_catches_single_tangent_conflicts(self):
        import fast_fit as ff
        from tangent_constraints import TangentConflict
        from concurrent.futures import CancelledError
        counts=[]
        def conflict(curves,parts,*args,**kwargs):counts.append(len(parts));raise TangentConflict()
        with patch.object(ff,'adjust_parts',side_effect=conflict):
            with self.assertRaises(TangentConflict):fit(self.curve(),policy='auto')
        self.assertEqual(counts,[1,2])
        for error in (RuntimeError,CancelledError):
            with patch.object(ff,'adjust_parts',side_effect=error()):
                with self.assertRaises(error):fit(self.curve(),policy='auto')



class FeasibilityPruningTests(unittest.TestCase):
    def test_impossible_parallel_single_skips_unconstrained_search(self):
        import fast_fit as ff
        from tangent_constraints import TangentConflict
        p=(0j,30j,100+30j,100+0j);rays=((p[0],p[1]-p[0]),(p[3],p[2]-p[3]))
        with patch.object(ff,'optimize_one',side_effect=AssertionError('infeasible rays')):
            with self.assertRaises(TangentConflict):ff.fit(p,policy='single',tangents=rays)

    def test_impossible_parallel_merged_control_skips_unconstrained_search(self):
        import merge_fit as mf
        from quad_fit import split
        from tangent_constraints import TangentConflict
        p=(0j,30j,100+30j,100+0j);rays=((p[0],p[1]-p[0]),(p[3],p[2]-p[3]))
        with patch.object(mf,'optimize_composite',side_effect=AssertionError('infeasible rays')):
            with self.assertRaises(TangentConflict):mf.fit_merged_count(split(p),1,.5,{}, {},tangents=rays)

    def test_feasible_parallel_domain_keeps_search(self):
        import fast_fit as ff
        from search_core import numeric_cache
        p=(0j,30j,100+30j,100+0j);numeric_cache().clear()
        with patch.object(ff,'optimize_one',wraps=ff.optimize_one) as search:
            result=ff.fit(p,policy='single',tangents=((0j,1+0j),(100+0j,-1+0j)))
        self.assertEqual(search.call_count,1)
        self.assertEqual(result['parts'][0][1].imag,0)

    def test_integer_cells_can_be_feasible_with_disjoint_exact_rays(self):
        import fast_fit as ff
        from tangent_constraints import on_ray
        p=(0j,3+1j,7+1j,10+.5j);rays=((0j,1+0j),(10+.5j,-1+0j))
        with patch.object(ff,'unique_tangent_control',side_effect=AssertionError('float-only shortcut')):
            result=ff.fit(p,policy='single',tangents=rays,integer_step=1)
        self.assertTrue(all(on_ray(result['parts'][0][1],ray,1) for ray in rays))


class PartitionSuffixPruningTests(unittest.TestCase):
    def chain(self,length):
        return tuple((complex(i),complex(i+1/3),complex(i+2/3),complex(i+1)) for i in range(length))

    def test_all_unreachable_suffixes_fit_only_intervals_ending_at_end(self):
        import merge_fit as mf
        from tangent_constraints import TangentConflict
        calls=[]
        def single(curves,*args,**kwargs):calls.append((int(curves[0][0].real),1));raise TangentConflict()
        def merged(chains,*args,**kwargs):calls.append((int(chains[0][0][0].real),len(chains[0])));return None
        with patch.object(mf,'fit_corresponding',single),patch.object(mf,'try_merged_corresponding',merged):
            with self.assertRaises(TangentConflict):mf.fit_run_corresponding([self.chain(12)],1,3)
        self.assertEqual(len(calls),12)
        self.assertEqual(set(calls),{(start,12-start) for start in range(12)})

    def test_unreachable_transition_skips_still_check_cancellation(self):
        import merge_fit as mf
        from tangent_constraints import TangentConflict
        from concurrent.futures import CancelledError
        cancelled=[False]
        def single(*args,**kwargs):cancelled[0]=True;raise TangentConflict()
        with patch.object(mf,'fit_corresponding',single),patch.object(mf,'try_merged_corresponding',return_value=None):
            with self.assertRaises(CancelledError):mf.fit_run_corresponding([self.chain(3)],1,1,cancel=lambda:cancelled[0])



class BoundedIntegerScoreTests(unittest.TestCase):
    def test_completed_scores_are_exact_and_rejections_cannot_win(self):
        import random,math
        from search_core import bounded_score,sample_norms,score_norms,unpack
        rng=random.Random(57079);rejected=0
        for _ in range(15):
            p=tuple(complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(4))
            context=Context(p,count=17,reverse_count=9)
            for _ in range(20):
                parts=unpack(p,[rng.uniform(-1,1) for _ in range(2*rng.randint(1,4))])
                full=score_norms(sample_norms(parts,context))
                self.assertEqual(bounded_score(parts,context,float('inf')),full)
                for limit in (full,math.nextafter(full,float('inf')),full*rng.uniform(.2,1.8)):
                    value=bounded_score(parts,context,limit)
                    if value is None:self.assertGreaterEqual(full,limit);rejected+=1
                    else:self.assertEqual(value,full)
        self.assertGreater(rejected,0)

    def test_forward_lower_bound_can_skip_all_reverse_queries(self):
        from search_core import bounded_score
        context=SimpleNamespace(samples=[(100j,1/8)]*8,reverse_count=5,
                                nearest=lambda z:self.fail('cannot win before reverse queries'))
        self.assertIsNone(bounded_score([(0j,0j,1+0j)],context,1))

    def test_completed_reverse_normalization_matches_full_score(self):
        from search_core import bounded_score,sample_norms,score_norms
        p=(0j,.3+.7j,.9-.2j,1+0j);context=Context(p,count=9,reverse_count=17)
        parts=[(0j,.2+1j,.5+.5j),(.5+.5j,.8+0j,1+0j)]
        full=score_norms(sample_norms(parts,context))
        self.assertEqual(bounded_score(parts,context,full*10),full)

    def test_bounded_comparison_keeps_cancellation(self):
        from search_core import bounded_score
        from concurrent.futures import CancelledError
        def check():raise CancelledError()
        with self.assertRaises(CancelledError):bounded_score([(0j,0j,1+0j)],Context((0j,.1j,.2j,1+0j)),1,check)

    def test_single_controls_and_constrained_fits_keep_full_objective(self):
        import options_fit as of,fast_fit as ff,merge_fit as mf
        p=(0j,30+120j,180+10j,220+0j)
        curves=((0j,16+0j,34+1j,50+1j),(50+1j,66+1j,84+0j,100+0j))
        with patch.object(of,'bounded_score',side_effect=AssertionError('full-score-only route')):
            ff.fit(p,policy='single',integer_step=1)
            ff.fit(p,policy='pair',integer_step=1,tangents=((p[0],p[1]-p[0]),(p[3],p[2]-p[3])))
            mf.fit_merged_count(curves,1,1,{}, {},integer_step=1)

    def test_rejected_partial_results_do_not_enter_complete_score_cache(self):
        import options_fit as of
        from collections import Counter
        counts=Counter()
        def bounded(parts,context,limit,check):
            key=tuple(q[1] for q in parts);counts[key]+=1
            return .5 if key==(-.1+0j,1+0j) else None
        p=(0j,3+0j,7+0j,10+0j);parts=[(0j,0j,5+0j),(5+0j,10+0j,10+0j)]
        with patch.object(of,'bounded_score',side_effect=bounded),patch.object(of,'sample_norms',return_value=[(1.,1.)]):
            result=of.adjust_parts([p],parts,.5,integer_step=1,context_factory=lambda curves:object())
        self.assertEqual([q[1] for q in result],[-1+0j,10+0j])
        self.assertTrue(any(times>=2 for key,times in counts.items() if key[0].imag))


if __name__=='__main__':unittest.main()
