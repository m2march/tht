'''Library with functions used in evaluation of models'''

import math
import numpy as np


def gaussian_window(d):
    'From Cemgil 2000'
    sigma = 0.04 * 1000  # 0.04 sec to ms
    return math.exp(-(d ** 2) / (2 * (sigma ** 2)))


def cemgil_similarity(expected_beats, result_beats):
    'From Cemgil 2000'
    expected_beats = np.array(expected_beats)

    max_scores = np.array(
        [max([gaussian_window(e - r) for r in result_beats])
         for e in expected_beats])

    denom = ((len(expected_beats) + len(result_beats)) / 2)

    ret = max_scores.sum() / denom
    return ret


def min_proj_k(h, onset):
    '''
    Returns the index of the projection of the hypothesis closest to the onset.

    Args:
        h: class with .r and .d methods for rho and delta
        onset: onset in ms
    '''
    offset = 1 if (onset - h.r) % h.d > h.d / 2.0 else 0
    return ((onset - h.r) // h.d) + offset


def min_proj(h, onset):
    '''
    Returns the values of the projection of the hypothesis closest to the
    onset.
    '''
    return h.r + h.d * min_proj_k(h, onset)


def min_proj_dist(h, onset):
    '''
    Returns the abs min distance of the projection of
    the hypothesis to the onset.
    '''
    dist = (onset - h.r) % h.d
    return min(abs(dist), abs(dist - h.d))


def min_rel_proj_dist(h, onset):
    return min_proj_dist(h, onset) / float(h.d)
