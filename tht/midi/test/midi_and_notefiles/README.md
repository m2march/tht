The following files are from the kp dataset (and their related .notes):
* bach.annamin.mid
* bach.jesu.mid
* bach.kindlein.mid
* beet.rondo.mid

The following files are from the kp-pref dataset (and their related .notes):
* beet.son10-1.II.mid
* beet.son10-3.II.mid

Some .notes files had to be modified by hand since their content did not
perfectly match the midi (turns out the midi has two on events for the same
pitch at the same time and two off events for those at different times. Melisma
mftext seems to take the longer of both durations for both on events while our
converter takes the lenght specified in the midi).
