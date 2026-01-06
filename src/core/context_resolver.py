import json
import logging
from typing import Dict, Any, Optional
from src.llm.gemini import get_gemini_response

_logger = logging.getLogger(__name__)

class ContextResolver:
    def __init__(self):
        pass

    def resolve(self, target_schema: Dict[str, Any], knowledge_context: str) -> Dict[str, Any]:
        """
        Populates the target_schema based on the provided knowledge_context.
        """
        if not knowledge_context:
            _logger.warning("Empty knowledge context provided to ContextResolver.")
            return {field: None for field in target_schema}

        prompt = self._build_prompt(target_schema, knowledge_context)
        system_instruction = (
            "You are an expert data extractor. Your goal is to map information from a user's documents into a specific JSON schema. "
            "Be semantic and accurate. If information for a field is not found, set it to null. "
            "Return ONLY valid JSON. Accuracy is paramount."
        )
        
        response = get_gemini_response(
            prompt=prompt,
            system_instruction=system_instruction,
            response_mime_type="application/json"
        )

        if not response:
            _logger.error("Failed to get response from Gemini for context resolution.")
            return {field: None for field in target_schema}

        try:
            resolved_data = json.loads(response)
            # Ensure all keys from target_schema are present in resolved_data
            for key in target_schema:
                if key not in resolved_data:
                    resolved_data[key] = None
            return resolved_data
        except json.JSONDecodeError as e:
            _logger.error(f"Failed to parse JSON response from Gemini: {e}. Response: {response}")
            return {field: None for field in target_schema}

    def identify_gaps(self, resolved_data: Dict[str, Any]) -> list[str]:
        """
        Identifies fields that are null or missing in the resolved data.
        """
        return [key for key, value in resolved_data.items() if value is None]

    def _build_prompt(self, target_schema: Dict[str, Any], knowledge_context: str) -> str:
        schema_str = json.dumps(target_schema, indent=2)
        return f"""
Given the following documents (Knowledge Context):
---
{knowledge_context}
---

Populate the following JSON schema:
{schema_str}

Ensure that:
1. All fields in the schema are present in the output.
2. If a value is missing or cannot be inferred from the documents, set it to null.
3. Use semantic mapping (e.g., if the schema asks for 'years_of_experience' and the resume lists dates, calculate the total years).
4. For lists/arrays, provide all relevant items found.
5. For boolean fields, infer the value based on the content (e.g., 'has_drivers_license').
6. Dates should be in YYYY-MM-DD format if possible, otherwise as they appear.
"""
