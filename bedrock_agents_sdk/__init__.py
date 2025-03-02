"""
Amazon Bedrock Agents with Return Control SDK

This SDK provides a simple yet powerful way to create and interact with Amazon Bedrock Agents 
using the Return Control pattern. It allows you to easily define function tools, organize them 
into action groups, and handle the entire conversation flow with minimal boilerplate code.
"""

from bedrock_agents_sdk.core.client import Client
from bedrock_agents_sdk.models.agent import Agent
from bedrock_agents_sdk.models.message import Message
from bedrock_agents_sdk.models.function import Function
from bedrock_agents_sdk.models.action_group import ActionGroup
from bedrock_agents_sdk.models.files import InputFile, OutputFile
from bedrock_agents_sdk.plugins.base import AgentPlugin, BedrockAgentsPlugin, ClientPlugin
from bedrock_agents_sdk.plugins.security import SecurityPlugin
from bedrock_agents_sdk.plugins.guardrail import GuardrailPlugin
from bedrock_agents_sdk.plugins.knowledge_base import KnowledgeBasePlugin
from bedrock_agents_sdk.deployment.sam_template import SAMTemplateGenerator

# For backward compatibility
BedrockAgents = Client

__version__ = "0.1.0"

__all__ = [
    "Client",
    "BedrockAgents",  # Keep for backward compatibility
    "Agent",
    "Message",
    "Function",
    "ActionGroup",
    "InputFile",
    "OutputFile",
    "AgentPlugin",
    "BedrockAgentsPlugin",  # Keep for backward compatibility
    "ClientPlugin",  # Keep for backward compatibility
    "SecurityPlugin",
    "GuardrailPlugin",
    "KnowledgeBasePlugin",
    "SAMTemplateGenerator",
]
