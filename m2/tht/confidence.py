"""Module containing functions to evaluate the confidence of a hypothesis
over a ongoing playback."""

import utils


def conf(proj, onsets, delta):
    '''Confidence of a set of tactus projections over a playback.

    Complexity: O(|proj|) \in O(|ongoing_play|)
    '''
    r_p = utils.project(proj, onsets)
    errors = abs(proj - r_p)
    relative_errors = errors / float(delta)
    ret = 0.01 ** relative_errors
    return ret


def all_history_eval(ht, ongoing_play):
    '''
    Evaluates a hypothesis on an ongoing_play. It takes into consideration the
    whole history of the playback.

    Complexity: O(|ongoing_play|)
    '''
    proj = ht.proj(ongoing_play)
    conf_sum = sum(conf(proj, ongoing_play.discovered_play(), ht.d))
    return ((conf_sum / len(proj)) *
            (conf_sum / len(ongoing_play.discovered_play())))


class OnsetRestrictedEval:
    '''
    Function class for evaluating a hypothesis on a restricted set of the onsets
    of the playback. In this class, onsets are restricted to *n* before the
    last discovered onset.
    '''

    def __init__(self, prev_onsets_allowed):
        '''
        Initializes the function class.

        Args:
            prev_onsets_allowed: number of onsets used in the eval before the
            last discovered onset.
        '''
        self.prev = prev_onsets_allowed

    def __call__(self, ht, ongoing_play):
        starting_idx = max(ongoing_play.up_to_discovered_index - self.prev, 0)
        onsets = ongoing_play.discovered_play()[starting_idx:]

        proj = ht.proj_in_range(onsets[0], onsets[-1])
        conf_sum = sum(conf(proj, onsets, ht.d))
        return ((conf_sum / len(proj)) *
                (conf_sum / len(onsets)))
