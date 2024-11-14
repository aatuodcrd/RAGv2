from utils.cohere import cohere_connector
from utils.pinecone import pinecone_connect
import datetime
import google.generativeai as genai
from utils.mongoDB import chatlogs_collection
import env.settings as ENV

def embed_question(question: str) -> list:
    cohere = cohere_connector()
    return cohere.embed(texts=[question], input_type="search_document", model=ENV.COHERE_EMBEDDING_MODEL, truncate=None)

def search_documents_pinecone(question: str, kFromUser: int, threshold: float, namespace: str) -> list:
    vectors = embed_question(question).embeddings
    pinecone = pinecone_connect()
    matches_dict = pinecone.query(vector=vectors[0], top_k=kFromUser, namespace=namespace, include_metadata=True)
    doc_list = matches_dict.get('matches', [])
    return_doc_list = []
    if doc_list == []:
        return []
    for doc in doc_list:
        if doc['score'] >= threshold:
            doc['metadata']['score'] = doc['score']
            return_doc_list.append(doc['metadata'])
    return return_doc_list

def askChat(username: str, question: str, namespace: str) -> list:
    data_dict = chatlogs_collection.find_one({"username": username, "namespace": namespace})
    kFromUser = data_dict.get("config", {}).get("kFromUser", 3)
    threshold = data_dict.get("config", {}).get("threshold", 0.7)
    memory = data_dict.get("config", {}).get("memory", False)
    language = data_dict.get("config", {}).get("language", "Thai")
    retrieve_doc_list = search_documents_pinecone(question, kFromUser, threshold, namespace)
    text_retrieve_doc_list = [doc.get('text', '') for doc in retrieve_doc_list]
    
    genai.configure(api_key=ENV.GEMINI_API_KEY)
    LLM_model = ENV.GEMINI_MODEL
    model = genai.GenerativeModel(LLM_model)
    
    if memory:
        memory_list = data_dict.get("chatmemory", [])
        if retrieve_doc_list == [] and memory_list != []:
            ontop_text = "(Since I couldn't find any documents related to your question, I used only the data from memory and my basic knowledge to answer the question)\n" if language != "Thai" else "(เนื่องจากผมไม่พบเอกสารที่เกี่ยวข้องกับคำถามของคุณ ผมจึงใช้เพียงข้อมูลที่ได้รับจาก memory และความรู้พื้นฐานของผม ในการตอบคำถามเท่านั้น)\n"
            response = model.generate_content(f'You are a helpful assistant who can answer questions about documents uploaded by users. I would like you to answer in {language} language only.\nHere is the Chat history: """{memory_list}"""\nUse the Chat history to answer the question\nQuestion: {question}')
            answer = response.text + "\n\n" + ontop_text
            chatlogs_collection.update_one(
                {"username": username, "namespace": namespace},
                {
                    "$push": {
                        "chatmemory": {
                            "$each": [{"question": question, 
                                       "answer": response.text,
                                       "reference_docs": retrieve_doc_list if retrieve_doc_list else None}],
                            "$slice": -3
                        },
                        "chatlog": {
                            "question": question,
                            "answer": answer,
                            "reference_docs": retrieve_doc_list if retrieve_doc_list else None,
                            "chatmemory": memory_list if memory_list else [],
                            "LLM_model": LLM_model,
                            "config": data_dict.get("config", {}),
                            "timestamp": datetime.datetime.utcnow()
                        }
                    }
                }
            )
            return answer
        
        if retrieve_doc_list == [] and memory_list == []:
            answer = "Sorry, I couldn't find any memory and documents related to your question. Please try again with a lower threshold value." if language != "Thai" else "ขออภัยครับ ผมไม่พบ memory และเอกสารที่เกี่ยวข้องกับคำถามของคุณ โปรดลองใหม่อีกครั้งโดยปรับลดค่า Threshold ลงครับ"
            chatlogs_collection.update_one(
                {"username": username, "namespace": namespace},
                {
                    "$push": {
                        "chatlog": {
                            "question": question,
                            "answer": answer,
                            "reference_docs": retrieve_doc_list if retrieve_doc_list else None,
                            "chatmemory": memory_list if memory_list else [],
                            "LLM_model": LLM_model,
                            "config": data_dict.get("config", {}),
                            "timestamp": datetime.datetime.utcnow()
                        }
                    }
                }
            )
            return answer
        
        if retrieve_doc_list != [] and memory_list == []:
            ontop_text = "(Since I couldn't find any memory related to your question, I used only the data from the documents to answer the question)\n" if language != "Thai" else "(เนื่องจากผมไม่พบ memory ที่เกี่ยวข้องกับคำถามของคุณ ผมจึงใช้เพียงข้อมูลที่ได้รับจากเอกสารเท่านั้น)\n"
            response = model.generate_content(f'You are a helpful assistant who can answer questions about documents uploaded by users. I would like you to answer in {language} language only.\nHere is the document pieces: """{text_retrieve_doc_list}"""\nUse the document pieces to answer the question\nQuestion: {question}')
            answer = response.text + "\n\n" + ontop_text
            chatlogs_collection.update_one(
                {"username": username, "namespace": namespace},
                {
                    "$push": {
                        "chatmemory": {
                            "$each": [{"question": question, 
                                       "answer": response.text,
                                       "reference_docs": retrieve_doc_list if retrieve_doc_list else None}],
                            "$slice": -3
                        },
                        "chatlog": {
                            "question": question,
                            "answer": answer,
                            "reference_docs": retrieve_doc_list if retrieve_doc_list else None,
                            "chatmemory": memory_list if memory_list else [],
                            "LLM_model": LLM_model,
                            "config": data_dict.get("config", {}),
                            "timestamp": datetime.datetime.utcnow()
                        }
                    }
                }
            )
            return answer
        
        response = model.generate_content(f'You are a helpful assistant who can answer questions about documents uploaded by users. I would like you to answer in {language} language only.\nHere is the document pieces: """{text_retrieve_doc_list}"""\nChat history: """{memory_list}"""\nUse the document pieces and Chat history to answer the question\nQuestion: {question}')
        chatlogs_collection.update_one(
            {"username": username, "namespace": namespace}, 
            {
                "$push": {
                    "chatmemory": {
                        "$each": [{"question": question,
                                   "answer": response.text,
                                   "reference_docs": retrieve_doc_list if retrieve_doc_list else None}], 
                        "$slice": -3
                    }, 
                    "chatlog": {
                        "question": question, 
                        "answer": response.text, 
                        "reference_docs": retrieve_doc_list if retrieve_doc_list else None, 
                        "memory": memory_list if memory_list else [], 
                        "LLM_model": LLM_model, 
                        "config": data_dict.get("config", {}), 
                        "timestamp": datetime.datetime.utcnow()
                    }
                }
            }
        )
        
    else:
        if retrieve_doc_list == []:
            answer = "Sorry, I couldn't find any documents related to your question. Please try again with a lower threshold value." if language != "Thai" else "ขออภัยครับ ผมไม่พบเอกสารที่เกี่ยวข้องกับคำถามของคุณ โปรดลองใหม่อีกครั้งโดยปรับลดค่า Threshold ลงครับ"
            chatlogs_collection.update_one(
                {"username": username, "namespace": namespace}, 
                {
                    "$push": {
                        "chatlog": {
                            "question": question, 
                            "answer": answer, 
                            "reference_docs": retrieve_doc_list if retrieve_doc_list else None, 
                            "chatmemory": [], 
                            "LLM_model": LLM_model, 
                            "config": data_dict.get("config", {}), 
                            "timestamp": datetime.datetime.utcnow()
                        }
                    }
                }
            )
            return answer
        
        response = model.generate_content(f'You are a helpful assistant who can answer questions about documents uploaded by users. I would like you to answer in {language} language only.\nHere is the document pieces: """{text_retrieve_doc_list}"""\nUse the document pieces to answer the question\nQuestion: {question}')
        chatlogs_collection.update_one(
            {"username": username, "namespace": namespace}, 
            {
                "$push": {
                    "chatlog": {
                    "question": question, 
                    "answer": response.text, 
                    "reference_docs": retrieve_doc_list if retrieve_doc_list else None, 
                    "chatmemory": [], 
                    "LLM_model": LLM_model, 
                    "config": data_dict.get("config", {}), 
                    "timestamp": datetime.datetime.utcnow()
                    }
                }
            }
        )
    return response.text
