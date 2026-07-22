import pandas as pd

from src.analyzer import (
    get_duplicate_rows,
    get_missing_values,
    calculate_quality_score
)


def test_duplicate_rows():

    df = pd.DataFrame({

        "Name":[

            "John",

            "John",

            "Mike"

        ]

    })

    assert get_duplicate_rows(df) == 1


def test_missing_values():

    df = pd.DataFrame({

        "Age":[

            20,

            None,

            30

        ]

    })

    result = get_missing_values(df)

    assert result["Age"] == 1


def test_quality_score():

    df = pd.DataFrame({

        "A":[

            1,

            2,

            3

        ]

    })

    assert calculate_quality_score(df) == 100