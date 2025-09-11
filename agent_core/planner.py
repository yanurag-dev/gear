from agent_core.models import Plan
from llm_provider.adapter import generate_response
import json

class Planner:
    def generate_plan(self, goal: str) -> Plan | str:
        # This calls the adapter, which might use Gemini or mock logic
        llm_output = generate_response(goal)

        if isinstance(llm_output, Plan):
            return llm_output
        elif isinstance(llm_output, str):
            # If LLM returns a string, try to parse it as a Plan (e.g., from Gemini)
            try:
                # Assuming LLM might return a JSON string representing a Plan
                plan_data = json.loads(llm_output)
                plan = Plan(**plan_data)
                return plan
            except (json.JSONDecodeError, ValueError):
                # If it's not a valid JSON Plan, treat it as a direct text response
                return llm_output
        else:
            raise ValueError(f"Could not generate a plan or direct response for goal: {goal}")