import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("Listing available models...")
for m in genai.list_models():
    if 'embedContent' in m.supported_generation_methods:
        print(f"Embedding Model: {m.name}")
    elif 'generateContent' in m.supported_generation_methods:
        print(f"Generation Model: {m.name}")
