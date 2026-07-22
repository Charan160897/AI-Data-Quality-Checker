import streamlit as st

USERNAME = "admin"
PASSWORD = "admin123"

def login():

    st.sidebar.header("🔐 Login")

    username = st.sidebar.text_input("Username")

    password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button("Login"):

        if username == USERNAME and password == PASSWORD:

            st.session_state["logged_in"] = True

        else:

            st.error("Invalid username or password")

    return st.session_state.get("logged_in", False)