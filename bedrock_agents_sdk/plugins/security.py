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
    
    def pre_deploy(self, template):
        """Add security configuration to the SAM template"""
        if self.customer_encryption_key_arn and "Resources" in template and "BedrockAgent" in template["Resources"]:
            # Add customer encryption key to agent properties
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            agent_props["CustomerEncryptionKeyArn"] = self.customer_encryption_key_arn
            
            # Add IAM permissions for the KMS key
            agent_role = template["Resources"].get("BedrockAgentRole")
            if agent_role and "Properties" in agent_role and "Policies" in agent_role["Properties"]:
                # Get the first policy (or create one if it doesn't exist)
                if not agent_role["Properties"]["Policies"]:
                    agent_role["Properties"]["Policies"] = [
                        {
                            "PolicyName": {"Fn::Sub": "BedrockAgentPolicy-${AWS::StackName}"},
                            "PolicyDocument": {
                                "Version": "2012-10-17",
                                "Statement": []
                            }
                        }
                    ]
                
                policy = agent_role["Properties"]["Policies"][0]
                
                # Add KMS permissions to the policy
                if "PolicyDocument" in policy and "Statement" in policy["PolicyDocument"]:
                    kms_statement = {
                        "Effect": "Allow",
                        "Action": [
                            "kms:Decrypt",
                            "kms:GenerateDataKey"
                        ],
                        "Resource": self.customer_encryption_key_arn
                    }
                    
                    # Add the statement if it doesn't already exist
                    statements = policy["PolicyDocument"]["Statement"]
                    if not any(s.get("Resource") == self.customer_encryption_key_arn for s in statements):
                        statements.append(kms_statement)
        
        return template 