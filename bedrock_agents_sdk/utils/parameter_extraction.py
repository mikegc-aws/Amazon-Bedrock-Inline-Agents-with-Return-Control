"""
Utility functions for parameter extraction.
"""
import inspect
from typing import Dict, Any, Callable

def extract_parameter_info(function: Callable) -> Dict[str, Dict[str, Any]]:
    """
    Extract parameter information from a function using type hints and docstring
    
    Args:
        function: The function to extract parameter information from
        
    Returns:
        Dictionary of parameter information
    """
    params = {}
    sig = inspect.signature(function)
    
    for param_name, param in sig.parameters.items():
        # Skip self parameter for methods
        if param_name == 'self':
            continue
            
        # Determine parameter type from annotations or default to string
        param_type = "string"
        if param.annotation != inspect.Parameter.empty:
            if param.annotation == int or param.annotation == float:
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
        
        # Determine if parameter is required
        required = param.default == inspect.Parameter.empty
        
        # Look for parameter description in docstring
        param_desc = f"The {param_name} parameter"
        if function.__doc__:
            # Look for :param param_name: in docstring
            for line in function.__doc__.split('\n'):
                line = line.strip()
                if line.startswith(f":param {param_name}:"):
                    param_desc = line.split(f":param {param_name}:")[1].strip()
        
        # Add parameter definition
        params[param_name] = {
            "description": param_desc,
            "required": required,
            "type": param_type
        }
    
    return params 