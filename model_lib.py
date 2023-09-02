import json
import os
import numpy as np
import librosa

# -------------------------------------------
# --------- Parameters ---------------------
max_pad_len = 190
n_mfcc = 13


# -------------------------------------------
# --------- Preprocessing -------------------
def extract_mfcc(file_path, max_pad_len=max_pad_len, n_mfcc=n_mfcc):
    """Extract MFCC from .wav file."""
    y, sr = librosa.load(file_path, mono=True, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    pad_width = max_pad_len - mfcc.shape[1]
    mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode="constant")
    return mfcc
