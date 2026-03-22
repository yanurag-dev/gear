import json
import logging
from typing import Dict, Any, List
from src.llm.adapter import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

_logger = logging.getLogger(__name__)

_SYSTEM = (
    "You are an expert data extractor. Your goal is to map information from a user's documents "
    "into a specific JSON schema. Be semantic and accurate. If information for a field is not found, "
    "set it to null. Return ONLY valid JSON. Accuracy is paramount."
)

_HUMAN = """Given the following documents (Knowledge Context):
---
{knowledge_context}
---

Populate the following JSON schema:
{schema}

Ensure that:
1. All fields in the schema are present in the output.
2. If a value is missing or cannot be inferred from the documents, set it to null.
3. Use semantic mapping (e.g., if the schema asks for 'years_of_experience' and the resume lists dates, calculate the total years).
4. For lists/arrays, provide all relevant items found.
5. For boolean fields, infer the value based on the content (e.g., 'has_drivers_license').
6. Dates should be in YYYY-MM-DD format if possible, otherwise as they appear.
"""


class ContextResolver:
    def __init__(self) -> None:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", _SYSTEM),
            ("human", _HUMAN),
        ])
        self._chain = prompt | llm | JsonOutputParser()

    def resolve(self, target_schema: Dict[str, Any], knowledge_context: str) -> Dict[str, Any]:
        if not knowledge_context:
            _logger.warning("Empty knowledge context provided to ContextResolver.")
            return {field: None for field in target_schema}

        try:
            result = self._chain.invoke({
                "knowledge_context": knowledge_context,
                "schema": json.dumps(target_schema, indent=2),
            })
            assert isinstance(result, dict)
            for key in target_schema:
                if key not in result:
                    result[key] = None
            return result
        except Exception as e:
            _logger.error(f"ContextResolver chain failed: {e}")
            return {field: None for field in target_schema}

    def identify_gaps(self, resolved_data: Dict[str, Any]) -> List[str]:
        return [key for key, value in resolved_data.items() if value is None]
