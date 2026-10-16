import math,random,unittest,importlib.util
from pathlib import Path
from quad_fit import dot,quadratic,cubic
from segment_index import SegmentIndex
from geometry_fit import nearest_quadratic,geometric_bounds
from fast_fit import fit,numeric_cache
spec=importlib.util.spec_from_file_location('old_geometry',Path(__file__).parent/'reference_geometry.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)


class FastTests(unittest.TestCase):
    def test_spatial_index_matches_exhaustive_search(self):
        rng=random.Random(509)
        for case in range(12):
            line=[complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(70)]
            if case==0:line=[0j]*70
            line.insert(30,line[29]);index=SegmentIndex(line)
            for _ in range(80):
                z=complex(rng.uniform(-2,2),rng.uniform(-2,2))
                want=old.nearest_polyline(z,line)[0];got,i,t=index.nearest(z)
                self.assertAlmostEqual(want,got,places=12)
                self.assertAlmostEqual(abs(line[i]+t*(line[i+1]-line[i])-z),got,places=12)

    def test_quadratic_projection_matches_old_root_isolation(self):
        rng=random.Random(505)
        for k in range(2600):
            q=tuple(complex(rng.uniform(-2,2),rng.uniform(-2,2)) for _ in range(3))
            if k%5==0:q=(q[0],(q[0]+q[2])/2+10**(-k%14-14)*q[1],q[2])
            if k%29==0:q=(q[0],q[1],q[0])
            if k%31==0:q=(q[0],q[0],q[0])
            z=complex(rng.uniform(-3,3),rng.uniform(-3,3))
            want=old.nearest_quadratic(z,q)[0];got,t=nearest_quadratic(z,q)
            self.assertAlmostEqual(want,got,places=10,msg=repr((z,q)))

    def test_exact_reduction_and_forced_implicit_join(self):
        q=(0j,60+100j,200+20j)
        p=(q[0],(q[0]+2*q[1])/3,(2*q[1]+q[2])/3,q[2])
        for policy,count in [('single',1),('auto',1),('pair',2)]:
            r=fit(p,policy=policy)
            self.assertEqual(len(r['parts']),count)
            for i in range(41):
                t=i/40
                if count==1:z=quadratic(r['parts'][0],t)
                else:z=quadratic(r['parts'][min(1,int(t*2))],min(1,t*2) if t<.5 else 2*t-1)
                self.assertLess(abs(cubic(p,t)-z),1e-10)

    def test_two_control_midpoint_and_endpoints(self):
        p=(0j,30+120j,180+10j,220+0j)
        for _ in range(1):
            r=fit(p,policy='pair',metrics=True);a,b=r['parts']
            self.assertEqual(a[0],p[0]);self.assertEqual(b[2],p[3])
            self.assertEqual(a[2],b[0])
            self.assertLess(abs(a[2]-(a[1]+b[1])/2),1e-10)
            self.assertIsNone(r['single_error'])
            self.assertLess(r['rms'],.55)

    def test_point_and_straight_line(self):
        for p in [(1+2j,)*4,(0j,20+0j,100+0j,220+0j)]:
            for policy in ('single','pair'):
                r=fit(p,policy=policy)
                self.assertTrue(all(math.isfinite(z.real+z.imag) for q in r['parts'] for z in q))
                self.assertLess(r['error'][1],.03)

    def test_bad_input(self):
        for p in [(0j,1j,2j),(0j,1j,2j,complex(float('nan'),0))]:
            with self.assertRaises(ValueError):fit(p)
        with self.assertRaises(ValueError):fit((0j,1j,2j,3j),tolerance=0)

if __name__=='__main__':unittest.main(verbosity=2)
