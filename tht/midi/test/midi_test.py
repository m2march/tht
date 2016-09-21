import os
import re
import math
from glob import glob
from tht import midi

NOTEFILES_DIR = 'midi_and_notefiles'


def parse_notefile(notefile_name):
    notes = []
    with open(notefile_name) as f:
        r = re.compile('Note *(\d*) *(\d*) *(\d*)')
        for l in f.readlines():
            m = r.match(l)
            if m:
                g = m.groups()
                notes.append((int(g[0]), int(g[1]), int(g[2])))

    return notes


def test_with_melisma_notefiles():
    this_path = os.path.dirname(os.path.realpath(__file__))
    midi_file_names = glob(os.path.join(this_path, NOTEFILES_DIR, '*.mid'))
    print 'Midi files: %s' % str(midi_file_names)
    for midi_file_name in midi_file_names:
        notefile_name = midi_file_name.replace('.mid', '.notes')

        notes = midi.MidiPlayback(midi_file_name).notes
        notefile_notes = parse_notefile(notefile_name)

        print midi_file_name, notefile_name

        assert len(notes) == len(notefile_notes)

        first_onset = notes[0].ms

        sorted_notes = sorted(notes,
                              key=lambda n: (int(n.ms), int(n.ms + n.duration), n.pitch))
        sorted_notefile_notes = sorted(notefile_notes)

        for note, notefile_note in zip(sorted_notes, sorted_notefile_notes):
            assert note.pitch == notefile_note[2]
            assert abs((note.ms - first_onset) - notefile_note[0]) < 2
            assert abs((note.ms + note.duration_ms - first_onset) - notefile_note[1]) < 2
