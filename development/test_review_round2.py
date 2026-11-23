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


if __name__=='__main__':unittest.main()
