import pandas as pd

from .const import COLS, COL_NAME


def annotation_to_pandas(data: list) -> pd.DataFrame:
    """
    Convert list of paths to a pandas table with coordinates.

    Parameters
    ----------
    data : list
        List of paths, each of which is a list of coordinates of shape N x 3,
            where N is the number of points in the path.

    Returns
    -------
    pd.DataFrame:
        pandas DataFrame with coordinates
    """

    df = pd.DataFrame()
    if len(data) > 0:
        for i, d in enumerate(data):
            cur_df = pd.DataFrame(d, columns=COLS)
            cur_df[COL_NAME] = i
            df = pd.concat([df, cur_df], ignore_index=True)
    return df


def pandas_to_annotations(df: pd.DataFrame) -> list:
    """
    Convert pandas table with coordinate to a list of paths.

    Parameters
    ----------
    df : pd.DataFrame
        pandas DataFrame with coordinates, including an ID column for individual paths.

    Returns
    -------
    list:
        List of paths, each of shape N x 3
    """
    data = []
    labels = []
    if len(df) > 0:
        for s in df[COL_NAME].unique():
            d = df[df[COL_NAME] == s][COLS].values
            data.append(d)
            labels.append(s)
    return data, labels
