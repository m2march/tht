import unittest
import collections
from tht.tht import tactus_hypothesis_tracker

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
