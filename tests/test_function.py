import pytest
from bedrock_agents_sdk import Function

# Sample functions for testing
def sample_function() -> dict:
    """A sample function that returns a dictionary"""
    return {"status": "success"}

def sample_function_with_params(param1: str, param2: int = 123) -> dict:
    """A sample function that takes parameters and returns a dictionary
    
    :param param1: A string parameter
    :param param2: An integer parameter
    """
    return {"param1": param1, "param2": param2}

class TestFunction:
    def test_function_initialization(self):
        """Test that a function can be initialized"""
        func = Function(
            name="test_function",
            description="A test function",
            function=sample_function
        )
        
        assert func.name == "test_function"
        assert func.description == "A test function"
        assert func.function == sample_function
        assert func.action_group is None
    
    def test_function_with_action_group(self):
        """Test that a function can be initialized with an action group"""
        func = Function(
            name="test_function",
            description="A test function",
            function=sample_function,
            action_group="TestActions"
        )
        
        assert func.name == "test_function"
        assert func.description == "A test function"
        assert func.function == sample_function
        assert func.action_group == "TestActions"
    
    def test_function_execution(self):
        """Test that a function can be executed"""
        func = Function(
            name="sample_function",
            description="A sample function",
            function=sample_function
        )
        
        result = func.function()
        assert result == {"status": "success"}
    
    def test_function_with_params_execution(self):
        """Test that a function with parameters can be executed"""
        func = Function(
            name="sample_function_with_params",
            description="A sample function with parameters",
            function=sample_function_with_params
        )
        
        result = func.function(param1="test", param2=456)
        assert result == {"param1": "test", "param2": 456} 