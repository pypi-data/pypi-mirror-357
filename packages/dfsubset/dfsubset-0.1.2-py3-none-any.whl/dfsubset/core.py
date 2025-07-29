import pandas as pd

def subset(data, condition=None, select=None):
    """
    A powerful R-style subset function for pandas DataFrames.

    Parameters:
        data (DataFrame): Your table.
        condition (str): Row filter condition, written as a string (e.g. 'score > 70').
        select (str or list of str): Columns to keep.

    Returns:
        A new DataFrame with filtered rows and selected columns.
    """
    df = data

    if condition is not None:
        df = df.query(condition)

    if select is not None:
        if isinstance(select, str):
            select = [select]
        df = df[select]

    return df