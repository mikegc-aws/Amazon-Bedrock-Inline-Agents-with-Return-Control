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
    
    def pre_deploy(self, template):
        """Add guardrail configuration to the SAM template"""
        # Add guardrail ID to agent properties
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add GuardrailConfiguration property
            agent_props["GuardrailConfiguration"] = {
                "GuardrailIdentifier": self.guardrail_id
            }
            
            if self.guardrail_version:
                agent_props["GuardrailConfiguration"]["GuardrailVersion"] = self.guardrail_version
            
            # Add IAM permissions for the guardrail
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
                
                # Add guardrail permissions to the policy
                if "PolicyDocument" in policy and "Statement" in policy["PolicyDocument"]:
                    guardrail_statement = {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock:ApplyGuardrail"
                        ],
                        "Resource": {"Fn::Sub": f"arn:aws:bedrock:${{AWS::Region}}:${{AWS::AccountId}}:guardrail/{self.guardrail_id}"}
                    }
                    
                    # Add the statement if it doesn't already exist
                    statements = policy["PolicyDocument"]["Statement"]
                    if not any(self._is_same_guardrail_resource(s, self.guardrail_id) for s in statements):
                        statements.append(guardrail_statement)
        
        return template
        
    def _is_same_guardrail_resource(self, statement, guardrail_id):
        """Check if a statement refers to the same guardrail resource"""
        resource = statement.get("Resource")
        if isinstance(resource, dict) and "Fn::Sub" in resource:
            return resource["Fn::Sub"].endswith(f"guardrail/{guardrail_id}")
        elif isinstance(resource, str):
            return resource.endswith(f"guardrail/{guardrail_id}")
        return False 