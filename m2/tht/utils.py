"""Utils for tactus processing."""

import numpy as np
import more_itertools as mit


def real_proj(xs, proj, ongoing_play):
    return project(xs, proj, ongoing_play.discovered_play())


def centered_real_proj(xs, proj, ongoing_play):
    _xs = np.array(xs)
    _proj = np.array(proj)
    _r_p_pos = project(_xs[_xs >= 0], _proj[_xs >= 0], 
                       ongoing_play.discovered_play())
    _r_p_neg = reversed(project(reversed(_xs[_xs < 0]), 
                                reversed(_proj[_xs < 0]),
                                reversed(ongoing_play.discovered_play())))
    return list(_r_p_neg) + list(_r_p_pos)


def project(xs, base, reference):
    '''
    For each value in base obtains the closest value in reference without
    repetition. Reference values are processed in order, so some of them may
    not be used because there are neighbors closer to the base value. As a
    result, some base values might not be matched.

    Args:
        xs: index associated with base
        base: iterable
        reference: iterable

    Returns:
        :: [(index, base value, reference value)]
        List of matched pairs of values. Some values from base might not appear
        in the result.
    '''
    _base = list(base)
    if len(_base) == 0:
        return []

    play_it = mit.peekable(reference)
    proj_it = mit.peekable(zip(xs, _base))
    last_play_onset = next(play_it)
    more_proj = True
    ret = []
    while more_proj:
        try:
            last_proj_idx, last_proj_onset = next(proj_it)
            last_dist = abs(last_play_onset - last_proj_onset)
            try:
                while True:
                    new_dist = abs(play_it.peek() - last_proj_onset)
                    if new_dist < last_dist:
                        last_play_onset = next(play_it)
                        last_dist = new_dist
                    else:
                        break
                ret.append((last_proj_idx, last_proj_onset, last_play_onset))
                # TODO: Dividir la funcion en dos
                #last_play_onset = play_it.next()
            except StopIteration:
                more_proj = False
                ret.append((last_proj_idx, last_proj_onset, last_play_onset))
        except StopIteration:
            more_proj = False
    return ret
