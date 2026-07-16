import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loader import load_csv
from src.analyzer import (
    get_missing_values,
    get_missing_percentage,
    get_duplicate_rows
)

# ------------------------------
# Page Configuration
# ------------------------------

st.set_page_config(
    page_title="AI Data Quality Checker",
    page_icon="📊",
    layout="wide"
)

# ------------------------------
# Title
# ------------------------------

st.title("📊 AI Data Quality Checker")
st.write("Upload a CSV file for analysis.")

# ------------------------------
# File Upload
# ------------------------------

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

# ------------------------------
# Process Uploaded File
# ------------------------------

if uploaded_file is not None:

    # Load CSV
    df = load_csv(uploaded_file)

    # Invalid CSV
    if df is None:
        st.error("Unable to read the CSV file.")
        st.stop()

    # Empty CSV
    if isinstance(df, str):
        if df == "EMPTY":
            st.warning("CSV file contains no data.")
            st.stop()

    # Success Message
    st.success("File uploaded successfully!")

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

    # ==================================================
    # DATA QUALITY REPORT
    # ==================================================

    st.header("📊 Data Quality Report")

    # Missing Values

    missing_values = get_missing_values(df)

    missing_df = pd.DataFrame({
        "Column": missing_values.index,
        "Missing Values": missing_values.values
    })

    st.subheader("Missing Values")

    st.dataframe(missing_df)

    # Missing Percentage

    missing_percentage = get_missing_percentage(df)

    percentage_df = pd.DataFrame({
        "Column": missing_percentage.index,
        "Missing Percentage": missing_percentage.round(2).values
    })

    st.subheader("Missing Values Percentage")

    st.dataframe(percentage_df)

    # Missing Value Percentage Chart
    st.subheader("📈 Missing Value Percentage Chart")
    fig, ax = plt.subplots()
    ax.bar(
        percentage_df["Column"],
        percentage_df["Missing Percentage"]
    )
    ax.set_xlabel("Columns")
    ax.set_ylabel("Percentage")
    ax.set_title("Missing Value Percentage")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Duplicate Rows
    duplicates = get_duplicate_rows(df)
    st.subheader("Duplicate Rows")
    st.metric("Duplicates", duplicates)

    # Dataset Health
    total_missing = missing_values.sum()
    st.subheader("Dataset Health")

    if total_missing == 0:
        st.success("✅ Excellent! No missing values found.")
    elif total_missing < 10:
        st.warning("⚠ Dataset contains a few missing values.")
    else:
        st.error("❌ Dataset contains many missing values.")

    # Dataset Shape
    st.subheader("Dataset Shape")
    st.write(f"Rows : {df.shape[0]}")
    st.write(f"Columns : {df.shape[1]}")

# ------------------------------
# Sidebar
# ------------------------------

st.sidebar.title("Navigation")

st.sidebar.info(
    """
AI Data Quality Checker

This tool helps you analyze datasets by checking:

• Missing Values
• Missing Percentage
• Duplicate Rows
• Dataset Shape
• Data Types
"""
)