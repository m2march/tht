from tht.tht import confidence, hypothesis, playback
import numpy as np


def test_onsetRestrictedEval_with_one_back():
    '''Tests that OnsetRestrictedEval sees the right amount of onsets.'''
    song = [1, 2, 3, 4, 5, 6]
    p = playback.OngoingPlayback(song)
    h = hypothesis.HypothesisFromIndex(0, 2, song)

    eval_f = confidence.OnsetRestrictedEval(1)
    while p.advance():
        assert eval_f(h, p) == (0.2 / 2) * 0.2
        if p.advance():
            assert eval_f(h, p) == 1.0


def test_onsetRestrictedEval_with_three_back():
    '''Tests that OnsetRestrictedEval sees the right amount of onsets.'''
    song = [1, 2, 3, 4, 5, 6]
    p = playback.OngoingPlayback(song)
    h = hypothesis.HypothesisFromIndex(0, 2, song)

    eval_f = confidence.OnsetRestrictedEval(3)
    assert eval_f(h, p) == 1.0
    p.advance()
    assert eval_f(h, p) == (1.1 / 2) ** 2
    p.advance()
    assert eval_f(h, p) == 2.0 / 3.0
    p.advance()

    np.testing.assert_approx_equal(eval_f(h, p), (1.2 / 3.0) ** 2)
    while p.advance():
        assert eval_f(h, p) == 2.0 / 3.0
        p.advance()
        np.testing.assert_approx_equal(eval_f(h, p), (1.2 / 3.0) ** 2)
