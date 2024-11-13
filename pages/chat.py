import streamlit as st

from utils.askChat import search_documents_pinecone

namespace = st.sidebar.selectbox("Select a namespace", st.session_state.namespace_list)
with st.sidebar.expander("Customize Chat"):
    stream_Toggle, memory_Toggle = st.columns(2)

    language_select = st.selectbox("Select Language",("Thai", "English"), help='Output Language')
    if language_select == "Thai":
        language = "Thai"
    elif language_select == "English":
        language = "English"
    
    stream = stream_Toggle.toggle('stream', value=True, help='Streaming mode')
    memory = memory_Toggle.toggle('memory', value=False, help='Memory mode uses the previous 3 conversations.')
    kFromUser = int(st.number_input("retrive documents", min_value=1, max_value=5, value=3))
    threshold = st.slider("Threshold", min_value=0.0, max_value=1.0, value=0.7)

question = st.chat_input("What is up?")
with st.container():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if question:
        st.chat_message("user").markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})
        st.write('<style>.stwrite_stream { overflow-wrap: break-word; }</style>', unsafe_allow_html=True)
        st.write('<style>.stChatMessage { overflow-wrap: break-word; }</style>', unsafe_allow_html=True)
        
        docs = search_documents_pinecone(question, kFromUser, namespace)
        st.write(docs)
        # if st.session_state.stream == True:
        #     with st.chat_message("assistant"):
        #         response = st.write_stream(res)