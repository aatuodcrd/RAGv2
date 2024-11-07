import env.settings as ENV
from utils.cohere import cohere_connector
from utils.pinecone import pinecone_connect

def embed_question(question):
    return cohere_connector().embed(texts=[question], input_type="search_document", model=ENV.COHERE_EMBEDDING_MODEL, truncate=None)

def search_documents_pinecone(question, kFromUser, namespace):
    vectors = embed_question(question).embeddings
    return pinecone_connect().query(vector=vectors[0], top_k=kFromUser, namespace=namespace)
