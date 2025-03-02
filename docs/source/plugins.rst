Plugins
=======

The Amazon Bedrock Agents with Return Control SDK includes a plugin system that allows you to extend the functionality of your agents. This section covers the built-in plugins and how to create your own.

Built-in Plugins
--------------

The SDK includes several built-in plugins:

Security Plugin
~~~~~~~~~~~~~~

The ``SecurityPlugin`` adds security features to your agent:

.. code-block:: python

    from bedrock_agents_sdk import Client, Agent
    from bedrock_agents_sdk import SecurityPlugin

    agent = Agent(
        name="SecureAgent",
        description="A secure agent",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant."
    )

    security_plugin = SecurityPlugin(
        allowed_domains=["example.com", "api.example.org"],
        blocked_domains=["malicious.com"],
        max_tokens_per_request=4096,
        max_requests_per_conversation=10
    )

    agent.add_plugin(security_plugin)

Guardrail Plugin
~~~~~~~~~~~~~~

The ``GuardrailPlugin`` adds content filtering and guardrails to your agent:

.. code-block:: python

    from bedrock_agents_sdk import Client, Agent
    from bedrock_agents_sdk import GuardrailPlugin

    agent = Agent(
        name="GuardrailedAgent",
        description="An agent with guardrails",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant."
    )

    guardrail_plugin = GuardrailPlugin(
        content_policy={
            "block_unsafe_content": True,
            "block_ungrounded_content": True,
            "block_harmful_content": True
        },
        guardrail_id="my-guardrail-id",  # Optional: ID of an existing Amazon Bedrock Guardrail
        guardrail_version="DRAFT"  # Optional: Version of the guardrail to use
    )

    agent.add_plugin(guardrail_plugin)

Knowledge Base Plugin
~~~~~~~~~~~~~~~~~~

The ``KnowledgeBasePlugin`` connects your agent to an Amazon Bedrock Knowledge Base:

.. code-block:: python

    from bedrock_agents_sdk import Client, Agent
    from bedrock_agents_sdk import KnowledgeBasePlugin

    agent = Agent(
        name="KnowledgeAgent",
        description="An agent with a knowledge base",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant."
    )

    kb_plugin = KnowledgeBasePlugin(
        knowledge_base_id="my-knowledge-base-id",
        retrieval_config={
            "vector_search_configuration": {
                "number_of_results": 5,
                "filter_configuration": {
                    "filters": [
                        {
                            "key": "category",
                            "value": "documentation"
                        }
                    ]
                }
            }
        }
    )

    agent.add_plugin(kb_plugin)

Creating Custom Plugins
---------------------

You can create your own plugins by extending the ``AgentPlugin`` class:

.. code-block:: python

    from bedrock_agents_sdk.plugins.base import AgentPlugin

    class MyCustomPlugin(AgentPlugin):
        def __init__(self, custom_param1, custom_param2):
            self.custom_param1 = custom_param1
            self.custom_param2 = custom_param2

        def on_message_received(self, message, agent):
            """Called when a message is received from the user"""
            print(f"Received message: {message}")
            return message

        def on_message_sent(self, message, agent):
            """Called when a message is sent to the user"""
            print(f"Sent message: {message}")
            return message

        def on_function_call(self, function_name, parameters, agent):
            """Called when a function is called by the agent"""
            print(f"Function call: {function_name}({parameters})")
            return function_name, parameters

        def on_function_result(self, function_name, result, agent):
            """Called when a function returns a result"""
            print(f"Function result: {function_name} -> {result}")
            return result

    # Using the custom plugin
    agent = Agent(
        name="CustomPluginAgent",
        description="An agent with a custom plugin",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant."
    )

    custom_plugin = MyCustomPlugin(
        custom_param1="value1",
        custom_param2="value2"
    )

    agent.add_plugin(custom_plugin)

Plugin Lifecycle
--------------

Plugins can hook into various points in the agent's lifecycle:

* ``on_message_received``: Called when a message is received from the user
* ``on_message_sent``: Called when a message is sent to the user
* ``on_function_call``: Called when a function is called by the agent
* ``on_function_result``: Called when a function returns a result
* ``on_conversation_start``: Called when a conversation starts
* ``on_conversation_end``: Called when a conversation ends
* ``on_agent_created``: Called when an agent is created
* ``on_agent_deployed``: Called when an agent is deployed

Plugin Ordering
-------------

When multiple plugins are added to an agent, they are executed in the order they were added. You can control the order by adding plugins in the desired sequence:

.. code-block:: python

    agent = Agent(
        name="MultiPluginAgent",
        description="An agent with multiple plugins",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant."
    )

    # Plugins will be executed in this order
    agent.add_plugin(security_plugin)
    agent.add_plugin(guardrail_plugin)
    agent.add_plugin(kb_plugin)
    agent.add_plugin(custom_plugin) 