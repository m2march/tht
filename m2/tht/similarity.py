"""Module containing functions to measure similarity between two hypothesis
trackers with respect to a ongoing playback."""

import confidence
import playback


def proj_conf_sim(h, i, ongoing_play):
    """Evaluates the similarity between two hypothesis measuring the confidence
    of one on another."""
    proj = playback.Playback(i.proj(ongoing_play))
    return confidence.all_history_eval(h, proj)


def id_sim(h, i, ongoing_play):
    """Two hypothesis are similar if they have the same delta and equivalent
    phase.
    """
    return int(h.d == i.d and ((h.r - i.r) / float(i.d)) % 1 == 0)


def min_dist_sim(h, i, *args):
    """
    Similarity index comes from relative similarity at their closest point.

    Asumes i is a newer hypothesis than h.

    For how dR is calculated, see https://goo.gl/photos/pSQ6gkvgPkn2D4rm9
    """
    assert (i.r > h.r or (i.r == h.r and i.d > h.d),
            'i (%s) is not newer than h (%s)')
    D = abs(h.d - i.d)
    dD = D / max(h.d, i.d)
    R = abs(i.r - h.r) % h.d
    A = h.d / 2
    dR = (A - abs(R - A)) / A
    return 1 - max(dD, dR)
