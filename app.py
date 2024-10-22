import streamlit as st

login_page = st.Page("pages/login.py", title="Login", icon="🔐")
upload_page = st.Page("pages/upload.py", title="Upload file", icon="📁")



if 'username' not in st.session_state:
    pg = st.navigation([login_page])
else:
    pg = st.navigation([upload_page])

st.set_page_config(page_title="RAG GenAI-PIM", page_icon="🐍")
pg.run()