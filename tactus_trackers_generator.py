"""This module contains the TactusTrackersGenerator class that can be configured
to generate complete hypothesis trackers for the playback of a case."""

import localdeps # NOQA
import gflags
import playback

from tesis.rhythm.tactus import hypothesis

from debug_output import dstr, for_debug


gflags.DEFINE_bool('report_trims', False,
                   'Defines whether to print information on hypothesis trims.')


FLAGS = gflags.FLAGS


@for_debug
def status_report(ongoing_play, hypothesis_trackers, trimmed_hs):
    pnt_advance = int(18 *
                      (ongoing_play.discovered_index + 1)
                      / float(len(ongoing_play.onset_times)))
    adv_str = (('=' * pnt_advance +
                (' ' * (18 - pnt_advance))))
    dstr.write('\r[%s] (%d/%d) | Hts: %d' % (adv_str,
                                             ongoing_play.discovered_index,
                                             len(ongoing_play.onset_times),
                                             len(hypothesis_trackers)))
    if FLAGS.report_trims:
        print >>dstr, ''
        print >>dstr, 'Step:', ongoing_play.discovered_index
        for trimmed_h, original_h in trimmed_hs:
            print >>dstr, '%s -> %s' % (trimmed_h.name, original_h.name)


class HypothesisTracker(hypothesis.HypothesisFromIndex):
    """Class that holds information of the hypothesis evolution.

    A hypothesis is defined as a rho and a delta values, where all tactus
    predictions are described as: rho + delta * k, for some integer k.

    The 'name' of the hypothesis is given by the two onset indexes used
    to originate the hypothesis. The 'beta' value is the first hypothesis.
    'corr' contains a list of Correction objects with information about
    each correction performed over the hypothesis. 'cur' is the current value
    of the hypothesis. 'conf' contains the evolution of the confidence for
    the hypothesis.

    The tracker also contains some convenience methods to work with the
    current hypothesis. The 'r' property gives as the current rho value,
    the 'd' property the current 'delta'. The 'proj' generates all
    tactus predictions by the hypothesis within range of a playback.

    The 'update' method allows us to correct the current hypothesis with
    a correction function and to update the confence status with a
    confidence function.
    """

    def __init__(self, start_idx, end_idx, onset_times):
        super(self.__class__, self).__init__(start_idx, end_idx, onset_times)
        self.beta = self.htuple
        self.corr = []  # [(onset_idx, hypothesis_correction)]
        self.conf = []  # [(onset_idx, conf_value)]

    def update(self, ongoing_play, eval_f, corr_f):
        "Updates a hypothesis with new conf and applying corrections."
        correction = corr_f(self, ongoing_play)
        self.corr.append((ongoing_play.discovered_index, correction))
        self.htuple = correction.new_hypothesis()
        n_conf = eval_f(self, ongoing_play)
        self.conf.append((ongoing_play.discovered_index, n_conf))

    @property
    def cur(self):
        return self.htuple

    def origin_onsets(self):
        return (self.beta[0], sum(self.beta))


class TactusTrackersGenerator():
    """Configurable class to generate hypothesis trackers
    for a case.

    Configuration includes:
        * an eval function that defines how to evaluate a hypothesis over
        certain Playback
        * a correction functions that produces a HypothesisCorrection for a
        hypothesis over a Playback
        * a similarity function that defines how similar are two hypothesis
        * a similarity_epsilon that defines the threshold for trimming

    When called on a set of onset_times it will generate a list of
    hypothesis trackers
    """

    def __init__(self, eval_f, corr_f, sim_f, similarity_epsilon,
                 min_delta, max_delta):
        self.eval_f = eval_f
        self.corr_f = corr_f
        self.sim_f = sim_f
        self.similarity_epsilon = similarity_epsilon
        self.min_delta = min_delta
        self.max_delta = max_delta

    def __call__(self, onset_times):
        ongoing_play = playback.OngoingPlayback(onset_times)
        hypothesis_trackers = []
        while ongoing_play.advance():
            n_hts = self._generate_new_hypothesis(ongoing_play)

            hypothesis_trackers.extend(n_hts)

            for h in hypothesis_trackers:
                h.update(ongoing_play, self.eval_f, self.corr_f)

            kept_hs, trimmed_hs = self._trim_hypothesis(hypothesis_trackers,
                                                        ongoing_play)
            hypothesis_trackers = kept_hs
            status_report(ongoing_play, hypothesis_trackers, trimmed_hs)

        return dict([(ht.name, ht) for ht in hypothesis_trackers])

    def _generate_new_hypothesis(self, ongoing_play):
        "Generates new hypothesis trackers given discovered onset in playback."
        end_index = ongoing_play.discovered_index - 1
        for k in xrange(end_index):
            delta = (ongoing_play.onset_times[end_index] -
                     ongoing_play.onset_times[k])
            if self.min_delta <= delta and delta <= self.max_delta:
                yield HypothesisTracker(k, end_index,
                                        ongoing_play.onset_times)

    def _trim_hypothesis(self, hts, ongoing_play):
        """Partitions new hypothesis into those that should be trimmed given
        a set of comparsion hypothesis."""
        trimmed_hs_data = []
        kept_hs = []
        for idx, h in enumerate(hts):
            max_similarity = max([(0, 0)] +
                                 [(self.sim_f(h, i, ongoing_play), i)
                                  for i in hts[:idx]],
                                 key=lambda x: x[0])
            if max_similarity[0] > (1 - self.similarity_epsilon):
                trimmed_hs_data.append((h, max_similarity[1]))
                # TODO(march): assert that living ht has greater conf
            else:
                kept_hs.append(h)
        return (kept_hs, trimmed_hs_data)
