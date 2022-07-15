import pandas as pd


def annotation_to_pandas(data: list) -> pd.DataFrame:
    """
    Convert list of path to a pandas table with coordinates.

    Parameters
    ----------
    data : list
        List of paths, each of which is a list of coordinates.

    Returns
    -------
    pd.DataFrame:
        pandas DataFrame with coordinates
    """

    df = pd.DataFrame()
    if len(data) > 0:
        columns = ['t', 'z', 'y', 'x']
        columns = columns[-data[0].shape[1]:]
        for i, d in enumerate(data):
            cur_df = pd.DataFrame(d, columns=columns)
            cur_df['id'] = i
            df = pd.concat([df, cur_df], ignore_index=True)
    return df
