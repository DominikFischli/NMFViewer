import pandas as pd
import numpy as np


def transform_time_grades(
    time_grades: pd.DataFrame, sampling_frequency: int = 50
) -> pd.DataFrame:
    """
    Loads the time grades based in the Dataframe and sets time values to indices of the corresponding data matrix.
    Columns "Onset" and "Duration" are assumed to hold IED onset and duration.

    Parameters
    ----------
    sampling_frequency : int
        Sampling frequency of the corresponding data matrix
    time_grades : pd.DataFrame
        DataFrame containing columns "Onset" and "Duration", values are expected to be in seconds and relative to the data start.

    Returns
    -------
    pd.DataFrame
        The transformed dataframe

    """
    time_grades.loc[:, "Onset":"Duration"] = round(
        time_grades.loc[:, "Onset":"Duration"] * sampling_frequency
    )
    return time_grades


def transform_triggers(
    triggers: np.ndarray, sampling_frequency: int = 50
) -> np.ndarray:
    """
    Converts trigger values to index values.
    Triggers are expected to be values in seconds since the start of the recording.

    Parameters
    ----------
    sampling_frequency : int
        Sampling frequency of the recording
    triggers : np.ndarray
        Numpy array containing trigger time points in seconds

    Returns
    -------
    np.ndarray
        Numpy array containing indices corresponding to trigger time points.

    """
    triggers *= sampling_frequency
    return np.rint(triggers)
