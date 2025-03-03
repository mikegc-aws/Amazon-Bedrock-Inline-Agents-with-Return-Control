Advanced Usage
==============

This section covers advanced usage patterns for the Amazon Bedrock Agents with Return Control SDK.

Verbosity and Trace Levels
-------------------------

The SDK provides two separate but complementary control systems for output:

1. **Verbosity** - Controls SDK-level logs (client operations, function calls, etc.)
2. **Trace Level** - Controls agent-level traces (reasoning, decisions, code execution, etc.)

This separation allows you to independently control what you see from the SDK itself versus what you see from the agent's internal processes.

.. code-block:: python

    # Simple unified verbosity control
    client = Client(verbosity="normal")  # Default level

    # Available verbosity levels:
    client = Client(verbosity="quiet")    # No output except errors
    client = Client(verbosity="normal")   # Basic operational information
    client = Client(verbosity="verbose")  # Detailed operational information
    client = Client(verbosity="debug")    # All available information

    # Trace level control (independent of verbosity)
    client = Client(
        verbosity="normal",     # Controls SDK logs
        trace_level="standard"  # Controls agent trace information
    )

    # Advanced control (overrides specific aspects of verbosity)
    client = Client(
        verbosity="normal",     # Base verbosity level
        sdk_logs=True,          # Override to show SDK-level logs
        agent_traces=True,      # Override to show agent reasoning and decisions
        trace_level="detailed"  # Override level of trace detail
    )

    # Example with raw trace level for seeing code interpreter output
    client = Client(
        verbosity="normal",
        trace_level="raw"       # Show complete unprocessed trace data, including code interpreter output
    )

Why Two Separate Settings?
~~~~~~~~~~~~~~~~~~~~~~~~~

- **Verbosity** focuses on the SDK's operations (what your code is doing)
- **Trace Level** focuses on the agent's thinking process (what the AI is doing)

This separation allows you to, for example, have minimal SDK logs but detailed agent traces, or vice versa, depending on what you're trying to debug or understand.

For example:
- When developing your function tools, you might want high verbosity but minimal trace level
- When debugging agent reasoning, you might want low verbosity but detailed trace level
- When viewing code interpreter output, you might want low verbosity but raw trace level

The two settings give you fine-grained control over what information you see, making it easier to focus on what's important for your current task.

Custom Function Schemas
---------------------

While the SDK automatically generates JSON schemas for your functions based on type hints and docstrings, you can also provide custom schemas:

.. code-block:: python

    from bedrock_agents_sdk import Function

    custom_schema = {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. 'Seattle, WA'"
                }
            },
            "required": ["location"]
        }
    }

    function = Function(
        func=get_weather,
        schema=custom_schema
    )

Advanced Configuration
--------------------

The SDK provides advanced configuration options for both agents and the client:

.. code-block:: python

    from bedrock_agents_sdk import Client, Agent

    agent = Agent(
        name="AdvancedAgent",
        description="An agent with advanced configuration",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant.",
        advanced_config={
            "timeout_seconds": 300,
            "customerEncryptionKeyArn": "arn:aws:kms:us-west-2:123456789012:key/abcd1234-ab12-cd34-ef56-abcdef123456",
            "guardrailConfiguration": {
                "guardrailIdentifier": "my-guardrail-id",
                "guardrailVersion": "1.0"
            },
            "bedrockModelConfigurations": {
                "performanceConfig": {
                    "latency": "optimized"
                }
            }
        }
    )

    client = Client(
        region_name="us-west-2",
        profile_name="my-profile",
        endpoint_url="https://bedrock-runtime.us-west-2.amazonaws.com",
        advanced_config={
            "max_retries": 3,
            "retry_delay": 1.0,
            "timeout": 60,
        }
    )

Working with Multiple Agents
--------------------------

You can create and manage multiple agents with a single client:

.. code-block:: python

    from bedrock_agents_sdk import Client, Agent

    weather_agent = Agent(
        name="WeatherAgent",
        description="An agent that can tell you the weather",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful weather assistant."
    )

    time_agent = Agent(
        name="TimeAgent",
        description="An agent that can tell you the time",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful time assistant."
    )

    client = Client()
    client.add_agent(weather_agent)
    client.add_agent(time_agent)

    # Switch between agents
    client.set_active_agent("WeatherAgent")
    # or
    client.set_active_agent(weather_agent)

Conversation Management
---------------------

The SDK provides methods for managing conversations:

.. code-block:: python

    from bedrock_agents_sdk import Client, Agent, Message

    agent = Agent(
        name="ConversationAgent",
        description="An agent that can manage conversations",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant."
    )

    client = Client()
    client.add_agent(agent)

    # Start a new conversation
    conversation_id = client.start_conversation()

    # Send a message
    response = client.send_message("Hello, how are you?", conversation_id=conversation_id)

    # Get conversation history
    history = client.get_conversation_history(conversation_id)

    # End a conversation
    client.end_conversation(conversation_id) 