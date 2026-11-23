"""Cancellation boundaries must apply to cached, exact and floating fits."""
import unittest
from concurrent.futures import CancelledError
from unittest.mock import patch

import fast_fit as ff
import merge_fit as mf
import options_fit as of
from quad_fit import single_l2

CURVE=(0j,30+120j,180+10j,220+0j)
EXACT=(0j,(1+2j)/3,(2+2j)/3,1+0j)


class CancellationTests(unittest.TestCase):
    def setUp(self):ff.numeric_cache().clear()
    def tearDown(self):ff.numeric_cache().clear()

    def test_already_cancelled_exact_and_search_policies_do_no_fitting(self):
        with patch.object(ff,'optimize_one',side_effect=AssertionError('cancelled')), \
             patch.object(ff,'optimize_pair',side_effect=AssertionError('cancelled')), \
             patch.object(ff,'optimize_chain',side_effect=AssertionError('cancelled')):
            for p in (EXACT,CURVE):
                for policy in ('single','pair','multiple','auto'):
                    with self.subTest(p=p,policy=policy):
                        with self.assertRaises(CancelledError):ff.fit(p,policy=policy,cancel=lambda:True)

    def test_cancel_during_search_stops_before_adjustment(self):
        cancelled=[False]
        def search(p,*args,**kwargs):cancelled[0]=True;return single_l2(p)
        with patch.object(ff,'make_context',return_value=None),patch.object(ff,'optimize_one',side_effect=search), \
             patch.object(ff,'adjust_parts',side_effect=AssertionError('cancelled result must not be adjusted')):
            with self.assertRaises(CancelledError):ff.fit(CURVE,policy='single',cancel=lambda:cancelled[0])

    def test_cancel_during_validation_does_not_return_success(self):
        cancelled=[False]
        def bounds(*args,**kwargs):cancelled[0]=True;return 0.,0.
        with patch.object(ff,'make_context',return_value=None),patch.object(ff,'optimize_one',side_effect=lambda p,*a,**k:single_l2(p)), \
             patch.object(ff,'geometric_bounds',side_effect=bounds):
            with self.assertRaises(CancelledError):ff.fit(CURVE,policy='single',cancel=lambda:cancelled[0])

    def test_corresponding_fit_forwards_predicate_in_float_and_integer_modes(self):
        cancel=lambda:False
        def fit(*args,**kwargs):
            self.assertIs(kwargs['cancel'],cancel)
            return dict(parts=[(0j,1j,1+0j)],error=None,within=None)
        with patch.object(ff,'fit',side_effect=fit):
            for step in (0,1):ff.fit_corresponding([CURVE],max_controls=1,integer_step=step,cancel=cancel)

    def test_cancelled_merged_fit_stops_before_optimization(self):
        with patch.object(mf,'optimize_composite',side_effect=AssertionError('cancelled')):
            for count in (1,2):
                with self.assertRaises(CancelledError):mf.fit_merged_count((CURVE,),count,.5,{}, {},cancel=lambda:True)

    def test_cancelled_merged_validation_does_not_return_success(self):
        cancelled=[False]
        def bounds(*args,**kwargs):cancelled[0]=True;return 0.,0.
        with patch.object(mf,'optimize_composite',side_effect=lambda curves,*a:([single_l2(curves[0])],None)), \
             patch.object(mf,'single_quadratic_bound',return_value=float('inf')),patch.object(mf,'geometric_bounds',side_effect=bounds):
            with self.assertRaises(CancelledError):mf.fit_merged_count((CURVE,),1,.5,{}, {},cancel=lambda:cancelled[0])

    def test_adjustment_and_centering_fast_paths_honor_cancellation(self):
        parts=[single_l2(CURVE)]
        with self.assertRaises(CancelledError):of.adjust_parts([CURVE],parts,.5,cancel=lambda:True)
        with self.assertRaises(CancelledError):of.center_parts([CURVE],parts,.5,0,cancel=lambda:True)


if __name__=='__main__':unittest.main()
