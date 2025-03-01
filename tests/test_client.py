import pytest
import json
import uuid
from unittest.mock import patch, MagicMock, call
from bedrock_agents_sdk import BedrockAgents, Agent, Message, Function
from bedrock_agents_sdk.plugins.base import BedrockAgentsPlugin

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

# Sample plugin for testing
class TestPlugin(BedrockAgentsPlugin):
    def pre_invoke(self, params):
        params["test_plugin"] = True
        return params

# Fixtures
@pytest.fixture
def mock_boto3_session():
    with patch("boto3.Session") as mock_session:
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        yield mock_session, mock_client

@pytest.fixture
def client(mock_boto3_session):
    _, _ = mock_boto3_session
    return BedrockAgents(verbosity="quiet")

@pytest.fixture
def agent():
    return Agent(
        name="TestAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a test agent",
        functions=[sample_function, sample_function_with_params]
    )

class TestBedrockAgents:
    def test_client_initialization(self, mock_boto3_session):
        """Test that a client can be initialized"""
        mock_session, mock_client = mock_boto3_session
        
        client = BedrockAgents(
            region_name="us-west-2",
            profile_name="test-profile",
            verbosity="normal",
            trace_level="standard",
            max_tool_calls=5
        )
        
        # Check that the session was created with the correct parameters
        mock_session.assert_called_once_with(region_name="us-west-2", profile_name="test-profile")
        
        # Check that the client was created
        mock_session.return_value.client.assert_called_once_with("bedrock-agent-runtime")
        
        # Check that the client properties were set correctly
        assert client.verbosity == "normal"
        assert client.sdk_logs == True
        assert client.debug_logs == False
        assert client.trace_level == "standard"
        assert client.agent_traces == True
        assert client.max_tool_calls == 5
        assert client.plugins == []
    
    def test_register_plugin(self, client):
        """Test that a plugin can be registered with the client"""
        plugin = TestPlugin()
        
        client.register_plugin(plugin)
        
        assert len(client.plugins) == 1
        assert client.plugins[0] == plugin
        assert plugin.client == client
    
    def test_build_action_groups(self, client, agent):
        """Test that action groups can be built from agent functions"""
        action_groups = client._build_action_groups(agent)
        
        assert len(action_groups) == 1
        assert action_groups[0]["actionGroupName"] == "DefaultActions"
        assert action_groups[0]["description"] == "Actions related to Default"
        assert action_groups[0]["actionGroupExecutor"]["customControl"] == "RETURN_CONTROL"
        
        # Check that the functions were added to the action group
        functions = action_groups[0]["functionSchema"]["functions"]
        assert len(functions) == 2
        
        # Check the first function
        assert functions[0]["name"] == "sample_function"
        assert functions[0]["description"] == "A sample function that returns a dictionary"
        assert functions[0]["requireConfirmation"] == "DISABLED"
        
        # Check the second function
        assert functions[1]["name"] == "sample_function_with_params"
        assert functions[1]["description"] == "A sample function that takes parameters and returns a dictionary"
        assert functions[1]["requireConfirmation"] == "DISABLED"
        
        # Check that the parameters were added to the second function
        assert "parameters" in functions[1]
        assert "param1" in functions[1]["parameters"]
        assert "param2" in functions[1]["parameters"]
        
        # Check the parameter types
        assert functions[1]["parameters"]["param1"]["type"] == "string"
        assert functions[1]["parameters"]["param1"]["required"] == True
        assert functions[1]["parameters"]["param2"]["type"] == "number"
        assert functions[1]["parameters"]["param2"]["required"] == False
    
    def test_execute_function(self, client):
        """Test that a function can be executed"""
        function_map = {
            "sample_function": sample_function,
            "sample_function_with_params": sample_function_with_params
        }
        
        # Test executing a function with no parameters
        result = client._execute_function(function_map, "sample_function", {})
        assert result == {"status": "success"}
        
        # Test executing a function with parameters
        result = client._execute_function(function_map, "sample_function_with_params", {"param1": "test", "param2": 456})
        assert result == {"param1": "test", "param2": 456}
        
        # Test executing a function that doesn't exist
        result = client._execute_function(function_map, "non_existent_function", {})
        assert result is None

    def test_run_with_string_input(self, client, agent, mock_boto3_session):
        """Test that the run method can handle a simple string as input"""
        # Unpack the mock session and client
        mock_session, mock_client = mock_boto3_session
        
        # Mock the invoke_inline_agent response
        mock_response = {
            'completion': [{'chunk': {'bytes': b'This is a test response'}}],
            'stopReason': 'COMPLETE'
        }
        mock_client.invoke_inline_agent.return_value = mock_response
        
        # Run with a simple string input
        result = client.run(agent=agent, message="Hello, world!")
        
        # Verify that the agent was invoked with the correct parameters
        mock_client.invoke_inline_agent.assert_called()
        call_args = mock_client.invoke_inline_agent.call_args[1]
        
        # Check that the input text is correct
        assert call_args['inputText'] == "Hello, world!"
        
        # Check that the response is correct
        assert result['response'] == 'This is a test response'

    def test_run_with_both_message_types(self, client, agent):
        """Test that providing both message and messages raises an error"""
        with pytest.raises(ValueError) as excinfo:
            client.run(
                agent=agent, 
                message="Hello, world!", 
                messages=[{"role": "user", "content": "Another message"}]
            )
        
        assert "Only one of 'message' or 'messages' should be provided, not both" in str(excinfo.value)

    def test_run_with_no_message(self, client, agent):
        """Test that providing neither message nor messages raises an error"""
        with pytest.raises(ValueError) as excinfo:
            client.run(agent=agent)
        
        assert "Either 'message' or 'messages' must be provided" in str(excinfo.value) 