"""Utils for tactus processing."""

import numpy as np
import more_itertools as mit


def real_proj(proj, ongoing_play):
    'Obtains onsets of the ongoing playback that best suit the projection.'
    ret = np.zeros(len(proj))
    play_it = mit.peekable(ongoing_play.discovered_play())
    proj_it = mit.peekable(enumerate(proj))
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
