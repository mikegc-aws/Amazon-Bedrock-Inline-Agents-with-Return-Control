"""
Function model for Bedrock Agents SDK.
"""
from typing import Callable, Optional
from pydantic import BaseModel, ConfigDict

class Function(BaseModel):
    """Represents a function that can be called by the agent"""
    name: str
    description: str
    function: Callable
    action_group: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True) 