"""
Base plugin class for Bedrock Agents SDK.
"""
from typing import Dict, Any

class AgentPlugin:
    """Base class for all plugins for the Bedrock Agents SDK"""
    
    def pre_invoke(self, params):
        """Called before invoke_inline_agent, can modify params"""
        return params
    
    def post_invoke(self, response):
        """Called after invoke_inline_agent, can modify response"""
        return response
    
    def post_process(self, result):
        """Called after processing the response, can modify the final result"""
        return result
    
    def pre_deploy(self, template):
        """
        Called before generating the SAM template, can modify the template
        
        Args:
            template: The SAM template dictionary
            
        Returns:
            The modified SAM template dictionary
        """
        return template

# For backward compatibility
BedrockAgentsPlugin = AgentPlugin
ClientPlugin = AgentPlugin 