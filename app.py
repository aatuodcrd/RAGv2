import streamlit as st
from utils.mongoDB import chatlogs_collection

login_page = st.Page("pages/login.py", title="Login", icon="🔐")
upload_page = st.Page("pages/upload.py", title="Upload file", icon="📁")



if 'username' not in st.session_state:
    pg = st.navigation([login_page])
else:
    username = st.session_state['username']
    chatlogs_docs = chatlogs_collection.find({"username": username})
    st.session_state.namespace_list = []
    for doc in chatlogs_docs:
        st.session_state.namespace_list.append(doc['namespace'])

    pg = st.navigation([upload_page])

st.set_page_config(page_title="RAG GenAI-PIM", page_icon="🐍")
pg.run()