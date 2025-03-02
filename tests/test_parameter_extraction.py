import pytest
from bedrock_agents_sdk.utils.parameter_extraction import extract_parameter_info

# Sample functions for testing
def function_with_no_params():
    """A function with no parameters"""
    return {"status": "success"}

def function_with_params(param1: str, param2: int = 123):
    """A function with parameters
    
    :param param1: A string parameter
    :param param2: An integer parameter with default value
    """
    return {"param1": param1, "param2": param2}

def function_with_bool_param(enable: bool = False):
    """A function with a boolean parameter
    
    :param enable: A boolean parameter
    """
    return {"enable": enable}

def function_with_no_docstring(param1: str, param2: int = 123):
    return {"param1": param1, "param2": param2}

class TestParameterExtraction:
    def test_extract_no_params(self):
        """Test extracting parameters from a function with no parameters"""
        params = extract_parameter_info(function_with_no_params)
        assert params == {}
    
    def test_extract_with_params(self):
        """Test extracting parameters from a function with parameters"""
        params = extract_parameter_info(function_with_params)
        
        assert "param1" in params
        assert "param2" in params
        
        assert params["param1"]["type"] == "string"
        assert params["param1"]["required"] == True
        assert params["param1"]["description"] == "A string parameter"
        
        assert params["param2"]["type"] == "number"
        assert params["param2"]["required"] == False
        assert params["param2"]["description"] == "An integer parameter with default value"
    
    def test_extract_bool_param(self):
        """Test extracting a boolean parameter"""
        params = extract_parameter_info(function_with_bool_param)
        
        assert "enable" in params
        assert params["enable"]["type"] == "boolean"
        assert params["enable"]["required"] == False
        assert params["enable"]["description"] == "A boolean parameter"
    
    def test_extract_no_docstring(self):
        """Test extracting parameters from a function with no docstring"""
        params = extract_parameter_info(function_with_no_docstring)
        
        assert "param1" in params
        assert "param2" in params
        
        assert params["param1"]["type"] == "string"
        assert params["param1"]["required"] == True
        assert params["param1"]["description"] == "The param1 parameter"
        
        assert params["param2"]["type"] == "number"
        assert params["param2"]["required"] == False
        assert params["param2"]["description"] == "The param2 parameter" 