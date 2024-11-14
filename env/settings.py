import os
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGO_URI=os.getenv("MONGO_URI")
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME=os.getenv("PINECONE_INDEX_NAME")
COHERE_API_KEY=os.getenv("COHERE_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

MONGO_PROJECT_DATABASE="Project"
MONGO_USERS_COLLECTION="users"
MONGO_CHATLOGS_COLLECTION="chatlogs"

COHERE_EMBEDDING_MODEL="embed-multilingual-v3.0"

GEMINI_MODEL="gemini-1.5-flash"