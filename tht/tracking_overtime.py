
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

        # Update time with one HAT per hypothesis at a given time
        for name, ht in hts.items():
           assert ([x[0] for x in ht.corr] == [x[0] for x in ht.confs], 
                   'hts corrections and conf does not have same onset indexes')
           for idx in xrange(len(ht.corr)):
               onset_idx, corr = ht.corr[idx]
               conf = ht.confs[idx][1]
               hts_at_time = self.time.get(onset_idx, [])
               hts_at_time.append(HypothesisAtTime(hts, onset_idx,
                   corr, conf))
               self.time[onset_idx] = hts_at_time

        self.total_onsets = max(self.time.keys())

    def hypothesis_at_time(self, time):
        'Returns the list of HTS at given onset time'
        return self.time.get(time, [])


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
