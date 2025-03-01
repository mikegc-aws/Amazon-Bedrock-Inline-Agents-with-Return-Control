"""
Base plugin class for Bedrock Agents SDK.
"""
from typing import Dict, Any

class BedrockAgentsPlugin:
    """Base class for all plugins for the BedrockAgents SDK"""
    
    def initialize(self, client):
        """Called when the plugin is registered with the client"""
        self.client = client
    
    def pre_invoke(self, params):
        """Called before invoke_inline_agent, can modify params"""
        return params
    
    def post_invoke(self, response):
        """Called after invoke_inline_agent, can modify response"""
        return response
    
    def post_process(self, result):
        """Called after processing the response, can modify the final result"""
        return result 