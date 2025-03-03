Core Concepts
============

The Amazon Bedrock Agents with Return Control SDK is built around several core concepts that work together to create a powerful agent experience.

Agent
-----

The ``Agent`` class is the central component of the SDK. It represents an Amazon Bedrock Agent and contains all the configuration, functions, and action groups that define the agent's capabilities.

Key properties of an Agent:

* **Name**: The name of the agent
* **Description**: A description of what the agent does
* **Foundation Model**: The Amazon Bedrock foundation model to use (e.g., Claude, Llama)
* **Instructions**: Detailed instructions for the agent's behavior
* **Functions**: The functions that the agent can call
* **Action Groups**: Logical groupings of related functions
* **Code Interpreter**: Optional capability to write and execute Python code

Client
-------------------

The ``Client`` class (formerly ``BedrockAgents``) is the main client for interacting with Amazon Bedrock Agents. It provides methods for:

* Adding agents
* Running agents locally
* Deploying agents to AWS
* Managing conversations

Verbosity and Logging
--------------------

The SDK provides two separate but complementary control systems for output:

1. **Verbosity** - Controls SDK-level logs (client operations, function calls, etc.)
2. **Trace Level** - Controls agent-level traces (reasoning, decisions, code execution, etc.)

This separation allows you to independently control what you see from the SDK itself versus what you see from the agent's internal processes.

Verbosity Levels:

* **quiet**: No SDK logs, no agent traces (errors are still displayed)
* **normal** (default): SDK logs and agent traces controlled by parameters
* **verbose**: SDK logs enabled, agent traces enabled, trace level set to at least "standard"
* **debug**: SDK logs enabled, agent traces enabled, trace level set to "detailed"

Trace Levels:

* **none** (default): No trace information
* **minimal**: Only basic reasoning and decisions
* **standard**: Reasoning, decisions, and function calls
* **detailed**: All formatted trace information
* **raw**: Complete unprocessed trace data in JSON format, including code interpreter output

The **raw** trace level is particularly useful for seeing the code generated and executed by the code interpreter.

Function
-------

Functions are the building blocks of agent capabilities. Each function represents a tool that the agent can use to perform a specific task. Functions are defined as regular Python functions with type hints and docstrings, which are used to generate the JSON schema for the agent.

Example:

.. code-block:: python

    def get_weather(location: str) -> dict:
        """Get the current weather for a location
        
        Args:
            location: The city and state, e.g. 'Seattle, WA'
            
        Returns:
            dict: Weather information including temperature and conditions
        """
        # Implementation
        return {"temperature": 72, "conditions": "sunny"}

Action Group
-----------

Action Groups are logical groupings of related functions. They help organize the agent's capabilities and make it easier for the agent to understand when to use specific functions.

The SDK supports multiple ways to configure agents with action groups, with the ActionGroup-first approach being the recommended method.

1. **Using ActionGroup Objects in Constructor (Recommended)**:

.. code-block:: python

    weather_group = ActionGroup(
        name="WeatherService",
        description="Provides weather information",
        functions=[get_weather, get_forecast]
    )
    
    agent = Agent(
        name="WeatherAgent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a weather assistant.",
        action_groups=[weather_group]
    )

2. **Adding ActionGroup Objects After Creation**:

.. code-block:: python

    agent = Agent(
        name="WeatherAgent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a weather assistant."
    )
    
    weather_group = ActionGroup(
        name="WeatherService",
        description="Provides weather information",
        functions=[get_weather, get_forecast]
    )
    
    agent.add_action_group(weather_group)

3. **Using Functions Dictionary**:

.. code-block:: python

    agent = Agent(
        name="WeatherAgent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a weather assistant.",
        functions={
            "WeatherService": [get_weather, get_forecast]
        }
    )

4. **Using Functions List** (functions will be added to a default action group):

.. code-block:: python

    agent = Agent(
        name="WeatherAgent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a weather assistant.",
        functions=[get_weather, get_forecast]
    )

The ActionGroup-first approach (options 1 and 2) is recommended as it provides the most explicit and clear way to organize your agent's capabilities.

Message
------

The ``Message`` class represents a message in a conversation with the agent. Messages can be from the user or the agent and can contain text, function calls, and function results.

Plugins
------

Plugins extend the functionality of the SDK by adding new capabilities to agents. The SDK includes several built-in plugins:

* **SecurityPlugin**: Adds security features to the agent
* **GuardrailPlugin**: Adds content filtering and guardrails
* **KnowledgeBasePlugin**: Connects the agent to an Amazon Bedrock Knowledge Base

All plugins inherit from the ``AgentPlugin`` base class (formerly ``ClientPlugin``).

Deployment
---------

The SDK provides tools for deploying agents to AWS using AWS SAM (Serverless Application Model). The ``SAMTemplateGenerator`` class generates the necessary templates and resources for deployment. 