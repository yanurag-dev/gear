from src.core.models import Plan, Action
from typing import Optional, Union
from src.config.loader import load_config
from src.llm.gemini import initialize_gemini, get_gemini_response
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

        if _llm_provider_type == 'google':
            if not _llm_api_key:
                _logger.warning("Gemini configured but LLM_API_KEY (or api_key in config) is missing. Falling back to mock responses.")
                _llm_provider_type = None  # Fall back to mock behavior
            else:
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

def generate_response(goal: str) -> Union[Plan, str, None]:

    if _llm_provider_type == 'google':
        # For Gemini, we'll send the raw goal and expect a text response or JSON plan.
        # We provide a system prompt to guide it to output JSON for tool calls.
        return get_gemini_response(goal, system_instruction=SYSTEM_PROMPT)
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