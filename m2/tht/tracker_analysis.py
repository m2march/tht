'''This module contains a class with methods to perform analysis of the tactus
phase.'''

import tactus_hypothesis_tracker
import numpy as np


class TactusCaseAnalyzer:

    def __init__(self):
        pass

    def top_hypothesis(self, case):
        'Given a case, returns a list of top tactus hypothesis'
        def _sorting_key_gen():
            for i in xrange(3, len(case['onset_times'])):
                def key(item):  # item :: (ht_name, conf_dict)
                    return item[1][i] if i in item[1] else 0.0
                yield key

        def _top_hypothesis_iter():
            hts = case['hypothesis_trackers']
            hts_iterators = [(ht, dict(ht.confs))
                             for ht in hts.values()]
            for key in _sorting_key_gen():
                yield max(hts_iterators, key=key)[0]
        return list(_top_hypothesis_iter())


def sorting_key_gen(onset_idx):
    'Returns the confidence sorting key for hypothesis items at onset index'
    def key(item):  # item :: (ht_name, conf_dict)
        return item[1][onset_idx] if onset_idx in item[1] else None
    return key


def hypothesis_ranks_overtime(hypothesis_trackers, playback_length):
    """Returns a structure to evaluate hypothesis rank over time.

    Args:
        hypothesis_trackers: dictionary of hypothesis_name -> HypothesisTracker
        playback_length: total amount of onsets considered of the playback

    Returns:
        dict(onset_idx -> hypothesis_ranking) as list
        with
            hypothesis_ranking :: dict(ranking ->
                (hypothesis_tracker, abs_confidence_at_onset_idx))
                as list
    """
    results = []
    for i in xrange(playback_length):  # Filtering confidence values
        sort_key = sorting_key_gen(i)
        enhanced_trackers = [(item[0], sort_key(item))
                             for item in [(t, dict(t.confs)) for t
                                          in hypothesis_trackers.values()]
                             if sort_key(item)]
        sorted_trackers = sorted(enhanced_trackers, key=lambda x: x[1],
                                 reverse=True)
        results.append((i, sorted_trackers))

    return results


def create_trackers_segments(hypothesis_ranks_overtime, trackers_to_show):
    'Creates segments: tracker -> [(onset_times: [], conf: [])]'
    trackers_segments = {}
    for idx, hypothesis_ranking in enumerate(hypothesis_ranks_overtime):
        for t, t_conf in hypothesis_ranking[:trackers_to_show]:
            if t not in trackers_segments:
                trackers_segments[t] = []
            last_segment = None
            if (trackers_segments[t] and
                trackers_segments[t][-1][0][-1] == idx - 1):
                last_segment = trackers_segments[t][-1]
            if last_segment:
                last_segment[0].append(idx)
                last_segment[1].append(t_conf)
            else:
                last_segment = ([idx], [t_conf])
                trackers_segments[t].append(last_segment)

    return trackers_segments


def tracker_dump(tracker, stream):
    print >> stream, 'ht name', tracker.name
    print >> stream, 'ht beta %f %f' % tracker.beta
    for n, corr in tracker.corr:
        print >> stream, 'ht corr %d %f %f' % (n, corr.n_rho, corr.n_delta)
    for n, conf in tracker.confs:
        print >> stream, 'ht conf %d %f' % (n, conf)


def top_hypothesis(hts, onset_times_count):
    '''
    Given a case, returns a list of top tactus hypothesis

    Returns:
        :: [(onset_idx :: int, ht :: HypothesisTracker)]
    '''
    def _sorting_key_gen():
        for i in xrange(3, onset_times_count):
            def key(item):  # item :: (ht_name, conf_dict)
                return item[1][i] if i in item[1] else None
            yield (i, key)

    def _top_hypothesis_iter():
        hts_iterators = [(ht, dict(ht.confs))
                         for ht in hts.values()]
        for idx, key in _sorting_key_gen():
            m = max(hts_iterators, key=key)
            if key(m) is None:
                continue
            yield (idx, m[0])
    return list(_top_hypothesis_iter())


def produce_beats_information(onset_times, top_hts):
    '''
    Runs through trackers and onset times, generating beats by projecting each
    top hypothesis correction at that onset time on the interval between said
    onset time and the next one.

    Args:
        onset_times :: [ms]
        top_hts :: [(onset_idx, HypothesisTracker)]

    Returns:
        :: [ms]
    '''
    top_onset_idxs = [onset_idx for onset_idx, _ in top_hts]
    onset_idxs = [0] + top_onset_idxs[1:] + [top_onset_idxs[-1]]
    onset_limits_idx = [(onset_idxs[i], onset_idxs[i+1])
                        for i in xrange(0, len(onset_idxs) - 1)]
    onset_limits = [(onset_times[l], onset_times[r])
                    for l, r in onset_limits_idx]
    assert len(onset_limits) == len(top_hts)

    ret = []
    for idx in xrange(len(onset_limits)):
        onset_idx, top_ht = top_hts[idx]
        left_limit, right_limit = onset_limits[idx]
        iht = dict(top_ht.corr)[onset_idx].new_hypothesis()
        beats = np.array(iht.proj_in_range(left_limit, right_limit))
        for beat in beats[1:]:
            ret.append(beat)
    return ret
        

def track_beats(onset_times, tracker=tactus_hypothesis_tracker.default_tht()):
    '''Generates tracked beats from onset_times by projecting to hypothesis
    during tracking.'''
    hts = tracker(onset_times)

    top_hts = top_hypothesis(hts, len(onset_times))

    beats = produce_beats_information(onset_times, top_hts)

    return beats
