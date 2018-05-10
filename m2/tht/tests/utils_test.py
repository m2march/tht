import unittest
import mock

from m2.tht import utils

class RealProjTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_real_proj(self):
        matched = mock.MagicMock()
        matched.discovered_play = mock.MagicMock(return_value=[1, 2, 3, 4, 5])
        to_match = [-2, 2.2, 2.3, 2.5, 4, 4.5, 6, 7]
        xs = range(len(to_match))
        expected = [1, 2, 2, 2, 4, 4, 5]
        _, _, result = zip(*utils.real_proj(xs, to_match, matched))
        self.assertEqual(list(result), expected)
