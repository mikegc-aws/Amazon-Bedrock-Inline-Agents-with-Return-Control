import pytest
from bedrock_agents_sdk import Agent, Function

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

class TestAgent:
    def test_agent_initialization(self):
        """Test that an agent can be initialized with functions"""
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            functions=[sample_function, sample_function_with_params]
        )
        
        assert agent.name == "TestAgent"
        assert agent.model == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert agent.instructions == "You are a test agent"
        assert len(agent.functions) == 2
        
        # Check that functions were properly processed
        func_names = [func.name for func in agent.functions]
        assert "sample_function" in func_names
        assert "sample_function_with_params" in func_names
    
    def test_agent_with_action_groups(self):
        """Test that an agent can be initialized with action groups"""
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            functions={
                "TestActions": [sample_function],
                "ParamActions": [sample_function_with_params]
            }
        )
        
        assert len(agent.functions) == 2
        
        # Check that action groups were properly assigned
        for func in agent.functions:
            if func.name == "sample_function":
                assert func.action_group == "TestActions"
            elif func.name == "sample_function_with_params":
                assert func.action_group == "ParamActions"
    
    def test_add_function(self):
        """Test that functions can be added to an agent"""
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent"
        )
        
        # Initially no functions
        assert len(agent.functions) == 0
        
        # Add a function
        agent.add_function(sample_function)
        assert len(agent.functions) == 1
        assert agent.functions[0].name == "sample_function"
        
        # Add another function with an action group
        agent.add_function(sample_function_with_params, action_group="ParamActions")
        assert len(agent.functions) == 2
        assert agent.functions[1].name == "sample_function_with_params"
        assert agent.functions[1].action_group == "ParamActions" 