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

# Sample agent plugin for testing
class TestAgentPlugin(BedrockAgentsPlugin):
    def pre_invoke(self, params):
        params["agent_plugin"] = True
        return params
        
    def post_invoke(self, response):
        if "agent_post_invoke" not in response:
            response["agent_post_invoke"] = True
        return response
        
    def post_process(self, result):
        if "agent_post_process" not in result:
            result["agent_post_process"] = True
        return result

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
        
        # Execute a function without parameters
        result = client._execute_function(function_map, "sample_function", {})
        assert result == {"status": "success"}
        
        # Execute a function with parameters
        result = client._execute_function(function_map, "sample_function_with_params", {"param1": "test", "param2": 456})
        assert result == {"param1": "test", "param2": 456}
        
        # Execute a function with missing parameters
        result = client._execute_function(function_map, "sample_function_with_params", {"param1": "test"})
        assert result == {"param1": "test", "param2": 123}
        
        # Execute a non-existent function
        result = client._execute_function(function_map, "non_existent_function", {})
        assert result is None
    
    def test_invoke_agent_basic(self, client, agent, mock_boto3_session):
        """Test that an agent can be invoked with a basic message"""
        _, mock_client = mock_boto3_session
        
        # Set up the mock response
        mock_client.invoke_inline_agent.return_value = {
            "completion": [
                {
                    "chunk": {
                        "bytes": b"This is a test response"
                    }
                }
            ]
        }
        
        # Invoke the agent
        result = client._invoke_agent(
            agent=agent,
            action_groups=[],
            function_map={},
            session_id="test-session",
            input_text="Hello, agent!",
            tool_call_count=0
        )
        
        # Check that the agent was invoked with the correct parameters
        mock_client.invoke_inline_agent.assert_called_once()
        invoke_args = mock_client.invoke_inline_agent.call_args[1]
        assert invoke_args["sessionId"] == "test-session"
        assert invoke_args["inputText"] == "Hello, agent!"
        assert invoke_args["instruction"] == agent.instructions
        assert invoke_args["foundationModel"] == agent.model
        
        # Check the result
        assert result["response"] == "This is a test response"
        assert result["files"] == []
    
    def test_invoke_agent_with_function_call(self, client, agent, mock_boto3_session):
        """Test that an agent can invoke a function"""
        _, mock_client = mock_boto3_session
        
        # Set up the mock responses
        mock_client.invoke_inline_agent.side_effect = [
            # First response: agent wants to call a function
            {
                "completion": [
                    {
                        "chunk": {
                            "bytes": b"Let me check that for you."
                        }
                    },
                    {
                        "returnControl": {
                            "invocationId": "test-invocation",
                            "invocationInputs": [
                                {
                                    "functionInvocationInput": {
                                        "function": "sample_function",
                                        "actionGroup": "DefaultActions",
                                        "parameters": []
                                    }
                                }
                            ]
                        }
                    }
                ]
            },
            # Second response: agent completes the response
            {
                "completion": [
                    {
                        "chunk": {
                            "bytes": b"The function returned success."
                        }
                    }
                ]
            }
        ]
        
        # Create a function map
        function_map = {"sample_function": sample_function}
        
        # Invoke the agent
        result = client._invoke_agent(
            agent=agent,
            action_groups=[],
            function_map=function_map,
            session_id="test-session",
            input_text="Call the sample function",
            tool_call_count=0
        )
        
        # Check that the agent was invoked twice
        assert mock_client.invoke_inline_agent.call_count == 2
        
        # Check the result
        assert result["response"] == "Let me check that for you.\nThe function returned success."
        assert result["files"] == []
    
    def test_agent_plugins_integration(self, client, mock_boto3_session):
        """Test that agent plugins are applied during invocation"""
        _, mock_client = mock_boto3_session
        
        # Set up the mock response
        mock_client.invoke_inline_agent.return_value = {
            "completion": [
                {
                    "chunk": {
                        "bytes": b"This is a test response"
                    }
                }
            ]
        }
        
        # Create an agent with a plugin
        agent_plugin = TestAgentPlugin()
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            functions=[sample_function],
            plugins=[agent_plugin]
        )
        
        # Run the agent
        result = client.run(agent=agent, message="Test message")
        
        # Check that the plugin was applied
        # First, check that pre_invoke was called
        invoke_args = mock_client.invoke_inline_agent.call_args[1]
        assert "agent_plugin" in invoke_args
        assert invoke_args["agent_plugin"] is True
        
        # Check that post_process was called
        assert "agent_post_process" in result
        assert result["agent_post_process"] is True 