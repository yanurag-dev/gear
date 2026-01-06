from src.core.models import Plan
from pydantic import ValidationError
from src.llm.adapter import generate_response
import json

class Planner:
    def generate_plan(self, goal: str, context: dict = None) -> Plan | str:
        # Pass the context (like current URL) to the adapter
        llm_output = generate_response(goal, context=context)

        if isinstance(llm_output, Plan):
            return llm_output
        elif isinstance(llm_output, str):
            try:
                # Try Pydantic's native parsing for strings (Pydantic v1/v2)
                if hasattr(Plan, 'parse_raw'): # Pydantic v1/v2
                    plan = Plan.parse_raw(llm_output)
                elif hasattr(Plan, 'model_validate_json'): # Pydantic v2
                    plan = Plan.model_validate_json(llm_output)
                else: # Pydantic v1 fallback
                    plan = Plan.parse_obj(json.loads(llm_output))
                return plan
            except ValidationError:
                # If it's a Pydantic validation error, return raw output
                return llm_output
            except json.JSONDecodeError:
                # If it's a JSON decode error, return raw output
                return llm_output
            except Exception:
                # Fallback for generic dataclass/POJO JSON
                try:
                    plan_data = json.loads(llm_output)
                    plan = Plan(**plan_data)
                    return plan
                except (json.JSONDecodeError, ValidationError):
                    # If still not a valid JSON Plan, treat as direct text response
                    return llm_output
        else:
            raise ValueError(f"Could not generate a plan or direct response for goal: {goal}")