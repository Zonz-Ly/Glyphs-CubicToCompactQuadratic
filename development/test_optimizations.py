import random,unittest
from search_core import Context,sample_rows,sample_norms,unpack,pack
from geometry_fit import geometric_bounds
from fast_fit import fit,fit_corresponding,numeric_cache
from mock_glyphs import HARD,EXACT,PAIR_NEEDED

class OptimizationTests(unittest.TestCase):
    def test_distance_only_path_is_bit_identical(self):
        rng=random.Random(606)
        for case in range(12):
            p=tuple(complex(rng.uniform(-1,1),rng.uniform(-1,1)) for _ in range(4))
            context=Context(p,33,17)
            x=[rng.uniform(-1,1) for _ in range(2 if case%2 else 4)]
            parts=unpack(p,x)
            self.assertEqual(sample_rows(parts,context)[1],sample_norms(parts,context))

    def test_shared_projection_geometry_identical(self):
        a=Context(HARD,33,17);b=Context(HARD,65,25,geometry=a.geometry);c=Context(HARD,65,25)
        self.assertIs(a.index,b.index);self.assertEqual(b.samples,c.samples)
        for z in [0j,50+80j,200+20j]:self.assertEqual(b.nearest(z),c.nearest(z))

    def test_early_reject_is_valid_and_same_decision(self):
        r=fit(HARD,policy='single');tight=r['error']
        early=geometric_bounds(HARD,r['parts'],.75,reject_above=.75)
        self.assertGreater(early[0],.75)
        self.assertLessEqual(early[0],tight[1]);self.assertGreaterEqual(early[1],tight[0])
        self.assertEqual(len(fit(HARD)['parts']),2)

    def test_reuse_source_flattening(self):
        cache={};r=fit(HARD,policy='single');a=geometric_bounds(HARD,r['parts'],source_cache=cache)
        key=next(iter(cache));line=cache[key][0]
        b=geometric_bounds(HARD,r['parts'],source_cache=cache)
        self.assertIs(line,cache[key][0]);self.assertEqual(a,b)

    def test_no_metrics_do_not_change_controls(self):
        a=fit(HARD,metrics=False);b=fit(HARD,metrics=True)
        self.assertEqual(a['parts'],b['parts']);self.assertIsNone(a['rms'])

    def test_single_tests_stop_after_first_failed_master(self):
        from unittest.mock import patch
        import fast_fit
        numeric_cache().clear();calls=[];original=fast_fit.fit
        def wrapped(p,*args,**kwargs):calls.append(kwargs.get('policy'));return original(p,*args,**kwargs)
        with patch.object(fast_fit,'fit',wrapped):r=fit_corresponding([PAIR_NEEDED,EXACT,EXACT])
        self.assertEqual(calls,['single','pair','pair','pair'])
        self.assertEqual([len(x['parts']) for x in r],[2,2,2])

if __name__=='__main__':unittest.main(verbosity=2)
