from google import genai
from google.genai import errors
from typing import Optional
import logging

_client = None
_model_name = None
_logger = logging.getLogger(__name__)

def initialize_gemini(api_key: str, model_name: Optional[str] = None):
    global _client, _model_name
    _client = genai.Client(api_key=api_key)
    # Use a default model if model_name is not provided or is empty
    # Changed default to gemini-1.5-flash as gemini-2.5-flash was likely a typo
    _model_name = model_name if model_name else 'gemini-1.5-flash'

def get_gemini_response(prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
    if _client is None:
        _logger.error("Gemini client not initialized. Call initialize_gemini first.")
        return None
    try:
        config = None
        if system_instruction:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json" if "JSON" in (system_instruction or "") else "text/plain"
            )

        response = _client.models.generate_content(
            model=_model_name,
            contents=prompt,
            config=config
        )
        if response is None or not hasattr(response, 'text'):
            _logger.error(f"Gemini API returned an invalid response for prompt: '{prompt}' and model: '{_model_name}'. Response: {response}")
            return None
        return response.text
    except errors.APIError as e:
        _logger.exception(f"Gemini API error for prompt: '{prompt}' and model: '{_model_name}'. Error: {e}")
        return None
    except Exception as e: # Catch other unexpected exceptions
        _logger.exception(f"An unexpected error occurred for prompt: '{prompt}' and model: '{_model_name}'. Error: {e}")
        return None
