from utils.cohere import cohere_connector
from utils.pinecone import pinecone_connect
import env.settings  as ENV

def embed_question(question):
    cohere = cohere_connector()
    return cohere.embed(texts=[question], input_type="search_document", model=ENV.COHERE_EMBEDDING_MODEL, truncate=None)

def search_documents_pinecone(question, kFromUser, namespace):
    vectors = embed_question(question).embeddings
    pinecone = pinecone_connect()
    return pinecone.query(vector=vectors[0], top_k=kFromUser, namespace=namespace, include_metadata=True)