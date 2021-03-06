import numpy as np
import scipy as sp
import madmom
import librosa, librosa.display
import mir_eval
import pytube
import collections
from scipy.spatial.distance import euclidean, cosine
import os
from joblib import Memory

memory = Memory("/tmp/cache/")

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

@memory.cache()
def audio_to_madmom_ddf(y):
	y_mono = librosa.core.to_mono(y)
	detection_function = madmom.features.beats.RNNDownBeatProcessor()(y_mono)
	return detection_function

@memory.cache()
def audio_to_madmom_bdf(y):
	y_mono = librosa.core.to_mono(y)
	detection_function = madmom.features.beats.RNNBeatProcessor()(y_mono)
	return detection_function

@memory.cache()
def madmom_bdf_to_beats(beat_detection_function, sr):
	fps_ratio = sr * 1.0 / 44100
	beat_estimates = madmom.features.beats.DBNBeatTrackingProcessor(fps=int(100*fps_ratio))(beat_detection_function)
	return beat_estimates


@memory.cache()
def madmom_ddf_to_downbeats(detection_function, sr, bar_opts=[3,4]):
	fps_ratio = sr * 1.0 / 44100
	downbeat_estimates = madmom.features.beats.DBNDownBeatTrackingProcessor(beats_per_bar=bar_opts, fps=int(100*fps_ratio))(detection_function)
	return downbeat_estimates

@memory.cache()
def madmom_ddf_to_beats(detection_function, sr):
	fps_ratio = sr * 1.0 / 44100
	beat_estimates = madmom.features.beats.DBNBeatTrackingProcessor(fps=int(100*fps_ratio))(detection_function)
	return beat_estimates

@memory.cache()
def get_ddf_feats_from_bar_onsets(ddf, bar_onsets):
	feats_i = []
	for t in range(len(bar_onsets)-1):
		t1 = int(100*bar_onsets[t])
		t2 = int(100*bar_onsets[t+1])
		feature_seq_t = ddf[t1:t2,:]
		feats_i += [feature_seq_t[:,1]]   # Take just the 2nd column, which is the downbeat detection function. 1st col has beat detection function.
	return feats_i

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
