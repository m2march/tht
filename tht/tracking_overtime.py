import numpy as np

class OvertimeTracking:
    '''
    Class for analysing the results of tracking a set of onsets during the
    tracking process.
    '''

    def __init__(self, hts):
        '''
        Initialize the instance analyze the tracking overtime.

        Args:
            hts: string -> HypothesisTracker result of a
            TactusHypothesisTracker
        '''
        self.hts = hts
        self.time = {}
        self.onset_times = hts.values()[0].onset_times

        assert all([np.array_equal(self.onset_times, ht.onset_times)
                    for ht in hts.values()])

        # Update time with one HAT per hypothesis at a given time
        for name, ht in hts.items():
            assert (([x[0] for x in ht.corr] == [x[0] for x in ht.confs]),
                    'hts corrections and conf does not have same onset indexes')
            for idx in xrange(len(ht.corr)):
                onset_idx, corr = ht.corr[idx]
                conf = ht.confs[idx][1]
                onset_time = self.onset_times[onset_idx - 1]
                hts_at_time = self.time.get(onset_time, [])
                hts_at_time.append(HypothesisAtTime(hts, onset_idx, corr, conf))
                self.time[onset_time] = hts_at_time

    def hipothesis_by_time(self):
        'Returns the list of HTS sorted by time'
        times = sorted(self.time.keys())
        return (self.time[time] for time in times)


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
