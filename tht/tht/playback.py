"""Module containing classes that represents playbacks. A playback is an
enhanced container for a set of onset events (onset times)."""

import numpy as np


class Playback():
    """Represents the entire playback of a song.

    Has the same interface as OngoingPlayback except for the discovering
    methods.
    """

    def __init__(self, onset_times):
        self.onset_times = onset_times

    @property
    def min(self):
        'First onset'
        return self.onset_times[0]

    @property
    def max(self):
        'Last onset'
        return self.onset_times[-1]

    def discovered_play(self):
        'Onsets discovered at the moment'
        return self.onset_times


class OngoingPlayback(Playback):
    """Represents a playback that is discovered onset by onset.

    This class is used to manage the discovery process of a song, by exposing
    only a chuck of the song, adding one more onset to what's been discovered
    at a time.

    Interal Variables
        onset_times: numpy array of all milliseconds with events in order
        up_to_discovered_index: index up to which all events were discovered
            (not inclusive)
    """

    def __init__(self, onset_times):
        self.onset_times = np.array(onset_times)
        self.up_to_discovered_index = 1

    def advance(self):
        'Discover a new onset'
        if (self.up_to_discovered_index < len(self.onset_times)):
            self.up_to_discovered_index += 1
            return True
        return False

    @property
    def discovered_index(self):
        'Returns the index of the last discovered onset'
        return self.up_to_discovered_index - 1

    @property
    def max(self):
        'Last onset discovered. None if no onset has been discovered yet'
        return self.onset_times[self.discovered_index]

    @property
    def discovered_onset(self):
        'Last onset discovered. Same as max.'
        return self.max

    def discovered_play(self):
        return self.onset_times[:self.up_to_discovered_index]
