import pandas as pd

from src.validator import detect_constant_columns


def test_constant_columns():

    df = pd.DataFrame({

        "A":[

            10,

            10,

            10

        ],

        "B":[

            1,

            2,

            3

        ]

    })

    result = detect_constant_columns(df)

    assert "A" in result