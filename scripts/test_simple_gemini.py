import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

# Try with gemini-2.0-flash which was listed as available
model_name = "gemini-2.0-flash"

print(f"Testing model: {model_name}...")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, are you working?")
    print("Success!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error testing {model_name}:")
    print(e)
