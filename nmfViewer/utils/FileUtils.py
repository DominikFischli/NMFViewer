import pandas as pd
import os

from h5py import File


def load_time_grades(filepath: str) -> pd.DataFrame:
    """
    Loads time grades from the indicated filepath.
    Expects a csv or h5 file at `filepath`.

    Parameters
    ----------
    filepath : str
        Filepath containing time grade data. CSV or HDF5 format.

    Returns
    -------
    pd.DataFrame
        Dataframe containing "Onset", "Duration" and "Description" columns.
        "Description" contains information about what kind of time has been graded.

    """
    _filename, file_extension = os.path.splitext(filepath)
    if file_extension == ".csv":
        return pd.read_csv(filepath)
    elif file_extension == ".h5":
        return load_from_h5(filepath)
    else:
        print(f"file not csv or h5 format: {filepath}")
        return pd.DataFrame()


def load_from_h5(filepath: str) -> pd.DataFrame:
    """
    Loads time grades from HDF5 file.

    Parameters
    ----------
    filepath : str
        Filepath pointing to HDF5 file.
        The following datasets are expected:
        "/time_grades/text"     -> Descriptive entries
        "/time_grades/time"     -> Onset of time period
        "/time_grades/duration" -> Duration of time period

    Returns
    -------
    pd.DataFrame
        Dataframe containing "Onset", "Duration" and "Description" columns.
        "Description" contains information about what kind of time has been graded.

    """
    recording = File(filepath)

    with File(filepath) as recording:
        description = recording["/time_grades/text"]
        onset = recording["/time_grades/time"]
        dur = recording["/time_grades/duration"]

        time_grades = pd.DataFrame(
            {"Description": description, "Onset": onset, "Duration": dur}
        )
        time_grades["Description"] = time_grades["Description"].str.decode("utf-8")

        return time_grades
