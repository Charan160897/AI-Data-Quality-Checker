import pandas as pd

def generate_report(
    missing_df,
    percentage_df,
    outlier_df
):

    report = pd.concat(

        [

            missing_df,

            percentage_df["Missing Percentage"],

            outlier_df["Outliers"]

        ],

        axis=1

    )

    return report