'''This module contains a class with methods to perform analysis of the tactus
phase.'''


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
            hts_iterators = [(ht, dict(ht.conf))
                             for ht in hts.values()]
            for key in _sorting_key_gen():
                yield max(hts_iterators, key=key)[0]
        return list(_top_hypothesis_iter())


def sorting_key_gen(onset_idx):
    'Returns the confidence sorting key for hypothesis items at onset index'
    def key(item):
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
                             for item in [(t, dict(t.conf)) for t
                                          in hypothesis_trackers.values()]
                             if sort_key(item)]
        sorted_trackers = sorted(enhanced_trackers, key=lambda x: x[1],
                                 reverse=True)
        results.append(sorted_trackers)

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
    for n, conf in tracker.conf:
        print >> stream, 'ht conf %d %f' % (n, conf)
