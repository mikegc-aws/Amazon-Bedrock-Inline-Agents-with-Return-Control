"""
Agent model for Bedrock Agents SDK.
"""
from typing import List, Dict, Any, Optional, Union, Callable
from pydantic import BaseModel, ConfigDict

from bedrock_agents_sdk.models.function import Function
from bedrock_agents_sdk.models.files import InputFile

class Agent(BaseModel):
    """Represents a Bedrock agent configuration"""
    name: str
    model: str
    instructions: str
    functions: List[Union[Function, Callable]] = []
    enable_code_interpreter: bool = False
    files: List[InputFile] = []
    advanced_config: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, **data):
        """Initialize the agent and process functions if provided"""
        # Handle dictionary format for functions
        if 'functions' in data and isinstance(data['functions'], dict):
            action_groups = data.pop('functions')
            processed_functions = []
            
            for action_group, funcs in action_groups.items():
                for func in funcs:
                    processed_functions.append(self._create_function(func, action_group=action_group))
            
            data['functions'] = processed_functions
        
        # Initialize files list if not provided
        if 'files' not in data:
            data['files'] = []
            
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
                # Single function without action group
                processed_functions.append(self._create_function(item))
        
        # Replace the original functions list with processed functions
        self.functions = processed_functions
    
    def _create_function(self, function: Callable, description: Optional[str] = None, action_group: Optional[str] = None) -> Function:
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
            action_group=action_group
        )
    
    def add_function(self, function: Callable, description: Optional[str] = None, action_group: Optional[str] = None):
        """Add a function to the agent"""
        self.functions.append(self._create_function(function, description, action_group))
        return self

    def add_file(self, name: str, content: bytes, media_type: str, use_case: str = "CODE_INTERPRETER") -> InputFile:
        """Add a file to be sent to the agent"""
        file = InputFile(name=name, content=content, media_type=media_type, use_case=use_case)
        self.files.append(file)
        return file
    
    def add_file_from_path(self, file_path: str, use_case: str = "CODE_INTERPRETER") -> InputFile:
        """Add a file from a local path"""
        import mimetypes
        import os
        
        name = os.path.basename(file_path)
        media_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return self.add_file(name, content, media_type, use_case) 