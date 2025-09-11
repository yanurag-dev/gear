from agent_core.models import Plan, Action
from typing import Optional, Union
from config.loader import load_config
from llm_provider.gemini import initialize_gemini, get_gemini_response
import logging

_logger = logging.getLogger(__name__)

_initialized = False
_llm_provider_type = None
_llm_api_key = None
_llm_model = None # To store the model name if needed

def _ensure_initialized():
    global _initialized, _llm_provider_type, _llm_api_key, _llm_model
    if _initialized:
        return

    try:
        config = load_config()
        if config is None:
            raise ValueError("Failed to load configuration: config is None")
        _llm_provider_type = config.get('llm', {}).get('provider')
        _llm_api_key = config.get('llm', {}).get('api_key')
        _llm_model = config.get('llm', {}).get('model') # Get model name from config

        if _llm_provider_type == 'gemini':
            if not _llm_api_key:
                _logger.warning("Gemini configured but GEMINI_API_KEY is missing. Falling back to mock responses.")
                _llm_provider_type = None  # Fall back to mock behavior
            else:
                initialize_gemini(_llm_api_key, _llm_model) # Initialize Gemini with the API key and model
        # Add other LLM providers here if needed

        _initialized = True
    except Exception as e:
        _logger.exception(f"Failed to initialize LLM provider: {e}")
        raise # Re-raise the exception after logging

def generate_response(goal: str) -> Union[Plan, str, None]:
    _ensure_initialized() # Ensure initialization before proceeding

    if _llm_provider_type == 'gemini':
        # For Gemini, we'll send the raw goal and expect a text response.
        # The Planner will then interpret this text response.
        return get_gemini_response(goal)
    else: # Default to mock behavior
        if "open google" in goal.lower():
            return Plan(
                goal=goal,
                steps=[
                    Action(
                        mcp="playwright",
                        action="navigate",
                        args={
                            "url": "https://www.google.com"
                        }
                    )
                ]
            )
        elif "search for" in goal.lower():
            query = goal.lower().split("search for", 1)[1].strip()
            return Plan(
                goal=goal,
                steps=[
                    Action(
                        mcp="playwright",
                        action="navigate",
                        args={
                            "url": f"https://www.google.com/search?q={query}"
                        }
                    )
                ]
            )
        elif "what is" in goal.lower() or "calculate" in goal.lower():
            # Simulate a direct answer for knowledge-based queries
            if "2 + 2" in goal.lower():
                return "4"
            else:
                return "I don't know the answer to that directly yet."
        return None