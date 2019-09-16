#!/usr/bin/python
'''Utility to run the Tactus Hypothesis Tracker model on a midi file.

Usage: python tht.py in_file out_file

in_file can be either a midi or an audio file (mp3, wav)
out_file can be either a pickle (.pkl) or table (.csv)
'''

import sys
import filetype
import pickle

import pandas as pd
import numpy as np

from sys import argv
from m2.tht import tactus_hypothesis_tracker
from m2 import midi
from absl import flags
from absl import app
from m2.beatroot import beatroot

FLAGS = flags.FLAGS


def main(argv):
    if len(argv) < 3:
        print('Not enough parameters provided.\n'
              'Usage: python tht.py in_file out_file')
    tht = tactus_hypothesis_tracker.default_tht()

    in_file = argv[1]
    out_file = argv[2]
    
    in_ft = filetype.guess(in_file)
    if in_ft is None:
        print ('Unrecognized input file: {}'.format(in_file))
        sys.exit()

    if (in_ft.extension.startswith('midi')):
        m = midi.MidiPlayback(argv[1])
        onsets = m.onset_times_in_ms()
    else:
        onsets = beatroot(in_file, onsets=True)
        onsets = np.array(onsets) * 1000.

    trackers = tht(onsets)

    if (out_file.endswith('pkl')):
        with open(out_file, 'wb') as f:
            pickle.dump(trackers, f)
    elif (out_file.endswith('csv')):
        d = pd.DataFrame([
            {
                'a': tracker.onset_indexes[0],
                'b': tracker.onset_indexes[1],
                'onset_index': corr[0],
                'onset_time': tracker.onset_times[corr[0]],
                'score': conf[1],
                'phase': corr[1].n_rho,
                'period': corr[1].n_delta 
            }
            for name, tracker in trackers.items()
            for corr, conf in zip(tracker.corr, tracker.confs)
        ])
        d.to_csv(out_file, index=False, float_format='%.6f')


if __name__ == '__main__':
    app.run(main)
