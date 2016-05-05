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


def test_onsetRestrictedEval_evolution():
    '''Tests how OnsetRestrictedEval evolves on different examples.'''
    onsets = [500 * i for i in xrange(4 * 4)]
    onsets.extend([onsets[-1] + 500 + 250 * i for i in range(4 * 4 * 2)])
    assert len(onsets) == 16 + 32

    eval_f = confidence.OnsetRestrictedEval(4)

    h1 = hypothesis.HypothesisFromIndex(0, 1, onsets)
    assert h1.d == 500
    h2 = hypothesis.HypothesisFromIndex(16, 17, onsets)
    assert h2.d == 250

    # Hypothesis with double tempo evolves from confidence 1
    p = playback.OngoingPlayback(onsets)
    c = []
    while p.advance():
        c.append(eval_f(h1, p))
    assert c[0] == 1.0 and np.isclose(c[-1], 0.3675)
    
    # Hypothesis with double tempo evolves to confidence 1
    p = playback.OngoingPlayback(onsets)
    c = []
    while p.advance():
        c.append(eval_f(h2, p))
    assert np.isclose(c[3], 0.58, 0.001) and np.isclose(c[-1], 1.0)
