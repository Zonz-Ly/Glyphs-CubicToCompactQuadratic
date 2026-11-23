"""Regressions from the algorithm review; no native Glyphs dependency."""
import random
import unittest
from unittest.mock import patch

from geometry_fit import geometric_bounds
from quad_fit import single_l2
import merge_fit


class ReviewCorrectnessTests(unittest.TestCase):
    def test_small_tolerance_accepts_near_degree_reduction(self):
        p=(0j,(100+200j)/3+1e-6j,(200+200j)/3,100+0j)
        bounds=geometric_bounds(p,[single_l2(p)],1e-5)
        self.assertLessEqual(bounds[1],1e-5)

    def check_partition(self, costs, length, cyclic=False):
        def line(a,b):return (a,a+(b-a)/3,a+2*(b-a)/3,b)
        chain=tuple(line(complex(i),complex((i+1)%length if cyclic else i+1)) for i in range(length))
        def merged(chains,*args,**kwargs):
            key=(int(chains[0][0][0].real),len(chains[0]))
            if key not in costs:return None
            error,controls=costs[key]
            return [dict(parts=[(0j,0j,0j)]*controls,error=(error,error))]
        def single(*args,**kwargs):return [dict(parts=[(0j,0j,0j)],error=(0,0))]
        def score(blocks):
            return (len(blocks),max([costs[(s,c)][0] for s,c in blocks if c>1]+[0]),
                    sum(costs[(s,c)][1] if c>1 else 1 for s,c in blocks))
        def enumerate_parts(rotation,offset=0):
            if offset==length:yield [];return
            for count in range(1,length-offset+1):
                start=(rotation+offset)%length
                if count>1 and (start,count) not in costs:continue
                for tail in enumerate_parts(rotation,offset+count):yield [(start,count)]+tail
        optimum=min(score(p) for r in range(length if cyclic else 1) for p in enumerate_parts(r))
        with patch.object(merge_fit,'try_merged_corresponding',merged),patch.object(merge_fit,'fit_corresponding',single):
            got=merge_fit.fit_run_corresponding([chain],tolerance=1,max_controls=3,cyclic=cyclic,angle_limit=180)
        blocks=[(b['start'],b['count']) for b in got]
        self.assertEqual(score(blocks),optimum)
        self.assertEqual(sum(c for s,c in blocks),length)

    def test_masked_suffix_error_does_not_discard_fewer_controls(self):
        self.check_partition({(0,2):(.5,1),(2,2):(.2,1),(3,2):(.1,3)},5)

    def test_partition_matches_exhaustive_open_and_closed_search(self):
        rng=random.Random(509)
        for cyclic in (False,True):
            for length in range(3,8):
                for _ in range(12):
                    costs={(s,c):(rng.choice([.1,.2,.5]),rng.randint(1,3))
                           for s in range(length) for c in range(2,length)
                           if (cyclic or s+c<=length) and rng.random()<.6}
                    with self.subTest(cyclic=cyclic,length=length,costs=costs):
                        self.check_partition(costs,length,cyclic)


class ReviewRedundancyTests(unittest.TestCase):
    def test_precomputed_quadratic_queries_preserve_arithmetic(self):
        from geometry_fit import nearest_quadratic,quadratic_coefficients
        from roots_unit import polynomial_roots_unit
        from quad_fit import dot
        rng=random.Random(509)
        curves=[(0j,0j,0j),(0j,1+0j,2+0j),(0j,1e-14j,1e-14+0j)]
        curves += [tuple(complex(rng.uniform(-2,2),rng.uniform(-2,2)) for _ in range(3)) for _ in range(30)]
        for q in curves:
            for _ in range(65):
                z=complex(rng.uniform(-3,3),rng.uniform(-3,3))
                a=q[0]-z;b=2*(q[1]-q[0]);c=q[0]-2*q[1]+q[2]
                coefficients=(dot(a,b),dot(b,b)+2*dot(a,c),3*dot(b,c),2*dot(c,c))
                t=min([0.,1.]+polynomial_roots_unit(coefficients),key=lambda t:abs(a+b*t+c*t*t))
                self.assertEqual(nearest_quadratic(z,list(q)),(abs(a+b*t+c*t*t),t))
        self.assertLessEqual(quadratic_coefficients.cache_info().currsize,256)

    def test_flatten_intermediates_do_not_build_indexes(self):
        import geometry_fit as gf
        from quad_fit import split
        p=(0j,30+120j,180+10j,220+0j);parts=[single_l2(q) for q in split(p)]
        with patch.object(gf,'IndexedLine',wraps=gf.IndexedLine) as index:
            gf.geometric_bounds(p,parts,.5,source_curves=split(p))
        self.assertEqual(index.call_count,2)

    def test_single_seed_deduplicates_after_selection(self):
        import geometry_fit as gf
        p=(0j,1j,1+1j,1+0j)
        with patch.object(gf,'single_l2',return_value=(0j,1j,1+0j)), \
             patch.object(gf,'single_weighted',return_value=(0j,1j,1+0j)), \
             patch.object(gf,'intersection',return_value=(0j,2j,1+0j)), \
             patch.object(gf,'sampled_objective',side_effect=lambda parts,*args:abs(parts[0][1])), \
             patch.object(gf,'nelder_mead',return_value=(1,[0,1])) as search:
            gf.optimize_one(p,None)
        self.assertEqual(search.call_count,1)

    def test_unique_tangent_control_skips_search_and_context(self):
        import fast_fit as ff
        import options_fit as of
        from tangent_constraints import project_controls
        p=(0j,33+66j,66.5+67j,100+0j)
        rays=((p[0],p[1]-p[0]),(p[3],p[2]-p[3]))
        parts=[(p[0],project_controls([single_l2(p)[1]],rays)[0],p[3])]
        expected=geometric_bounds(p,parts,.5)
        with patch.object(ff,'optimize_one',side_effect=AssertionError('unnecessary search')), \
             patch.object(ff,'Context',side_effect=AssertionError('unnecessary context')), \
             patch.object(of,'sample_norms',side_effect=AssertionError('unnecessary objective')):
            got=ff.fit(p,policy='single',tangents=rays)
        self.assertEqual(got['parts'],parts);self.assertEqual(got['error'],expected)
        self.assertTrue(got['within'])

    def test_infeasible_tangents_reject_before_search(self):
        import fast_fit as ff
        from tangent_constraints import TangentConflict
        p=(0j,33+66j,66.5+67j,100+0j)
        for rays in (((0j,-1-1j),(100+0j,-1+1j)),((0j,0j),(100+0j,1j))):
            with patch.object(ff,'optimize_one',side_effect=AssertionError('unnecessary search')):
                with self.assertRaises(TangentConflict):ff.fit(p,policy='single',tangents=rays)

    def test_integer_tangents_still_search(self):
        import fast_fit as ff
        p=(0j,33+66j,66.5+67j,100+0j);ff.numeric_cache().clear()
        rays=((p[0],p[1]-p[0]),(p[3],p[2]-p[3]))
        with patch.object(ff,'single_parameter_bound',return_value=float('inf')), \
             patch.object(ff,'unique_tangent_control',side_effect=AssertionError('integer rays are not unique')), \
             patch.object(ff,'optimize_one',wraps=ff.optimize_one) as search:
            ff.fit(p,policy='single',tangents=rays,integer_step=1)
        self.assertEqual(search.call_count,1)

    def test_corresponding_counts_share_source_validation_cache(self):
        import fast_fit as ff
        from mock_glyphs import HARD
        caches=[];original=ff.fit
        def compute(*args,**kwargs):
            caches.append(kwargs['source_cache']);return original(*args,**kwargs)
        with patch.object(ff,'fit',side_effect=compute):
            ff.fit_corresponding([HARD],tolerance=.01,max_controls=3)
        self.assertGreaterEqual(len(caches),2)
        self.assertTrue(all(cache is caches[0] for cache in caches))
        self.assertTrue(caches[0])


class ReviewAcceptanceTests(unittest.TestCase):
    def test_parameter_bound_covers_sampled_error_with_adjusted_controls(self):
        from geometry_fit import single_parameter_bound
        from quad_fit import cubic,quadratic
        import math
        rng=random.Random(20261123)
        times=[i/100 for i in range(101)]+[(3-math.sqrt(3))/6,(3+math.sqrt(3))/6]
        for scale,origin in ((1,0j),(1000,1e6+2e6j),(.0001,2-3j)):
            for _ in range(20):
                p=tuple(origin+scale*complex(rng.uniform(-2,2),rng.uniform(-2,2)) for _ in range(4))
                q=single_l2(p);q=(q[0],q[1]+scale*complex(.1,-.2),q[2])
                bound=single_parameter_bound(p,q)
                for t in times:self.assertLessEqual(abs(cubic(p,t)-quadratic(q,t)),bound)

    def test_passing_seed_skips_search_in_float_and_integer_modes(self):
        import fast_fit as ff
        p=(0j,33+66j,66.5+67j,100+0j)
        for step in (0,1):
            with patch.object(ff,'optimize_one',side_effect=AssertionError('unnecessary search')):
                result=ff.fit(p,policy='single',integer_step=step)
            self.assertTrue(result['within'])
            independent=geometric_bounds(p,result['parts'],.5)
            self.assertLessEqual(independent[1],.5)
            if step:self.assertTrue(all(z.real.is_integer() and z.imag.is_integer() for q in result['parts'] for z in q))

    def test_failed_proof_falls_back_to_search(self):
        import fast_fit as ff
        from mock_glyphs import HARD
        ff.numeric_cache().clear()
        with patch.object(ff,'optimize_one',wraps=ff.optimize_one) as search:
            result=ff.fit(HARD,policy='single')
        self.assertEqual(search.call_count,1)
        self.assertIsNotNone(result['error'])

    def test_adjusted_seed_must_pass_proof(self):
        import fast_fit as ff
        p=(0j,33+66j,66.5+67j,100+0j);ff.numeric_cache().clear()
        # A large control movement invalidates the cheap proof even though the
        # original L2 candidate passes. The full optimizer must still run.
        def moved(curves,parts,*args,**kwargs):return [(p[0],1000j,p[3])]
        with patch.object(ff,'adjust_parts',side_effect=moved),patch.object(ff,'optimize_one',wraps=ff.optimize_one) as search:
            result=ff.fit(p,policy='single')
        self.assertEqual(search.call_count,1);self.assertFalse(result['within'])

    def test_infeasible_cheap_lattice_seed_falls_back_to_full_search(self):
        import fast_fit as ff
        from tangent_constraints import TangentConflict
        p=(0j,33+66j,66.5+67j,100+0j);ff.numeric_cache().clear()
        original=ff.adjust_parts;calls=[]
        def prepare(*args,**kwargs):
            calls.append(args)
            if len(calls)==1:raise TangentConflict()
            return original(*args,**kwargs)
        with patch.object(ff,'adjust_parts',side_effect=prepare),patch.object(ff,'optimize_one',wraps=ff.optimize_one) as search:
            result=ff.fit(p,policy='single',integer_step=1)
        self.assertEqual(search.call_count,1);self.assertTrue(result['within'])


class ReviewScalingTests(unittest.TestCase):
    def test_box_tree_order_matches_exhaustive_bounds(self):
        import math
        from segment_index import BoxIndex
        rng=random.Random(101)
        boxes=[(0,0,0,0)]*8
        for _ in range(64):
            x,y=rng.uniform(-10,10),rng.uniform(-10,10)
            boxes.append((x,x+rng.random(),y,y+rng.random()))
        tree=BoxIndex(boxes)
        for z in [0j,10+10j]+[complex(rng.uniform(-20,20),rng.uniform(-20,20)) for _ in range(30)]:
            want=sorted((math.hypot(max(b[0]-z.real,0,z.real-b[1]),max(b[2]-z.imag,0,z.imag-b[3])),i) for i,b in enumerate(boxes))
            self.assertEqual(list(tree.ordered(z)),want)
        self.assertEqual(list(BoxIndex([]).ordered(0j)),[])

    def test_composite_box_tree_preserves_projection_and_tie_order(self):
        from merge_fit import CompositeContext
        curves=tuple((complex(i),complex(i+.3,1),complex(i+.7,1),complex(i+1)) for i in range(16))
        context=CompositeContext(curves);rng=random.Random(77)
        self.assertIsNotNone(context.box_index)
        for z in [0j,1+0j]+[complex(rng.uniform(-1,17),rng.uniform(-1,2)) for _ in range(50)]:
            candidates=[(abs(p-z),i,p,t) for i,c in enumerate(context.contexts) for p,t in [c.nearest(z)]]
            best=min(candidates,key=lambda r:r[:2])
            self.assertEqual(context.nearest(z),(best[2],(best[1],best[3])))

    def test_sparse_normal_system_matches_known_equations(self):
        from search_core import normal_equations
        rows=[(2,[1,0,3,0],.5),(-1,[0,2,0,0],2)]
        matrix,rhs=normal_equations(rows,4,2)
        self.assertEqual(matrix,[[.5,0,1.5,0],[0,8,0,0],[1.5,0,4.5,0],[0,0,0,0]])
        self.assertEqual(rhs,[-1,4,-3,0])

    def test_rejected_lm_steps_reuse_undamped_system(self):
        import search_core as sc
        p=(0j,1j,1+1j,1+0j)
        # Every proposed position has the same score, so damping changes while
        # the residual/Jacobian and its undamped normal system remain fixed.
        with patch.object(sc,'sample_rows',return_value=([(1,[1,0],1),(1,[0,1],1)],[(1,1)])), \
             patch.object(sc,'normal_equations',wraps=sc.normal_equations) as assemble:
            x,score=sc.refine_lm(p,[0,0],None,iterations=6)
        self.assertEqual(x,[0,0]);self.assertEqual(score,1)
        self.assertEqual(assemble.call_count,1)

    def test_score_path_does_not_build_jacobians(self):
        import search_core as sc
        p=(0j,1j,1+1j,1+0j);context=sc.Context(p)
        with patch.object(sc,'basis',side_effect=AssertionError('scoring allocated Jacobian')):
            norms=sc.sample_norms([single_l2(p)],context)
        self.assertTrue(norms)


if __name__=='__main__':unittest.main()
