"""Modulec containing functions to measure similarity between two hypothesis
trackers with respect to a ongoing playback."""

import confidence
import playback


def proj_conf_sim(h, i, ongoing_play):
    """Evaluates the similarity between two hypothesis measuring the confidence
    of one on another."""
    proj = playback.Playback(i.proj(ongoing_play))
    return confidence.eval(h, proj)


def id_sim(h, i, ongoing_play):
    """Two hypothesis are similar if they have the same delta and equivalent
    phase."""
    return int(h.d == i.d and ((h.r - i.r) / float(i.d)) % 1 == 0)


def min_dist_sim(h, i, *args):
    'Similarity index comes from relative similarity at their closest point.'
    D = abs(h.d - i.d)
    R = abs(i.r - h.r) % h.d
    A = h.d / 2
    return 1 - max(D / max(h.d, i.d), (A - abs(R - A)) / A)
