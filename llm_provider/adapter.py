from agent_core.models import Plan, Action
from typing import Optional, Union
from config.loader import load_config
from llm_provider.gemini import initialize_gemini, get_gemini_response

config = load_config()
llm_provider_type = config.get('llm', {}).get('provider')
llm_api_key = config.get('llm', {}).get('api_key')

if llm_provider_type == 'gemini' and llm_api_key:
    initialize_gemini(llm_api_key)

def generate_response(goal: str) -> Union[Plan, str, None]:
    if llm_provider_type == 'gemini':
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