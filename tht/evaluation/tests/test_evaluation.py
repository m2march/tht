'''Tests for the evaluation module.'''

import numpy as np

from tht.evaluation import min_proj_k, min_proj
from tht.evaluation import min_proj_dist, min_rel_proj_dist

np.random.seed(5301)


class SimpleHypothesis:

    def __init__(self, r, d):
        self.r = r
        self.d = d


class TestMinProjDist:

    random_onset_sequence = [-10]
    for x in xrange(100):
        random_onset_sequence.append(random_onset_sequence[-1] +
                                     np.random.normal())

    random_hypotheses = [SimpleHypothesis(np.random.normal(),
                                          np.random.normal(1.0, 0.1))
                         for x in xrange(10)]
    random_hypotheses.append(SimpleHypothesis(-20, 5))
    random_hypotheses.append(SimpleHypothesis(200, 15))
    assert max(random_onset_sequence) < 200
    assert max(random_onset_sequence) > -20
    assert all([h.d > 0.1 for h in random_hypotheses])

    def index_test(self, h, searched, expected):
        print 'searched:      ', searched
        print 'indexes:       ', [min_proj_k(h, x) for x in searched]
        print 'found:         ', [min_proj(h, x) for x in searched]
        print 'expected_indexes', expected
        assert expected.tolist() == [min_proj_k(h, x) for x in searched]

    def test_min_proj_k_exact(self):
        h = SimpleHypothesis(0, 1)
        assert range(-5, 5) == [min_proj_k(h, x) for x in range(-5, 5)]

    def test_min_proj_k_small_onset_offset(self):
        h = SimpleHypothesis(0, 1)
        searched = np.array(range(-5, 5)) + .3
        expected_indexes = np.array(range(-5, 5))
        self.index_test(h, searched, expected_indexes)

    def test_min_proj_k_small_rho_offset(self):
        h = SimpleHypothesis(0.3, 1)
        searched = np.array(range(-5, 5))
        self.index_test(h, searched, searched)

    def test_min_proj_k_large_rho_offset(self):
        h = SimpleHypothesis(0.7, 1)
        searched = np.array(range(-5, 5))
        expected_indexes = searched - 1
        self.index_test(h, searched, expected_indexes)

    def test_min_proj_k_small_delta_offset(self):
        h = SimpleHypothesis(0, 0.7)
        searched = np.array(range(-5, 5))
        expected_indexes = np.array([-7, -6, -4, -3, -1, 0, 1, 3, 4, 6])
        self.index_test(h, searched, expected_indexes)

    def test_min_proj_randomly(self):
        for h in self.random_hypotheses:
            for onset in self.random_onset_sequence:
                proj_dist = abs(onset - min_proj(h, onset))
                assert min_proj(h, onset) == h.r + min_proj_k(h, onset) * h.d
                assert (min_proj_dist(h, onset) - proj_dist) < 0.00001
                assert min_proj_dist(h, onset) <= h.d / 2.0
                assert ((min_proj_dist(h, onset) / (float(h.d))) -
                        min_rel_proj_dist(h, onset)) <= 0.0000001

    def test_rho_affects_distance(self):
        onset = 1
        rs = np.linspace(0, 1, 20)
        hs = [SimpleHypothesis(x, 1) for x in rs]
        expected_distances = np.concatenate(([0], rs[1:rs.size/2],
                                             1 - rs[rs.size/2:]))
        result_distances = [min_proj_dist(h, onset) for h in hs]
        assert (expected_distances - result_distances < 0.0001).all()
