from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loader import load_csv
from src.validator import (
    validate_column_names,
    detect_constant_columns,
    unique_value_report
)
from src.analyzer import (
    get_missing_values,
    get_missing_percentage,
    get_duplicate_rows,
    get_summary_statistics,
    detect_outliers,
    calculate_quality_score,
    correlation_matrix
)
from src.report_generator import generate_report
from src.ai_helper import generate_recommendations
from src.report_generator import create_pdf
from src.logger import logger
from src.ai_helper import dataset_summary
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
    # DATASET OVERVIEW
    # ==================================================

    st.header("📋 Dataset Overview")
    col1, col2 = st.columns(2)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("📌 Column Names")
    st.write(df.columns.tolist())

    st.subheader("📊 Data Types")
    dtype_df = df.dtypes.astype(str).reset_index()
    dtype_df.columns = ["Column Name", "Data Type"]
    st.dataframe(dtype_df)

    st.header("📌 Data Type Summary")

    datatype_summary = (
         df.dtypes
           .value_counts()
           .reset_index()
        )

    datatype_summary.columns = [
           "Data Type",
            "Count"
      ]

    st.dataframe(datatype_summary)

    # ==================================================
    # DATA QUALITY REPORT
    # ==================================================

    st.header("📊 Data Quality Report")

    missing_values = get_missing_values(df)
    missing_df = pd.DataFrame(
        {
            "Column": missing_values.index,
            "Missing Values": missing_values.values,
        }
    )

    st.subheader("Missing Values")
    st.dataframe(missing_df)

    missing_percentage = get_missing_percentage(df)
    percentage_df = pd.DataFrame(
        {
            "Column": missing_percentage.index,
            "Missing Percentage": missing_percentage.round(2).values,
        }
    )

    st.subheader("Missing Values Percentage")
    st.dataframe(percentage_df)

    st.subheader("📊 Missing Values Chart")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(percentage_df["Column"], percentage_df["Missing Percentage"])
    ax.set_xlabel("Columns")
    ax.set_ylabel("Percentage")
    ax.set_title("Missing Value Percentage")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    duplicates = get_duplicate_rows(df)
    st.subheader("Duplicate Rows")
    st.metric("Duplicates", duplicates)

    total_missing = missing_values.sum()
    st.subheader("Dataset Health")

    if total_missing == 0:
        st.success("✅ Excellent! No missing values found.")
    elif total_missing < 10:
        st.warning("⚠ Dataset contains a few missing values.")
    else:
        st.error("❌ Dataset contains many missing values.")

    st.subheader("Dataset Shape")
    st.write(f"Rows : {df.shape[0]}")
    st.write(f"Columns : {df.shape[1]}")

    st.header("📈 Summary Statistics")
    summary = get_summary_statistics(df)
    st.dataframe(summary)

    st.header("✅ Column Validation")
    issues = validate_column_names(df)

    if len(issues) == 0:
        st.success("No column issues detected.")
    else:
        for issue in issues:
            st.error(issue)

    st.header("📌 Constant Columns")
    constant_columns = detect_constant_columns(df)

    if len(constant_columns) == 0:
        st.success("No constant columns found.")
    else:
        st.write(constant_columns)

    st.header("📊 Unique Value Count")

    unique_counts = unique_value_report(df)
    unique_df = unique_counts.reset_index()
    unique_df.columns = [
        "Column",
        "Unique Values",
    ]

    st.dataframe(unique_df) 

    # ============================
# Interactive Column Explorer
# ============================

    st.header("🔍 Explore Dataset")

    selected_column = st.selectbox(
       "Select a column",
       df.columns
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

    st.header("📌 Outlier Detection")
    outliers = detect_outliers(df)
    outlier_df = pd.DataFrame(
        {
            "Column": list(outliers.keys()),
            "Outliers": list(outliers.values()),
        }
    )

    st.dataframe(outlier_df)

    st.subheader("📊 Outlier Chart")
    outlier_chart = outlier_df.set_index("Column")
    st.bar_chart(outlier_chart)

    score = calculate_quality_score(df)
    st.header("⭐ Overall Quality Score")
    st.metric("Quality Score", 
              f"{score}%")
    
    st.header("📄 Export Quality Report")

    quality_report = pd.DataFrame({

        "Metric": [
        "Rows",
        "Columns",
        "Missing Values",
        "Duplicate Rows",
        "Quality Score"
    ],

    "Value": [
        df.shape[0],
        df.shape[1],
        total_missing,
        duplicates,
        score
    ]

})

    csv = quality_report.to_csv(index=False)

    st.download_button(
    label="⬇ Download CSV Report",
    data=csv,
    file_name="quality_report.csv",
    mime="text/csv"
)

    report = generate_report(missing_df, percentage_df, outlier_df)
    csv = report.to_csv(index=False)

    st.header("🤖 AI Recommendations")

    recommendations = generate_recommendations(
    total_missing,
    duplicates,
    score
)
  
    for item in recommendations:
        st.info(item)

    st.header("🤖 AI Dataset Summary")

    summary = dataset_summary(
        df.shape[0],
        df.shape[1],
        score
    )

    st.success(summary)

    pdf_path = "reports/quality_report.pdf"
    create_pdf(
        score,
        total_missing,
        duplicates,
        pdf_path,
    )
    st.header("📊 Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
      "Rows",
      df.shape[0]
  )

    col2.metric(
    "Columns",
    df.shape[1]
   )

    col3.metric(
    "Duplicates",
    duplicates
   )

    col4.metric(
      "Quality Score",
      f"{score}%"
  )
    st.header("📈 Correlation Matrix")

    corr = correlation_matrix(df)

    st.dataframe(corr)

    st.line_chart(corr)
    if Path(pdf_path).exists():
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                "📄 Download PDF Report",
                pdf_file,
                file_name="quality_report.pdf",
            )
    st.header("📊 Distribution")

    numeric_columns = df.select_dtypes(
    include="number"
     ).columns

    selected = st.selectbox(
    "Choose Numeric Column",
    numeric_columns
  )

    st.bar_chart(
    df[selected].value_counts().sort_index()
)

    st.download_button(
        label="📥 Download Quality Report",
        data=csv,
        file_name="quality_report.csv",
        mime="text/csv",
    )

# ------------------------------
# Sidebar
# ------------------------------

st.sidebar.title("Navigation")

section = st.sidebar.radio(
    "Choose",
    ["Overview", "Quality", "Visualization", "AI Insights"]
)