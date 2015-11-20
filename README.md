# Tactus Hypothesis Tracker

This repository contains the `Tactus Hypothesis Tracker` model and
the _tap_ dataset.

The `Tactus Hypothesis Tracker` is a model for
[tactus](http://en.wikipedia.org/wiki/Pulse_%28music%29) inference over midi
musical files. The model receives the onsets of a musical passage, in the form
of a `midi`, and outputs an overtime analysis of tactus hypotheses. The model
is characterized for relaxing some musical preconceptions used in other systems
and providing overtime information of confidence and correction of different
tactus hypotheses.

The _tap_ dataset is a set of midi files that contain onset information for tap
dancing performances. This dataset was used to test whether the `tht` model
works on non-traditional performances. The transcripts in the dataset stand out
for being rhythmically expressive.

## How to Use

The usable version of the model is implemented in `tht.py`. A use example is:

    $> python tht.py tap-dataset/dorrance-transcript.mid

### Dependencies

The code here presented has the following dependencies:

* [python-midi](https://github.com/vishnubob/python-midi)
* [numpy](http://www.numpy.org/)
* [more_itertools](https://pypi.python.org/pypi/more-itertools)

It also uses `unittest` and `mock` for the tests.

## Results

The `tht.py` program outputs the whole analysis performed. This means, a list
of all considered hypotheses and how the evolved over time. The output will
then have the following structure:

    ht name 26-27
    ht beta 13170.833333 533.854167
    ht corr 28 13188.442296 535.196325
    ht corr 29 13196.568261 536.048022
    ht corr 30 13199.750474 536.640084
    ht corr 31 13198.257970 537.017380
    ...
    ht conf 28 0.123900
    ht conf 29 0.119647
    ht conf 30 0.116557
    ...
    ht name 8-10
    ht beta 5077.083333 871.354167
    ht corr 11 5076.121179 873.019412
    ht corr 12 5076.359505 874.925853
    ht corr 13 5070.605792 875.163430
    ht corr 14 5088.399924 881.281182
    ...

All lines starting with `ht` contains information about a hypothesis. An `ht
name` line provides the name of the hypothesis and establishes that all
following lines until the next `ht name` line will be related to that
hypothesis. Currently, all information related to one hypothesis is given in a
batch. This means that once you start reading information of a hypothesis no
information of other hypothesis will show up until the end of the first one.

Other lines present in the output are:

* `ht beta _phase_ _delta_` where _phase_ and _delta_ are the phase and
    inter-pulse-interval of the tactus, respectively, of the moment the
    hypothesis was first created. Values are in milliseconds.
* `ht conf _n_ _value_` provide the confidence _value_ of the hypothesis at
    onset _n_ of the playback.
* `ht corr _n_ _phase_ _delta_` define the correction made to the hypothesis at
    onset _n_ with _phase_ and _delta_ defining the tactus after the
    correction.


## Model implementation 

The theoretical concepts of the model are implemented in the `tactus`
directory. The following is a breakdown of the implemented parts:

* `tactus_hypothesis_tracker.py` contains the main logic for the tracker. It
    moves from left to right of the playback and constantly generates
    hypotheses, corrects them and measures confidence. All intermediate steps
    are recorded to later be output.
* `confidence.py` contains de evaluation function to measure confidence of a
    hypothesis over a ongoing playback.
* `correction.py` contains different methods to correct a hypothesis to better
    fit the ongoing playback.
* `similarity.py` contains the similarity measure function between two
    hypothesis.


## Tap Dataset

The tap dataset contains 10 transcript from rhythmically expressive
performances. `guillem-transcript.mid` and `dorrance-transcript.mid` are
transcripts of tap exercises by professional tap dancers. `base-x-y.mid` are
improvised patterns. Each pattern was performed and recorded at two different
tempos: 80 and 100 bpms. The `y` value indicates the base bpm, the `x` value is
the pattern id.
