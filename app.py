import streamlit as st
from src.data_loader import load_csv

st.set_page_config(
    page_title="AI Data Quality Checker",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Data Quality Checker")

st.write("Upload a CSV file for analysis.")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    df = load_csv(uploaded_file)

    if df is None:
        st.error("Unable to read the CSV file.")
        st.stop()

    if isinstance(df, str):
   
     if df == "EMPTY":
        st.warning("CSV file contains no data.")
        st.stop()

    
    st.success("File uploaded successfully!")

    st.header("📋 Dataset Overview")

    col1, col2 = st.columns(2)

    col1.metric(
    label="Rows",
    value=df.shape[0]
)

    col2.metric(
    label="Columns",
    value=df.shape[1]
)

    st.subheader("Dataset Preview")

    st.dataframe(df.head()) 

    st.subheader("📌 Column Names")

    st.write(df.columns.tolist())

    st.subheader("📊 Data Types")

    dtype_df = df.dtypes.astype(str).reset_index()

    dtype_df.columns = ["Column Name", "Data Type"]

    st.dataframe(dtype_df)

    st.subheader("Dataset Shape")

    st.write(f"{df.shape[0]} rows")

    st.write(f"{df.shape[1]} columns")

    st.subheader("Dataset Information")

    col1, col2 = st.columns(2)

    col1.metric("Rows", df.shape[0])

    col2.metric("Columns", df.shape[1])

    st.subheader("Columns")

    st.write(df.columns.tolist())

    st.sidebar.title("Navigation")

    st.sidebar.info(
    "AI Data Quality Checker\n\n Data quality is crucial for building reliable AI models. This tool helps you analyze your dataset and identify potential issues."
    )

    
