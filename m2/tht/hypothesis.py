"""This module contains classes representing tactus hypothesis."""

import math

import numpy as np


class Hypothesis(object):
    """Represents a hypothesis (rho, delta) and contains several
    convenience methods."""

    def __init__(self, rho, delta):
        self.htuple = (rho, delta)

    @property
    def name(self):
        return self.__repr__()

    @property
    def r(self):
        return self.htuple[0]

    @property
    def d(self):
        return self.htuple[1]

    @property
    def cur(self):
        return self.htuple

    def bpm(self):
        return 60000.0 / self.d

    def proj_with_x_in_range(self, min, max):
        min_x, max_x = self.proj_x_range(min, max)
        return ((x, self.r + self.d * x) for x in range(min_x, max_x+1))

    def proj_with_x(self, play):
        return self.proj_with_x_in_range(play.min, play.max)

    def proj_in_range(self, min, max):
        return np.array([v[1] for v in self.proj_with_x_in_range(min, max)])

    def proj(self, play):
        return np.array([v[1] for v in self.proj_with_x(play)])

    def proj_x_range(self, min, max):
        min_x = int(math.ceil((min - self.d / 2.0 - self.r) / self.d))
        max_x = int(math.floor((max + self.d / 2.0 - self.r) / self.d))
        return min_x, max_x

    def __getitem__(self, key):
        if key == 0:
            return self.r
        if key == 1:
            return self.d
        else:
            return object.__getitem__(self, key)

    def __setitem__(self, key, value):
        if key == 0:
            self.htuple = (value, self.d)
        if key == 1:
            self.htuple = (self.r, value)
        else:
            return object.__setitem__(self, key, value)

    def __repr__(self):
        return 'H(%.2f, %.2f)' % self.htuple

    def __lt__(self, other):
        return self.r < other.r or (self.r == other.r and self.d < other.d)


class HypothesisFromIndex(Hypothesis):
    """Represents a hypothesis created from index on onset times.
    Name is represented from the onset numbers, rather than the onset times.

    onset_times must be in milliseconds."""

    def __init__(self, start_idx, end_idx, onset_times):
        start_offset = onset_times[start_idx]
        end_offset = onset_times[end_idx]
        Hypothesis.__init__(self, start_offset, end_offset - start_offset)
        self._name = '%d-%d' % (start_idx, end_idx)
        self.onset_indexes = (start_idx, end_idx)

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return 'Hi:%s' % (self.name)
