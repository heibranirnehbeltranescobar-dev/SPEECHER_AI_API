import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

#Injector: Provides a Google GenAI client's instance.
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Unable to find GEMINI_API_KEY in the .env file")
    return genai.Client(api_key=api_key)