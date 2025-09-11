from agent_core.models import Plan, Action
from typing import Optional

def generate_mock_plan(goal: str) -> Optional[Plan]:
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
    return None
