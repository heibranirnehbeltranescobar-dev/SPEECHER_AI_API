import os
from google import genai
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

#Injector: Provides a Google GenAI client's instance.
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Unable to find GEMINI_API_KEY in the .env file")
    return genai.Client(api_key=api_key)

def get_pinecone_client():

    api_key = os.getenv("PINECONE_API_KEY")
    api_index = os.getenv("PINECONE_INDEX_NAME")

    if not api_key or not api_index:
        raise ValueError("Unable to find PINECONE .env variables")
    pc = Pinecone(api_key=api_key)
    index = pc.Index(api_index)

    return index