'''This module contains a class with methods to perform analysis of the tactus
phase.'''

from typing import Dict, List, Tuple, Union, Optional
from . import tactus_hypothesis_tracker
import numpy as np
from m2.tht.tactus_hypothesis_tracker import HypothesisTracker
import m2.tht.defaults as tht_defaults
from scipy.stats import spearmanr, pearsonr, norm
import pandas as pd

Delta = float
Rho = float
Conf = float

class TactusCaseAnalyzer:

    def __init__(self):
        pass

    def top_hypothesis(self, case):
        'Given a case, returns a list of top tactus hypothesis'
        def _sorting_key_gen():
            for i in range(3, len(case['onset_times'])):
                def key(item):  # item :: (ht_name, conf_dict)
                    return item[1][i] if i in item[1] else 0.0
                yield key

        def _top_hypothesis_iter():
            hts = case['hypothesis_trackers']
            hts_iterators = [(ht, dict(ht.confs))
                             for ht in list(hts.values())]
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
    for i in range(playback_length):  # Filtering confidence values
        sort_key = sorting_key_gen(i)
        enhanced_trackers = [(item[0], sort_key(item))
                             for item in [(t, dict(t.confs)) for t
                                          in list(hypothesis_trackers.values())]
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
    print('ht name', tracker.name, file=stream)
    print('ht beta %f %f' % tracker.beta, file=stream)
    for n, corr in tracker.corr:
        print('ht corr %d %f %f' % (n, corr.n_rho, corr.n_delta), file=stream)
    for n, conf in tracker.confs:
        print('ht conf %d %f' % (n, conf), file=stream)


def top_hypothesis(hts, onset_times_count):
    '''
    Given a case, returns a list of top tactus hypothesis

    Returns:
        :: [(onset_idx :: int, ht :: HypothesisTracker)]
    '''
    def _sorting_key_gen():
        for i in range(3, onset_times_count):
            def key(item):  # item :: (ht_name, conf_dict)
                return item[1][i] if i in item[1] else None
            yield (i, key)

    def _top_hypothesis_iter():
        hts_iterators = [(ht, dict(ht.confs))
                         for ht in list(hts.values())]
        for idx, key in _sorting_key_gen():
            f_list = [item for item in hts_iterators if key(item) is not None]
            if len(f_list) == 0:
               continue
            yield (idx, max(f_list, key=key)[0])
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
                        for i in range(0, len(onset_idxs) - 1)]
    onset_limits = [(onset_times[l], onset_times[r])
                    for l, r in onset_limits_idx]
    assert len(onset_limits) == len(top_hts)

    ret = []
    for idx in range(len(onset_limits)):
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


def ht_grid(min_delta=tht_defaults.min_delta,
            max_delta=tht_defaults.max_delta,
            delta_sample_num=60, rho_sample_num=20):
    '''
    Delta and rho grid for distribution sampling.

    Return:
        delta_values: List
        rho_values: List
    '''
    delta_values = np.linspace(min_delta,
                               max_delta,
                               num=delta_sample_num)
    rho_values = np.linspace(0, 1, num=rho_sample_num)

    return delta_values, rho_values


def ht_weighted_distribution(points, delta_samples, rho_samples,
                             delta_sigma=25, rho_sigma=0.1):
    '''
    Calculates the probability of tactus hypothesis given 'points'.

    Calculates P(H | D) where H is a rho, delta tactus hypothesis and D is a
    set of rho, delta, confidence points. 

    P(r, d | t_i) prop= sum_{i} t_i.c * norm.pdf((t_i.r, t_i.d), mu=(r, d), 
                                                 sigma=(rho_sigma, delta_sigma))

    Args:
        points: List[Tuple[Delta, Rho, Weight]]
        delta_samples: delta values on which to calculate the distribution
        rho_samples: rho values on which to calculate the distribution
        delta_sigma: sigma used to weight the points relative to the sample
        rho_sigma: sigma used to weight the points relative to the sample

    Return:
        DataFrame with columns rho, delta, weight where rho and delta are the
        cross product of 'delta_samples' and 'rho_samples'.
    '''
    def weighted_sum(delta, rho, confs: List[Tuple[Delta, Rho, Conf]]):
        # Asumes P(delta | D) and P(rho | D) independent
        r_weight = norm.pdf([x[1] for x in confs], loc=rho, scale=rho_sigma)
        d_weight = norm.pdf([x[0] for x in confs], loc=delta,
                            scale=delta_sigma)
        cs = np.array([x[2] for x in confs])
        return (cs * r_weight * d_weight).sum()
        #return sum((
        #    norm.pdf(_d, loc=delta, scale=delta_sigma) *
        #    norm.pdf(_r, loc=rho, scale=rho_sigma) * c
        #    for _d, _r, c in confs))

    hist2d = np.array([
        (d, r, weighted_sum(d, r, points))
        for d in delta_samples
        for r in rho_samples
    ])
    print('#d: {}, #r: {}, #p {}'.format(len(delta_samples),
                                          len(rho_samples),
                                          len(points)))
    hist2d[:, 2] = hist2d[:, 2] / hist2d[:, 2].sum()
    return pd.DataFrame(hist2d, columns=('delta', 'rho', 'weight'))


def tht_ht_points(hts: Dict[str, HypothesisTracker]):
    '''
    Extracts delta and rho points from HypothesisTracker set.

    Returns:
        List[Tuple[Delta, Rho, Conf]]
    '''
    conf_values = [(corr.n_delta, 
                    (corr.n_rho % corr.n_delta) / corr.n_delta, 
                    conf)
                   for ht in hts.values()
                   for (idx, corr), (_, conf) in zip(ht.corr, ht.confs)]
    return conf_values


def tht_grid(hts: Dict[str, HypothesisTracker]):
    '''Calculates confidence map over rho and delta hypothesis space.

    The confidence map is calculated by creating a grid over rho and delta
    and on each point summing the confidence of hypothesis nearby.

    The resulting map is normalized by the sum of values as a histogram.

    Result:
        (n x 3) array with columns as: rho_value, delta_value and conf
    '''
    delta_samples, rho_samples = ht_grid()

    conf_values = tht_ht_points(hts)

    df = ht_weighted_distribution(conf_values, delta_samples,
                                  rho_samples)
    return df[['rho', 'delta', 'weight']].values


def tht_tracking_confs(tht_pkl_fn: Union[str, Dict[str, HypothesisTracker]], 
                      onset_count: Optional[int] = None) -> [float, float]:
    '''
    Obtains the tracking confidence from a tht pickle as the avg top conf.

    Args:
        tht_pkl_fn: either:
            * filename of the tht tracking pickle
            * unpickled tracking (dict[str, HypothesisTracker])
        onset_count: total number of onsets or None

    Returns:
        list of confidence values at each timepoint :: [ms, confidence score]
    '''
    if isinstance(tht_pkl_fn, str):
        with open(tht_pkl_fn, 'rb') as f:
            hts = pickle.load(f)
    else:
        hts = tht_pkl_fn

    if onset_count is None:
        onset_count = max([o for ht in hts.values() for o, c in ht.confs])

    top_hts = top_hypothesis(hts, onset_count)

    conf_values = [(ht.onset_times[idx], dict(ht.confs)[idx]) 
                   for idx, ht in top_hts]

    return conf_values


def tht_tracking_conf(tht_pkl_fn: Union[str, Dict[str, HypothesisTracker]], 
                      onset_count: Optional[int] = None) -> float:
    '''
    Mean tht top tracking confidence.

    See tht_tracking_confs for parameters details.
    '''
    time_values, conf_values = zip(*tht_tracking_confs(tht_pkl_fn,
                                                       onset_count))

    return np.mean(conf_values)
