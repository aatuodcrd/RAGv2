# Project Documentation

## Overview

This project is a document processing and chat application built with Streamlit. It allows users to upload files, process them, and interact with a chat interface that can answer questions based on the uploaded documents.

## Features

- **File Upload**: Supports uploading CSV, PDF, and Excel files.
- **Document Processing**: Cleans and preprocesses uploaded files.
- **Embedding and Upsert**: Embeds document content using Cohere and upserts it to Pinecone for efficient querying.
- **Chat Interface**: Provides a chat interface to ask questions about the uploaded documents.
- **Memory Mode**: Option to enable memory mode to use previous conversations for context.

## Install the required packages:
```sh
pip install -r requirements.txt
```

## Usage
1. Run the Streamlit application:
    ```sh
    streamlit run app.py
    ```

2. Open the application in your browser and log in with your credentials.

3. Navigate to the "Upload file" page to upload and process your documents.

4. Use the "Chat" page to ask questions about the uploaded documents.

