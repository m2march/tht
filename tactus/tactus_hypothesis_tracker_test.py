import unittest
import utils

import mock
import tactus_hypothesis_tracker


class TrimSimHypothesisTest(unittest.TestCase):

    def setUp(self):
        pass

    class sim_f_mock():

        def __init__(self):
            self.calls = []

        def __call__(self, h, i):
            self.calls.append((h, i))
            return i % h == 0

    def test_trim_sim_hypothesis(self):
        sim_f = self.sim_f_mock()
        tht = tactus_hypothesis_tracker.TactusHypothesisTracker(
            None, None, sim_f, 0.1, None, None, None)
        kept, trimmed = tht._trim_similar_hypotheses(range(2, 10), sim_f)
        self.assertEquals(sim_f.calls,
                          [ (2, x) for x in xrange(3, 10) ] +
                          [ (3, 5), (3, 7), (3, 9) ] +
                          [ (5, 7) ])
        self.assertEqual(kept, [2, 3, 5, 7])
        self.assertEqual(trimmed,
                         [ (4, 2), (6, 2), (8, 2) ] +
                         [ (6, 3), (9, 3))

