"""
Guardrail plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import AgentPlugin

class GuardrailPlugin(AgentPlugin):
    """Plugin for adding guardrails to Bedrock Agents"""
    
    def __init__(self, guardrail_id: str, guardrail_version: str = None):
        """
        Initialize the guardrail plugin
        
        Args:
            guardrail_id: The ID of the guardrail to use
            guardrail_version: The version of the guardrail to use (optional)
        """
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
    
    def pre_invoke(self, params):
        """Add guardrail configuration to the request parameters"""
        if "guardrailConfiguration" not in params:
            guardrail_config = {
                "guardrailIdentifier": self.guardrail_id
            }
            
            if self.guardrail_version:
                guardrail_config["guardrailVersion"] = self.guardrail_version
                
            params["guardrailConfiguration"] = guardrail_config
        return params
    
    def pre_deploy(self, template):
        """Add guardrail configuration to the agent in the SAM template"""
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add guardrail configuration to the agent
            if "guardrailConfiguration" not in agent_props:
                guardrail_config = {
                    "guardrailIdentifier": self.guardrail_id
                }
                
                if self.guardrail_version:
                    guardrail_config["guardrailVersion"] = self.guardrail_version
                    
                agent_props["guardrailConfiguration"] = guardrail_config
            
            # Add IAM permissions for guardrail
            if "BedrockAgentRole" in template["Resources"]:
                role_props = template["Resources"]["BedrockAgentRole"]["Properties"]
                
                # Get the policy document
                if "Policies" in role_props:
                    for policy in role_props["Policies"]:
                        if "PolicyDocument" in policy and "Statement" in policy["PolicyDocument"]:
                            statements = policy["PolicyDocument"]["Statement"]
                            
                            # Add guardrail permissions
                            guardrail_statement = {
                                "Effect": "Allow",
                                "Action": [
                                    "bedrock:ApplyGuardrail"
                                ],
                                "Resource": {
                                    "Fn::Sub": "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:guardrail/" + self.guardrail_id
                                }
                            }
                            
                            # Check if statement already exists
                            if not any(self._is_same_guardrail_resource(stmt, self.guardrail_id) for stmt in statements):
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