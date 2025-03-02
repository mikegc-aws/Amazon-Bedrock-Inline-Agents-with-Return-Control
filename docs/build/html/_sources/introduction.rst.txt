Introduction
============

.. warning::
   This is an unofficial SDK developed by Mike Chambers and is not an official AWS product or service. This project is not affiliated with, endorsed by, or sponsored by Amazon Web Services (AWS). Amazon Bedrock is a service provided by AWS, but this SDK is a community-developed tool to work with that service.

The Amazon Bedrock Agents with Return Control SDK provides a simple yet powerful way to create and interact with Amazon Bedrock Agents using the Return Control pattern. It allows you to easily define function tools, organize them into action groups, and handle the entire conversation flow with minimal boilerplate code.

Why Use This SDK?
----------------

This SDK simplifies the process of creating and deploying Amazon Bedrock Agents by:

1. Providing a clean, Pythonic interface for defining agent functionality
2. Automating the deployment process with AWS SAM templates
3. Handling conversation state management automatically
4. Offering a plugin system for extending functionality
5. Supporting local testing and debugging

Benefits
-------

* **Rapid Development**: Define Python functions locally that your cloud-hosted agent can call
* **Zero Conversation Management**: AWS handles all the state tracking and agent orchestration
* **Test Locally, Run in Cloud**: Develop on your machine, then deploy to AWS with auto-generated SAM templates
* **Extensible Architecture**: Use plugins to add security, guardrails, knowledge bases, and more
* **Simplified Deployment**: Deploy your agent to AWS with a single command

Features
-------

* Function tool definition with automatic schema generation
* Action group organization
* Conversation flow management
* Local testing and debugging
* AWS deployment with SAM templates
* Plugin system for extending functionality
* Support for file handling
* Command-line interface 