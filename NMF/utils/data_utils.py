from .utils import change_interval

import pandas
import numpy as np

def transform_time_grades(time_grades: pandas.DataFrame, duration: float, N: int) -> pandas.DataFrame:
    """Transforms the time grades into indices corresponding to the indices
    of the `H` matrix.

    Parameters
    ----------
    time_grades : pandas.DataFrame
        Time grades. Needs to contain the rows Description, Onset and Duration.
    duration : float
        The total duration of the corresponding recording.
    N : int
        The maximum index of `H`

    Returns
    -------
    pandas.DataFrame
        A dataframe made up of the indices corresponding to the IED events of the time_grades dataframe. Rows 'Onset' and 'Offset' determine start/end of an event.

    """
    drop = time_grades[time_grades['Description'] == 'NOISY'].index
    time_grades = time_grades.drop(drop)
    time_grades = round(change_interval(time_grades.loc[:, 'Onset':'Duration'], 0, N, 0, duration))
    time_grades['Offset'] = time_grades.loc[:, 'Onset'] + time_grades.loc[:, 'Duration']
    return time_grades

def create_from_periods(index_df, label_start, label_end, max_index,  min_index = 0):
    result = np.zeros(max_index - min_index)
    for _, row in index_df.iterrows():
        if np.isnan(row.loc[label_start]) or np.isnan(row.loc[label_end]):
            continue
        period_start = int(row.loc[label_start])
        period_end = int(row.loc[label_end])

        assert period_end >= period_start

        if period_end < min_index or period_start > max_index:
            continue

        # clamp start and end indices to valid values
        period_start = max(period_start, min_index)
        period_end = min(period_end, max_index)
            
        result[max(0, period_start):min(len(result)-1, period_end)] = 1
    return result

def time_grade_predictions(time_grades: pandas.DataFrame, duration: float, N: int) -> np.ndarray:
    time_grades = transform_time_grades(time_grades, duration, N)
    return create_from_periods(time_grades, 'Onset', 'Offset', N, 0)
