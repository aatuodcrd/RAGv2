import os
import itertools
import env.settings as ENV
from fixthaipdf import clean
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import CSVLoader, PyMuPDFLoader
from utils.cohere import cohere_connector
from utils.pinecone import pinecone_connect

def delete_file_duplicate(uploaded_filename, folder_path):
    try:
        file_path = os.path.join(folder_path, uploaded_filename)
        os.remove(file_path)
    except Exception as e:
        pass

def chunks(iterable, batch_size=100):
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))

def upsert_to_pinecone(filename, original_filename, document, namespace):
    folder = namespace
    embeddings_values_list = []
    chunk_size_embeddings = 90
    for i in range(0, len(document), chunk_size_embeddings):
        chunkForEmbeddings = [doc.page_content for doc in document[i:i+chunk_size_embeddings] if hasattr(doc, 'page_content')]
        if not chunkForEmbeddings:
            continue
        embeddings_values = cohere_connector().embed(
            texts=chunkForEmbeddings,
            input_type="search_document",
            model=ENV.COHERE_EMBEDDING_MODEL,
            truncate=None
        )
        embeddings_values_list.extend(embeddings_values.embeddings)
    upsert_data = []
    for i, (EBDV, doc) in enumerate(zip(embeddings_values_list, document)):
        id = f"{filename}_doc_{i+1}"
        metadata = {
            "fileName": original_filename,
            "text": doc.page_content
        }
        upsert_data.append({
            "id": id,
            "values": EBDV,
            "metadata": metadata
        })
    pinecone_connect().upsert(vectors=upsert_data, namespace=folder)
    document.clear()

def file_loader(namespace, filename, original_filename, directory):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    document = []
    length = None

    if filename.endswith(".csv"):
        number = 1500
        text_splitter_csv = RecursiveCharacterTextSplitter(chunk_size=number, chunk_overlap=0)
        loader = CSVLoader(os.path.join(directory, filename), encoding='utf-8')
        document.extend(text_splitter_csv.split_documents(loader.load()))
        length = len(document)
        upsert_to_pinecone(filename, original_filename, document, namespace)
        delete_file_duplicate(filename, directory)
        
    if filename.endswith(".pdf"):
        loader = PyMuPDFLoader(os.path.join(directory, filename))
        pages = loader.load()
        data = [clean(page.page_content) for page in pages]
        metadatas = [page.metadata for page in pages]
        document.extend(text_splitter.create_documents(data,metadatas=metadatas))
        length = len(document)
        upsert_to_pinecone(filename, original_filename, document, namespace)
        delete_file_duplicate(filename, directory)

    return length