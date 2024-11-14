import streamlit as st
from utils.file_clean import convert_excel_to_csv, preprocess_csv
from utils.file_upsert import file_loader
from utils.mongoDB import chatlogs_collection
from unidecode import unidecode
import tempfile
import os
import chardet
from pathlib import Path
from utils.pinecone import pinecone_connect

st.title("Upload file")
namespace = st.selectbox("Select a namespace", st.session_state.namespace_list)
show_old_filename, _, delete_namespace = st.columns(3)
file_list_old = chatlogs_collection.find_one({"namespace": namespace}).get("file", [])
if file_list_old:
    if show_old_filename.toggle("Show uploaded files"):
        st.write("#### Uploaded files:")
        for file in file_list_old:
            st.write(f"- {file}")

with st.sidebar.expander("Create new namespace"):
    new_namespace = st.text_input("Enter namespace")
    if st.button("Create namespace"):
        if new_namespace in st.session_state.namespace_list:
            st.error("Namespace already exists.")
            st.stop()
        if chatlogs_collection.find({"namespace": namespace}):
            st.error("Namespace is already in use.")
            st.stop()
        chatlogs_collection.insert_one({"username": st.session_state.username, 
                                        "namespace": new_namespace, 
                                        "file": [], 
                                        "config": {
                                            "stream": True,
                                            "memory": False,
                                            "language": "Thai",
                                            "kFromUser": 3,
                                            "threshold": 0.65},
                                        "chatlog": [],
                                        "chatmemory": []})
        st.session_state.namespace_list.append(new_namespace)
        st.rerun()

if len(st.session_state.namespace_list) >1:
    if delete_namespace.button("Delete namespace"):
        chatlogs_collection.delete_one({"namespace": namespace})
        try:
            pinecone_connect().delete(namespace=namespace, delete_all=True)
        except Exception:
            pass
        st.session_state.namespace_list.remove(namespace)
        st.session_state.namespace_list = st.session_state.namespace_list
        st.rerun()

uploaded_file = st.file_uploader("Choose a file", type=['csv', 'pdf', 'xlsx'])
uploaded_filename_list = None
if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)
        original_filename = uploaded_file.name
        uploaded_filename = unidecode(original_filename)
        st.write("Original Filename:", original_filename)
        st.write("Filename:", uploaded_filename)

        if original_filename in file_list_old:
            st.error("Duplicate file detected. Please upload a different file.")
            st.stop()
        else:
            try:
                file_extension = uploaded_filename.split('.')
                if file_extension[-1] in ['xls', 'xlsx']:
                    uploaded_filename_list = convert_excel_to_csv(uploaded_file, temp_dir, ".".join(file_extension[:-1]))
                elif file_extension == 'csv':
                    uploaded_filename = preprocess_csv(uploaded_filename, temp_dir)
                else:
                    with open(os.path.join(temp_dir, uploaded_filename), "wb") as f:
                        rawdata = uploaded_file.read()
                        result = chardet.detect(rawdata)
                        if result['encoding'] is None:
                            f.write(rawdata)
                        else:
                            encoding = 'utf-8' if file_extension in ['csv'] else result['encoding']
                            if result['encoding'] == 'UTF-16':
                                content = rawdata.decode('UTF-16').encode('utf-8')
                            else:
                                content = rawdata.decode(result['encoding'], 'ignore').encode(encoding)
                            f.write(content)
                if uploaded_filename_list is not None:
                    for file_name in uploaded_filename_list:
                        file_loader(namespace, file_name, original_filename, temp_dir)
                else:
                    file_loader(namespace, uploaded_filename, original_filename, temp_dir)
                
                
                if file_list_old is not None:
                    file_list_new = file_list_old + [original_filename]
                    chatlogs_collection.update_one({"namespace": namespace}, {"$set": {"file": file_list_new}})
                else:
                    chatlogs_collection.update_one({"namespace": namespace}, {"$set": {"file": [original_filename]}})
                
            except Exception as e:
                print("Error:", e)