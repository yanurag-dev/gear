from src.core.models import Plan, Action
from typing import Optional, Union
from src.config.loader import load_config
from src.llm.gemini import initialize_gemini, get_gemini_response
import logging
import json

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

        if _llm_provider_type == 'google':
            if not _llm_api_key:
                _logger.warning("Google GenAI (Gemini) configured but LLM_API_KEY (or api_key in config) is missing. Falling back to mock responses.")
                _llm_provider_type = None  # Fall back to mock behavior
            else:
                # The 'google' provider uses Gemini under the hood
                initialize_gemini(_llm_api_key, _llm_model) # Initialize Gemini with the API key and model
        # Add other LLM providers here if needed

        _initialized = True
    except Exception as e:
        _logger.exception(f"Failed to initialize LLM provider: {e}")
        raise # Re-raise the exception after logging

SYSTEM_PROMPT = """You are an AI task-runner agent called 'Gear'. 
Your goal is to help users automate tasks by generating structured execution plans or providing direct answers.

### AVAILABLE TOOLS (MCPs)
1. **playwright**: For browser automation.
   - action: 'navigate' (args: {url: str})
   - action: 'click' (args: {selector: str})
   - action: 'type' (args: {selector: str, text: str})
   - action: 'scrape' (args: {url: str})
   - action: 'get_form_fields' (args: {}): Returns JSON list of all input fields on the page.
2. **filesystem**: For binary and text file operations.
   - action: 'read_file' (args: {path: str})
   - action: 'write_file' (args: {path: str, content: str})
3. **ai**: For intelligent reasoning and vision.
   - action: 'ocr' (args: {path: str, prompt: str}): Performs OCR on an image and returns structured data.
4. **notion**: For Notion workspace interactions.
   - action: 'create_page' (args: {parent_id: str, properties: dict})

### FORM FILLING CAPABILITY
Gear is an autonomous form-filling agent. The workflow is:
1. **Scouting**: When asked to investigate or analyze a form, use `playwright.navigate` then `playwright.get_form_fields`. This returns a JSON schema of the form to the user.
2. **Filling**: When provided with a URL and data (JSON/text), map the data values to the fields discovered in scouting. Use `playwright.type(selector=..., text=...)` for each field. Use the `id`, `name`, or a CSS selector based on the scouting results.
3. **Submission**: Click the submit button after filling.

### OUTPUT FORMAT
... (rest of the format)
If the task requires multiple steps or external tools, respond with a JSON object following this structure:
{
    "goal": "the original user goal",
    "steps": [
        {
            "mcp": "mcp_name",
            "action": "action_name",
            "args": {"arg_name": "value"}
        }
    ]
}

If the task can be answered directly without tools (e.g., 'what is the capital of France?'), respond with a plain text answer.
Always prefer direct text answers for simple knowledge questions.
"""

def generate_response(goal: str, context: Optional[dict] = None) -> Union[Plan, str, None]:
    _ensure_initialized()
    
    # Enrich the goal with current browser context if available
    enriched_goal = goal
    url = context.get("url") if context else None
    if isinstance(url, str) and url.strip():
        enriched_goal = f"Current Browser URL: {url}\nUser Goal: {goal}"

    if _llm_provider_type == 'google':
        # For Gemini, we'll send the raw goal and expect a text response or JSON plan.
        response = get_gemini_response(
            enriched_goal, 
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json"
        )
        
        if not response:
            return None
            
        # Try to parse response as a JSON Plan
        if isinstance(response, str):
            try:
                # Clean up potential markdown formatting
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
                # Try to load as Plan
                return Plan.model_validate_json(cleaned_response)
            except Exception:
                _logger.debug("Failed to parse response as Plan, returning as raw string.")
        
        return response
    else: # Default to mock behavior
        if "open google" in enriched_goal.lower():
            return Plan(
                goal=enriched_goal,
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
        elif "search for" in enriched_goal.lower():
            query = enriched_goal.lower().split("search for", 1)[1].strip()
            return Plan(
                goal=enriched_goal,
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
        elif "what is" in enriched_goal.lower() or "calculate" in enriched_goal.lower():
            # Simulate a direct answer for knowledge-based queries
            if "2 + 2" in enriched_goal.lower():
                return "4"
            else:
                return "I don't know the answer to that directly yet."
        return None