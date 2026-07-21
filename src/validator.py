import pandas as pd


def validate_column_names(df):
    """
    Detect empty or duplicate column names.
    """
    issues = []

    if df.columns.duplicated().any():
        issues.append("Duplicate column names found.")

    for col in df.columns:
        if str(col).strip() == "":
            issues.append("Empty column name found.")

    return issues


def detect_constant_columns(df):
    """
    Detect columns containing only one unique value.
    """
    constant_columns = []

    for col in df.columns:
        if df[col].nunique(dropna=False) == 1:
            constant_columns.append(col)

    return constant_columns


def unique_value_report(df):
    """
    Return unique value count for every column.
    """
    return df.nunique(dropna=False)

def validate_numeric_columns(df):

    issues = []

    numeric = df.select_dtypes(include="number")

    for column in numeric.columns:

        if df[column].min() < 0:

            issues.append(
                f"{column} contains negative values."
            )

    return issues