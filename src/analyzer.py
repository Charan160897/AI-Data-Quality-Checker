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

def get_summary_statistics(df):
    """
    Returns summary statistics for numeric columns.
    """
    return df.describe().T

def get_numeric_columns(df):

    return df.select_dtypes(include="number").columns.tolist()

def detect_outliers(df):

    numeric_columns = df.select_dtypes(include="number")

    outlier_report = {}

    for column in numeric_columns.columns:

        Q1 = df[column].quantile(0.25)

        Q3 = df[column].quantile(0.75)

        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR

        upper = Q3 + 1.5 * IQR

        outliers = df[
            (df[column] < lower) |
            (df[column] > upper)
        ]

        outlier_report[column] = len(outliers)

    return outlier_report

def calculate_quality_score(df):

    missing = df.isnull().sum().sum()

    duplicates = df.duplicated().sum()

    outliers = sum(detect_outliers(df).values())

    score = 100 - missing - duplicates - outliers

    return max(score, 0)