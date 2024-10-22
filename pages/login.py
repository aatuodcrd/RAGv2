import streamlit as st
from utils.mongoDB import users_collection

st.title("Login")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if username and password:
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid username or password")