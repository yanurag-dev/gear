import google.generativeai as genai
from typing import Optional
import logging

_gemini_model = None
_logger = logging.getLogger(__name__)

def initialize_gemini(api_key: str):
    global _gemini_model
    genai.configure(api_key=api_key)
    _gemini_model = genai.GenerativeModel('gemini-2.5-flash')

def get_gemini_response(prompt: str) -> Optional[str]:
    if _gemini_model is None:
        _logger.error("Gemini model not initialized. Call initialize_gemini first.")
        return None
    try:
        response = _gemini_model.generate_content(prompt)
        if response is None or not hasattr(response, 'text'):
            _logger.error(f"Gemini API returned an invalid response for prompt: '{prompt}' and model: '{_gemini_model.model_name}'. Response: {response}")
            return None
        return response.text
    except genai.APIError as e:
        _logger.exception(f"Error interacting with Gemini API for prompt: '{prompt}' and model: '{_gemini_model.model_name}'. Error: {e}")
        return None
    except Exception as e: # Catch other unexpected exceptions
        _logger.exception(f"An unexpected error occurred for prompt: '{prompt}' and model: '{_gemini_model.model_name}'. Error: {e}")
        return None
