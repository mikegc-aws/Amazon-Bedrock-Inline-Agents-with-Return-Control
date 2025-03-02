Examples
========

This section provides examples of using the Amazon Bedrock Agents with Return Control SDK for various use cases.

Simple Weather Agent
------------------

.. code-block:: python

    import requests
    from bedrock_agents_sdk import BedrockAgents, Agent

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

    client = BedrockAgents()
    client.add_agent(agent)
    client.run()

File Processing Agent
-------------------

.. code-block:: python

    import os
    import json
    from bedrock_agents_sdk import BedrockAgents, Agent, InputFile, OutputFile

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

    client = BedrockAgents()
    client.add_agent(agent)
    client.run()

Multi-Agent System
----------------

.. code-block:: python

    from bedrock_agents_sdk import BedrockAgents, Agent, ActionGroup

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
    client = BedrockAgents()
    client.add_agent(weather_agent)
    client.add_agent(time_agent)

    # Set the active agent
    client.set_active_agent("WeatherAgent")

    # Run the client
    client.run()

Agent with Knowledge Base
----------------------

.. code-block:: python

    from bedrock_agents_sdk import BedrockAgents, Agent, KnowledgeBasePlugin

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

    client = BedrockAgents()
    client.add_agent(agent)
    client.run() 