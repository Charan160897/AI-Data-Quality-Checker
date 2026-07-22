import os

import streamlit as st
from dotenv import load_dotenv


load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME")
APP_PASSWORD = os.getenv("APP_PASSWORD")


def login():
    if not APP_USERNAME or not APP_PASSWORD:
        st.error(
            "Application login credentials are not configured. "
            "Add APP_USERNAME and APP_PASSWORD to the .env file."
        )
        return False

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        st.sidebar.success("You are logged in.")

        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

        return True

    st.sidebar.subheader("Login")

    username = st.sidebar.text_input(
        "Username",
        key="login_username",
    )

    password = st.sidebar.text_input(
        "Password",
        type="password",
        key="login_password",
    )

    if st.sidebar.button("Login"):
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")

    return False