def generate_recommendations(
    missing,
    duplicates,
    score
):

    recommendations = []

    if missing > 0:
        recommendations.append(
            "Fill missing values before model training."
        )

    if duplicates > 0:
        recommendations.append(
            "Remove duplicate records."
        )

    if score < 90:
        recommendations.append(
            "Dataset quality can be improved."
        )

    if len(recommendations) == 0:
        recommendations.append(
            "Dataset quality is excellent."
        )

    return recommendations

def dataset_summary(
    rows,
    columns,
    score
):

    return f"""
Dataset contains {rows} rows
and {columns} columns.

Overall quality score is
{score}%.

The dataset is ready
for analysis.
"""