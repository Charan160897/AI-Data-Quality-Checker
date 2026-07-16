import pandas as pd


def get_missing_values(df):
    """
    Returns missing values for each column.
    """
    return df.isnull().sum()


def get_missing_percentage(df):
    """
    Returns missing value percentage.
    """
    return (df.isnull().sum() / len(df)) * 100


def get_duplicate_rows(df):
    """
    Returns duplicate row count.
    """
    return df.duplicated().sum()