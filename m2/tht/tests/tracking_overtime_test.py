import pytest
import addict
from m2.tht import tracking_overtime


@pytest.fixture
def basic_hts_mock(mocker):
    '''A mock tht result with two HypothesisTracker'''
    m = mocker

    onset_times = [0, 100, 200, 300]

    h1 = m.MagicMock()
    h1.confs = zip(range(1, 4), [1, 1, 4])
    h1.corr = zip(range(1, 4), [m.MagicMock() for _ in range(3)])
    h1.onset_times = onset_times
    h1.__repr__ = m.Mock(return_value='h1')

    h2 = m.MagicMock()
    h2.confs = zip(range(2, 4), [2, 3])
    h2.corr = zip(range(2, 4), [m.MagicMock() for _ in range(1, 3)])
    h2.onset_times = onset_times
    h2.__repr__ = m.Mock(return_value='h2')

    hts = {'h1': h1, 'h2': h2}
    return addict.Dict({
        'hts': hts,
        'h1': h1,
        'h2': h2,
        'onset_times': onset_times
    })


def matchesHypothesisAtTime(hts=None,
                            onset_idx=None, corr=None,
                            ht_value=None, conf=None):
    def match(hat):
        if hts:
            hat.hts == hts
        if onset_idx:
            assert hat.onset_idx == onset_idx
        if corr:
            assert hat.corr == corr
        if ht_value:
            assert ht_value == ht_value
        if conf:
            assert conf == conf
        return True
    return match


def equalsToMatchers(hats, matchers):
    assert len(hats) == len(matchers)
    assert all([m(h) for m, h in zip(matchers, hats)])


def test_overtime_tracking_init(basic_hts_mock):
    b = basic_hts_mock
    hts_at_time = tracking_overtime.OvertimeTracking(b.hts)
    assert hts_at_time.onset_times == b.onset_times
    assert sorted(hts_at_time.time.keys()) == b.onset_times[1:]
    hts_at_sorted_time = list(hts_at_time.hypothesis_by_time())
    print hts_at_sorted_time
    equalsToMatchers(hts_at_sorted_time[0][1],
                     [matchesHypothesisAtTime(hts=b.h1, onset_idx=1, conf=1)])
    equalsToMatchers(hts_at_sorted_time[1][1],
                     [matchesHypothesisAtTime(hts=b.h1, onset_idx=2, conf=1),
                      matchesHypothesisAtTime(hts=b.h2, onset_idx=2, conf=2)])
    equalsToMatchers(hts_at_sorted_time[2][1],
                     [matchesHypothesisAtTime(hts=b.h1, onset_idx=3, conf=4),
                      matchesHypothesisAtTime(hts=b.h2, onset_idx=3, conf=3)])


def test_conf_sorted_hats(basic_hts_mock):
    b = basic_hts_mock
    hts_at_time = tracking_overtime.OvertimeTracking(b.hts)
    hts_at_sorted_time = list(hts_at_time.hypothesis_sorted_by_conf())
    equalsToMatchers(hts_at_sorted_time[0][1],
                     [matchesHypothesisAtTime(hts=b.h1, onset_idx=1, conf=1)])
    equalsToMatchers(hts_at_sorted_time[1][1],
                     [matchesHypothesisAtTime(hts=b.h2, onset_idx=2, conf=2),
                      matchesHypothesisAtTime(hts=b.h1, onset_idx=2, conf=1)])
    equalsToMatchers(hts_at_sorted_time[2][1],
                     [matchesHypothesisAtTime(hts=b.h1, onset_idx=3, conf=4),
                      matchesHypothesisAtTime(hts=b.h2, onset_idx=3, conf=3)])
