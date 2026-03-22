from src.core.models import Plan
from src.llm.adapter import get_llm, generate_response, SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Optional, Union
import json
import logging

_logger = logging.getLogger(__name__)


class Planner:
    def generate_plan(self, goal: str, context: Optional[dict] = None) -> Union[Plan, str]:
        llm = get_llm()

        enriched_goal = goal
        url = context.get("url") if context else None
        if isinstance(url, str) and url.strip():
            enriched_goal = f"Current Browser URL: {url}\nUser Goal: {goal}"

        # Use structured output to get a Plan directly when possible
        structured_llm = llm.with_structured_output(Plan, include_raw=True)

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=enriched_goal),
        ]

        try:
            result = structured_llm.invoke(messages)
            parsed = result.get("parsed")
            if isinstance(parsed, Plan):
                return parsed
        except Exception:
            _logger.debug("Structured output failed, falling back to raw response.")

        # Fallback: raw text response, try to parse as JSON Plan
        raw = generate_response(goal, context=context)
        if not raw:
            raise ValueError(f"Could not generate a plan or direct response for goal: {goal}")

        try:
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            return Plan.model_validate_json(cleaned)
        except Exception:
            pass

        try:
            data = json.loads(raw.strip())
            return Plan.model_validate(data)
        except Exception:
            pass

        return raw
