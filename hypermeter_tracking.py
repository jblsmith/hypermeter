import os
from hypermeter.utils import load_audio, load_audio_from_youtube, audio_to_madmom_ddf, madmom_ddf_to_downbeats, madmom_ddf_to_beats, get_ddf_feats_from_bar_onsets, compute_dists_from_ddf_feats
import numpy as np
import scipy as sp
import madmom
import librosa, librosa.display
import mir_eval
import pytube
import matplotlib.pyplot as plt
plt.ion()
plt.close("all")
from matplotlib import gridspec
import collections
from scipy.spatial.distance import euclidean, cosine



# # Get audio from Youtube or local directory:
# you_make_me = "I98OWrboh-M"
# y, sr, filepath = load_audio_from_youtube(you_make_me)
# filepath = "./01 Hey Ya.mp3"
# filepath = "./10 The Stars.mp3"
filepath = "/Users/rhennequin/Downloads/Weird Al Yankovic Even Worse - You Make Me.mp4"
filepath = "/Users/rhennequin/Downloads/01 Hey Ya.mp3"
filepath = "/Users/rhennequin/Downloads/love_is_all.mp3"
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
bar_length = 3
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




dists = compute_dists_from_ddf_feats(feats)
# dists = dists[:,:80,:80]
plt.figure(1)
for i in range(bar_length):
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
cmap = plt.cm.get_cmap('jet', bar_length)
plt.imshow(np.argmin(dists,axis=0),cmap=cmap, interpolation="nearest")
plt.title("Argmin across all Phase-0-Phase-X plots")
# plt.colorbar()
plt.tight_layout()
plt.savefig(savefile_stem + "_argmin_phase_invariant.jpg")
plt.colorbar()
