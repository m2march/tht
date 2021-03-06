import numpy as np

class OvertimeTracking:
    '''
    Class for analysing the results of tracking a set of onsets during the
    tracking process.
    '''

    def __init__(self, hts):
        '''
        Initialize the instance analyze the tracking overtime.

        self.hts: tracking result
        self.time: time(ms) -> [HypothesisAtTime]
        self.onset_times: [ms]

        Args:
            hts: string -> HypothesisTracker result of a
            TactusHypothesisTracker
        '''
        self.hts = hts
        self.time = {}
        self.onset_times = sorted(list(hts.values())[0].onset_times)

        assert all([np.array_equal(self.onset_times, ht.onset_times)
                    for ht in list(hts.values())])

        # Update time with one HAT per hypothesis at a given time
        for name, ht in list(hts.items()):
            assert (([x[0] for x in ht.corr] == [x[0] for x in ht.confs]),
                    'hts corrections and conf does not have same onset indexes')
            for idx in range(len(ht.corr)):
                onset_idx, corr = ht.corr[idx]
                conf = ht.confs[idx][1]
                onset_time = self.onset_times[onset_idx]
                hts_at_time = self.time.get(onset_time, [])
                hts_at_time.append(HypothesisAtTime(ht, onset_idx, corr, conf))
                self.time[onset_time] = hts_at_time

    def hypothesis_by_time(self):
        'Returns the list of HTS sorted by time'
        return ((time, self.time[time]) for time in self.onset_times[1:]
                if time in self.time) # TODO(march): verify that check is necessary

    def hypothesis_sorted_by_conf(self):
        'Returns the list of HTS sorted by time and then by confidence'
        for time, hats in self.hypothesis_by_time():
            yield (time, sorted(hats, key=lambda hat: hat.conf, reverse=True))


class HypothesisAtTime:
    '''
    Class to represent a hypothesis at a given time.
    '''
    def __init__(self, hts_ref, onset_idx, corr, conf):
        self.hts = hts_ref
        self.onset_idx = onset_idx
        self.corr = corr
        self.ht_value = corr.new_hypothesis()
        self.conf = conf

    def __repr__(self):
        return '%s (c:%.2f)' % (self.hts, self.conf)
