import pandas as pd

from src.analyzer import (
    calculate_quality_score,
    detect_outliers,
    get_duplicate_rows,
    get_missing_values,
)


def test_duplicate_rows():
    df = pd.DataFrame({"A": [1, 1, 2]})

    assert get_duplicate_rows(df) == 1


def test_missing_values():
    df = pd.DataFrame({"A": [1, None, 3]})

    result = get_missing_values(df)

    assert result["A"] == 1


def test_outlier_detection():
    df = pd.DataFrame(
        {
            "Salary": [
                50000,
                51000,
                49000,
                50500,
                2500000,
            ]
        }
    )

    result = detect_outliers(df)

    assert result["Salary"] == 1


def test_clean_dataset_quality_score():
    df = pd.DataFrame({"A": [1, 2, 3]})

    assert calculate_quality_score(df) == 100