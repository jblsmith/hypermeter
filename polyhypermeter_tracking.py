import numpy as np
import scipy as sp
import madmom
import librosa, librosa.display
import mir_eval
import pytube
import matplotlib.pyplot as plt
plt.ion()
from matplotlib import gridspec
import collections
from scipy.spatial.distance import euclidean, cosine

# Load audio
def load_audio(path):
	y, sr = librosa.core.load(path, sr=None, mono=False)
	return y, sr

# Load audio from YouTube!
def load_audio_from_youtube(youtube_id):
	# The YouTube ID is an 11-character string.
	# Download file
	destination_folder = "./"
	print "Downloading from YouTube..."
	destination_path = pytube.YouTube('http://youtube.com/watch?v=' + youtube_id).streams.first().download(destination_folder)
	# TODO: refine above to avoid overwriting indiscriminately, and to get preferred format?
	print "Saved to: " + destination_path
	print "Loading audio..."
	y, sr = load_audio(destination_path)
	return y, sr

# Basic audio preparation: get mono / spectrum / real
you_make_me = "I98OWrboh-M"
y, sr = load_audio_from_youtube(you_make_me)
y, sr = load_audio("~/Dropbox/Apps/01 Hey Ya.mp3")
y_mono = librosa.core.to_mono(y)

# Do beat tracking using madmom
detection_function = madmom.features.beats.RNNDownBeatProcessor()(y_mono)
# Save detection function to matlab for sharing:
# sp.io.savemat("hey_ya_detection_function.m", {'detecfunc':detection_function})
fps_ratio = sr * 1.0 / 44100
beat_estimates = madmom.features.beats.DBNDownBeatTrackingProcessor(beats_per_bar=[3,4], fps=int(100*fps_ratio))(detection_function)
beat_estimates = madmom.features.beats.DBNDownBeatTrackingProcessor(beats_per_bar=[2,3,4,5,6,7], fps=int(100*fps_ratio))(detection_function)


x = sp.io.loadmat("hey_ya_detection_function.m")


### Once you have a downbeat detection function (DDF), let's compare the DDF for all pairs of measures, for all possible offsets.
# Set bar length
bar_length = 4
beat_estimates = madmom.features.beats.DBNDownBeatTrackingProcessor(beats_per_bar=[bar_length], fps=int(100*fps_ratio))(detection_function)

# Generate different hypothesis downbeat streams
#  [1234] [1234]  ... vs [2341] [2341] ... etc.
# bar_onsets_i = beat_estimates[range(0,beat_estimates.shape[0],4),0]
bar_onsets = [beat_estimates[range(i,beat_estimates.shape[0],bar_length),0] for i in range(bar_length)]

# For each, collect DDF excerpts as our features.
# feature_seq_i = detection_function[time:time+bar_length]
feats = []
for bar_onsets_i in bar_onsets:
	feats_i = []
	for t in range(len(bar_onsets_i)-1):
		t1 = int(100*bar_onsets_i[t])
		t2 = int(100*bar_onsets_i[t+1])
		feature_seq_t = detection_function_heyya[t1:t2,:]
		feats_i += [feature_seq_t[:,1]]   # Take just the 2nd column, which is the downbeat detection function. 1st col has beat detection function.
	feats += [feats_i]

# For each bar_onset hypothesis, we create a different feature set, and these are assembled in feats. Thus:
len(feats) == bar_length
# Each sequence of bar-features has the same length, the number of bars (which should be equal to each other.)
[len(feat) for feat in feats]
# But the "feature" for each bar (the downbeat detection function for it) can have slightly different lengths.
collections.Counter([len(x) for x in feats[0]])
# Therefore, to compare them, we will either need to truncate/pad them to some fixed length, or use a flexible similarity metric like DTW distance.


# To start, look at truncations:
# Generate self-similarity matrix for all paris of beat-stream-feature_sets
dists = np.zeros((len(feats),len(feats[0]),len(feats[0])))
for i in range(len(feats)):
	for k_i in range(len(feats[i])):
		for k_j in range(len(feats[j])):
			x = feats[0][k_i]
			y = feats[i][k_j]
			if len(x)>0 and len(y)>0:
				min_len = np.min((len(x),len(y)))
				dists[i,k_i,k_j] = cosine(x[:min_len], y[:min_len])

plt.figure(1)
for i in range(4):
	plt.subplot(2,2,i+1)
	plt.imshow(dists[i,:,:])
	plt.title("Phase-0 vs. Phase-"+str(i))

plt.tight_layout()
plt.savefig("phase_comparison_plot_heyya.jpg")
plt.figure(2)
# make "phase-invariant" bar-similarity matrix
plt.imshow(np.min(dists,axis=0))
plt.title("Min across all Phase-0-Phase-X plots")
plt.tight_layout()
plt.savefig("phase_invariant_plot_heyya.jpg")


# Tentative work using DTW distance --- but it's very slow!
from fastdtw import fastdtw as fdtw
dtwdists = np.zeros((len(feats),len(feats[0]),len(feats[0])))
for i in range(len(feats)):
	print str(i) + "/" + str(len(feats))
	for k_i in range(len(feats[i])):
		print k_i
		for k_j in range(k_i,len(feats[j])):
			x = feats[0][k_i]
			y = feats[i][k_j]
			if len(x)>0 and len(y)>0:
				min_len = np.min((len(x),len(y)))
				dtwdists[i,k_i,k_j], path = fdtw(x[:min_len], y[:min_len], dist=euclidean, radius=2)







# NB: Madmom expects a signal rate of 44100 and returns a detection function at 100Hz,
# but librosa and youtube might provide other rates, hence the fps_ratio thing.

# Slice matrix into beats or downbeats
beat_onset = beat_estimates[:,0]
db_onset = beat_estimates[beat_estimates[:,1]==1,0]
# Pick one:
onsets = db_onset



## Looking at Beatles annotations for unusual songs.
#  Quickly scan to find examples of songs with unusual sequences of measure lengths.
import glob
beat_files = glob.glob("~/Documents/data/Isophonics/The Beatles Annotations/beat/The Beatles/*/*.txt")
import pandas as pd
import os.path

def load_beats(path):
	lines = open(path, 'r').readlines()
	onset, beat = zip(*[ [float(line.split()[0]), int(line.split()[1])] for line in lines])
	onset = np.array(onset)
	beat = np.array(beat)
	return onset, beat

odd_songs = {}
for beat_file in beat_files:
	onset, beat = load_beats(beat_file)
	beat_iters = np.diff(beat)
	step_backs = beat_iters[beat_iters<0]
	step_backs = 1 - step_backs
	if len(set(step_backs))>1:
		odd_songs[len(odd_songs)] = [onset, beat, step_backs, beat_file]
		# print str(list(set(step_backs))) + "\t\t" + beat_file

for i in odd_songs.keys():
	print odd_songs[i]

