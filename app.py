import streamlit as st
import pandas as pd

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

    df = pd.read_csv(uploaded_file)

    st.success("File uploaded successfully!")

    st.subheader("Dataset Preview")

    st.subheader("First Five Rows")

    st.dataframe(df.head()) 

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

    
