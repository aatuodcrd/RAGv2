import streamlit as st
from utils.mongoDB import chatlogs_collection, users_collection

if 'username' not in st.session_state:
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
else:
    upload_page = st.Page("pages/upload.py", title="Upload file", icon="📁")
    chat_page = st.Page("pages/chat.py", title="Chat", icon="💬")
    
    username = st.session_state['username']
    chatlogs_docs = chatlogs_collection.find({"username": username})
    st.session_state.namespace_list = []
    for doc in chatlogs_docs:
        st.session_state.namespace_list.append(doc['namespace'])

    pg = st.navigation([upload_page, chat_page])
    pg.run()