"""Module containing functions to evaluate the confidence of a hypothesis
over a ongoing playback."""

import utils


def conf(proj, ongoing_play, delta):
    'Confidence of a set of tactus projections over a playback.'
    r_p = utils.real_proj(proj, ongoing_play)
    errors = abs(proj - r_p)
    relative_errors = errors / float(delta)
    ret = 0.01 ** relative_errors
    return ret


def eval(ht, ongoing_play):
    'Evaluates a hypothesis on an ongoing_play.'
    proj = ht.proj(ongoing_play)
    conf_sum = sum(conf(proj, ongoing_play, ht.d))
    assert len(proj) > 0, ('Projection of ht (%d, %d) on ongoing_play (%s) is empty' %
             (ht.r, ht.d, ongoing_play.discovered_play()))
    assert len(ongoing_play.discovered_play()) > 0, ('Ongoing play (%s) has no onsets' % ongoing_play)
    return ((conf_sum / len(proj)) *
            (conf_sum / len(ongoing_play.discovered_play())))
