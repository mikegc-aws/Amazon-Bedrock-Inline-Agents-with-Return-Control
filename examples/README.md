# Bedrock Agents SDK Examples

This directory contains example scripts demonstrating how to use the Bedrock Agents SDK for various use cases.

## Prerequisites

Before running these examples, make sure you have:

1. Installed the Bedrock Agents SDK: `pip install bedrock-agents-sdk`
2. Configured AWS credentials with appropriate permissions for Amazon Bedrock
3. Access to the Amazon Bedrock service and the models used in the examples

## Examples Overview

### Simple Example

**File:** `simple_example.py`

A basic example demonstrating how to create a Bedrock Agents client, define an agent with simple functions, and run it with user queries. This example includes functions for getting the current time, date, and adding numbers.

```bash
python simple_example.py
```

### Plugin Example

**File:** `plugin_example.py`

Demonstrates how to use plugins with the Bedrock Agents SDK. This example shows how to create and register various plugins including a custom logging plugin, security plugin, guardrail plugin, and knowledge base plugin.

```bash
python plugin_example.py
```

### Action Groups Example

**File:** `action_groups_example.py`

Shows how to organize functions into action groups. This example creates a weather service action group with functions for getting current weather and forecasts.

```bash
python action_groups_example.py
```

### Knowledge Base Example

**File:** `knowledge_base_example.py`

Demonstrates how to integrate knowledge bases with your agent. This example shows how to reference an existing knowledge base and use it to answer user queries.

```bash
python knowledge_base_example.py
```

### Deployment Example

**File:** `deployment_example.py`

Shows how to deploy your agent to AWS using the SAM (Serverless Application Model) template generator. This example demonstrates how to create a local agent, test it, and then generate a complete SAM project for cloud deployment.

```bash
python deployment_example.py
```

## Customizing the Examples

To adapt these examples for your own use:

1. Replace placeholder values (like "your-knowledge-base-id") with your actual resource IDs
2. Modify the agent instructions to suit your specific use case
3. Replace mock implementations with actual API calls or database queries
4. Adjust the model parameters as needed

## Additional Resources

- [Bedrock Agents SDK Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Amazon Bedrock Developer Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [AWS SDK for Python (Boto3) Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) 