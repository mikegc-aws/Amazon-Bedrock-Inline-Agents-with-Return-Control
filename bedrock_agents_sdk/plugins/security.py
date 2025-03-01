"""
Security plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import BedrockAgentsPlugin

class SecurityPlugin(BedrockAgentsPlugin):
    """Plugin for security features"""
    
    def __init__(self, customer_encryption_key_arn=None):
        """Initialize the security plugin"""
        self.customer_encryption_key_arn = customer_encryption_key_arn
    
    def pre_invoke(self, params):
        """Add security parameters before invocation"""
        if self.customer_encryption_key_arn:
            params["customerEncryptionKeyArn"] = self.customer_encryption_key_arn
        return params 