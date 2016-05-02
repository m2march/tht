"""Utils for tactus processing."""

import numpy as np
import more_itertools as mit


def real_proj(proj, ongoing_play):
    return project(proj, ongoing_play.discovered_play())


def project(base, reference):
    '''
    For each value in base obtains the closest value in reference.

    Args:
        base: iterable
        reference: iterable
    '''
    ret = np.zeros(len(base))
    play_it = mit.peekable(reference)
    proj_it = mit.peekable(enumerate(base))
    last_play_onset = play_it.next()
    while proj_it:
        last_proj_idx, last_proj_onset = proj_it.next()
        last_dist = abs(last_play_onset - last_proj_onset)
        while play_it:
            new_dist = abs(play_it.peek() - last_proj_onset)
            if new_dist < last_dist:
                last_play_onset = play_it.next()
                last_dist = new_dist
            else:
                break
        ret[last_proj_idx] = last_play_onset
    return ret
