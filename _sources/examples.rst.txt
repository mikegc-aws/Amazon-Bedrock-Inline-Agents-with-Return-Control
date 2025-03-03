Examples
========

The SDK includes several examples to help you get started. These examples demonstrate different features and use cases for the SDK.

Simple Example
-------------

The simple example demonstrates how to create a basic agent with time and math functions.

.. literalinclude:: ../../examples/simple_example.py
   :language: python
   :linenos:

Action Groups Example
-------------------

The action groups example demonstrates how to use action groups to organize your agent's functions.

.. literalinclude:: ../../examples/action_groups_example.py
   :language: python
   :linenos:

Configuration Methods Example
----------------------------

This example demonstrates the four different ways to configure agents with action groups, highlighting the recommended ActionGroup-first approach.

.. literalinclude:: ../../examples/configuration_methods_example.py
   :language: python
   :linenos:

Parameter Handling Example
-------------------------

The parameter handling example demonstrates how to work with function parameters and validation.

.. literalinclude:: ../../examples/parameter_handling_example.py
   :language: python
   :linenos:

Code Interpreter Example
----------------------

The code interpreter example demonstrates how to use the Code Interpreter feature to write and execute Python code.

.. literalinclude:: ../../examples/code_interpreter_example.py
   :language: python
   :linenos:

Plugin Example
------------

The plugin example demonstrates how to use plugins to extend your agent's capabilities.

.. literalinclude:: ../../examples/plugin_example.py
   :language: python
   :linenos:

Dependency Example
----------------

The dependency example demonstrates how to handle dependencies in your agent's functions.

.. literalinclude:: ../../examples/dependency_example.py
   :language: python
   :linenos:

Deployment Example
----------------

The deployment example demonstrates how to deploy your agent to AWS.

.. literalinclude:: ../../examples/deployment_example.py
   :language: python
   :linenos:

Knowledge Base Example
--------------------

The knowledge base example demonstrates how to connect your agent to an Amazon Bedrock Knowledge Base.

.. literalinclude:: ../../examples/knowledge_base_example.py
   :language: python
   :linenos:

Simple Weather Agent
------------------

.. code-block:: python

    import requests
    from bedrock_agents_sdk import Client, Agent

    def get_weather(location: str) -> dict:
        """Get the current weather for a location
        
        Args:
            location: The city and state, e.g. 'Seattle, WA'
            
        Returns:
            dict: Weather information including temperature and conditions
        """
        # This is a mock implementation - in a real application, you would call a weather API
        return {
            "location": location,
            "temperature": 72,
            "conditions": "sunny",
            "humidity": 45,
            "wind_speed": 5
        }

    agent = Agent(
        name="WeatherAgent",
        description="An agent that can tell you the weather",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful weather assistant. You can tell users the current weather for a location."
    )

    agent.add_function(get_weather)

    client = Client()
    client.add_agent(agent)
    client.run()

File Processing Agent
-------------------

.. code-block:: python

    import os
    import json
    from bedrock_agents_sdk import Client, Agent, InputFile, OutputFile

    def read_file(file_path: InputFile) -> dict:
        """Read the contents of a file
        
        Args:
            file_path: The path to the file to read
            
        Returns:
            dict: The contents of the file
        """
        with open(file_path.local_path, "r") as f:
            content = f.read()
        
        return {"content": content}

    def write_file(content: str, file_name: str) -> OutputFile:
        """Write content to a file
        
        Args:
            content: The content to write to the file
            file_name: The name of the file to write
            
        Returns:
            OutputFile: The file that was written
        """
        file_path = f"/tmp/{file_name}"
        with open(file_path, "w") as f:
            f.write(content)
        
        return OutputFile(local_path=file_path, file_name=file_name)

    agent = Agent(
        name="FileAgent",
        description="An agent that can read and write files",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can read and write files."
    )

    agent.add_function(read_file)
    agent.add_function(write_file)

    client = Client()
    client.add_agent(agent)
    client.run()

Multi-Agent System
----------------

.. code-block:: python

    from bedrock_agents_sdk import Client, Agent, ActionGroup

    # Weather functions
    def get_weather(location: str) -> dict:
        """Get the current weather for a location"""
        return {"temperature": 72, "conditions": "sunny"}

    def get_forecast(location: str, days: int) -> dict:
        """Get the weather forecast for a location"""
        return {"forecast": [{"day": i, "temperature": 70 + i, "conditions": "sunny"} for i in range(days)]}

    # Time functions
    def get_time() -> dict:
        """Get the current time"""
        import datetime
        now = datetime.datetime.now()
        return {"time": now.strftime("%H:%M:%S")}

    def get_date() -> dict:
        """Get the current date"""
        import datetime
        now = datetime.datetime.now()
        return {"date": now.strftime("%Y-%m-%d")}

    # Create agents
    weather_agent = Agent(
        name="WeatherAgent",
        description="An agent that can tell you the weather",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful weather assistant."
    )

    time_agent = Agent(
        name="TimeAgent",
        description="An agent that can tell you the time and date",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful time assistant."
    )

    # Create action groups
    weather_group = ActionGroup(
        name="weather",
        description="Functions for getting weather information"
    )
    weather_group.add_function(get_weather)
    weather_group.add_function(get_forecast)

    time_group = ActionGroup(
        name="time",
        description="Functions for getting time information"
    )
    time_group.add_function(get_time)
    time_group.add_function(get_date)

    # Add action groups to agents
    weather_agent.add_action_group(weather_group)
    time_agent.add_action_group(time_group)

    # Create client and add agents
    client = Client()
    client.add_agent(weather_agent)
    client.add_agent(time_agent)

    # Set the active agent
    client.set_active_agent("WeatherAgent")

    # Run the client
    client.run()

Agent with Knowledge Base
----------------------

.. code-block:: python

    from bedrock_agents_sdk import Client, Agent, KnowledgeBasePlugin

    agent = Agent(
        name="DocsAgent",
        description="An agent that can answer questions about documentation",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can answer questions about documentation."
    )

    kb_plugin = KnowledgeBasePlugin(
        knowledge_base_id="my-docs-kb",
        retrieval_config={
            "vector_search_configuration": {
                "number_of_results": 5
            }
        }
    )

    agent.add_plugin(kb_plugin)

    client = Client()
    client.add_agent(agent)
    client.run() 