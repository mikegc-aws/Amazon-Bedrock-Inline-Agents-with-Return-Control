Deployment
==========

This section covers how to deploy your Amazon Bedrock Agents to AWS.

Prerequisites
------------

Before deploying your agent, ensure you have:

* AWS CLI configured with appropriate credentials
* AWS SAM CLI installed
* An S3 bucket for deployment artifacts
* Appropriate permissions to create and manage AWS resources

Deployment Process
----------------

The SDK provides a simple way to deploy your agent to AWS using the ``deploy`` method:

.. code-block:: python

    from bedrock_agents_sdk import BedrockAgents, Agent

    def get_time() -> dict:
        """Get the current time"""
        import datetime
        now = datetime.datetime.now()
        return {"time": now.strftime("%H:%M:%S")}

    agent = Agent(
        name="TimeAgent",
        description="An agent that can tell you the current time",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can tell the time."
    )

    agent.add_function(get_time)

    client = BedrockAgents()
    client.add_agent(agent)

    # Deploy the agent to AWS
    client.deploy(
        stack_name="time-agent",
        s3_bucket="my-deployment-bucket",
        s3_prefix="time-agent"
    )

Deployment Options
----------------

The ``deploy`` method accepts several options to customize the deployment:

* ``stack_name``: The name of the CloudFormation stack to create
* ``s3_bucket``: The S3 bucket to store deployment artifacts
* ``s3_prefix``: The prefix for deployment artifacts in the S3 bucket
* ``region_name``: The AWS region to deploy to
* ``profile_name``: The AWS profile to use for deployment
* ``capabilities``: The CloudFormation capabilities to use
* ``parameter_overrides``: CloudFormation parameter overrides
* ``no_confirm_changeset``: Whether to skip confirmation of the CloudFormation changeset
* ``fail_on_empty_changeset``: Whether to fail if the CloudFormation changeset is empty

SAM Template Generation
---------------------

The SDK generates an AWS SAM template for deployment. You can customize the template generation process using the ``SAMTemplateGenerator`` class:

.. code-block:: python

    from bedrock_agents_sdk import BedrockAgents, Agent
    from bedrock_agents_sdk.deployment import SAMTemplateGenerator

    agent = Agent(
        name="CustomAgent",
        description="An agent with custom deployment",
        foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant."
    )

    # Create a custom SAM template generator
    template_generator = SAMTemplateGenerator(
        memory_size=512,
        timeout=30,
        runtime="python3.9",
        environment_variables={
            "DEBUG": "true",
            "LOG_LEVEL": "INFO"
        }
    )

    # Deploy with the custom template generator
    client = BedrockAgents()
    client.add_agent(agent)
    client.deploy(
        stack_name="custom-agent",
        s3_bucket="my-deployment-bucket",
        s3_prefix="custom-agent",
        template_generator=template_generator
    )

Updating Deployed Agents
----------------------

To update a deployed agent, simply make changes to your agent and redeploy:

.. code-block:: python

    # Update the agent
    agent.instructions = "You are a helpful assistant that can tell the time and date."

    # Add a new function
    def get_date() -> dict:
        """Get the current date"""
        import datetime
        now = datetime.datetime.now()
        return {"date": now.strftime("%Y-%m-%d")}

    agent.add_function(get_date)

    # Redeploy the agent
    client.deploy(
        stack_name="time-agent",
        s3_bucket="my-deployment-bucket",
        s3_prefix="time-agent"
    ) 