from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class Action(BaseModel):
    mcp: Literal["playwright", "filesystem", "notion"] = Field(..., description="The Model Context Protocol (MCP) to invoke.")
    action: str = Field(..., description="The specific action to perform within the MCP.")
    args: Dict[str, Any] = Field(default_factory=dict, description="Arguments for the MCP action.")

class Plan(BaseModel):
    goal: str = Field(..., description="The original high-level goal.")
    steps: List[Action] = Field(..., description="A list of actions to achieve the goal.")
