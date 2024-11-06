import cohere
import env.settings as ENV

def cohere_connector():
    cohere_connect = cohere.Client(ENV.COHERE_API_KEY)
    return cohere_connect