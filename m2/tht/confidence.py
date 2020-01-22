"""Module containing functions to evaluate the confidence of a hypothesis
over a ongoing playback."""

from m2.tht import utils
import m2.povel1985
import scipy.stats as st
import numpy as np
import m2.tht.playback as play
from m2.tht import hypothesis


def gaussian_weight(distances):
    return np.exp(-(distances ** 2))


def conf_exp(xs, proj, onsets, delta):
    _, r_p, p = zip(*utils.project(xs, proj, onsets))
    errors = abs(np.array(p) - np.array(r_p))
    relative_errors = errors / float(delta)
    ret = 0.01 ** relative_errors
    return ret


def conf(xs, proj, onsets, delta, mult, decay, weight_func=gaussian_weight):
    '''Confidence of a set of tactus projections over a playback.

    Complexity: O(|proj|) \in O(|ongoing_play|)
    '''
    xs, r_p, p = list(zip(*utils.project(xs, proj, onsets)))
    errors = np.array(p) - np.array(r_p) 
    relative_errors = decay * errors / float(delta)
    ret = weight_func(relative_errors)
    return mult * ret


def all_history_eval_exp(ht, ongoing_play):
    '''
    Evaluates a hypothesis on an ongoing_play. It takes into consideration the
    whole history of the playback. Uses exponential function for distance.

    Complexity: O(|ongoing_play|)
    '''
    xs, proj = zip(*ht.proj_with_x(ongoing_play))
    conf_sum = sum(conf_exp(xs, proj, ongoing_play.discovered_play(), ht.d))
    return ((conf_sum / len(proj)) *
            (conf_sum / len(ongoing_play.discovered_play())))


class WindowedExpEval:
    '''Confidence is evaluated with exp function over a window of time.'''

    def __init__(self, window):
        self.window = window

    def __call__(self, ht, ongoing_play):
        discovered_play = ongoing_play.discovered_play()
        last = discovered_play[-1]
        discovered_play_f = [o for o in discovered_play 
                             if o > last - self.window]
        return all_history_eval_exp(ht, play.Playback(discovered_play_f))


def all_history_eval(ht, ongoing_play):
    '''
    Evaluates a hypothesis on an ongoing_play. It takes into consideration the
    whole history of the playback.

    Complexity: O(|ongoing_play|)
    '''
    xs, proj = list(zip(*ht.proj_with_x(ongoing_play)))
    conf_sum = sum(conf(xs, proj, ongoing_play.discovered_play(), 
                        ht.d, 1, 0.01, lambda x: abs(x)))
    return ((conf_sum / len(proj)) *
            (conf_sum / len(ongoing_play.discovered_play())))


class EvalAssembler:
    '''
    Assembler for hypothesis evaluation functions.

    Args:
        conf_modifiers: list of confs modifiers.
        end_modifiers: list of end modifiers.

    Conf Modifiers modify the list of confidence scores per projected beat.
    They must be callable with the following signature:
        (ht, projected_onsets, discovered_onsets, confidence_scores) ->
          (projected_onsets, discovered_onsets, confidence_scores)

    End Modifiers modify the final confidence score, after it was summed
    and normalized.
    They must be callable with the following signature:
        hypothesis_tracker, ongoing_play, confidence_score -> confidence_score
    '''

    def __init__(self, conf_modifiers, end_modifiers, mult=1, decay=5):
        self.conf_modifiers = conf_modifiers 
        self.end_modifiers = end_modifiers
        self.mult = mult
        self.decay = decay

    def __call__(self, ht, ongoing_play):
        try:
            xs, proj = list(zip(*ht.proj_with_x(ongoing_play)))
        except ValueError as ve:
            print(ht, ht.r, ht.d)
            raise ve
        discovered_onsets = ongoing_play.discovered_play()
        confs = conf(xs, proj, discovered_onsets, ht.d, self.mult, self.decay)
        for cm in self.conf_modifiers:
            proj, discovered_onsets, confs = cm(ht, proj, discovered_onsets,
                                                confs)

        conf_sum = sum(confs)
        try:
            if len(proj) == 0:
                return 0

            end_conf  = ((conf_sum / len(proj)) *
                         (conf_sum / len(discovered_onsets)))

            for em in self.end_modifiers:
                end_conf = em(ht, ongoing_play, end_conf)

            return end_conf
        except ZeroDivisionError:
            print(('> Zero Division Error with ongoing_play: {} '
                   '| ht = {} | proj = {}').format(
                       ongoing_play.discovered_play(),
                       ht, proj))


class PovelAccentConfMod:
    '''
    Function class for evaluating a hypothesis where confidence on each beat
    onset is multiplied if the onset is accented according to Povel 1981 rules.
    '''

    def __init__(self, accent_multiplier):
        self.multiplier = accent_multiplier

    def __call__(self, ht, proj, discovered_onsets, confs):
        accents = set(m2.povel1985.accented_onsets(discovered_onsets))
        accented_confs = [
            c * self.multiplier
            for c, o in zip(confs, discovered_onsets)
            if o in accents
        ]
        return proj, discovered_onsets, accented_confs


class OnsetRestrictedConfMod:
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

    def __call__(self, ht, proj, discovered_onsets, confs):
        starting_idx = max(len(discovered_onsets) - self.prev, 0)
        return (proj[starting_idx:], discovered_onsets[starting_idx:],
                confs[starting_idx:])


class TimeRestrictedConfMod:
    '''
    Function class for evaluating a hypothesis on a restricted time before now
    of the playback.
    '''

    def __init__(self, prev_ms_allowed, mult=1, decay=5):
        self.prev = prev_ms_allowed
        self.mult = mult
        self.decay = decay

    def __call__(self, ht, proj, discovered_onsets, confs):
        onsets_idx = 0
        while (discovered_onsets[onsets_idx] < 
               discovered_onsets[-1] - self.prev):
            onsets_idx += 1

        n_discovered_onsets = discovered_onsets[onsets_idx:]

        xs, n_proj = list(zip(*ht.proj_with_x(play.Playback(n_discovered_onsets))))
        n_confs = conf(xs, n_proj, n_discovered_onsets, ht.d, self.mult,
                       self.decay) 

        return (n_proj, n_discovered_onsets, n_confs)


class DeltaPriorEndMod:
    '''
    Function class for evaluating hypothesis that scores by usign another
    eval function for confidence and also multiplies by a prior distribution
    over the delta value.
    '''
    
    MAX_DELTA = 1500  # ms
    MIN_DELTA = 187  # ms
    DELTA_MU = 600.0  # ms
    DELTA_SIGMA = 400 # 250.0  175 # ms
    delta_clip_a = (MIN_DELTA - DELTA_MU) / DELTA_SIGMA
    delta_clip_b = (MAX_DELTA - DELTA_MU) / DELTA_SIGMA

    def _delta_prior(self, d):
        return st.truncnorm.pdf(d, a=self.delta_clip_a, b=self.delta_clip_b,
                                loc=self.DELTA_MU, scale=self.DELTA_SIGMA)

    def __call__(self, ht, ongoing_play, end_conf):
        return self._delta_prior(ht.d) * end_conf


class WindowedExpEvalPrior:

    def __init__(self, window):
        self.window = window

    def __call__(self, ht, ongoing_play):
        win_score = WindowedExpEval(self.window)(ht, ongoing_play)
        delta_score = DeltaPriorEndMod()(ht, ongoing_play, win_score)
        return delta_score

conf_all_exp = all_history_eval_exp
conf_all = EvalAssembler([], [], 1, 5)
conf_prev = EvalAssembler([TimeRestrictedConfMod(1000, 1, 5)], [])
conf_all_w_prior = EvalAssembler([], [DeltaPriorEndMod()])
conf_prev_w_prior = EvalAssembler([TimeRestrictedConfMod(5000)],
                                  [DeltaPriorEndMod()])
conf_accents_prior = EvalAssembler([PovelAccentConfMod(4)], [DeltaPriorEndMod()])
conf_accents_prev_prior = EvalAssembler(
    [PovelAccentConfMod(4), TimeRestrictedConfMod(1000)], [DeltaPriorEndMod()])

windowed_conf = WindowedExpEval(6000)
