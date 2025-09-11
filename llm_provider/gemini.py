import google.generativeai as genai
from typing import Optional

def initialize_gemini(api_key: str):
    genai.configure(api_key=api_key)

def get_gemini_response(prompt: str) -> Optional[str]:
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error interacting with Gemini API: {e}")
        return None
