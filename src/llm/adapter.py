from typing import Optional
from src.config.loader import load_config
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
import logging

_logger = logging.getLogger(__name__)

_llm: Optional[BaseChatModel] = None
_initialized = False

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


def get_llm() -> BaseChatModel:
    """Returns the initialized LangChain LLM. Initializes on first call."""
    global _llm, _initialized
    if _initialized and _llm is not None:
        return _llm

    config = load_config()
    provider = config.get('llm', {}).get('provider', 'google')
    api_key = config.get('llm', {}).get('api_key')
    model = config.get('llm', {}).get('model')

    if provider == 'google':
        from langchain_google_genai import ChatGoogleGenerativeAI
        _llm = ChatGoogleGenerativeAI(
            model=model or 'gemini-1.5-flash',
            google_api_key=api_key,
        )
    elif provider == 'openai':
        from langchain_openai import ChatOpenAI
        _llm = ChatOpenAI(
            model=model or 'gpt-4o-mini',
            api_key=api_key,
        )
    elif provider == 'anthropic':
        from langchain_anthropic import ChatAnthropic
        _llm = ChatAnthropic(
            model=model or 'claude-sonnet-4-6',
            api_key=api_key,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    _initialized = True
    return _llm


def _ensure_initialized() -> None:
    get_llm()


def generate_response(goal: str, context: Optional[dict] = None) -> str:
    """Send a goal to the LLM and return the raw text response."""
    llm = get_llm()

    enriched_goal = goal
    url = context.get("url") if context else None
    if isinstance(url, str) and url.strip():
        enriched_goal = f"Current Browser URL: {url}\nUser Goal: {goal}"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=enriched_goal),
    ]

    response = llm.invoke(messages)
    return str(response.content)
