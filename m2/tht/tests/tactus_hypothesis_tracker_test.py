import unittest
import pytest
import collections

from m2.tht import tactus_hypothesis_tracker
from m2.tht import correction


class TrimSimHypothesisTest(unittest.TestCase):

    def setUp(self):
        pass

    class sim_f_mock():

        def __init__(self):
            self.calls = []

        def __call__(self, h, i, _):
            self.calls.append((h, i))
            return int(i % h == 0)

    def test_trim_sim_hypothesis(self):
        sim_f = self.sim_f_mock()
        tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
            None, None, sim_f, 0.00001, None, None, None)
        kept, trimmed = tht._trim_similar_hypotheses(range(2, 10), sim_f)
        self.assertEquals(sim_f.calls,
                          [(2, x) for x in xrange(3, 10)] +
                          [(3, 5), (3, 7), (3, 9)] +
                          [(5, 7)])
        self.assertEqual(kept, [2, 3, 5, 7])
        self.assertEqual(trimmed,
                         [(4, 2), (6, 2), (8, 2)] +
                         [(9, 3)])

    def test_k_best_hypothesis(self):
        HT = collections.namedtuple('HT', ['id', 'conf'])
        hts = [HT(idx, 7 if idx % 3 == 0 else idx)
               for idx in xrange(11)]
        tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
            None, None, None, None, None, None, 5)
        k_best, other = tht._split_k_best_hypotheses(hts)
        self.assertEqual(k_best, [hts[0], hts[3], hts[6], hts[8], hts[10]])
        self.assertEqual(other, [hts[1], hts[2], hts[4],
                                 hts[5], hts[7], hts[9]])


class TestHypothesisGeneration:

    def test_generated_hypothesis_with_no_restrictions(self, mocker):
        onset_times = list(xrange(10))
        tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
                eval_f=lambda ht, op: ht.r,
                corr_f=lambda ht, op: mocker.MagicMock(return_value=ht),
                sim_f=lambda h, i, *a: False,
                similarity_epsilon=0,
                max_delta=1000,
                min_delta=1,
                max_hypotheses=1000)
        hts = tht(onset_times)
        assert len(hts) == (10 * 9) / 2
        

    def test_generated_hypothesis_with_max_hypothesis_restriction(self,
            mocker):
        onset_times = list(xrange(10))
        tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
                eval_f=lambda ht, op: ht.r,
                corr_f=lambda ht, op: mocker.MagicMock(return_value=ht),
                sim_f=lambda h, i, *a: False,
                similarity_epsilon=0,
                max_delta=1000,
                min_delta=1,
                max_hypotheses=10)
        hts = tht(onset_times)
        assert len(hts) == 10

    def test_generated_hypothesis_with_max_delta_restriction(self, mocker):
        onset_times = list(xrange(10))
        tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
                eval_f=lambda ht, op: ht.r,
                corr_f=lambda ht, op: mocker.MagicMock(return_value=ht),
                sim_f=lambda h, i, *a: False,
                similarity_epsilon=0,
                max_delta=1,
                min_delta=1,
                max_hypotheses=1000)
        hts = tht(onset_times)
        assert len(hts) == 9
        
        tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
                eval_f=lambda ht, op: ht.r,
                corr_f=lambda ht, op: mocker.MagicMock(return_value=ht),
                sim_f=lambda h, i, *a: False,
                similarity_epsilon=0,
                max_delta=2,
                min_delta=1,
                max_hypotheses=1000)
        hts = tht(onset_times)
        assert len(hts) == 9 + 8

    def test_generated_hypothesis_with_min_delta_restriction(self, mocker):
        onset_times = list(xrange(10))
        tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
                eval_f=lambda ht, op: ht.r,
                corr_f=lambda ht, op: mocker.MagicMock(return_value=ht),
                sim_f=lambda h, i, *a: False,
                similarity_epsilon=0,
                max_delta=3,
                min_delta=3,
                max_hypotheses=1000)
        hts = tht(onset_times)
        assert len(hts) == 7


onset_times = list(xrange(10))
proj_1 = lambda xs: [x[0] for x in xs]

@pytest.fixture
def hts(mocker):
    tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
            eval_f=lambda ht, op: ht.r,
            corr_f=correction.no_corr,
            sim_f=lambda h, i, *a: False,
            similarity_epsilon=0,
            max_delta=4,
            min_delta=2,
            max_hypotheses=50)
    hts = tht(onset_times)
    return hts


class TestGeneralTrackingResults:
        

    def test_deltas_in_range(self, hts):
        print [ht.d for ht in hts.values()]
        assert all([ht.d >= 2 and ht.d <= 4
                    for ht in hts.values()
                    ])

    def test_non_repeated_hypothesis(self, hts):
        assert (len(set([ht.origin_onsets() for ht in hts.values()])) ==
                len(hts))

    def test_conf_and_corr_onset_index_are_equal(self, hts):
        assert all([proj_1(ht.corr) == proj_1(ht.confs)
            for ht in hts.values()])

    def test_conf_onsets_are_complete_and_greater_than_beta_2(self, hts):
        assert all([proj_1(ht.confs) == list(range(ht.onset_indexes[1], 10))
            for ht in hts.values()])
