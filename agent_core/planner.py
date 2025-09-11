from agent_core.models import Plan
from llm_provider.adapter import generate_mock_plan

class Planner:
    def generate_plan(self, goal: str) -> Plan:
        # In a real scenario, this would call a real LLM
        plan = generate_mock_plan(goal)
        if not plan:
            raise ValueError(f"Could not generate a plan for goal: {goal}")
        return plan
