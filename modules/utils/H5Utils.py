import numpy as np

from h5py import File, Dataset, Group

def find_dataset_paths(recording: File, path = ''):
    if len(path) == 0:
        paths = []
        for key in recording.keys():
            paths += find_dataset_paths(recording, '/' + key)
        return paths


    if not path_valid(recording, path):
        return []

    elif isinstance(recording[path], Group):
        paths = []
        for key in recording[path].keys():
            paths += find_dataset_paths(recording, '/'.join([path, key]))
        return paths
    elif isinstance(recording[path], Dataset):
        return [path]
    return []

def path_valid(recording, path):
    try:
        return len(recording[path])
    except:
        print(f"path invalid: {path}")
        return 0



def find_channel_paths(recording: File):
    paths = find_dataset_paths(recording)
    return filter_list_for('bipolar/lead', paths)

def read_recording_duration(recording: File):
    return recording['meta'].attrs['duration']

def read_start_timestamp(recording: File):
    return int(recording['meta'].attrs['start_timestamp'])

def read_utility_freq(recording: File):
    return recording['meta'].attrs['utility_freq']

def get_n_samples(recording: File):
    return len(recording[find_channel_paths(recording)[0]])

def get_frequency(recording: File):
    n = get_n_samples(recording)
    t = read_recording_duration(recording)
    return int(n / t)

def load_data(recording, paths=None):
    if paths is None:
        paths = find_channel_paths(recording)

    data = []
    for path in paths:
        try:
            data.append(np.array(recording[path]))
        except:
            print(f'data loading failed for path {path}')
    return np.vstack(data).astype(float)

def print_summary(recording: File):
    start_timestamp = read_start_timestamp(recording)
    n_samples = get_n_samples(recording)
    duration = read_recording_duration(recording)
    frequency = get_frequency(recording)
    channels = find_channel_paths(recording)
    print(f'start_timestamp:\t{start_timestamp}\nsamples:\t\t{n_samples}\nduration:\t\t{duration}\nfrequency:\t\t{frequency}\nchannels:\t\t{len(channels)}')
    
def get_timestamp(recording: File, index: int):
    start_timestamp = read_start_timestamp(recording)
    duration = read_recording_duration(recording)
    n_samples = get_n_samples(recording)
    
    return start_timestamp + index * duration / n_samples

def get_timestamps(recording: File, indices):
    return [get_timestamp(recording, index) for index in indices]

def get_index(recording: File, time):
    '''
    time: Time since start of recording measured in seconds.
    '''
    duration = read_recording_duration(recording)
    n_samples = get_n_samples(recording)
    
    return int(n_samples * time / duration)

def filter_list_for(s: str, paths: list[str]):
    return list(filter(lambda path: s in path, paths))
