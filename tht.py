#!/usr/bin/python
'''Utility to run the Tactus Hypothesis Tracker model on a midi file.
Usage: tht.py midi_file ARGS
'''

import gflags
import sys

from sys import argv
from m2.tht import tactus_hypothesis_tracker
from m2 import midi

FLAGS = gflags.FLAGS


def main():
    tht = tactus_hypothesis_tracker.default_tht()
    m = midi.MidiPlayback(argv[1])
    trackers = tht(m.onset_times_in_ms())
    for name, tracker in trackers.items():
        print 'ht name', tracker.name
        print 'ht beta %f %f' % tracker.beta
        for n, corr in tracker.corr:
            print 'ht corr %d %f %f' % (n, corr.n_rho, corr.n_delta)
        for n, conf in tracker.confs:
            print 'ht conf %d %f' % (n, conf)


if __name__ == '__main__':
    try:
        argv = FLAGS(argv)  # parse flags
        if len(argv) < 2:
            raise ValueError('No midi_file declared')
    except gflags.FlagsError, e:
        print '%s\\nUsage: %s midi_file ARGS\\n%s' % (e, argv[0], FLAGS)
        sys.exit(1)
    main()
