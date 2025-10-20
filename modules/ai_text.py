import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def improve_description(text):
    # PSEUDO: call OpenAI completion/chat completion and return improved text
    # For now return a simple enhanced string
    return text + "\n\n[Improved by AI: concise & catchy invitation text]"
