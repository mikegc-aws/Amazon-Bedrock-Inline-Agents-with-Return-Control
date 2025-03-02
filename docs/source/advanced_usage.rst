Advanced Usage
==============

This section covers advanced usage patterns for the Amazon Bedrock Agents with Return Control SDK.

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

    from bedrock_agents_sdk import BedrockAgents, Agent

    agent = Agent(
        name="AdvancedAgent",
        description="An agent with advanced configuration",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant.",
        advanced_config={
            "timeout_seconds": 300,
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.9,
            "stop_sequences": ["User:"],
        }
    )

    client = BedrockAgents(
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

    from bedrock_agents_sdk import BedrockAgents, Agent

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

    client = BedrockAgents()
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

    from bedrock_agents_sdk import BedrockAgents, Agent, Message

    agent = Agent(
        name="ConversationAgent",
        description="An agent that can manage conversations",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant."
    )

    client = BedrockAgents()
    client.add_agent(agent)

    # Start a new conversation
    conversation_id = client.start_conversation()

    # Send a message
    response = client.send_message("Hello, how are you?", conversation_id=conversation_id)

    # Get conversation history
    history = client.get_conversation_history(conversation_id)

    # End a conversation
    client.end_conversation(conversation_id) 