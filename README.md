# AI Data Quality Checker

## Overview

AI Data Quality Checker is a Streamlit application that analyzes CSV datasets and identifies missing values, duplicate rows, outliers, constant columns, and other data-quality issues.

## Features

- CSV upload and preview
- Missing-value analysis
- Duplicate detection
- Outlier detection using IQR
- Column profiling
- Constant-column detection
- Numeric validation
- Correlation analysis
- Distribution charts
- Data-quality score
- Automated recommendations
- Cleaning preview
- Analysis history
- PDF and CSV report downloads
- Application logging
- Unit tests

## Tech Stack

- Python
- Pandas
- Streamlit
- Matplotlib
- ReportLab
- Pytest
- Git and GitHub

## Run Locally

```bash
git clone <repository-url>
cd AI-Data-Quality-Checker

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py