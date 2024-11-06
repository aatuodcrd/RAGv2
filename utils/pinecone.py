from pinecone.grpc import PineconeGRPC as Pinecone
import env.settings as ENV

def pinecone_connect():
    pc = Pinecone(api_key=ENV.PINECONE_API_KEY)
    index = pc.Index(ENV.PINECONE_INDEX_NAME)
    return index