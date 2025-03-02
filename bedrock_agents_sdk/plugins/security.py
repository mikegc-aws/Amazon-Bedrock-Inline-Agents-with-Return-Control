"""
Security plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import AgentPlugin

class SecurityPlugin(AgentPlugin):
    """Plugin for adding security features to Bedrock Agents"""
    
    def __init__(self, customer_encryption_key_arn=None):
        """
        Initialize the security plugin
        
        Args:
            customer_encryption_key_arn: The ARN of the KMS key to use for encryption
        """
        self.customer_encryption_key_arn = customer_encryption_key_arn
    
    def pre_invoke(self, params):
        """Add KMS key ARN to the request parameters"""
        if self.customer_encryption_key_arn and "customerEncryptionKeyArn" not in params:
            params["customerEncryptionKeyArn"] = self.customer_encryption_key_arn
        return params
    
    def pre_deploy(self, template):
        """Add KMS key ARN to the agent configuration in the SAM template"""
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add KMS key ARN to the agent configuration
            if self.customer_encryption_key_arn and "customerEncryptionKeyArn" not in agent_props:
                agent_props["customerEncryptionKeyArn"] = self.customer_encryption_key_arn
            
            # Add IAM permissions for KMS key
            if self.customer_encryption_key_arn and "BedrockAgentRole" in template["Resources"]:
                role_props = template["Resources"]["BedrockAgentRole"]["Properties"]
                
                # Get the policy document
                if "Policies" in role_props:
                    for policy in role_props["Policies"]:
                        if "PolicyDocument" in policy and "Statement" in policy["PolicyDocument"]:
                            statements = policy["PolicyDocument"]["Statement"]
                            
                            # Add KMS permissions
                            kms_statement = {
                                "Effect": "Allow",
                                "Action": [
                                    "kms:Decrypt",
                                    "kms:GenerateDataKey"
                                ],
                                "Resource": self.customer_encryption_key_arn
                            }
                            
                            # Check if statement already exists
                            if not any(self._is_same_kms_resource(stmt, self.customer_encryption_key_arn) for stmt in statements):
                                statements.append(kms_statement)
            
        return template
        
    def _is_same_kms_resource(self, statement, kms_arn):
        """Check if a statement refers to the same KMS resource"""
        resource = statement.get("Resource")
        return resource == kms_arn 