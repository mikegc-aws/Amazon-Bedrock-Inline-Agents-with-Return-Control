"""
ActionGroup model for Bedrock Agents SDK.
"""
from typing import List, Union, Callable, Optional
from pydantic import BaseModel, ConfigDict

from bedrock_agents_sdk.models.function import Function

class ActionGroup(BaseModel):
    """Represents an action group in the agent"""
    name: str
    description: str
    functions: List[Union[Function, Callable]] = []
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, **data):
        """Initialize the action group and process functions if provided"""
        super().__init__(**data)
        self._process_functions()
    
    def _process_functions(self):
        """Process functions provided in the constructor"""
        processed_functions = []
        
        # Process each function
        for item in self.functions:
            if isinstance(item, Function):
                # Already a Function object, keep as is
                processed_functions.append(item)
            elif callable(item):
                # Convert callable to Function object
                processed_functions.append(self._create_function(item))
        
        # Replace the original functions list with processed functions
        self.functions = processed_functions
    
    def _create_function(self, function: Callable, description: Optional[str] = None) -> Function:
        """Create a Function object from a callable"""
        func_name = function.__name__
        
        # Use provided description or extract first line of docstring
        if description:
            func_desc = description
        elif function.__doc__:
            # Extract only the first line of the docstring
            func_desc = function.__doc__.strip().split('\n')[0]
        else:
            func_desc = f"Execute the {func_name} function"
        
        return Function(
            name=func_name,
            description=func_desc,
            function=function,
            action_group=self.name
        ) 