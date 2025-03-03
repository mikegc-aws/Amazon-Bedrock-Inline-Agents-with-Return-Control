Quick Start
==========

This guide will help you get started with the Amazon Bedrock Agents with Return Control SDK by creating a simple agent that can tell you the current time.

Minimal Working Example
----------------------

.. code-block:: python

    # Minimal working example
    import datetime
    from bedrock_agents_sdk import Client, Agent, ActionGroup

    def get_time() -> dict:
        """Get the current time"""
        now = datetime.datetime.now()
        return {"time": now.strftime("%H:%M:%S")}

    # Create an action group for time-related functions
    time_group = ActionGroup(
        name="TimeService",
        description="Provides time-related information",
        functions=[get_time]
    )

    # Create the agent with the action group
    agent = Agent(
        name="TimeAgent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can tell the time.",
        action_groups=[time_group]
    )

    client = Client()

    # Run the agent locally
    client.run(agent=agent)

Step-by-Step Guide
-----------------

1. Install the SDK
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install git+https://github.com/aws-samples/bedrock-agents-sdk.git

2. Create a Python File
~~~~~~~~~~~~~~~~~~~~~~

Create a new file called ``time_agent.py`` and add the code from the minimal working example above.

3. Run the Agent Locally
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python time_agent.py

4. Deploy to AWS
~~~~~~~~~~~~~~~

To deploy your agent to AWS, use the ``deploy`` method:

.. code-block:: python

    client.deploy(
        stack_name="time-agent",
        s3_bucket="my-deployment-bucket",
        s3_prefix="time-agent"
    )

That's it! You've created and deployed your first agent using the Amazon Bedrock Agents with Return Control SDK. 