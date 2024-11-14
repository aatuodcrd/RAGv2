import streamlit as st
import time
from utils.askChat import askChat
from utils.mongoDB import chatlogs_collection

def stream_data(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

# Sidebar selections
namespace = st.sidebar.selectbox("Select a namespace", st.session_state.get("namespace_list", []))
user_doc = chatlogs_collection.find_one({"username": st.session_state.username, "namespace": namespace})
config = user_doc.get("config", {})
stream = config.get("stream", True)
memory = config.get("memory", False)
language = config.get("language", "Thai")
kFromUser = config.get("kFromUser", 3)
threshold = config.get("threshold", 0.7)
chatmemory = user_doc.get("chatmemory", [])
chatlogs = user_doc.get("chatlog", [])
chatlogs = chatlogs[-5:]

# Customize chat sidebar options
with st.sidebar.expander("Customize Chat"):
    stream_Toggle, memory_Toggle = st.columns(2)

    # Language selection
    language_select = st.selectbox("Select Language", ("Thai", "English"), help='Output Language')
    language = language_select

    # Stream and memory toggles
    stream = stream_Toggle.checkbox('Enable Stream', value=stream, help='Streaming mode')
    memory = memory_Toggle.checkbox('Enable Memory', value=memory, help='Memory mode uses the previous 3 conversations.')

    # Other configurations
    kFromUser = int(st.number_input("Retrieve documents", min_value=1, max_value=5, value=kFromUser))
    threshold = st.slider("Threshold", min_value=0.0, max_value=1.0, value=threshold)

    
    if st.button("Update Config"):
        chatlogs_collection.update_one({"username": st.session_state.username, "namespace": namespace}, {
            "$set": {
                "config": {
                    "kFromUser": kFromUser,
                    "threshold": threshold,
                    "memory": memory,
                    "language": language
                }
            }
        })
    
with st.sidebar.expander("Chat Memory"):
    for chat in chatmemory:
        st.chat_message("user").markdown(chat['question'])
        st.chat_message("assistant").markdown(chat['answer'])
        st.divider()
    if st.button("Clear Memory"):
        chatlogs_collection.update_one({"username": st.session_state.username, "namespace": namespace}, {"$set": {"chatmemory": []}})

# Main chat interface
question = st.chat_input("What is up?")
with st.container():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        for chat in chatlogs:
            st.session_state.messages.append({"role": "user", "content": chat["question"]})
            st.session_state.messages.append({"role": "assistant", "content": chat["answer"]})

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # New question handling
    if question:
        st.chat_message("user").markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        # Fetching assistant response
        res = askChat(username=st.session_state.username, question=question, namespace=namespace)

        # Stream or display response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            if stream:
                response_text = ""
                for word in stream_data(res):
                    response_text += word
                    response_placeholder.markdown(response_text)
            else:
                response_placeholder.markdown(res)
            
            # Save assistant response in session
            st.session_state.messages.append({"role": "assistant", "content": res})