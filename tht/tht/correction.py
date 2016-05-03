"""Module with correction functions thta given a hypothesis tracker and
a ongoing playback return a HypothesisCorrection class."""

import utils
import math

import numpy as np
import hypothesis as hs

from scipy import stats


def error_conf(error, multiplicator, decay, delta):
    return multiplicator * error * (decay ** (np.abs(error) / float(delta)))


class HypothesisCorrection():
    """Structure holding information of each hypothesis correction.

    This class contains information pertaining the correction event.
    """

    def __init__(self, o_rho, o_delta, n_rho, n_delta,
                 r_value=None, p_value=None, stderr=None,
                 o_mse=None, n_mse=None):
        self.o_rho = o_rho
        self.o_delta = o_delta
        self.n_rho = n_rho
        self.n_delta = n_delta
        self.r_value = r_value
        self.p_value = p_value
        self.stderr = stderr
        self.o_mse = o_mse
        self.n_mse = n_mse

    def new_hypothesis(self):
        return hs.Hypothesis(self.n_rho, self.n_delta)

    def __repr__(self):
        return '(dr: %.2f, dd: %.2f)' % (self.n_rho - self.o_rho,
                                         self.n_delta - self.o_delta)


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
        p_w_x = ht.proj_with_x(ongoing_play)
        xs, p = zip(*p_w_x)
        r_p = utils.real_proj(p, ongoing_play)

        err = r_p - p
        conf = error_conf(err, self.mult, self.decay, ht.d)

        (delta_delta, delta_rho, r_value,
         p_value, stderr) = stats.linregress(xs, conf)

        return HypothesisCorrection(o_rho=ht.r, o_delta=ht.d,
                                    n_rho=ht.r + delta_rho,
                                    n_delta=ht.d + delta_delta,
                                    r_value=r_value, p_value=p_value,
                                    stderr=stderr)


class LinRegsOverSmoothedErrorCorrectionWithPeak(HypothesisCorrectionMethod):

    def __init__(self, decay=0.0001):
        self.decay = decay

    def __call__(self, ht, ongoing_play):
        mult = (-1 * ht.d) / math.log(self.decay)
        lin_r_corr = LinearRegressOverSmoothedErrorCorrection(mult, self.decay)
        return lin_r_corr(ht, ongoing_play)


class MultLinRegsOSEC(LinearRegressOverSmoothedErrorCorrection):

    def __call__(self, ht, ongoing_play):
        nh = ht
        for i in xrange(5):
            nc = super(self.__class__, self).__call__(nh, ongoing_play)
            nh = nc.new_hypothesis()
        return nc

lin_r_corr = LinearRegressOverSmoothedErrorCorrection()
lin_r_corr_alt = LinearRegressOverSmoothedErrorCorrection(1, 0.001)
lin_r_corr_max = LinRegsOverSmoothedErrorCorrectionWithPeak()
lin_r_corr_max_descent = LinRegsOverSmoothedErrorCorrectionWithPeak(0.001)
lin_r_corr_by_5 = MultLinRegsOSEC()
lin_r_corr_opt = LinearRegressOverSmoothedErrorCorrection(2, .0001)


def no_corr(ht, ongoing_play):
    'Correction function that performs no correction'
    return HypothesisCorrection(ht.r, ht.d, ht.r, ht.d)
