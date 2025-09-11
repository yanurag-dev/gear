import google.generativeai as genai
from typing import Optional
import logging
from google.generativeai.types import (
    BlockedPromptException,
    BrokenResponseError,
    IncompleteIterationError,
    StopCandidateException
)
from google.api_core import exceptions as api_core_exceptions # For gRPC errors

_gemini_model = None
_logger = logging.getLogger(__name__)

def initialize_gemini(api_key: str, model_name: Optional[str] = None):
    global _gemini_model
    genai.configure(api_key=api_key)
    # Use a default model if model_name is not provided or is empty
    actual_model_name = model_name if model_name else 'gemini-2.5-flash'
    _gemini_model = genai.GenerativeModel(actual_model_name)

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
    except (
        BlockedPromptException,
        BrokenResponseError,
        IncompleteIterationError,
        StopCandidateException
    ) as e: # Gemini-specific exceptions
        _logger.exception(f"Gemini API error for prompt: '{prompt}' and model: '{_gemini_model.model_name}'. Error: {e}")
        return None
    except (
        api_core_exceptions.InvalidArgument,
        api_core_exceptions.NotFound,
        api_core_exceptions.PermissionDenied,
        api_core_exceptions.DeadlineExceeded,
        api_core_exceptions.ServiceUnavailable,
        api_core_exceptions.ResourceExhausted, # TooManyRequests
        api_core_exceptions.InternalServerError, # Internal/Unknown
        api_core_exceptions.Unknown
    ) as e:
        _logger.exception(f"Google API Core exception for prompt: '{prompt}' and model: '{_gemini_model.model_name}'. Error: {e}")
        return None
    except Exception as e: # Catch other unexpected exceptions
        _logger.exception(f"An unexpected error occurred for prompt: '{prompt}' and model: '{_gemini_model.model_name}'. Error: {e}")
        return None
