# Tactus Hypothesis Tracker

This repository contains the `Tactus Hypothesis Tracker` model.

The `Tactus Hypothesis Tracker` is a model for 
[tactus or beat](http://en.wikipedia.org/wiki/Pulse_%28music%29) expectation. 
The model works as a beat tracking model (as
in keeping the beat of a song with your foot) but also analyses how strong is
the feeling of the beat throughout the tracking.

More specifically, the model returns analytic information that allows for
further analysis such as: which is the most probable tactus at each part of the
song?  how probable is that tactus? are there more possible tactus? when does
it change? did the same feeling of tactus adapt to the song or was it overruled
by another tactus feeling?

The model was built with the intention to mimic the reasoning and workings
behind the tactus tracking as a cognitive event. 

## Installation

The module can be installed using `setuptools` standard `setup.py` but some
dependencies are not available on pip. Therefor, the whole codebase should be
installed from https://github.com/m2march/tht-dist .

## Usage

The `tht` script allows for three different usages:

### full

    tht full input.wav

The full modality outputs information for entire tracking. The tracking process
works in an agent-based fashion, where each agent holds a possible tactus
hypothesis and are hence called `hypothesis tracker`s. Each tracker has an
initial tactus hypothesis (defined by a _phase_ and _period_ of the beat) that
evolves over time. Along with how the parameter changes, each hypothesis has a
_congruency score_, which rates how fit is the beat tracked to the music heard.

The `full` output can be produced as a table (`-t csv`) or as a python pickle 
(`-t pkl -o out_file`). The csv looks like the one below.


  a    b    onset_index    onset_time     score       phase    period
---  ---  -------------  ------------  --------  ----------  --------
  0    1              1       501.042  1            1.04167   500
  0    1              2      1001.04   1            1.04167   500
  0    1              3      1501.04   1            1.04167   500
  0    2              2      1001.04   0.666667     1.04167  1000
  0    2              3      1501.04   0.5          1.04167  1000
  0    2              4      2001.04   0.6          1.04167  1000
  8    9              9      4751.04   0.074675  4248.59      499.045
  8    9             10      5251.04   0.116558  4251.8       498.88
  8    9             11      5751.04   0.155319  4254.02      498.44


### congruence

	tht congruence input.wav

The congruence modality produces the congruency score for the higher ranking 
hypothesis throughout the passage. The output is a time point and a score value 
per line.


### beat

	tht beat input.wav

The beat modality produces a final beat tracking. The output is a serie of beat 
times (in ms), one beat per line.


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
