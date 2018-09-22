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
	return y, sr, destination_path

def audio_to_madmom_ddf(y, savefile_stem=None):
	if savefile_stem is not None:
		if os.path.exists(savefile_stem + "_ddf.mat"):
			ddf = sp.io.loadmat(savefile_stem + "_ddf")['ddf']
			return ddf
	y_mono = librosa.core.to_mono(y)
	detection_function = madmom.features.beats.RNNDownBeatProcessor()(y_mono)
	if savefile_stem is not None:
		sp.io.savemat(savefile_stem, {'ddf':detection_function})
	return detection_function

def madmom_ddf_to_downbeats(detection_function, sr, bar_opts=[3,4]):
	fps_ratio = sr * 1.0 / 44100
	downbeat_estimates = madmom.features.beats.DBNDownBeatTrackingProcessor(beats_per_bar=bar_opts, fps=int(100*fps_ratio))(detection_function)
	return downbeat_estimates

def madmom_ddf_to_beats(detection_function, sr):
	fps_ratio = sr * 1.0 / 44100
	beat_estimates = madmom.features.beats.DBNBeatTrackingProcessor(fps=int(100*fps_ratio))(detection_function)
	return beat_estimates

def get_ddf_feats_from_bar_onsets(ddf, bar_onsets):
	feats_i = []
	for t in range(len(bar_onsets_i)-1):
		t1 = int(100*bar_onsets_i[t])
		t2 = int(100*bar_onsets_i[t+1])
		feature_seq_t = ddf[t1:t2,:]
		feats_i += [feature_seq_t[:,1]]   # Take just the 2nd column, which is the downbeat detection function. 1st col has beat detection function.
	return feats_i

# Get audio from Youtube or local directory:
you_make_me = "I98OWrboh-M"
y, sr, filepath = load_audio_from_youtube(you_make_me)
filepath = "./01 Hey Ya.mp3"
filepath = "./10 The Stars.mp3"
filepath = "./Weird Al Yankovic Even Worse - You Make Me.mp4"
y, sr = load_audio(filepath)
savefile_stem = os.path.splitext(os.path.basename(filepath))[0]

# Do beat tracking using madmom
ddf = audio_to_madmom_ddf(y, savefile_stem)

# The downbeat tracking of this madmom function assumes a constant bar length.
# So if any bars are shortened or lengthened, or the time signature changes, the phase of the estimated downbeats will be thrown off.
# Let's compare every pair of bars, considering every different initial offset in beats.
# We will characterize each bar by its DDF.
beat_est = madmom_ddf_to_downbeats(ddf, sr, bar_opts=[3,4])
beat_est_only = madmom_ddf_to_beats(ddf[:,0], sr)
beat_est = np.stack((beat_est_only, np.zeros_like(beat_est_only)), axis=1)
bar_length = int(np.max(beat_est[:,1]))
bar_length = 4
# Generate different hypothesis downbeat streams
bar_onsets = [beat_est[range(i,beat_est.shape[0],bar_length),0] for i in range(bar_length)]
# For each, collect DDF excerpts as our features.
feats = [get_ddf_feats_from_bar_onsets(ddf, onsets) for onsets in bar_onsets]


# For each bar_onset hypothesis, we create a different feature set, and these are assembled in feats. Thus:
len(feats) == bar_length
# Each sequence of bar-features has the same length, the number of bars (which should be equal to each other.)
[len(feat) for feat in feats]
# But the "feature" for each bar (the downbeat detection function for it) can have slightly different lengths.
collections.Counter([len(x) for x in feats[0]])
# Therefore, to compare them, we will either need to truncate/pad them to some fixed length, or use a flexible similarity metric like DTW distance.

# To start, look at truncations:
# Generate self-similarity matrix for all paris of beat-stream-feature_sets

def compute_dists_from_ddf_feats(feats):
	bar_length = len(feats)
	n_bars = len(feats[0])
	dists = np.zeros((bar_length, n_bars, n_bars))
	for i in range(bar_length):
		for k_x in range(n_bars-1):
			for k_y in range(n_bars-1):
				x = feats[0][k_x]
				y = feats[i][k_y]
				if len(x)>0 and len(y)>0:
					min_len = np.min((len(x),len(y)))
					dists[i,k_x,k_y] = cosine(x[:min_len], y[:min_len])
	return dists


dists = compute_dists_from_ddf_feats(feats)
dists = dists[:,:80,:80]
plt.figure(1)
for i in range(4):
	plt.subplot(2,2,i+1)
	plt.imshow(dists[i,:,:])
	plt.title("Phase-0 vs. Phase-"+str(i))

plt.tight_layout()
plt.savefig(savefile_stem + "_phase_comp.jpg")
plt.figure(2)
# make "phase-invariant" bar-similarity matrix
plt.imshow(np.min(dists,axis=0))
plt.title("Min across all Phase-0-Phase-X plots")
plt.tight_layout()
plt.savefig(savefile_stem + "_phase_invariant.jpg")

plt.figure(3)
# make "phase-invariant" bar-similarity matrix
plt.imshow(np.argmin(dists,axis=0))
plt.title("Min across all Phase-0-Phase-X plots")
plt.tight_layout()
plt.savefig(savefile_stem + "_argmin_phase_invariant.jpg")













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

