
# new trick! joblib version of the above, for quick computation and saving:

from joblib import Memory
mem = Memory(cachedir='~/Documents/repositories/hypermeter/')

@mem.cache()
def get_detection_function(y_mono):
    return madmom.features.beats.RNNDownBeatProcessor()(y_mono)

@mem.cache()
def audiopath_to_ddf(filepath):
	y, sr = load_audio(filepath)
	y_mono = librosa.core.to_mono(y)
	detection_function = madmom.features.beats.RNNDownBeatProcessor()(y_mono)
	return detection_function

audiopath_to_ddf("./10 The Stars.mp3")
audiopath_to_ddf("/Users/jordan/Dropbox/Ircam/hackday/10 The Stars.mp3")
neat_song_paths = ["/Users/jordan/Music/iTunes/iTunes Music/Rubblebucket/Omega La La/04 Came Out Of A Lady.m4a",
	"/Users/jordan/Music/iTunes/iTunes Music/Final Fantasy/Spectrum, 14th Century/01 Oh Spectrum.mp3",
	"/Users/jordan/Music/iTunes/iTunes Music/Sebastien Tellier/Politics/05 La ritournelle.mp3",
	"/Users/jordan/Music/iTunes/iTunes Music/Paul Simon/Rhythm Of The Saints/03 The Coast.mp3",
	"/Users/jordan/Music/iTunes/iTunes Music/Paul Simon/Rhythm Of The Saints/08 The Cool, Cool River.mp3",
	"/Users/jordan/Music/iTunes/iTunes Music/Paul Simon/Rhythm Of The Saints/10 Rhythm Of The Saints.mp3"]

for songpath in neat_song_paths:
	audiopath_to_ddf(songpath)



ddf = audiopath_to_ddf(neat_song_paths[5])
savefile_stem = "the_cool_cool_river"
# detection_function = get_detection_function(y_mono)```

# Get audio from Youtube or local directory:
you_make_me = "I98OWrboh-M"
silence = "RZYpzXjdtwg"
y, sr, filepath = load_audio_from_youtube(rapunzel)
filepath = "./01 Hey Ya.mp3"
filepath = "./10 The Stars.mp3"
filepath = "./Weird Al Yankovic Even Worse - You Make Me.mp4"
y, sr = load_audio(filepath)
savefile_stem = os.path.splitext(os.path.basename(filepath))[0]

# Do beat tracking using madmom
ddf = audio_to_madmom_ddf(y, savefile_stem)

plt.figure(1),plt.clf()
plt.plot(-ddf[:,0])
plt.plot(ddf[:,1])
plt.xlim([7860,9250])

# The downbeat tracking of this madmom function assumes a constant bar length.
# So if any bars are shortened or lengthened, or the time signature changes, the phase of the estimated downbeats will be thrown off.
# Let's compare every pair of bars, considering every different initial offset in beats.
# We will characterize each bar by its DDF.

# Use downbeat tracking:
beat_est = madmom_ddf_to_downbeats(ddf, sr, bar_opts=[3,4,5,6,7,8,9])
bar_length = int(np.max(beat_est[:,1]))

# Use beat tracking
beat_est_only = madmom_ddf_to_beats(ddf[:,0], sr)
beat_est = np.stack((beat_est_only, np.zeros_like(beat_est_only)), axis=1)

dist_set = []
for bar_length in range(2,9):
	print bar_length
	bar_onsets = [beat_est[range(i,beat_est.shape[0],bar_length),0] for i in range(bar_length)]
	feats = [get_ddf_feats_from_bar_onsets(ddf, onsets) for onsets in bar_onsets]
	dists = compute_dists_from_ddf_feats(feats)
	dist_set += [dists]


plt.figure(1)
plt.clf()
for i,dists in enumerate(dist_set):
	plt.subplot(3,3,i+1)
	plt.imshow(np.argmin(dists,axis=0))
	plt.title(str(i+2)+"/4")
	plt.colorbar()


	plt.figure(3)
	# make "phase-invariant" bar-similarity matrix
	plt.imshow(np.argmin(dists,axis=0))
	plt.title("Argmin across all Phase-0-Phase-X plots")
	plt.colorbar()
	plt.tight_layout()
	plt.savefig(savefile_stem + "_argmin_phase_invariant.jpg")
	
	
bar_length = 9

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



dists = compute_dists_from_ddf_feats(feats)
# dists = dists[:,:80,:80]
plt.figure(1)
for i in range(9):
	plt.subplot(3,3,i+1)
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
plt.title("Argmin across all Phase-0-Phase-X plots")
plt.colorbar()
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
