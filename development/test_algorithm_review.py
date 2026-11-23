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


if __name__=='__main__':unittest.main()
