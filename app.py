import os
from pathlib import Path

import pandas as pd
import streamlit as st

import config
from src.ai_helper import (
    cleaning_suggestions,
    dataset_summary,
    generate_ai_summary,
    generate_recommendations,
)
from src.analyzer import (
    calculate_quality_score,
    correlation_matrix,
    detect_outliers,
    get_duplicate_rows,
    get_missing_percentage,
    get_missing_values,
    get_numeric_columns,
    get_summary_statistics,
    profile_columns,
)
from src.authentication import login
from src.data_loader import load_csv
from src.logger import logger
from src.report_generator import create_pdf, generate_report
from src.validator import (
    detect_constant_columns,
    unique_value_report,
    validate_column_names,
    validate_numeric_columns,
)


# =========================================================
# PAGE CONFIGURATION
# This must be the first Streamlit command.
# =========================================================

APP_NAME = getattr(config, "APP_NAME", "AI Data Quality Checker")
APP_VERSION = getattr(config, "APP_VERSION", "1.0.0")
DEFAULT_QUALITY_LIMIT = getattr(config, "QUALITY_SCORE_WARNING", 80)
REPORT_FOLDER = getattr(config, "REPORT_FOLDER", "reports")

st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
)


# =========================================================
# AUTHENTICATION
# =========================================================

if not login():
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(APP_NAME)
st.sidebar.caption(f"Version {APP_VERSION}")

quality_limit = st.sidebar.slider(
    "Minimum acceptable quality score",
    min_value=0,
    max_value=100,
    value=DEFAULT_QUALITY_LIMIT,
)

st.sidebar.info(
    "Upload a CSV dataset for analysis. You may optionally upload "
    "a second CSV to compare its size and quality metrics."
)


# =========================================================
# APPLICATION HEADER
# =========================================================

st.title(f"📊 {APP_NAME}")

st.caption(
    "Analyze CSV files for missing values, duplicate rows, outliers, "
    "constant columns, data types, validation issues, and overall quality."
)


# =========================================================
# FILE UPLOADS
# =========================================================

uploaded_file = st.file_uploader(
    "Choose the primary CSV file",
    type=["csv"],
    key="primary_csv",
)

uploaded_file2 = st.file_uploader(
    "Upload a second CSV for comparison (optional)",
    type=["csv"],
    key="comparison_csv",
)


# =========================================================
# PROCESS PRIMARY DATASET
# =========================================================

if uploaded_file is None:
    st.info("Upload a CSV file to begin the analysis.")
    st.stop()


try:
    df = load_csv(uploaded_file)

    if df is None:
        st.error("Unable to read the CSV file.")
        st.stop()

    if isinstance(df, str) and df == "EMPTY":
        st.warning("The CSV file contains column headers but no data rows.")
        st.stop()

    if not isinstance(df, pd.DataFrame):
        st.error("The uploaded file did not produce a valid dataset.")
        st.stop()

except Exception as error:
    logger.exception("Primary CSV loading failed.")

    st.error(
        "An unexpected error occurred while loading the dataset.\n\n"
        f"Error details: {error}"
    )
    st.stop()


st.success("File uploaded successfully!")

st.caption(
    f"File: {uploaded_file.name} | "
    f"Size: {uploaded_file.size / 1024:.2f} KB"
)

logger.info(
    "Dataset uploaded: %s | rows=%s | columns=%s",
    uploaded_file.name,
    df.shape[0],
    df.shape[1],
)


# =========================================================
# CALCULATE DATA QUALITY RESULTS
# =========================================================

try:
    missing_values = get_missing_values(df)
    missing_percentage = get_missing_percentage(df)
    duplicates = int(get_duplicate_rows(df))
    total_missing = int(missing_values.sum())

    summary_statistics = get_summary_statistics(df)
    column_profile = profile_columns(df)

    column_issues = validate_column_names(df)
    numeric_issues = validate_numeric_columns(df)
    constant_columns = detect_constant_columns(df)

    unique_values = unique_value_report(df)
    outlier_counts = detect_outliers(df)
    score = calculate_quality_score(df)

   # =========================================================
# SAVE ANALYSIS HISTORY ONCE PER UPLOADED FILE
# =========================================================

    history_folder = Path("history")
    history_folder.mkdir(parents=True, exist_ok=True)

    history_file = history_folder / "analysis_history.csv"

    file_key = f"{uploaded_file.name}-{uploaded_file.size}"

    if "saved_history_files" not in st.session_state:
       st.session_state.saved_history_files = set()

    if file_key not in st.session_state.saved_history_files:
       history_row = pd.DataFrame(
        {
            "Date": [pd.Timestamp.now()],
            "Filename": [uploaded_file.name],
            "Rows": [df.shape[0]],
            "Columns": [df.shape[1]],
            "Missing": [total_missing],
            "Duplicates": [duplicates],
            "Quality Score": [score],
        }
    )
    
    history_row.to_csv(
        history_file,
        mode="a",
        header=not history_file.exists(),
        index=False,
    )

    st.session_state.saved_history_files.add(file_key)

    numeric_columns = get_numeric_columns(df)
    correlation = correlation_matrix(df)

except Exception as error:
    logger.exception("Dataset analysis failed.")

    st.error(
        "The dataset was loaded, but the quality analysis failed.\n\n"
        f"Error details: {error}"
    )
    st.stop()


# =========================================================
# PREPARE DISPLAY TABLES
# =========================================================

dtype_df = pd.DataFrame(
    {
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
    }
)

dtype_counts = df.dtypes.astype(str).value_counts()

datatype_summary_df = pd.DataFrame(
    {
        "Data Type": dtype_counts.index,
        "Column Count": dtype_counts.values,
    }
)

missing_df = pd.DataFrame(
    {
        "Column": missing_values.index,
        "Missing Values": missing_values.values,
        "Missing Percentage": missing_percentage.round(2).values,
    }
)

unique_df = pd.DataFrame(
    {
        "Column": unique_values.index,
        "Unique Values": unique_values.values,
    }
)

outlier_df = pd.DataFrame(
    {
        "Column": list(outlier_counts.keys()),
        "Outliers": list(outlier_counts.values()),
    }
)

total_outliers = int(sum(outlier_counts.values()))


# =========================================================
# SAVE ANALYSIS HISTORY ONCE PER UPLOADED FILE
# =========================================================

history_folder = Path("history")
history_folder.mkdir(parents=True, exist_ok=True)

history_file = history_folder / "analysis_history.csv"

file_key = f"{uploaded_file.name}-{uploaded_file.size}"

if "saved_history_files" not in st.session_state:
    st.session_state.saved_history_files = set()

if file_key not in st.session_state.saved_history_files:
    history_row = pd.DataFrame(
        {
            "Date": [pd.Timestamp.now()],
            "Filename": [uploaded_file.name],
            "Rows": [df.shape[0]],
            "Columns": [df.shape[1]],
            "Missing": [total_missing],
            "Duplicates": [duplicates],
            "Outliers": [total_outliers],
            "Quality Score": [score],
        }
    )

    try:
        history_row.to_csv(
            history_file,
            mode="a",
            header=not history_file.exists(),
            index=False,
        )

        st.session_state.saved_history_files.add(file_key)

    except Exception:
        logger.exception("Unable to save analysis history.")


# =========================================================
# PREPARE SECOND DATASET COMPARISON
# =========================================================

comparison_df = None
comparison_message = None

if uploaded_file2 is not None:
    try:
        df2 = load_csv(uploaded_file2)

        if df2 is None:
            comparison_message = "Unable to read the second CSV file."

        elif isinstance(df2, str) and df2 == "EMPTY":
            comparison_message = "The second CSV contains no data rows."

        elif isinstance(df2, pd.DataFrame):
            dataset2_missing = int(get_missing_values(df2).sum())
            dataset2_duplicates = int(get_duplicate_rows(df2))
            dataset2_score = calculate_quality_score(df2)

            comparison_df = pd.DataFrame(
                {
                    "Metric": [
                        "Rows",
                        "Columns",
                        "Missing Values",
                        "Duplicate Rows",
                        "Quality Score",
                    ],
                    "Primary Dataset": [
                        df.shape[0],
                        df.shape[1],
                        total_missing,
                        duplicates,
                        score,
                    ],
                    "Second Dataset": [
                        df2.shape[0],
                        df2.shape[1],
                        dataset2_missing,
                        dataset2_duplicates,
                        dataset2_score,
                    ],
                }
            )

    except Exception as error:
        logger.exception("Second dataset comparison failed.")
        comparison_message = f"Unable to compare the second dataset: {error}"


# =========================================================
# AI-STYLE INSIGHTS
# =========================================================

try:
    recommendations = generate_recommendations(
        total_missing,
        duplicates,
        score,
    )
except Exception:
    logger.exception("Recommendation generation failed.")
    recommendations = ["Unable to generate automated recommendations."]

try:
    ai_summary = generate_ai_summary(
        score,
        total_missing,
        duplicates,
    )
except Exception:
    logger.exception("AI summary generation failed.")
    ai_summary = "Unable to generate the automated quality summary."

try:
    dataset_summary_text = dataset_summary(
        df.shape[0],
        df.shape[1],
        score,
    )
except Exception:
    logger.exception("Dataset summary generation failed.")
    dataset_summary_text = "Unable to generate the dataset summary."

try:
    cleaning_recommendations = cleaning_suggestions(df)
except Exception:
    logger.exception("Cleaning suggestion generation failed.")
    cleaning_recommendations = [
        "Unable to generate automated cleaning suggestions."
    ]


# =========================================================
# APPLICATION TABS
# =========================================================

overview_tab, quality_tab, charts_tab, ai_tab, reports_tab = st.tabs(
    [
        "📋 Overview",
        "✅ Quality",
        "📈 Visualizations",
        "🤖 AI Insights",
        "📥 Reports",
    ]
)


# =========================================================
# OVERVIEW TAB
# =========================================================

with overview_tab:
    st.header("Dataset Overview")

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("Rows", df.shape[0])
    metric2.metric("Columns", df.shape[1])
    metric3.metric("Missing Values", total_missing)
    metric4.metric("Quality Score", f"{score}%")

    st.subheader("Dataset Preview")

    st.dataframe(
        df.head(20),
        use_container_width=True,
    )

    st.subheader("Column Names")
    st.write(df.columns.tolist())

    st.subheader("Data Types")

    st.dataframe(
        dtype_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Data Type Summary")

    st.dataframe(
        datatype_summary_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Column Profile")

    st.dataframe(
        column_profile,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Missing Value Map")

    st.caption(
        "True indicates a missing value. False indicates a populated value."
    )

    st.dataframe(
        df.isnull(),
        use_container_width=True,
    )

    st.subheader("Explore a Column")

    selected_column = st.selectbox(
        "Select a column",
        options=df.columns.tolist(),
        key="overview_selected_column",
    )

    st.dataframe(
        df[[selected_column]],
        use_container_width=True,
    )

    st.subheader("Value Counts")

    value_counts_df = (
        df[selected_column]
        .value_counts(dropna=False)
        .rename_axis("Value")
        .reset_index(name="Count")
    )

    st.dataframe(
        value_counts_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# QUALITY TAB
# =========================================================

with quality_tab:
    st.header("Data Quality Report")

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("Missing Values", total_missing)
    metric2.metric("Duplicate Rows", duplicates)
    metric3.metric("Outliers", total_outliers)
    metric4.metric("Quality Score", f"{score}%")

    if score < quality_limit:
        st.error(
            f"Quality Score ({score}%) is below the selected "
            f"minimum ({quality_limit}%)."
        )
    else:
        st.success(
            f"Quality Score ({score}%) meets the selected "
            f"minimum ({quality_limit}%)."
        )

    st.subheader("Missing Values")

    st.dataframe(
        missing_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Missing Values Chart")

    missing_chart_df = missing_df.set_index("Column")

    st.bar_chart(
        missing_chart_df[["Missing Percentage"]]
    )

    st.subheader("Dataset Health")

    if total_missing == 0 and duplicates == 0:
        st.success(
            "The dataset contains no missing values or duplicate rows."
        )
    elif total_missing < 10 and duplicates < 5:
        st.warning(
            "The dataset contains a small number of quality issues."
        )
    else:
        st.error(
            "The dataset contains significant missing or duplicate data."
        )

    st.subheader("Summary Statistics")

    if summary_statistics.empty:
        st.info("No numeric summary statistics are available.")
    else:
        st.dataframe(
            summary_statistics,
            use_container_width=True,
        )

    st.subheader("Column Validation")

    if not column_issues:
        st.success("No column-name issues detected.")
    else:
        for issue in column_issues:
            st.error(issue)

    st.subheader("Numeric Validation")

    if not numeric_issues:
        st.success("No numeric validation issues detected.")
    else:
        for issue in numeric_issues:
            st.warning(issue)

    st.subheader("Constant Columns")

    if constant_columns:
        st.warning(
            "Constant columns detected: "
            + ", ".join(map(str, constant_columns))
        )
    else:
        st.success("No constant columns detected.")

    st.subheader("Unique Value Counts")

    st.dataframe(
        unique_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Outlier Detection")

    if outlier_df.empty:
        st.info("No numeric columns are available for outlier detection.")
    else:
        st.dataframe(
            outlier_df,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Outlier Chart")

        st.bar_chart(
            outlier_df.set_index("Column")[["Outliers"]]
        )


# =========================================================
# VISUALIZATION TAB
# =========================================================

with charts_tab:
    st.header("Dashboard")

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("Rows", df.shape[0])
    metric2.metric("Columns", df.shape[1])
    metric3.metric("Duplicates", duplicates)
    metric4.metric("Quality Score", f"{score}%")

    st.subheader("Correlation Matrix")

    if correlation.empty:
        st.info(
            "At least two usable numeric columns are required "
            "for meaningful correlation analysis."
        )
    else:
        st.dataframe(
            correlation,
            use_container_width=True,
        )

    st.subheader("Numeric Column Distribution")

    if numeric_columns:
        selected_numeric_column = st.selectbox(
            "Choose a numeric column",
            options=numeric_columns,
            key="distribution_numeric_column",
        )

        distribution_series = (
            df[selected_numeric_column]
            .dropna()
            .value_counts()
            .sort_index()
        )

        if distribution_series.empty:
            st.info("The selected column has no values to display.")
        else:
            st.bar_chart(distribution_series)

    else:
        st.info("The dataset contains no numeric columns.")

    st.subheader("Dataset Comparison")

    if comparison_df is not None:
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
        )
    elif comparison_message:
        st.warning(comparison_message)
    else:
        st.info("Upload a second CSV file to compare datasets.")


# =========================================================
# AI INSIGHTS TAB
# =========================================================

with ai_tab:
    st.header("Automated Quality Summary")
    st.info(ai_summary)

    st.header("Dataset Summary")
    st.success(dataset_summary_text)

    st.header("Recommendations")

    for recommendation in recommendations:
        st.info(recommendation)

    st.header("Cleaning Suggestions")

    for suggestion in cleaning_recommendations:
        st.info(suggestion)

    st.header("Data Cleaning Preview")

    cleaned_df = df.drop_duplicates().dropna()

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Original Rows", df.shape[0])
    metric2.metric("Rows After Cleaning", cleaned_df.shape[0])
    metric3.metric(
        "Rows Removed",
        df.shape[0] - cleaned_df.shape[0],
    )

    st.dataframe(
        cleaned_df.head(20),
        use_container_width=True,
    )

    st.header("Search Columns")

    search_term = st.text_input(
        "Search for a column",
        key="column_search",
    )

    if not search_term:
        st.info("Enter part of a column name to search.")

    else:
        matching_columns = [
            column
            for column in df.columns
            if search_term.lower() in str(column).lower()
        ]

        if matching_columns:
            st.success(
                f"Found {len(matching_columns)} matching column(s)."
            )
            st.write(matching_columns)
        else:
            st.warning("No matching columns found.")

    st.header("Analysis History")

    history = None

    try:
        if history_file.exists():
            history = pd.read_csv(history_file)

            st.dataframe(
                history,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No analysis history is available yet.")

    except Exception:
        logger.exception("Unable to read analysis history.")
        st.warning("Unable to read the analysis history.")

    st.header("Quality Trend")

    if history is not None and not history.empty:
        try:
            history["Date"] = pd.to_datetime(
                history["Date"],
                errors="coerce",
            )

            history["Quality Score"] = pd.to_numeric(
                history["Quality Score"],
                errors="coerce",
            )

            trend_df = (
                history.dropna(
                    subset=["Date", "Quality Score"]
                )
                .sort_values("Date")
                .set_index("Date")
            )

            if trend_df.empty:
                st.info("There is not enough history for a trend chart.")
            else:
                st.line_chart(
                    trend_df[["Quality Score"]]
                )

        except Exception:
            logger.exception("Quality trend generation failed.")
            st.warning("Unable to generate the quality trend chart.")

    else:
        st.info("Upload and analyze datasets to create a quality trend.")


# =========================================================
# REPORTS TAB
# =========================================================

with reports_tab:
    st.header("Download Reports")

    quality_summary_df = pd.DataFrame(
        {
            "Metric": [
                "Filename",
                "Rows",
                "Columns",
                "Missing Values",
                "Duplicate Rows",
                "Outliers",
                "Quality Score",
            ],
            "Value": [
                uploaded_file.name,
                df.shape[0],
                df.shape[1],
                total_missing,
                duplicates,
                total_outliers,
                score,
            ],
        }
    )

    st.subheader("Quality Summary")

    st.dataframe(
        quality_summary_df,
        use_container_width=True,
        hide_index=True,
    )

    summary_csv = quality_summary_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇ Download Summary CSV",
        data=summary_csv,
        file_name="data_quality_summary.csv",
        mime="text/csv",
    )

    detailed_report = None

    try:
        report_percentage_df = missing_percentage.to_frame(
            name="Missing Percentage"
        )

        report_outlier_df = pd.DataFrame(
            {"Outliers": outlier_counts}
        )

        detailed_report = generate_report(
            missing_values.rename("Missing Values"),
            report_percentage_df,
            report_outlier_df,
        )

    except Exception:
        logger.exception("Detailed CSV report generation failed.")
        st.warning("Unable to generate the detailed CSV report.")

    if detailed_report is not None:
        detailed_csv = detailed_report.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇ Download Detailed CSV",
            data=detailed_csv,
            file_name="detailed_quality_report.csv",
            mime="text/csv",
        )

    reports_folder = Path(REPORT_FOLDER)
    reports_folder.mkdir(parents=True, exist_ok=True)

    pdf_path = reports_folder / "quality_report.pdf"

    try:
        create_pdf(
            score,
            total_missing,
            duplicates,
            str(pdf_path),
        )

        if pdf_path.exists():
            pdf_data = pdf_path.read_bytes()

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name="quality_report.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("The PDF report could not be created.")

    except Exception as error:
        logger.exception("PDF report generation failed.")

        st.warning(
            f"Unable to generate the PDF report: {error}"
        )