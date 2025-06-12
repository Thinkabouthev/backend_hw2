import os
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

model = genai.GenerativeModel("gemini-pro") 

def ask_gemini(promt: str) -> str:
    response = model.generate_content(promt)
    return response.text


