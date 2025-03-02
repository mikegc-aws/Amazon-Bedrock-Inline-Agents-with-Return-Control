"""
Security plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import AgentPlugin

class SecurityPlugin(AgentPlugin):
    """Plugin for adding security features to Bedrock Agents"""
    
    def __init__(self, kms_key_arn: str):
        """
        Initialize the security plugin
        
        Args:
            kms_key_arn: The ARN of the KMS key to use for encryption
        """
        self.kms_key_arn = kms_key_arn
    
    def pre_invoke(self, params):
        """Add KMS key ARN to the request parameters"""
        if "customerEncryptionKeyArn" not in params:
            params["customerEncryptionKeyArn"] = self.kms_key_arn
        return params
    
    def pre_deploy(self, template):
        """Add KMS key ARN to the agent configuration in the SAM template"""
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add KMS key ARN to the agent configuration
            if "customerEncryptionKeyArn" not in agent_props:
                agent_props["customerEncryptionKeyArn"] = self.kms_key_arn
            
        return template 