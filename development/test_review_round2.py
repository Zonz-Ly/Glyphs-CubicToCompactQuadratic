"""Second review regressions and projection/constraint boundary cases."""
import unittest
from unittest.mock import patch

from search_core import Context
from tangent_constraints import optimize_constrained,on_ray
from merge_fit import fit_run_corresponding,try_merged_corresponding
from fast_fit import fit_corresponding,numeric_cache

class AlgorithmRegressions(unittest.TestCase):
    def setUp(self):numeric_cache().clear()

    def test_nearest_point_on_monotone_straight_cubic(self):
        for p in ((0j,0j,0j,1+0j),(0j,.01+0j,.02+0j,1+0j)):
            with self.subTest(p=p):
                point,t=Context(p).nearest(.1+0j)
                # This point belongs to the exact curve image [0,1].
                self.assertLessEqual(abs(point-(.1+0j)),1e-10)

    def test_parallel_overlapping_rays_retain_one_free_parameter(self):
        rays=((0j,1+0j),(10+0j,-1+0j))
        calls=[]
        def objective(values):
            calls.append(tuple(values))
            return abs(values[0]-7)**2
        controls=optimize_constrained([2+0j],rays,0j,10,objective,lambda:None)
        self.assertTrue(all(on_ray(controls[0],r) for r in rays))
        self.assertGreater(len(calls),0)
        self.assertLess(abs(controls[0]-7),1e-4)

    def test_infeasible_singleton_does_not_abort_feasible_partition(self):
        p0=(0j,16+0j,34+1j,50+1j)
        p1=(50+1j,66+1j,84+0j,100+0j)
        q=(100+0j,200+0j,100+100j)
        p2=(q[0],(q[0]+2*q[1])/3,(2*q[1]+q[2])/3,q[2])
        chain=(p0,p1,p2)
        rays=[((p0[0],1+0j),(p0[3],-1+0j)),
              ((p1[0],1+0j),(p1[3],-1+0j)),
              ((p2[0],1+0j),(p2[3],100-100j))]
        # Demonstrate the feasible solution using the actual numeric fitter.
        merged=try_merged_corresponding([chain[:2]],1.1,1,
            tangents=[(rays[0][0],rays[1][1])])
        self.assertIsNotNone(merged)
        self.assertLessEqual(merged[0]['error'][1],1.1)
        single=fit_corresponding([p2],1.1,1,tangents=[rays[2]])
        self.assertEqual(single[0]['parts'],[q])
        blocks=fit_run_corresponding([chain],1.1,1,join_tangents=[rays])
        self.assertEqual([(b['start'],b['count']) for b in blocks],[(0,2),(2,1)])



class ProjectionPrecisionTests(unittest.TestCase):
    def test_monotone_straight_samples_and_projection_are_geometric(self):
        from quad_fit import cubic
        from search_core import sample_norms,score_norms
        for source in ((0j,0j,0j,1+0j),(0j,.01+0j,.02+0j,1+0j),(0j,1+0j,0j,1+0j)):
            for scale in (1+0j,1024j):
                for reverse in (False,True):
                    p=tuple(2-3j+scale*z for z in source)
                    if reverse:p=p[::-1]
                    context=Context(p,count=33);chord=p[3]-p[0]
                    for i,(z,weight) in enumerate(context.samples):
                        self.assertLess(abs(z-(p[0]+chord*i/32)),abs(scale)*1e-11)
                    q=(p[0],(p[0]+p[3])/2,p[3])
                    self.assertLess(score_norms(sample_norms([q],context)),abs(scale)*1e-10)
                    for fraction in (.001,.1,.5,.99):
                        target=p[0]+fraction*chord;query=target+.2j*chord
                        point,t=context.nearest(query)
                        self.assertLess(abs(point-target),abs(scale)*1e-11)
                        self.assertEqual(point,cubic(p,t))

    def test_compound_arc_samples_invert_each_piece_parameter(self):
        from merge_fit import CompositeContext
        curves=((0j,0j,0j,1+0j),(1+0j,1.01+0j,1.02+0j,2+0j))
        context=CompositeContext(curves,count=65)
        for i,(point,weight) in enumerate(context.samples):self.assertLess(abs(point-2*i/64),1e-11)

    def test_failed_newton_retains_candidates_and_finds_point_on_curve(self):
        from quad_fit import cubic
        from segment_index import SegmentIndex
        import search_core as sc
        p=(0j,.01+.001j,.02-.001j,1+0j)
        # Force a coarse initial bracket to exercise the nonpositive-denominator
        # fallback independently of the adaptive line builder.
        line=[p[0],p[3]]
        context=Context(p,geometry=(line,[0.,1.],SegmentIndex(line)))
        z=cubic(p,.45)
        with patch.object(sc,'polynomial_roots_interval',wraps=sc.polynomial_roots_interval) as fallback:
            point,t=context.nearest(z)
        self.assertGreater(fallback.call_count,0)
        self.assertLess(abs(point-z),1e-11)

    def test_curved_loop_and_backtracking_point_queries(self):
        from quad_fit import cubic
        curves=((0j,2+2j,-1+2j,1+0j),(0j,3+0j,-2+0j,1+0j),
                (0j,1+1j,-1-1j,0j),(0j,0j,1j,1+0j))
        for p in curves:
            context=Context(p)
            for i in range(33):
                z=cubic(p,i/32);point,t=context.nearest(z)
                self.assertLess(abs(point-z),1e-10,msg=repr((p,i,t)))

    def test_constant_curve_has_finite_samples_and_projection(self):
        context=Context((1+2j,)*4)
        self.assertEqual(context.nearest(7+5j),(1+2j,0.))
        self.assertTrue(all(z==1+2j for z,weight in context.samples))


class ParallelConstraintTests(unittest.TestCase):
    def test_nearly_parallel_common_domain_keeps_both_ray_checks(self):
        rays=((0j,1+0j),(10+0j,1+1e-13j));calls=[]
        def objective(values):
            self.assertTrue(all(on_ray(values[0],ray) for ray in rays))
            calls.append(values[0]);return abs(values[0]-1e7)**2
        controls=optimize_constrained([12+0j],rays,0j,1e7,objective,lambda:None)
        self.assertTrue(calls);self.assertTrue(all(on_ray(controls[0],ray) for ray in rays))
        self.assertGreater(controls[0].real,12)

    def test_search_preserves_both_rays_at_interval_boundary(self):
        for rays,seed,target,boundary in (
            (((0j,1+0j),(10+0j,-1+0j)),2+0j,12+0j,10+0j),
            (((0j,1+0j),(10+0j,1+0j)),12+0j,7+0j,10+0j),
            (((2+1j,1j),(2+11j,-1j)),2+3j,2+8j,2+8j)):
            calls=[]
            def objective(values):
                self.assertTrue(all(on_ray(values[0],ray) for ray in rays),repr(values))
                calls.append(values[0]);return abs(values[0]-target)**2
            controls=optimize_constrained([seed],rays,rays[0][0],10,objective,lambda:None)
            self.assertTrue(calls);self.assertLess(abs(controls[0]-boundary),1e-4)

    def test_unique_intersection_still_skips_objective(self):
        rays=((0j,1+1j),(10+0j,-1+1j))
        result=optimize_constrained([2+1j],rays,0j,10,
            lambda values:self.fail('unique control has no free parameter'),lambda:None)
        self.assertEqual(result,[5+5j])


class PartitionAvailabilityTests(unittest.TestCase):
    def chain(self,cyclic=False):
        def line(a,b):return a,a+(b-a)/3,a+2*(b-a)/3,b
        return tuple(line(complex(i),complex((i+1)%3 if cyclic else i+1)) for i in range(3))

    def result(self):return [dict(parts=[(0j,1+0j,2+0j)],error=(0.,.1),within=True)]

    def test_unreachable_suffix_is_skipped_for_another_valid_partition(self):
        import merge_fit as mf
        from tangent_constraints import TangentConflict
        def one(curves,*args,**kwargs):
            if curves[0][0]!=0:raise TangentConflict()
            return self.result()
        def merged(chains,*args,**kwargs):
            return self.result() if len(chains[0])==2 else None
        with patch.object(mf,'fit_corresponding',one),patch.object(mf,'try_merged_corresponding',merged):
            blocks=mf.fit_run_corresponding([self.chain()],1,1)
        self.assertEqual([(b['start'],b['count']) for b in blocks],[(0,1),(1,2)])

    def test_infeasible_rotation_does_not_hide_feasible_wrapped_partition(self):
        import merge_fit as mf
        from tangent_constraints import TangentConflict
        def one(curves,*args,**kwargs):
            if curves[0][0]!=1:raise TangentConflict()
            return self.result()
        def merged(chains,*args,**kwargs):
            return self.result() if len(chains[0])==2 and chains[0][0][0]==2 else None
        with patch.object(mf,'fit_corresponding',one),patch.object(mf,'try_merged_corresponding',merged):
            blocks=mf.fit_run_corresponding([self.chain(True)],1,1,cyclic=True,angle_limit=180)
        self.assertEqual({(b['start'],b['count']) for b in blocks},{(1,1),(2,2)})

    def test_only_all_unavailable_complete_partitions_raise_conflict(self):
        import merge_fit as mf
        from tangent_constraints import TangentConflict
        for cyclic in (False,True):
            for length in (1,3):
                chain=self.chain(cyclic) if length==3 else ((0j,0j,0j,0j),)
                with patch.object(mf,'fit_corresponding',side_effect=TangentConflict()),patch.object(mf,'try_merged_corresponding',return_value=None):
                    with self.assertRaises(TangentConflict):mf.fit_run_corresponding([chain],1,1,cyclic=cyclic)

    def test_unrelated_errors_and_cancellation_propagate(self):
        import merge_fit as mf
        from concurrent.futures import CancelledError
        for error in (CancelledError,RuntimeError):
            with patch.object(mf,'fit_corresponding',side_effect=error('not a tangent conflict')):
                with self.assertRaises(error):mf.fit_run_corresponding([self.chain()[:1]],1,1)




class ConservativeProjectionTests(unittest.TestCase):
    def test_forward_pruning_matches_exhaustive_projection(self):
        import random
        from search_core import PreparedParts,forward_projection,unpack
        from geometry_fit import nearest_quadratic
        rng=random.Random(20261124)
        for _ in range(2000):
            p=tuple(complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(4))
            parts=PreparedParts(unpack(p,[rng.uniform(-1,1) for _ in range(2*rng.randint(1,6))]))
            for _ in range(10):
                z=complex(rng.uniform(-2,2),rng.uniform(-2,2))
                expected=min((nearest_quadratic(z,q)+(i,) for i,q in enumerate(parts)),key=lambda v:v[0])
                self.assertEqual(forward_projection(z,parts),expected)

    def test_same_distance_retains_original_index_after_bounds_sorting(self):
        from search_core import forward_projection
        from geometry_fit import nearest_quadratic
        parts=[(-1-1j,)*3,(1+1j,3+0j,1-1j)]
        expected=nearest_quadratic(0j,parts[0])+(0,)
        self.assertEqual(forward_projection(0j,parts),expected)

    def test_projection_margin_covers_extreme_query_scales(self):
        from search_core import PreparedParts,forward_projection
        from geometry_fit import nearest_quadratic
        parts=PreparedParts([(0j,1+1j,2+0j),(2+0j,3-1j,4+0j),(4+0j,4+0j,4+0j)])
        for z in (0j,1e-20+1e-20j,1e16+1j,-1e16+1e16j,4+1e-15j):
            expected=min((nearest_quadratic(z,q)+(i,) for i,q in enumerate(parts)),key=lambda v:v[0])
            self.assertEqual(forward_projection(z,parts),expected)

    def test_pruning_skips_only_impossible_root_queries(self):
        import search_core as sc
        parts=sc.PreparedParts([(0j,0j,0j),(100+0j,110+1j,120+0j),(-120+0j,-110+1j,-100+0j)])
        with patch.object(sc,'nearest_quadratic',wraps=sc.nearest_quadratic) as nearest:
            self.assertEqual(sc.forward_projection(0j,parts),(0.,0.,0))
        self.assertEqual(nearest.call_count,1)


class MergedUniqueControlTests(unittest.TestCase):
    def setUp(self):numeric_cache().clear()

    def curves_and_rays(self):
        from quad_fit import split
        p=(0j,33+53j,67+53j,100+0j)
        return split(p),((p[0],p[1]-p[0]),(p[3],p[2]-p[3]))

    def test_unique_merged_control_skips_search_and_unconstrained_cache(self):
        import merge_fit as mf
        from tangent_constraints import unique_tangent_control
        curves,rays=self.curves_and_rays();control=unique_tangent_control(rays)
        with patch.object(mf,'optimize_composite',side_effect=AssertionError('no free control')), \
             patch.object(mf,'CompositeContext',side_effect=AssertionError('no objective needed')):
            result=mf.fit_merged_count(curves,1,1.,{}, {},tangents=rays)
        self.assertEqual(result['parts'],[(curves[0][0],control,curves[-1][3])])
        self.assertTrue(result['within']);self.assertEqual(numeric_cache(),{})

    def test_different_rays_do_not_reuse_or_poison_unconstrained_solution(self):
        import merge_fit as mf
        curves,rays=self.curves_and_rays()
        first=mf.fit_merged_count(curves,1,1.,{}, {})
        before=dict(numeric_cache())
        for other in (rays,((0j,1+2j),(100+0j,-1+2j))):
            with patch.object(mf,'optimize_composite',side_effect=AssertionError('unique control')):
                result=mf.fit_merged_count(curves,1,1.,{}, {},tangents=other)
            self.assertTrue(all(on_ray(result['parts'][0][1],ray) for ray in other))
            self.assertEqual(numeric_cache(),before)
        self.assertEqual(mf.fit_merged_count(curves,1,1.,{}, {}),first)

    def test_integer_mode_retains_composite_search(self):
        import merge_fit as mf
        curves,rays=self.curves_and_rays()
        with patch.object(mf,'optimize_composite',wraps=mf.optimize_composite) as search:
            mf.fit_merged_count(curves,1,1.,{}, {},tangents=rays,integer_step=1)
        self.assertEqual(search.call_count,1)

    def test_parallel_mode_retains_composite_search(self):
        import merge_fit as mf
        curves,rays=self.curves_and_rays()
        with patch.object(mf,'optimize_composite',wraps=mf.optimize_composite) as search:
            mf.fit_merged_count(curves,1,1.,{}, {},tangents=((0j,1+0j),(100+0j,-1+0j)))
        self.assertEqual(search.call_count,1)

    def test_impossible_unique_intersection_rejects_before_search(self):
        import merge_fit as mf
        from tangent_constraints import TangentConflict
        curves,rays=self.curves_and_rays()
        with patch.object(mf,'optimize_composite',side_effect=AssertionError('infeasible unique control')):
            with self.assertRaises(TangentConflict):
                mf.fit_merged_count(curves,1,1.,{}, {},tangents=((0j,-1-1j),(100+0j,-1+1j)))


if __name__=='__main__':unittest.main()
