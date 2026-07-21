from pathlib import Path

import streamlit as st
import pandas as pd
import config
import matplotlib.pyplot as plt

from src.data_loader import load_csv
from src.validator import (
    validate_column_names,
    detect_constant_columns,
    unique_value_report,
    validate_numeric_columns
)
from src.analyzer import (
    get_missing_values,
    get_missing_percentage,
    get_duplicate_rows,
    get_summary_statistics,
    get_numeric_columns,
    detect_outliers,
    calculate_quality_score,
    correlation_matrix,
    profile_columns
)
from src.report_generator import generate_report, create_pdf
from src.ai_helper import (
    generate_recommendations,
    generate_ai_summary,
    cleaning_suggestions,
    dataset_summary
)
from src.logger import logger

# ------------------------------
# Page Configuration
# ------------------------------

st.set_page_config(
    page_title="AI Data Quality Checker",
    page_icon="📊",
    layout="wide",
)

# ------------------------------
# Title
# ------------------------------

st.title("📊 AI Data Quality Checker")
st.write("Upload a CSV file for analysis.")

# ------------------------------
# File Upload
# ------------------------------

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

uploaded_file2 = st.file_uploader(
    "Upload Second Dataset (Optional)",
    type="csv"
)

# ------------------------------
# Process Uploaded File
# ------------------------------

if uploaded_file is not None:
    df = load_csv(uploaded_file)

    if df is None:
        st.error("Unable to read the CSV file.")
        st.stop()

    if isinstance(df, str) and df == "EMPTY":
        st.warning("CSV file contains no data.")
        st.stop()

    st.success("File uploaded successfully!")

    logger.info("Dataset uploaded successfully.")
    logger.info(f"Rows : {df.shape[0]}")
    logger.info(f"Columns : {df.shape[1]}")

    # ==================================================
    # COMPUTE EVERYTHING NEEDED BY THE TABS UP FRONT
    # ==================================================

    # --- Overview helpers ---
    dtype_df = pd.DataFrame({
        "Column": df.columns,
        "Dtype": df.dtypes.astype(str).values
    })

    dtype_counts = df.dtypes.astype(str).value_counts()
    datatype_summary = pd.DataFrame({
        "Dtype": dtype_counts.index,
        "Count": dtype_counts.values
    })

    profile = profile_columns(df)
    heatmap = df.isnull()

    # --- Quality tab ---
    # analyzer.py returns Series here, not DataFrames — convert for display
    missing_series = get_missing_values(df)          # Series: column -> missing count
    percentage_series = get_missing_percentage(df)   # Series: column -> missing %

    missing_df = (
        missing_series.rename("Missing Values")
        .reset_index()
        .rename(columns={"index": "Column"})
    )
    percentage_df = (
        percentage_series.rename("Missing Percentage")
        .reset_index()
        .rename(columns={"index": "Column"})
    )

    fig, ax = plt.subplots()
    missing_series.plot(kind="bar", ax=ax)
    ax.set_ylabel("Missing Values")
    ax.set_xlabel("Column")

    duplicates = int(get_duplicate_rows(df))
    total_missing = int(missing_series.sum())

    summary = get_summary_statistics(df)
    issues = validate_column_names(df)
    numeric_issues = validate_numeric_columns(df)
    constant_columns = detect_constant_columns(df)

    unique_series = unique_value_report(df)  # Series: column -> unique count
    unique_df = (
        unique_series.rename("Unique Values")
        .reset_index()
        .rename(columns={"index": "Column"})
    )

    outlier_counts = detect_outliers(df)  # dict: column -> outlier count
    outlier_df = pd.DataFrame(
        list(outlier_counts.items()),
        columns=["Column", "Outliers"]
    )
    outlier_chart = pd.Series(outlier_counts)

    score = calculate_quality_score(df)

    # Build the internal report table (generate_report expects Series/DataFrames
    # aligned on the column-name index, not the reset-index display versions above)
    try:
        report_percentage_df = percentage_series.to_frame(name="Missing Percentage")
        report_outlier_df = pd.DataFrame({"Outliers": outlier_counts})
        internal_report = generate_report(
            missing_series.rename("Missing Values"),
            report_percentage_df,
            report_outlier_df
        )
    except Exception as e:
        internal_report = None
        logger.info(f"generate_report failed: {e}")

    # CSV export of the quality report
    quality_report_df = pd.DataFrame({
        "Metric": ["Rows", "Columns", "Duplicates", "Total Missing Values", "Quality Score"],
        "Value": [df.shape[0], df.shape[1], duplicates, total_missing, score],
    })
    csv = quality_report_df.to_csv(index=False).encode("utf-8")

    # PDF report (create_pdf writes directly to disk and returns None)
    pdf_path = Path("reports") / "quality_report.pdf"
    try:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        create_pdf(score, total_missing, duplicates, str(pdf_path))
    except Exception as e:
        pdf_path = None
        logger.info(f"create_pdf failed: {e}")

    # --- Visualization tab ---
    corr = correlation_matrix(df)
    numeric_columns = get_numeric_columns(df)

    comparison = None
    if uploaded_file2 is not None:
        df2 = load_csv(uploaded_file2)
        if df2 is not None and not (isinstance(df2, str) and df2 == "EMPTY"):
            comparison = pd.DataFrame({
                "Metric": ["Rows", "Columns", "Duplicates", "Missing Values"],
                "Dataset 1": [df.shape[0], df.shape[1], duplicates, total_missing],
                "Dataset 2": [
                    df2.shape[0],
                    df2.shape[1],
                    int(get_duplicate_rows(df2)),
                    int(get_missing_values(df2).sum())
                ],
            })

    # --- AI tab ---
    recommendations = generate_recommendations(total_missing, duplicates, score)
    ai_summary = generate_ai_summary(score, total_missing, duplicates)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Overview",
        "✅ Quality",
        "📈 Visualization",
        "🤖 AI"
    ])

    # ==================================================
    # DATASET OVERVIEW
    # ==================================================
    with tab1:

        st.header("📋 Dataset Overview")

        col1, col2 = st.columns(2)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])

        st.subheader("Dataset Preview")
        st.dataframe(df.head())

        st.subheader("📌 Column Names")
        st.write(df.columns.tolist())

        st.subheader("📊 Data Types")
        st.dataframe(dtype_df)

        st.header("📌 Data Type Summary")
        st.dataframe(datatype_summary)

        st.header("📋 Column Profile")
        st.dataframe(profile)

        st.header("🔥 Missing Value Heatmap")
        st.dataframe(heatmap)

        st.header("🔍 Explore Dataset")

        selected_column = st.selectbox(
            "Select a column",
            df.columns,
            key="overview_column"
        )

        st.subheader(f"Values in '{selected_column}'")
        st.dataframe(df[[selected_column]])

        st.subheader("Value Counts")
        st.dataframe(
            df[selected_column]
            .value_counts(dropna=False)
            .reset_index()
            .rename(columns={
                "index": "Value",
                selected_column: "Count"
            })
        )

    # ==================================================
    # DATA QUALITY REPORT
    # ==================================================
    with tab2:

        st.header("📊 Data Quality Report")

        st.subheader("Missing Values")
        st.dataframe(missing_df)

        st.subheader("Missing Value Percentage")
        st.dataframe(percentage_df)

        st.subheader("Missing Values Chart")
        st.pyplot(fig)

        st.subheader("Duplicate Rows")
        st.metric("Duplicates", duplicates)

        st.subheader("Dataset Health")

        if total_missing == 0:
            st.success("✅ Excellent! No missing values found.")
        elif total_missing < 10:
            st.warning("⚠ Dataset contains a few missing values.")
        else:
            st.error("❌ Dataset contains many missing values.")

        st.header("📈 Summary Statistics")
        st.dataframe(summary)

        st.header("✅ Column Validation")

        if len(issues) == 0:
            st.success("No column issues detected.")
        else:
            for issue in issues:
                st.error(issue)

        st.header("🔢 Numeric Validation")

        if len(numeric_issues) == 0:
            st.success("No numeric validation issues found.")
        else:
            for issue in numeric_issues:
                st.warning(issue)

        st.header("📌 Constant Columns")

        if len(constant_columns) == 0:
            st.success("No constant columns found.")
        else:
            st.write(constant_columns)

        st.header("📊 Unique Value Count")
        st.dataframe(unique_df)

        st.header("📌 Outlier Detection")
        st.dataframe(outlier_df)

        st.subheader("Outlier Chart")
        st.bar_chart(outlier_chart)

        st.header("⭐ Overall Quality Score")
        st.metric("Quality Score", f"{score}%")

        if score < config.QUALITY_SCORE_WARNING:
            st.error("⚠ Dataset quality is poor.")
        else:
            st.success("✅ Dataset quality is acceptable.")

        st.header("📄 Export Quality Report")

        st.download_button(
            "⬇ Download CSV Report",
            data=csv,
            file_name="quality_report.csv",
            mime="text/csv"
        )

    # ==================================================
    # VISUALIZATION / DASHBOARD
    # ==================================================
    with tab3:

        st.header("📊 Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Duplicates", duplicates)
        col4.metric("Quality Score", f"{score}%")

        st.header("📈 Correlation Matrix")
        st.dataframe(corr)
        if not corr.empty:
            st.line_chart(corr)

        st.header("📊 Distribution")

        if numeric_columns:
            selected = st.selectbox(
                "Choose Numeric Column",
                numeric_columns,
                key="distribution_column"
            )

            st.bar_chart(
                df[selected].value_counts().sort_index()
            )
        else:
            st.info("No numeric columns available for distribution analysis.")

        st.header("📊 Dataset Comparison")

        if comparison is not None:
            st.dataframe(comparison)
        else:
            st.info("Upload a second dataset to compare.")

        if pdf_path and Path(pdf_path).exists():
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    "📄 Download PDF Report",
                    pdf_file,
                    file_name="quality_report.pdf"
                )

    # ==================================================
    # AI TAB
    # ==================================================
    with tab4:

        st.header("🤖 AI Recommendations")

        for item in recommendations:
            st.info(item)

        st.header("🤖 AI Insights")
        st.success(ai_summary)

        st.header("🧹 Cleaning Suggestions")

        for item in cleaning_suggestions(df):
            st.info(item)

        st.header("🤖 AI Dataset Summary")
        st.success(dataset_summary(
            df.shape[0],
            df.shape[1],
            score
        ))

    # ------------------------------
    # Sidebar
    # ------------------------------
    st.sidebar.title("Navigation")

    section = st.sidebar.radio(
        "Choose",
        ["Overview", "Quality", "Visualization", "AI Insights"]
    )