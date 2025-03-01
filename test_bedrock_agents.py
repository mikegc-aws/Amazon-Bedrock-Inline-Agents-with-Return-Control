import pytest
import json
import uuid
import boto3
from unittest.mock import patch, MagicMock, call
from typing import Dict, Any, List

from bedrockAgents import BedrockAgents, Agent, Message, Function


# Sample functions for testing
def sample_function() -> Dict[str, Any]:
    """A sample function that returns a dictionary"""
    return {"status": "success"}


def sample_function_with_params(param1: str, param2: int = 123) -> Dict[str, Any]:
    """A sample function that takes parameters and returns a dictionary
    
    :param param1: A string parameter
    :param param2: An integer parameter
    """
    return {"param1": param1, "param2": param2}


# Fixtures
@pytest.fixture
def bedrock_agents():
    """Return a BedrockAgents instance with SDK logs enabled"""
    return BedrockAgents(sdk_logs=True)


@pytest.fixture
def bedrock_agents_verbose():
    """Return a BedrockAgents instance with verbose mode enabled"""
    return BedrockAgents(verbosity="verbose")


@pytest.fixture
def bedrock_agents_debug():
    """Return a BedrockAgents instance with debug mode enabled"""
    return BedrockAgents(verbosity="debug")


@pytest.fixture
def bedrock_agents_quiet():
    """Return a BedrockAgents instance with quiet mode enabled"""
    return BedrockAgents(verbosity="quiet")


@pytest.fixture
def sample_agent():
    """Return a sample Agent instance with test functions"""
    return Agent(
        name="TestAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a test agent",
        functions=[sample_function, sample_function_with_params]
    )


@pytest.fixture
def sample_agent_with_action_groups():
    """Return a sample Agent instance with functions organized in action groups"""
    return Agent(
        name="TestAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a test agent",
        functions={
            "TestActions": [sample_function],
            "ParamActions": [sample_function_with_params]
        }
    )


# Tests for initialization
def test_bedrock_agents_init():
    """Test BedrockAgents initialization with different verbosity levels"""
    # Test with explicit sdk_logs
    client = BedrockAgents(sdk_logs=True)
    assert client.sdk_logs is True
    assert client.agent_traces is True  # Default
    assert client.trace_level == "standard"  # Default
    assert client.debug is True  # For backward compatibility
    assert client.max_tool_calls == 10
    
    # Test with quiet verbosity
    client = BedrockAgents(verbosity="quiet")
    assert client.sdk_logs is False
    assert client.agent_traces is False
    
    # Test with normal verbosity
    client = BedrockAgents(verbosity="normal")
    assert client.sdk_logs is False  # Default
    assert client.agent_traces is True  # Default
    
    # Test with verbose verbosity
    client = BedrockAgents(verbosity="verbose")
    assert client.sdk_logs is True
    assert client.agent_traces is True
    assert client.trace_level == "standard"
    
    # Test with debug verbosity
    client = BedrockAgents(verbosity="debug")
    assert client.sdk_logs is True
    assert client.agent_traces is True
    assert client.trace_level == "detailed"
    
    # Test with custom trace level
    client = BedrockAgents(trace_level="minimal")
    assert client.trace_level == "minimal"
    
    # Test backward compatibility
    client = BedrockAgents(debug=True)
    assert client.sdk_logs is True
    assert client.debug is True


def test_agent_init_with_functions_list():
    """Test Agent initialization with a list of functions"""
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
    assert isinstance(agent.functions[0], Function)
    assert agent.functions[0].name == "sample_function"
    assert agent.functions[0].function == sample_function
    assert agent.functions[0].action_group is None


def test_agent_init_with_action_groups():
    """Test Agent initialization with action groups"""
    agent = Agent(
        name="TestAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a test agent",
        functions={
            "TestActions": [sample_function],
            "ParamActions": [sample_function_with_params]
        }
    )
    
    assert agent.name == "TestAgent"
    assert len(agent.functions) == 2
    
    # Check that functions were properly processed with action groups
    test_action_functions = [f for f in agent.functions if f.action_group == "TestActions"]
    param_action_functions = [f for f in agent.functions if f.action_group == "ParamActions"]
    
    assert len(test_action_functions) == 1
    assert len(param_action_functions) == 1
    assert test_action_functions[0].name == "sample_function"
    assert param_action_functions[0].name == "sample_function_with_params"


# Tests for function processing
def test_create_function(sample_agent):
    """Test the _create_function method"""
    # Create a new function with a custom description
    func = sample_agent._create_function(
        function=sample_function,
        description="Custom description",
        action_group="CustomGroup"
    )
    
    assert isinstance(func, Function)
    assert func.name == "sample_function"
    assert func.description == "Custom description"
    assert func.function == sample_function
    assert func.action_group == "CustomGroup"
    
    # Test with default description (uses docstring)
    func = sample_agent._create_function(
        function=sample_function
    )
    
    assert func.description == "A sample function that returns a dictionary"


def test_add_function(sample_agent):
    """Test the add_function method"""
    # Define a new function
    def new_function() -> Dict[str, Any]:
        """A new test function"""
        return {"new": True}
    
    # Initial count
    initial_count = len(sample_agent.functions)
    
    # Add the function
    sample_agent.add_function(
        function=new_function,
        description="Custom description",
        action_group="NewGroup"
    )
    
    # Check that the function was added
    assert len(sample_agent.functions) == initial_count + 1
    
    # Check the added function
    added_func = next((f for f in sample_agent.functions if f.name == "new_function"), None)
    assert added_func is not None
    assert added_func.description == "Custom description"
    assert added_func.action_group == "NewGroup"


# Tests for parameter extraction and conversion
def test_extract_parameter_info(bedrock_agents):
    """Test the _extract_parameter_info method"""
    params = bedrock_agents._extract_parameter_info(sample_function_with_params)
    
    assert "param1" in params
    assert "param2" in params
    
    assert params["param1"]["type"] == "string"
    assert params["param1"]["required"] is True
    assert "A string parameter" in params["param1"]["description"]
    
    assert params["param2"]["type"] == "number"
    assert params["param2"]["required"] is False
    assert "An integer parameter" in params["param2"]["description"]


def test_convert_parameters(bedrock_agents):
    """Test the _convert_parameters method"""
    # Test string parameter
    params = [
        {"name": "param1", "value": "test", "type": "string"},
        {"name": "param2", "value": "42", "type": "number"},
        {"name": "param3", "value": "true", "type": "boolean"}
    ]
    
    converted = bedrock_agents._convert_parameters(params)
    
    assert converted["param1"] == "test"
    assert converted["param2"] == 42
    assert converted["param3"] is True


# Tests for action group building
def test_build_action_groups(bedrock_agents, sample_agent_with_action_groups):
    """Test the _build_action_groups method"""
    action_groups = bedrock_agents._build_action_groups(sample_agent_with_action_groups)
    
    # Should have two action groups
    assert len(action_groups) == 2
    
    # Find the action groups by name
    test_actions = next((g for g in action_groups if g["actionGroupName"] == "TestActions"), None)
    param_actions = next((g for g in action_groups if g["actionGroupName"] == "ParamActions"), None)
    
    assert test_actions is not None
    assert param_actions is not None
    
    # Check the functions in each action group
    assert len(test_actions["functionSchema"]["functions"]) == 1
    assert test_actions["functionSchema"]["functions"][0]["name"] == "sample_function"
    
    assert len(param_actions["functionSchema"]["functions"]) == 1
    assert param_actions["functionSchema"]["functions"][0]["name"] == "sample_function_with_params"
    
    # Check that parameters were included
    param_function = param_actions["functionSchema"]["functions"][0]
    assert "parameters" in param_function
    assert "param1" in param_function["parameters"]
    assert "param2" in param_function["parameters"]


# Tests for function execution
def test_execute_function(bedrock_agents):
    """Test the _execute_function method"""
    # Create a function map
    function_map = {
        "sample_function": sample_function,
        "sample_function_with_params": sample_function_with_params
    }
    
    # Test executing a function without parameters
    result = bedrock_agents._execute_function(
        function_map=function_map,
        function_name="sample_function",
        params={}
    )
    
    assert result == {"status": "success"}
    
    # Test executing a function with parameters
    result = bedrock_agents._execute_function(
        function_map=function_map,
        function_name="sample_function_with_params",
        params={"param1": "test", "param2": 42}
    )
    
    assert result == {"param1": "test", "param2": 42}
    
    # Test executing a non-existent function
    result = bedrock_agents._execute_function(
        function_map=function_map,
        function_name="non_existent_function",
        params={}
    )
    
    assert result is None


# Tests for agent invocation with mocks
@patch('boto3.client')
def test_invoke_agent_initial_call(mock_boto3_client, bedrock_agents, sample_agent):
    """Test the _invoke_agent method with an initial call"""
    # Set up mocks
    mock_bedrock_runtime = MagicMock()
    mock_bedrock_agent_runtime = MagicMock()
    mock_boto3_client.side_effect = [mock_bedrock_runtime, mock_bedrock_agent_runtime]
    
    # Set up the response
    mock_response = {
        "completion": [
            {"chunk": {"bytes": b"Hello, I'm an AI assistant."}}
        ]
    }
    mock_bedrock_agent_runtime.invoke_inline_agent.return_value = mock_response
    
    # Create a new BedrockAgents instance with the mocked clients
    bedrock_agents = BedrockAgents(sdk_logs=True)
    bedrock_agents.bedrock_runtime = mock_bedrock_runtime
    bedrock_agents.bedrock_agent_runtime = mock_bedrock_agent_runtime
    
    # Build action groups
    action_groups = bedrock_agents._build_action_groups(sample_agent)
    
    # Create a function map
    function_map = {func.name: func.function for func in sample_agent.functions}
    
    # Invoke the agent
    session_id = str(uuid.uuid4())
    result = bedrock_agents._invoke_agent(
        agent=sample_agent,
        action_groups=action_groups,
        function_map=function_map,
        session_id=session_id,
        input_text="Hello",
        tool_call_count=0
    )
    
    # Check that invoke_inline_agent was called correctly
    mock_bedrock_agent_runtime.invoke_inline_agent.assert_called_once_with(
        sessionId=session_id,
        actionGroups=action_groups,
        instruction=sample_agent.instructions,
        foundationModel=sample_agent.model,
        inputText="Hello",
        enableTrace=bedrock_agents.agent_traces
    )
    
    # Check the result
    assert result == "Hello, I'm an AI assistant."


@patch('boto3.client')
def test_invoke_agent_with_function_call(mock_boto3_client, bedrock_agents, sample_agent):
    """Test the _invoke_agent method with a function call"""
    # Set up mocks
    mock_bedrock_runtime = MagicMock()
    mock_bedrock_agent_runtime = MagicMock()
    mock_boto3_client.side_effect = [mock_bedrock_runtime, mock_bedrock_agent_runtime]
    
    # Set up the responses
    # First response with a function call
    first_response = {
        "completion": [
            {"chunk": {"bytes": b"I'll help you with that."}},
            {"returnControl": {
                "invocationId": "test-invocation-id",
                "invocationInputs": [{
                    "functionInvocationInput": {
                        "function": "sample_function",
                        "actionGroup": "DefaultActions",
                        "parameters": []
                    }
                }]
            }}
        ]
    }
    
    # Second response after function call
    second_response = {
        "completion": [
            {"chunk": {"bytes": b"The function returned success."}}
        ]
    }
    
    mock_bedrock_agent_runtime.invoke_inline_agent.side_effect = [first_response, second_response]
    
    # Create a new BedrockAgents instance with the mocked clients
    bedrock_agents = BedrockAgents(sdk_logs=True)
    bedrock_agents.bedrock_runtime = mock_bedrock_runtime
    bedrock_agents.bedrock_agent_runtime = mock_bedrock_agent_runtime
    
    # Build action groups
    action_groups = bedrock_agents._build_action_groups(sample_agent)
    
    # Create a function map
    function_map = {func.name: func.function for func in sample_agent.functions}
    
    # Invoke the agent
    session_id = str(uuid.uuid4())
    result = bedrock_agents._invoke_agent(
        agent=sample_agent,
        action_groups=action_groups,
        function_map=function_map,
        session_id=session_id,
        input_text="Call the sample function",
        tool_call_count=0
    )
    
    # Check that invoke_inline_agent was called correctly
    assert mock_bedrock_agent_runtime.invoke_inline_agent.call_count == 2
    
    # Check the first call
    first_call_args = mock_bedrock_agent_runtime.invoke_inline_agent.call_args_list[0][1]
    assert first_call_args["sessionId"] == session_id
    assert first_call_args["inputText"] == "Call the sample function"
    
    # Check the second call
    second_call_args = mock_bedrock_agent_runtime.invoke_inline_agent.call_args_list[1][1]
    assert second_call_args["sessionId"] == session_id
    assert "inlineSessionState" in second_call_args
    assert second_call_args["inlineSessionState"]["invocationId"] == "test-invocation-id"
    
    # Check the result
    assert result == "I'll help you with that.\nThe function returned success."


# Tests for the run method
@patch.object(BedrockAgents, '_invoke_agent')
def test_run(mock_invoke_agent, bedrock_agents, sample_agent):
    """Test the run method"""
    # Set up the mock
    mock_invoke_agent.return_value = "Test response"
    
    # Create messages
    messages = [
        Message(role="user", content="Hello")
    ]
    
    # Run the agent
    result = bedrock_agents.run(
        agent=sample_agent,
        messages=messages
    )
    
    # Check that _invoke_agent was called correctly
    mock_invoke_agent.assert_called_once()
    call_args = mock_invoke_agent.call_args[1]
    assert call_args["agent"] == sample_agent
    assert call_args["input_text"] == "Hello"
    assert call_args["tool_call_count"] == 0
    
    # Check the result
    assert result == "Test response"


# Test with dictionary messages
@patch.object(BedrockAgents, '_invoke_agent')
def test_run_with_dict_messages(mock_invoke_agent, bedrock_agents, sample_agent):
    """Test the run method with dictionary messages"""
    # Set up the mock
    mock_invoke_agent.return_value = "Test response"
    
    # Create messages as dictionaries
    messages = [
        {"role": "user", "content": "Hello"}
    ]
    
    # Run the agent
    result = bedrock_agents.run(
        agent=sample_agent,
        messages=messages
    )
    
    # Check that _invoke_agent was called correctly
    mock_invoke_agent.assert_called_once()
    call_args = mock_invoke_agent.call_args[1]
    assert call_args["agent"] == sample_agent
    assert call_args["input_text"] == "Hello"
    
    # Check the result
    assert result == "Test response"


# Test error handling
def test_run_with_invalid_messages(bedrock_agents, sample_agent):
    """Test the run method with invalid messages"""
    # Create messages with the last message not from user
    messages = [
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there")
    ]
    
    # Run the agent and expect an error
    with pytest.raises(ValueError, match="The last message must be from the user"):
        bedrock_agents.run(
            agent=sample_agent,
            messages=messages
        )


# Tests for the chat method
@patch.object(BedrockAgents, '_invoke_agent')
@patch('builtins.input')
@patch('builtins.print')
def test_chat_normal_exit(mock_print, mock_input, mock_invoke_agent, bedrock_agents, sample_agent):
    """Test the chat method with normal exit"""
    # Set up mocks
    mock_input.side_effect = ["Hello", "exit"]
    mock_invoke_agent.return_value = "Test response"
    
    # Start chat
    bedrock_agents.chat(sample_agent)
    
    # Check that _invoke_agent was called correctly
    mock_invoke_agent.assert_called_once()
    call_args = mock_invoke_agent.call_args[1]
    assert call_args["agent"] == sample_agent
    assert call_args["input_text"] == "Hello"
    
    # Check that print was called with the response
    assert any("Test response" in str(args) for args, _ in mock_print.call_args_list)


@patch.object(BedrockAgents, '_invoke_agent')
@patch('builtins.input')
@patch('builtins.print')
def test_chat_keyboard_interrupt(mock_print, mock_input, mock_invoke_agent, bedrock_agents, sample_agent):
    """Test the chat method with keyboard interrupt"""
    # Set up mocks
    mock_input.side_effect = KeyboardInterrupt()
    
    # Start chat
    bedrock_agents.chat(sample_agent)
    
    # Check that _invoke_agent was not called
    mock_invoke_agent.assert_not_called()
    
    # Check that print was called with goodbye message
    assert any("interrupted" in str(args) for args, _ in mock_print.call_args_list)


@patch.object(BedrockAgents, '_invoke_agent')
@patch('builtins.input')
@patch('builtins.print')
def test_chat_client_error(mock_print, mock_input, mock_invoke_agent, bedrock_agents, sample_agent):
    """Test the chat method with client error"""
    # Set up mocks
    mock_input.return_value = "Hello"
    mock_invoke_agent.side_effect = boto3.exceptions.botocore.exceptions.ClientError(
        {"Error": {"Code": "TestError", "Message": "Test error message"}},
        "operation"
    )
    
    # Start chat
    bedrock_agents.chat(sample_agent)
    
    # Check that _invoke_agent was called
    mock_invoke_agent.assert_called_once()
    
    # Check that print was called with error message
    assert any("Error:" in str(args) for args, _ in mock_print.call_args_list)


# Tests for edge cases
@patch('boto3.client')
def test_invoke_agent_max_tool_calls(mock_boto3_client, bedrock_agents, sample_agent):
    """Test the _invoke_agent method with maximum tool calls"""
    # Set up mocks
    mock_bedrock_runtime = MagicMock()
    mock_bedrock_agent_runtime = MagicMock()
    mock_boto3_client.side_effect = [mock_bedrock_runtime, mock_bedrock_agent_runtime]
    
    # Set up the response to always return a function call
    mock_response = {
        "completion": [
            {"chunk": {"bytes": b"I'll help you with that."}},
            {"returnControl": {
                "invocationId": "test-invocation-id",
                "invocationInputs": [{
                    "functionInvocationInput": {
                        "function": "sample_function",
                        "actionGroup": "DefaultActions",
                        "parameters": []
                    }
                }]
            }}
        ]
    }
    mock_bedrock_agent_runtime.invoke_inline_agent.return_value = mock_response
    
    # Create a new BedrockAgents instance with the mocked clients and a low max_tool_calls
    bedrock_agents = BedrockAgents(sdk_logs=True)
    bedrock_agents.bedrock_runtime = mock_bedrock_runtime
    bedrock_agents.bedrock_agent_runtime = mock_bedrock_agent_runtime
    bedrock_agents.max_tool_calls = 2  # Set a low limit for testing
    
    # Build action groups
    action_groups = bedrock_agents._build_action_groups(sample_agent)
    
    # Create a function map
    function_map = {func.name: func.function for func in sample_agent.functions}
    
    # Invoke the agent
    session_id = str(uuid.uuid4())
    result = bedrock_agents._invoke_agent(
        agent=sample_agent,
        action_groups=action_groups,
        function_map=function_map,
        session_id=session_id,
        input_text="Hello",
        tool_call_count=0
    )
    
    # Check that invoke_inline_agent was called the maximum number of times
    assert mock_bedrock_agent_runtime.invoke_inline_agent.call_count == 2
    
    # Check that the result contains the maximum tool calls message
    assert "maximum number of tool calls" in result


def test_convert_parameters_with_invalid_values(bedrock_agents):
    """Test the _convert_parameters method with invalid values"""
    # Test with invalid number
    params = [
        {"name": "param1", "value": "not_a_number", "type": "number"},
        {"name": "param2", "value": "true", "type": "boolean"}
    ]
    
    converted = bedrock_agents._convert_parameters(params)
    
    # The invalid number should be skipped
    assert "param1" not in converted
    assert converted["param2"] is True
    
    # Test with invalid boolean
    params = [
        {"name": "param1", "value": "invalid_boolean", "type": "boolean"}
    ]
    
    converted = bedrock_agents._convert_parameters(params)
    
    # The invalid boolean should be converted to a string
    assert converted["param1"] == "invalid_boolean"


def test_execute_function_with_errors(bedrock_agents):
    """Test the _execute_function method with errors"""
    # Create a function map with a function that raises an error
    def error_function():
        raise ValueError("Test error")
    
    function_map = {
        "error_function": error_function,
        "type_error_function": lambda x: x  # Will raise TypeError if called without args
    }
    
    # Test with a function that raises a ValueError
    result = bedrock_agents._execute_function(
        function_map=function_map,
        function_name="error_function",
        params={}
    )
    
    assert result is None
    
    # Test with a function that raises a TypeError
    result = bedrock_agents._execute_function(
        function_map=function_map,
        function_name="type_error_function",
        params={}
    )
    
    assert result is None


# Test with code interpreter
def test_agent_with_code_interpreter():
    """Test Agent initialization with code interpreter enabled"""
    agent = Agent(
        name="TestAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a test agent",
        functions=[sample_function],
        enable_code_interpreter=True
    )
    
    assert agent.enable_code_interpreter is True
    
    # Test building action groups with code interpreter
    client = BedrockAgents(sdk_logs=True)
    action_groups = client._build_action_groups(agent)
    
    # Should have two action groups (one for functions, one for code interpreter)
    assert len(action_groups) == 2
    
    # Find the code interpreter action group
    code_interpreter = next((g for g in action_groups if g["actionGroupName"] == "CodeInterpreterAction"), None)
    
    assert code_interpreter is not None
    assert code_interpreter["parentActionGroupSignature"] == "AMAZON.CodeInterpreter"


# Tests for Message class
def test_message_initialization():
    """Test Message initialization"""
    # Test with valid roles
    user_message = Message(role="user", content="Hello")
    assert user_message.role == "user"
    assert user_message.content == "Hello"
    
    assistant_message = Message(role="assistant", content="Hi there")
    assert assistant_message.role == "assistant"
    assert assistant_message.content == "Hi there"
    
    # Test with dictionary
    message_dict = {"role": "user", "content": "Hello from dict"}
    message = Message(**message_dict)
    assert message.role == "user"
    assert message.content == "Hello from dict"


# Test for empty functions
def test_agent_with_empty_functions():
    """Test Agent initialization with empty functions list"""
    agent = Agent(
        name="EmptyAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a test agent",
        functions=[]
    )
    
    assert len(agent.functions) == 0
    
    # Test building action groups with empty functions
    client = BedrockAgents(sdk_logs=True)
    action_groups = client._build_action_groups(agent)
    
    # Should have no action groups
    assert len(action_groups) == 0


# Test for function with complex return types
def test_function_with_complex_return():
    """Test handling of functions with complex return types"""
    def complex_function() -> Dict[str, Any]:
        """A function that returns a complex nested structure"""
        return {
            "string": "value",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "nested": {
                "key": "value"
            }
        }
    
    # Create agent with the complex function
    agent = Agent(
        name="ComplexAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a test agent",
        functions=[complex_function]
    )
    
    # Create client and function map
    client = BedrockAgents(sdk_logs=True)
    function_map = {func.name: func.function for func in agent.functions}
    
    # Execute the function
    result = client._execute_function(
        function_map=function_map,
        function_name="complex_function",
        params={}
    )
    
    # Check the result
    assert result["string"] == "value"
    assert result["number"] == 42
    assert result["boolean"] is True
    assert result["list"] == [1, 2, 3]
    assert result["nested"]["key"] == "value"
    
    # Test that it can be JSON serialized (for return_control_result)
    json_result = json.dumps(result)
    assert json_result is not None


# Test for handling non-dictionary return values
def test_non_dict_return_values(bedrock_agents):
    """Test handling of functions that don't return dictionaries"""
    # Define functions with various return types
    def return_string() -> str:
        """Return a string"""
        return "string value"
    
    def return_number() -> int:
        """Return a number"""
        return 42
    
    def return_list() -> List[int]:
        """Return a list"""
        return [1, 2, 3]
    
    def return_none() -> None:
        """Return None"""
        return None
    
    # Create function map
    function_map = {
        "return_string": return_string,
        "return_number": return_number,
        "return_list": return_list,
        "return_none": return_none
    }
    
    # Test each function
    string_result = bedrock_agents._execute_function(function_map, "return_string", {})
    number_result = bedrock_agents._execute_function(function_map, "return_number", {})
    list_result = bedrock_agents._execute_function(function_map, "return_list", {})
    none_result = bedrock_agents._execute_function(function_map, "return_none", {})
    
    # Check results
    assert string_result == "string value"
    assert number_result == 42
    assert list_result == [1, 2, 3]
    assert none_result is None


@patch.object(BedrockAgents, '_invoke_agent')
def test_run_with_custom_session_id(mock_invoke_agent, bedrock_agents, sample_agent):
    """Test the run method with a custom session ID"""
    # Set up the mock
    mock_invoke_agent.return_value = "Test response"
    
    # Create messages
    messages = [
        Message(role="user", content="Hello")
    ]
    
    # Custom session ID
    custom_session_id = "test-session-123"
    
    # Run the agent with custom session ID
    result = bedrock_agents.run(
        agent=sample_agent,
        messages=messages,
        session_id=custom_session_id
    )
    
    # Check that _invoke_agent was called correctly with the custom session ID
    mock_invoke_agent.assert_called_once()
    call_args = mock_invoke_agent.call_args[1]
    assert call_args["agent"] == sample_agent
    assert call_args["input_text"] == "Hello"
    assert call_args["session_id"] == custom_session_id
    assert call_args["tool_call_count"] == 0
    
    # Check the result
    assert result == "Test response"


@patch.object(BedrockAgents, '_invoke_agent')
@patch('builtins.input')
@patch('builtins.print')
def test_chat_with_custom_session_id(mock_print, mock_input, mock_invoke_agent, bedrock_agents, sample_agent):
    """Test the chat method with a custom session ID"""
    # Set up mocks
    mock_input.side_effect = ["Hello", "exit"]
    mock_invoke_agent.return_value = "Test response"
    
    # Custom session ID
    custom_session_id = "test-session-456"
    
    # Run the chat with custom session ID
    bedrock_agents.chat(agent=sample_agent, session_id=custom_session_id)
    
    # Check that _invoke_agent was called correctly with the custom session ID
    mock_invoke_agent.assert_called_once()
    call_args = mock_invoke_agent.call_args[1]
    assert call_args["agent"] == sample_agent
    assert call_args["input_text"] == "Hello"
    assert call_args["session_id"] == custom_session_id
    assert call_args["tool_call_count"] == 0


def test_process_trace_data(capsys):
    """Test the _process_trace_data method with different trace levels"""
    # Sample trace data
    trace_data = {
        "trace": {
            "orchestrationTrace": {
                "modelInvocationOutput": {
                    "reasoningContent": {
                        "reasoningText": {
                            "text": "This is the reasoning text"
                        }
                    }
                },
                "rationale": {
                    "text": "This is the rationale text"
                },
                "invocationInput": {
                    "invocationType": "TestInvocation",
                    "actionGroupInvocationInput": {
                        "actionGroupName": "TestActionGroup",
                        "function": "test_function",
                        "parameters": [
                            {"name": "param1", "value": "value1", "type": "string"}
                        ]
                    }
                }
            },
            "preProcessingTrace": {
                "modelInvocationOutput": {
                    "parsedResponse": {
                        "rationale": "Pre-processing rationale"
                    }
                }
            },
            "postProcessingTrace": {
                "modelInvocationOutput": {
                    "reasoningContent": {
                        "reasoningText": {
                            "text": "Post-processing reasoning"
                        }
                    }
                }
            }
        }
    }
    
    # Test with agent_traces disabled
    client = BedrockAgents(agent_traces=False)
    client._process_trace_data(trace_data)
    captured = capsys.readouterr()
    assert captured.out == ""  # No output when agent_traces is disabled
    
    # Test with minimal trace level
    client = BedrockAgents(agent_traces=True, trace_level="minimal")
    client._process_trace_data(trace_data)
    captured = capsys.readouterr()
    assert "Reasoning Process" in captured.out
    assert "Decision Rationale" in captured.out
    assert "Invocation Type" not in captured.out  # Not shown in minimal level
    assert "Pre-processing Rationale" not in captured.out  # Not shown in minimal level
    
    # Test with standard trace level
    client = BedrockAgents(agent_traces=True, trace_level="standard")
    client._process_trace_data(trace_data)
    captured = capsys.readouterr()
    assert "Reasoning Process" in captured.out
    assert "Decision Rationale" in captured.out
    assert "Invocation Type" in captured.out  # Shown in standard level
    assert "Pre-processing Rationale" not in captured.out  # Not shown in standard level
    
    # Test with detailed trace level
    client = BedrockAgents(agent_traces=True, trace_level="detailed")
    client._process_trace_data(trace_data)
    captured = capsys.readouterr()
    assert "Reasoning Process" in captured.out
    assert "Decision Rationale" in captured.out
    assert "Invocation Type" in captured.out  # Shown in detailed level
    assert "Pre-processing Rationale" in captured.out  # Shown in detailed level
    assert "Post-processing Reasoning" in captured.out  # Shown in detailed level


def test_verbosity_settings():
    """Test how the verbosity parameter affects sdk_logs and agent_traces"""
    # Test quiet verbosity
    client = BedrockAgents(verbosity="quiet")
    assert client.sdk_logs is False
    assert client.agent_traces is False
    assert client.debug is False  # For backward compatibility
    
    # Test normal verbosity with defaults
    client = BedrockAgents(verbosity="normal")
    assert client.sdk_logs is False
    assert client.agent_traces is True
    assert client.trace_level == "standard"
    
    # Test normal verbosity with overrides
    client = BedrockAgents(verbosity="normal", sdk_logs=True, agent_traces=False)
    assert client.sdk_logs is True
    assert client.agent_traces is False
    
    # Test verbose verbosity
    client = BedrockAgents(verbosity="verbose")
    assert client.sdk_logs is True
    assert client.agent_traces is True
    assert client.trace_level == "standard"
    
    # Test verbose verbosity with minimal trace level (should upgrade to standard)
    client = BedrockAgents(verbosity="verbose", trace_level="minimal")
    assert client.trace_level == "standard"
    
    # Test debug verbosity
    client = BedrockAgents(verbosity="debug")
    assert client.sdk_logs is True
    assert client.agent_traces is True
    assert client.trace_level == "detailed"
    
    # Test debug verbosity with trace level override (should still be detailed)
    client = BedrockAgents(verbosity="debug", trace_level="minimal")
    assert client.trace_level == "detailed"
    
    # Test unrecognized verbosity (should use provided values)
    client = BedrockAgents(verbosity="invalid", sdk_logs=True, agent_traces=False)
    assert client.sdk_logs is True
    assert client.agent_traces is False 