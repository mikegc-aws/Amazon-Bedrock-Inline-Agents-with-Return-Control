import pytest
from bedrock_agents_sdk import ActionGroup, Function

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

class TestActionGroup:
    def test_action_group_initialization(self):
        """Test that an action group can be initialized"""
        func1 = Function(
            name="sample_function",
            description="A sample function",
            function=sample_function
        )
        
        func2 = Function(
            name="sample_function_with_params",
            description="A sample function with parameters",
            function=sample_function_with_params
        )
        
        action_group = ActionGroup(
            name="TestActions",
            description="Test actions",
            functions=[func1, func2]
        )
        
        assert action_group.name == "TestActions"
        assert action_group.description == "Test actions"
        assert len(action_group.functions) == 2
        assert action_group.functions[0].name == "sample_function"
        assert action_group.functions[1].name == "sample_function_with_params"
    
    def test_action_group_model_dump(self):
        """Test that an action group can be converted to a dictionary"""
        func1 = Function(
            name="sample_function",
            description="A sample function",
            function=sample_function
        )
        
        func2 = Function(
            name="sample_function_with_params",
            description="A sample function with parameters",
            function=sample_function_with_params
        )
        
        action_group = ActionGroup(
            name="TestActions",
            description="Test actions",
            functions=[func1, func2]
        )
        
        action_group_dict = action_group.model_dump()
        
        assert action_group_dict["name"] == "TestActions"
        assert action_group_dict["description"] == "Test actions"
        assert len(action_group_dict["functions"]) == 2
        
        # Check that the functions were properly serialized
        assert action_group_dict["functions"][0]["name"] == "sample_function"
        assert action_group_dict["functions"][1]["name"] == "sample_function_with_params" 