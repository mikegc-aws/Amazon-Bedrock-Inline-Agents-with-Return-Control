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

BedrockAgents Client
-------------------

The ``BedrockAgents`` class is the main client for interacting with Amazon Bedrock Agents. It provides methods for:

* Adding agents
* Running agents locally
* Deploying agents to AWS
* Managing conversations

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

Example:

.. code-block:: python

    weather_group = ActionGroup(
        name="weather",
        description="Functions for getting weather information"
    )
    weather_group.add_function(get_weather)
    agent.add_action_group(weather_group)

Message
------

The ``Message`` class represents a message in a conversation with the agent. Messages can be from the user or the agent and can contain text, function calls, and function results.

Plugins
------

Plugins extend the functionality of the SDK by adding new capabilities to agents. The SDK includes several built-in plugins:

* **SecurityPlugin**: Adds security features to the agent
* **GuardrailPlugin**: Adds content filtering and guardrails
* **KnowledgeBasePlugin**: Connects the agent to an Amazon Bedrock Knowledge Base

Deployment
---------

The SDK provides tools for deploying agents to AWS using AWS SAM (Serverless Application Model). The ``SAMTemplateGenerator`` class generates the necessary templates and resources for deployment. 