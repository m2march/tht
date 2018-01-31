"""Module with correction functions thta given a hypothesis tracker and
a ongoing playback return a HypothesisCorrection class."""

import utils
import math

import numpy as np
import hypothesis as hs
import confidence

from m2.tht import playback, hypothesis

from scipy import stats



def exp_error_conf(error, multiplicator, decay, delta):
    return multiplicator * error * (decay ** (np.abs(error) / float(delta)))


def gauss_error_conf(error, multiplicator, decay, delta):
    return multiplicator * error * confidence.gaussian_weight(decay * error / delta)


def error_calc(ht, ongoing_play):
    p_w_x = ht.proj_with_x(ongoing_play)
    try:
        xs, p = zip(*p_w_x)
    except ValueError:
        print ht, ongoing_play.onset_times

    #xs, p, r_p = zip(*utils.centered_real_proj(xs, p, ongoing_play))
    xs, p, r_p = zip(*utils.project(xs, p, ongoing_play.discovered_play())) 

    err = np.array(r_p) - np.array(p)
    return xs, err, p


def proj_error_conf(ht, ongoing_play, mult, decay, err_conf_f):
    xs, err, p = error_calc(ht, ongoing_play)
    return xs, err_conf_f(np.array(err), mult, decay, ht.d), p


class HypothesisCorrection():
    """Structure holding information of each hypothesis correction.

    This class contains information pertaining the correction event.
    """

    def __init__(self, o_rho, o_delta, n_rho, n_delta,
                 r_value=None, p_value=None, stderr=None,
                 o_mse=None, n_mse=None, d_rho=None, d_delta=None):
        self.o_rho = o_rho
        self.o_delta = o_delta
        self.n_rho = n_rho
        self.n_delta = n_delta
        self.r_value = r_value
        self.p_value = p_value
        self.stderr = stderr
        self.o_mse = o_mse
        self.n_mse = n_mse
        self.d_rho = d_rho if d_rho is not None else n_rho - o_rho
        self.d_delta = d_delta if d_delta is not None else n_delta - o_delta

    def new_hypothesis(self):
        return hs.Hypothesis(self.n_rho, self.n_delta)

    def __repr__(self):
        return '(dr: %.2f, dd: %.2f)' % (self.dr, self.dd)

    @property
    def dr(self):
        return self.d_rho
    
    @property
    def dd(self):
        return self.d_delta


class HypothesisCorrectionMethod(object):
    """Represents a method to correct a hypothesis. Must be callable
    with a hypothesis (HypothesisTracker) and a playback."""

    def __call__(self, ht, ongoing_play):
        raise NotImplementedError()


class LinearRegressOverSmoothedErrorCorrection(HypothesisCorrectionMethod):
    """Generates a HypothesisCorrection for the hypothesis and the ongoing play.

    Correction is performed using a linear regression with the x values being
    those corresponding to the projection of the hypothesis. The y values are
    the error of the hypothesis prediction versus the closest onset for each
    passed through a smoothing function that tones down outliers.
    The linear regression then generates a intercept and slope value that
    minimize the mse between x and y. The intercept and slope values are
    considered the new rho and delta values of the hypothesis.

    Complexity: O(|ongoing_play|)
    """

    def __init__(self, multiplicator=1.0, decay=0.01):
        self.mult = multiplicator
        self.decay = decay

    def __call__(self, ht, ongoing_play):
        xs, err, p = error_calc(ht, ongoing_play)
        conf = exp_error_conf(err, self.mult, self.decay, ht.d)

        (delta_delta, delta_rho, r_value,
         p_value, stderr) = stats.linregress(xs, conf)

        return HypothesisCorrection(o_rho=ht.r, o_delta=ht.d,
                                    n_rho=ht.r + delta_rho,
                                    n_delta=ht.d + delta_delta,
                                    r_value=r_value, p_value=p_value,
                                    stderr=stderr)


class MovingWindowedSmoothCorrection(HypothesisCorrectionMethod):
    '''
    Correction function in which the new hypothesis is moved forward to
    the last projections. Correction is measured over a limited time before
    the current onset.
    '''

    def __init__(self, mult, decay, window):
        '''
        Args:
            mult: double multiplier of the error
            decay: double multiplier of the error on the decay part
            window: ms before last onsets to check for errors
        '''
        self.mult = mult
        self.decay = decay
        self.window = window

    def __call__(self, ht, ongoing_play):
        discovered_onsets = np.array(ongoing_play.discovered_play())
        discovered_onsets = discovered_onsets[discovered_onsets >
                                              discovered_onsets[-1] -
                                              self.window]
        sub_pl = playback.Playback(discovered_onsets)
        xs, err, p = error_calc(ht, sub_pl)
        conf = gauss_error_conf(err, self.mult, self.decay, ht.d)
        
        if len(p) > 2:
            (delta_delta, delta_rho, r_value,
             p_value, stderr) = stats.linregress(xs, conf)

            n_h = hypothesis.Hypothesis(ht.r + delta_rho, ht.d + delta_delta)
            
            n_p = n_h.proj(sub_pl)

            return HypothesisCorrection(o_rho=ht.r, o_delta=ht.d,
                                        n_rho=n_p[-2],
                                        n_delta=n_p[-1] - n_p[-2],
                                        d_rho=delta_rho, d_delta=delta_delta,
                                        r_value=r_value, p_value=p_value,
                                        stderr=stderr)

        else:
            return HypothesisCorrection(o_rho=ht.r, o_delta=ht.d,
                                        n_rho=ht.r, n_delta=ht.d)



class LinRegsOverSmoothedErrorCorrectionWithPeak(HypothesisCorrectionMethod):

    def __init__(self, decay=0.0001):
        self.decay = decay

    def __call__(self, ht, ongoing_play):
        mult = (-1 * ht.d) / math.log(self.decay)
        lin_r_corr = LinearRegressOverSmoothedErrorCorrection(mult, self.decay)
        return lin_r_corr(ht, ongoing_play)


class MultLinRegsOSEC(LinearRegressOverSmoothedErrorCorrection):

    def __init__(self, mult=1.0, decay=0.02, by=5):
        self.by = by

        LinearRegressOverSmoothedErrorCorrection.__init__(self, mult, decay)

    def __call__(self, ht, ongoing_play):
        nh = ht
        for i in xrange(self.by):
            nc = super(self.__class__, self).__call__(nh, ongoing_play)
            nh = nc.new_hypothesis()
        return nc

lin_r_corr = LinearRegressOverSmoothedErrorCorrection()
lin_r_corr_alt = LinearRegressOverSmoothedErrorCorrection(1, 0.001)
lin_r_corr_max = LinRegsOverSmoothedErrorCorrectionWithPeak()
lin_r_corr_max_descent = LinRegsOverSmoothedErrorCorrectionWithPeak(0.001)
lin_r_corr_opt_by_5 = MultLinRegsOSEC(2, 0.0001, 5)
lin_r_corr_opt = LinearRegressOverSmoothedErrorCorrection(2, .0001)


def no_corr(ht, ongoing_play):
    'Correction function that performs no correction'
    return HypothesisCorrection(ht.r, ht.d, ht.r, ht.d)
