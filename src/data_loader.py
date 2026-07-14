import pandas as pd


def load_csv(uploaded_file):

    try:

        df = pd.read_csv(uploaded_file)

        if df.empty:
            return "EMPTY"

        return df

    except Exception:

        return None
    
