import librosa
import parselmouth
import numpy as np
import noisereduce as nr
import matplotlib.pyplot as plt


def get_features(wav_path, denoise=False, noise_width=0.5, ms1_w=1, ms2_w=1, ms3_w=1):
    y, sr = librosa.load(wav_path, sr=None)

    # get noise window
    if denoise:
        noise_start, noise_stop = get_noise_window(y, sr, win_len=noise_width)
        noise_start = librosa.time_to_samples(noise_start, sr=sr)
        noise_stop = librosa.time_to_samples(noise_stop, sr=sr)
        noise = y[noise_start:noise_stop]
        y = nr.reduce_noise(y=y, sr=int(sr), n_jobs=-1, stationary=False, prop_decrease=1, y_noise=noise)

    # resample
    target_sr = 48000
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

    # padding/trimming
    target_dur = 1.5
    target_sample = int(target_dur * target_sr)
    if len(y) < target_sample:
        pad_width = target_sample - len(y)
        y = np.pad(y, pad_width=(0, pad_width))
    else:
        y = y[:target_sample]

    # pre-emphasis
    y = librosa.effects.preemphasis(y, coef=0.97)

    # multi hop spectrogram
    f_max = 5500
    ms1 = librosa.feature.melspectrogram(y=y, sr=target_sr, n_fft=1024, n_mels=80, fmax=f_max, hop_length=128, window='hamming')
    ms2 = librosa.feature.melspectrogram(y=y, sr=target_sr, n_fft=512, n_mels=40, fmax=f_max, hop_length=128, window='hamming')
    ms3 = librosa.feature.melspectrogram(y=y, sr=target_sr, n_fft=256, n_mels=20, fmax=f_max, hop_length=128, window='hamming')
    ms1 = ms1[:, :6000]
    ms2 = np.repeat(ms2, 2, axis=0)[:, :6000]
    ms3 = np.repeat(ms3, 4, axis=0)[:, :6000]
    ms1 = ms1 * ms1_w
    ms2 = ms2 * ms2_w
    ms3 = ms3 * ms3_w
    ms_total = (ms1 + ms2 + ms3) / (ms1_w + ms2_w + ms3_w)  # weighted blended spectrum
    ms1 = librosa.core.power_to_db(ms1, ref=np.max)
    ms2 = librosa.core.power_to_db(ms2, ref=np.max)
    ms3 = librosa.core.power_to_db(ms3, ref=np.max)
    ms_total = librosa.core.power_to_db(ms_total, ref=np.max)

    '''
    # praat spectrogram
    y = y.astype(np.float64)
    snd = parselmouth.Sound(values=y, sampling_frequency=target_sr)
    f_max = 5500
    spectrogram = snd.to_spectrogram(window_length=0.005, time_step=0.002, maximum_frequency=f_max, frequency_step=50)
    ms_total = 10 * np.log10(spectrogram.values + 1e-10)
    ms1 = ms_total
    ms2 = ms_total
    ms3 = ms_total
    # print(ms_total.shape)
    '''

    # normalize
    data_min = np.min(ms_total)
    data_max = np.max(ms_total)
    ms_total = (ms_total - data_min) / (data_max - data_min)

    return ms1, ms2, ms3, ms_total


def get_noise_window(y, sr, win_len=0.5, nfft=2048):
    dur = librosa.get_duration(y=y, sr=sr)
    s = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=nfft, n_mels=80, hop_length=int(nfft/2), window='hamming')
    win_npts = round((win_len / dur) * s.shape[1])

    if win_len > dur:
        return -1

    for k in range(1, (s.shape[1] - win_npts)):  # loop time points
        amp_std = 0

        for kk in range(s.shape[0]):  # loop frequencies
            amp_std_f = np.std(np.abs(s[kk, k:k + win_npts]) ** 2)
            amp_std += amp_std_f

        if k == 1:
            min_std_idx = 1
            cur_min_std = amp_std
        else:
            if amp_std < cur_min_std:
                cur_min_std = amp_std
                min_std_idx = k

    n_start_t = min_std_idx / s.shape[1] * dur
    n_stop_t = (min_std_idx + win_npts) / s.shape[1] * dur

    return n_start_t, n_stop_t


def view_features(audio, denoise, noise_width, ms1, ms2, ms3):
    spec_1, spec_2, spec_3, spec_t = get_features(wav_path=audio, denoise=denoise, noise_width=noise_width, ms1_w=ms1, ms2_w=ms2, ms3_w=ms3)
    fig, axes = plt.subplots(4, 1)
    librosa.display.specshow(spec_1, ax=axes[0], cmap='gray_r')
    librosa.display.specshow(spec_2, ax=axes[1], cmap='gray_r')
    librosa.display.specshow(spec_3, ax=axes[2], cmap='gray_r')
    librosa.display.specshow(spec_t, ax=axes[3], cmap='gray_r')
    plt.show()

