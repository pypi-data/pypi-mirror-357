import os
import csv
from tqdm import tqdm
from sklearn.model_selection import train_test_split
import pandas as pd
from mandsot import features
import torch
from torch.utils.data import Dataset, random_split, DataLoader


class VoiceDataset(Dataset):
    def __init__(self, dataframe, sr=48000, hop_length=128):
        self.dataframe = dataframe
        self.sr = sr
        self.hop_length = hop_length

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        mfcc = torch.from_numpy(self.dataframe.iloc[idx]['mfcc']).float()
        onset = self.dataframe.iloc[idx]['onset']
        initial = self.dataframe.iloc[idx]['initial']
        onset_frame = (onset/1000) * self.sr / self.hop_length  # → float frame index
        return mfcc, onset_frame, initial


class PredictionDataset(Dataset):
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        path = self.dataframe.iloc[idx]['location']
        mfcc = torch.from_numpy(self.dataframe.iloc[idx]['mfcc']).float()
        return mfcc, path


# scan directory and return files
def scan_dir(root_dir):
    roots, files = [], []
    for root, _, file in os.walk(root_dir):
        for item in file:
            files.append(item)
            roots.append(root)
    return roots, files


# find wav filename
def find_wav(name, roots, files):
    if name in files:
        return os.path.join(roots[files.index(name)], name)


def write_all_wav_to_csv(root_dir, output_csv):
    wav_paths = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.wav'):
                full_path = os.path.abspath(os.path.join(root, file))
                wav_paths.append(full_path)

    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        for path in wav_paths:
            writer.writerow([path])


def load_data_from_subject_csv(root_dir, output_name, rt_max, csv_encoding, verbose):
    roots, files = scan_dir(root_dir)
    csvs, wav_files, wav_dirs, wav_onsets, wav_initials = [], [], [], [], []

    # root_ctn = os.listdir(root_dir)
    root_list, file_list = scan_dir(root_dir)
    for idx, ctn in enumerate(file_list):
        if ctn.endswith('.csv') and not ctn.startswith('.'):
            csvs.append(os.path.join(root_list[idx], ctn))

    for csv_file in csvs:
        if verbose:
            print('Reading CSV: '+csv_file)
        with open(csv_file, 'r', encoding=csv_encoding) as csv_in:
            lines = csv.reader(csv_in)
            next(lines)
            for line in lines:
                if line[3] == "1" and line[2] != '' and line[2] != '--undefined--' and line[1] != '' and (float(line[2]) <= rt_max):
                    '''
                    # load with initial codings
                    i_code = get_mand_initial_coding(get_pinyin_from_code(int(line[1].split('/')[-1].split('-')[4])))
                    if i_code:
                        wav_files.append(line[1])
                        wav_dirs.append(find_wav(line[1], roots, files))
                        wav_onsets.append(float(line[2]))
                        wav_initials.append(int(i_code))
                    '''

                    # load without initial codings
                    wav_files.append(line[1])
                    wav_dirs.append(find_wav(line[1], roots, files))
                    wav_onsets.append(float(line[2]))
                    wav_initials.append(int(0))
    dataset = pd.DataFrame({'wav': wav_files, 'location': wav_dirs, 'onset': wav_onsets, 'initial': wav_initials})
    dataset.to_csv(output_name, index=False)
    if verbose:
        print('\nLoaded training data:')
        print(dataset)
    return dataset


def get_mand_initial_coding(input_str):
    code_mapping = {
        'b': 1,
        'p': 2,
        'm': 3,
        'f': 4,
        'd': 5,
        't': 6,
        'n': 7,
        'l': 8,
        'g': 9,
        'k': 10,
        'h': 11,
        'j': 12,
        'q': 13,
        'x': 14,
        'zh': 15,
        'ch': 16,
        'sh': 17,
        'r': 18,
        'z': 19,
        'c': 20,
        's': 21,
        'a': 22,
        'o': 23,
        'e': 24,
        'yuan': 25,
        'yue': 26,
        'yun': 27,
        'yu': 28,
        'y': 29,
        'w': 30
    }
    for key in code_mapping:
        if input_str.lower().startswith(key):
            return code_mapping[key]
    return 0


def get_pinyin_from_code(code):
    code_mapping = {
        16: 'deng1',
        17: 'shu4',
        18: 'tian1',
        19: 'chao1',
        20: 'chen4',
        21: 'gua1',
        22: 'mao2',
        23: 'wu1',
        24: 'bian1',
        25: 'yuan2',
        26: 'xue1',
        27: 'gan1',
        28: 'mi4',
        29: 'gong1',
        30: 'dan4',
        31: 'xiao3',
        32: 'wan1',
        33: 'sha1',
        34: 'pi2',
        35: 'ji2',
        36: 'di4',
        37: 'wei2',
        38: 'mo4',
        39: 'ci2',
        40: 'mei2',
        41: 'jiao4',
        42: 'shi2',
        43: 'zhu2',
        44: 'ping2',
        45: 'xi1',
        46: 'wen2',
        47: 'ya3',
        48: 'jian3',
        49: 'er3',
        50: 'jiang3',
        51: 'jie4',
        52: 'zhen3',
        53: 'yu3',
        54: 'wang3',
        55: 'zi3',
        56: 'jing4',
        57: 'qian2',
        58: 'hu2',
        59: 'qi4',
        60: 'zhang4',
        61: 'dian4',
        62: 'mu4',
        63: 'bei4',
        64: 'dun4',
        65: 'yun4',
        66: 'yan4',
        67: 'song1',
        68: 'gang1',
        69: 'jin1',
        70: 'xing4',
        71: 'shan1',
        72: 'ge1',
        73: 'qi3',
        74: 'qian1',
        75: 'ying1',
        76: 'shi4',
        77: 'bei1',
        78: 'ke1',
        79: 'zhuo1',
        80: 'feng1',
        81: 'ji1',
        82: 'yi1',
        83: 'dou4',
        84: 'jiao1',
        85: 'qiu1',
        86: 'tu2',
        87: 'mo2',
        88: 'tou2',
        89: 'ju2',
        90: 'wu2',
        91: 'mao4',
        92: 'wei3',
        93: 'di2',
        94: 'tang2',
        95: 'lian2',
        96: 'he2',
        97: 'ya2',
        98: 'shu3',
        99: 'bing3',
        100: 'gu3',
        101: 'zhi3',
        102: 'fu3',
        103: 'jing3',
        104: 'yu4',
        105: 'shou3',
        106: 'tan3',
        107: 'yan3',
        108: 'cheng2',
        109: 'jiu3',
        110: 'li4',
        111: 'la4',
        112: 'yao4',
        113: 'mu3',
        114: 'xiang4',
        115: 'jian4',
        116: 'bao4',
        117: 'tao2',
        118: 'bi4',
        119: 'you4'
    }
    return code_mapping.get(code, 'v')


def load_pred_from_dir(root_dir, verbose):
    wav_paths = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.wav'):
                abs_path = os.path.abspath(os.path.join(root, file))
                wav_paths.append(abs_path)
    df = pd.DataFrame({'location': wav_paths})
    if verbose:
        print('\nLoaded prediction data:')
        print(df)
    return df


def load_single_wav(wav_path, verbose):
    df = pd.DataFrame({'location': [wav_path]})
    if verbose:
        print('\nLoaded prediction data:')
        print(df)
    return df


def load_pred_csv(csv_file, verbose):
    dataset = pd.read_csv(csv_file)
    if verbose:
        print('\nLoaded prediction data:')
        print(dataset)
    return dataset


def load_train_csv(csv_file, verbose):
    if verbose:
        print('Reading CSV: ' + csv_file)
    dataset = pd.read_csv(csv_file)
    if verbose:
        print('\nLoaded training data:')
        print(dataset)
    return dataset


def load_features(dataset, noise, noise_width, w1, w2, w3, verbose):
    mfcc_list = []
    if verbose:
        print('\nPerforming feature extraction:')
    for idx, wav in enumerate(tqdm(dataset.location)):
        _, _, _, mfcc = features.get_features(wav, noise, noise_width, w1, w2, w3)
        mfcc_list.append(mfcc)
    dataset['mfcc'] = mfcc_list
    if verbose:
        print('\nData after feature extraction:')
        print(dataset)
    return dataset


def split_dataset(dataset, test_ratio, random_state):
    train_dataset, test_dataset = train_test_split(dataset, test_size=test_ratio, random_state=random_state)
    return train_dataset, test_dataset


def load_dataset(dataset, batch_size, shuffle):
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
