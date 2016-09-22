"""Library for opening midi transcription files."""

import midi
import collections as c

# Midi partial managing methods


class Note():
    'Represents a note in a midi playback.'

    def __init__(self, prev, tick, pitch, velocity, channel,
                 duration, bpm, resolution):
        self.prev = prev
        self.tick = tick
        self.pitch = pitch
        self.velocity = velocity
        self.channel = channel
        self.bpm = bpm
        self.resolution = resolution
        self.duration = duration

        ms_per_tick = (60000.0 / self.bpm / self.resolution)
        delta = (self.tick - self.prev.tick) * ms_per_tick
        self.ms = self.prev.ms + delta

    def __cmp__(self, other):
        return self.tick - other.tick or self.duration - other.duration

    @property
    def duration_ms(self):
        return self.duration * (60000.0 / self.bpm / self.resolution)


class CollapsedNote(Note):
    'Represents a note with other note collapsed on it.'

    def __init__(self, note, count):
        self.tick = note.tick
        self.pitch = note.pitch
        self.velocity = note.velocity
        self.channel = note.channel
        self.bpm = note.bpm
        self.resolution = note.resolution
        self.duration = note.duration
        self.prev = note.prev
        self.count = count

        ms_per_tick = (60000.0 / self.bpm / self.resolution)
        delta = (self.tick - self.prev.tick) * ms_per_tick
        self.ms = self.prev.ms + delta


class KickoffNote(Note):
    'A null note representing the beginning of the passage'

    def __init__(self):
        pass

    @property
    def tick(self):
        return 0

    @property
    def prev(self):
        return self

    @property
    def ms(self):
        return 0


class MidiPlayback():
    """Converts a midi into a playback and has methods for manipulation.

    Expects midi to:
        * Have only one instrument
        * Have one tempo event
    """

    def __init__(self, midi_file_name):
        pattern = midi.read_midifile(midi_file_name)
        assert len(set([e.channel for t in pattern for e in t
                        if isinstance(e, midi.NoteEvent)])) == 1, \
            'More than one channel found in: %s' % midi_file_name

        def _process_offevent(on_notes, offset):
            onset = on_notes[(e.pitch, e.channel)].popleft()
            prev = KickoffNote() if not self.notes else self.notes[-1]
            self.notes.append(
                Note(prev=prev,
                     tick=onset.tick, pitch=onset.pitch,
                     velocity=onset.velocity, channel=onset.channel,
                     bpm=self.bpm, resolution=self.resolution,
                     duration=offset.tick - onset.tick))

        def _update_bpm(tempo_event):
            self.bpm = tempo_event.bpm

        pattern.make_ticks_abs()
        self.resolution = pattern.resolution
        bpm_event = [e for t in pattern for e in t
                     if isinstance(e, midi.SetTempoEvent)][0]
        assert bpm_event.tick == 0

        self.bpm = bpm_event.bpm

        self.notes = []
        on_notes = dict()
        for t in pattern:
            for e in t:
                if isinstance(e, midi.NoteOnEvent):
                    if (e.pitch, e.channel) not in on_notes:
                        on_notes[(e.pitch, e.channel)] = c.deque()
                    elif (e.velocity == 0):
                        _process_offevent(on_notes, e)
                    on_notes[(e.pitch, e.channel)].append(e)
                elif isinstance(e, midi.NoteOffEvent):
                    _process_offevent(on_notes, e)
                elif isinstance(e, midi.SetTempoEvent):
                    _update_bpm(e)
        self.notes.sort()

    def collapse_onset_times(self):
        min_duration = min(self.notes, key=lambda n: n.duration).duration / 2.0
        new_notes = []
        last_note = self.notes[0]
        collapse_count = 1
        for n in self.notes[1:]:
            if n.tick - last_note.tick < min_duration:
                collapse_count += 1
            else:
                new_notes.append(CollapsedNote(last_note, collapse_count))
                last_note = n
                collapse_count = 1
        self.notes = new_notes

    def onset_times_in_ms(self):
        return [n.ms for n in self.notes]

    def onset_times_in_ticks(self):
        return [n.tick for n in self.notes]


# TODO(march): convert asserts into tests
def midi_to_collapsed_onset_times(midi_file_name):
    """Opens a midi file and returns milliseconds for every onset event,
    collapsing simultaneous events.

    Simultaneous events are those with onset distance less than half of the
    smaller note duration.
    """
    mp = MidiPlayback(midi_file_name)
    mp.collapse_onset_times()
    return mp.onset_times_in_ms()


# TODO(march): split file midi opening and pattern processing
def midi_to_onsets_times(midi_file_name):
    """Opens a midi file and returns the milliseconds for every onset event."""
    mp = MidiPlayback(midi_file_name)
    return mp.onset_times_in_ms()


def midi_to_onsets(midi_file_name, sample_rate):
    """Opens a midi file and returns the sample for every onset event given the
    specified sample_rate."""
    onset_times = midi_to_onsets_times(midi_file_name)
    millis_per_sample = 1000.0 / sample_rate
    onset_samples = [int(t / millis_per_sample) for t in onset_times]
    return onset_samples


if __name__ == "__main__":
    print midi_to_onsets("dorrance-transcript.mid", 44100)
