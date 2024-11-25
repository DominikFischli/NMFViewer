import pandas as pd

def transform_time_grades(time_grades: pd.DataFrame, sampling_frequency=50):
    time_grades.loc[:, 'Onset':'Duration'] = round(time_grades.loc[:, 'Onset':'Duration'] * sampling_frequency)
    return time_grades

