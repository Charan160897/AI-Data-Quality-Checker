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

def generate_ai_summary(

    score,

    missing,

    duplicates

):

    if score > 95:

        return "Excellent dataset ready for ML."

    elif score > 80:

        return "Good dataset with minor issues."

    else:

        return "Dataset needs cleaning before analysis."
    
def cleaning_suggestions(df):

    suggestions = []

    if df.isnull().sum().sum() > 0:

        suggestions.append(

            "Fill missing values."

        )

    if df.duplicated().sum() > 0:

        suggestions.append(

            "Remove duplicate rows."

        )

    if len(suggestions) == 0:

        suggestions.append(

            "No cleaning required."

        )

    return suggestions