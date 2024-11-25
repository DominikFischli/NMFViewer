from typing import List
import numpy as np
import pandas as pd
import os

from h5py import File

def load_matrix(filepath) -> np.ndarray:
    return np.loadtxt(filepath, delimiter=',').T

def find_nmf_folders(folder) -> List:
    folders = []
    for root, _, files in os.walk(folder):
        if 'H_best.csv' in files:
            folders.append(root)
    return folders

def load_time_grades(filepath) -> pd.DataFrame:
    _filename, file_extension = os.path.splitext(filepath)
    if file_extension == '.csv':
        return pd.read_csv(filepath)
    elif file_extension == '.h5':
        return load_from_h5(filepath)
    else:
        print(f'file not csv or h5 format: {filepath}')
        return pd.DataFrame()

def load_from_h5(filepath) -> pd.DataFrame:
    recording = File(filepath)

    description = recording['/time_grades/text']
    onset = recording['/time_grades/time']
    dur = recording['/time_grades/duration']

    time_grades = pd.DataFrame({'Description': description, 'Onset': onset, 'Duration': dur})
    time_grades['Description'] = time_grades['Description'].str.decode("utf-8")

    return time_grades
 