"""
Utility functions for parameter conversion.
"""
from typing import Dict, Any, List

def convert_parameters(parameters: List[Dict[str, Any]], sdk_logs: bool = False) -> Dict[str, Any]:
    """
    Convert parameters from agent format to Python format
    
    Args:
        parameters: List of parameter dictionaries from the agent
        sdk_logs: Whether to log conversion details
        
    Returns:
        Dictionary of converted parameters
    """
    param_dict = {}
    for param in parameters:
        name = param.get("name")
        value = param.get("value")
        param_type = param.get("type")
        
        if param_type == "number":
            try:
                value = float(value)
                if value.is_integer():
                    value = int(value)
            except ValueError:
                if sdk_logs:
                    print(f"\n[SDK LOG] Warning: Could not convert {value} to number")
                continue
        elif param_type == "boolean":
            if value.lower() in ["true", "yes", "1"]:
                value = True
            elif value.lower() in ["false", "no", "0"]:
                value = False
        
        param_dict[name] = value
    
    if sdk_logs:
        print(f"[SDK LOG] Parameters processed: {param_dict}")
    return param_dict 