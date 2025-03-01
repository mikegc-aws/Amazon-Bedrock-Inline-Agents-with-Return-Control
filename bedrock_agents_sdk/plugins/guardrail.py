"""
Guardrail plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import BedrockAgentsPlugin

class GuardrailPlugin(BedrockAgentsPlugin):
    """Plugin for guardrail features"""
    
    def __init__(self, guardrail_id, guardrail_version=None):
        """Initialize the guardrail plugin"""
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
    
    def pre_invoke(self, params):
        """Add guardrail configuration before invocation"""
        params["guardrailConfiguration"] = {
            "guardrailIdentifier": self.guardrail_id
        }
        
        if self.guardrail_version:
            params["guardrailConfiguration"]["guardrailVersion"] = self.guardrail_version
            
        return params 