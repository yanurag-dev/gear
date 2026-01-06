from google import genai
from google.genai import errors
from typing import Optional
import logging
import threading

_client = None
_model_name = None
_client_lock = threading.Lock()
_logger = logging.getLogger(__name__)

def initialize_gemini(api_key: str, model_name: Optional[str] = None):
    global _client, _model_name
    with _client_lock:
        _client = genai.Client(api_key=api_key)
        # Use a default model if model_name is not provided or is empty
        _model_name = model_name if model_name else 'gemini-1.5-flash'

def get_gemini_response(prompt: str, system_instruction: Optional[str] = None, response_mime_type: str = "text/plain") -> Optional[str]:
    with _client_lock:
        client = _client
        model_name = _model_name

    if client is None:
        _logger.error("Gemini client not initialized. Call initialize_gemini first.")
        return None
    try:
        config = None
        if system_instruction:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type=response_mime_type
            )

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )
        if response is None or not hasattr(response, 'text'):
            _logger.error(f"Gemini API returned an invalid response for prompt: '{prompt}' and model: '{model_name}'. Response: {response}")
            return None
        return response.text
    except errors.APIError as e:
        _logger.exception(f"Gemini API error for prompt: '{prompt}' and model: '{model_name}'. Error: {e}")
        return None
    except Exception as e: # Catch other unexpected exceptions
        _logger.exception(f"An unexpected error occurred for prompt: '{prompt}' and model: '{model_name}'. Error: {e}")
        return None

def get_gemini_multimodal_response(prompt: str, image_path: str, system_instruction: Optional[str] = None) -> Optional[str]:
    with _client_lock:
        client = _client
        model_name = _model_name

    if client is None:
        _logger.error("Gemini client not initialized.")
        return None
    try:
        from google.genai import types
        import pathlib
        import mimetypes

        image_data = pathlib.Path(image_path).read_bytes()
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image/'):
            _logger.error(f"Invalid or unsupported image type for: {image_path}")
            return None
        
        config = None
        if system_instruction:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="text/plain"
            )

        response = client.models.generate_content(
            model=model_name,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_data, mime_type=mime_type)
            ],
            config=config
        )
        if response is None or not hasattr(response, 'text'):
            _logger.error(f"Gemini API returned an invalid multimodal response. Model: '{model_name}', Image present: {image_data is not None}. Response: {response}")
            return None
        return response.text
    except Exception as e:
        _logger.exception(f"Multimodal error: {e}")
        return None
