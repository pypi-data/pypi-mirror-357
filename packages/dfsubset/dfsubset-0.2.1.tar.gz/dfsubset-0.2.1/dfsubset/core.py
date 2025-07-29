import pandas as pd

def subset(data, condition=None, select=None, summarize=None, save_as=None):
    """
    Simplified subsetting function like R's subset().

    Parameters:
        data (DataFrame): Your main table.
        condition (str): A filter expression for rows (e.g., 'score > 70').
        select (list, str, or dict): Columns to keep. If dict, rename them too.
        summarize (str or list): Column(s) to summarize (mean, median, min, max, std).
        save_as (str): If given, saves the result to a CSV file.

    Returns:
        DataFrame or Series: A filtered and/or selected DataFrame or summary statistics.
    """
    df = data

    if condition is not None:
        df = df.query(condition)

    if select is not None:
        if isinstance(select, dict):
            cols = list(select.keys())
            df = df[cols]
            df = df.rename(columns=select)
        elif isinstance(select, str):
            df = df[[select]]
        elif isinstance(select, list):
            df = df[select]

    if summarize is not None:
        if isinstance(summarize, str):
            cols = [summarize]
        else:
            cols = summarize
        return df[cols].agg(['mean', 'median', 'min', 'max', 'std']).transpose()

    if save_as:
        df.to_csv(save_as, index=False)

    return df