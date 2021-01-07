# Melody generator with RNNs 
<hr>

The goal of this project is to learn how to apply machine learning techniques to produce music. In this project I'll being training Google Magenta's Melody RNN model from scratch using songs in symbolic representation "midi" of Pop and Electronic songs. Midi describes the music using a notation containing the musical notes and timing, but not the sound or timbre of the actual sound. 

<hr>

# About the Data
<hr>

In this project I'll use the ["The Lakh MIDI Dataset v0.1."](https://colinraffel.com/projects/lmd/) I'll filter the dataset leaving only songs that are tagged "Pop" or "Electronic."

* LMD-matched - A subset of 45,129 files from LMD-full which have been matched to entries in the Million Song Dataset.

* Match scores - A json file which lists the match confidence score for every match in LMD-matched and LMD-aligned.

* Dataset not provided in this repo

## Data Visualization

* Distribution of Piano lengths of Pop and Electronic Songs

![](images/piano_length.png)

