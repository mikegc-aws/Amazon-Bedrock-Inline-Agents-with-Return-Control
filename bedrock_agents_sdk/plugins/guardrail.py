"""
Guardrail plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import AgentPlugin

class GuardrailPlugin(AgentPlugin):
    """Plugin for adding guardrails to Bedrock Agents"""
    
    def __init__(self, guardrail_id: str, guardrail_version: str):
        """
        Initialize the guardrail plugin
        
        Args:
            guardrail_id: The ID of the guardrail to use
            guardrail_version: The version of the guardrail to use
        """
        self.guardrail_id = guardrail_id
        self.guardrail_version = guardrail_version
    
    def pre_invoke(self, params):
        """Add guardrail configuration to the request parameters"""
        if "guardrailConfiguration" not in params:
            params["guardrailConfiguration"] = {
                "guardrailIdentifier": self.guardrail_id,
                "guardrailVersion": self.guardrail_version
            }
        return params
    
    def pre_deploy(self, template):
        """Add guardrail configuration to the agent in the SAM template"""
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add guardrail configuration to the agent
            if "guardrailConfiguration" not in agent_props:
                agent_props["guardrailConfiguration"] = {
                    "guardrailIdentifier": self.guardrail_id,
                    "guardrailVersion": self.guardrail_version
                }
            
        return template
        
    def _is_same_guardrail_resource(self, statement, guardrail_id):
        """Check if a statement refers to the same guardrail resource"""
        resource = statement.get("Resource")
        if isinstance(resource, dict) and "Fn::Sub" in resource:
            return resource["Fn::Sub"].endswith(f"guardrail/{guardrail_id}")
        elif isinstance(resource, str):
            return resource.endswith(f"guardrail/{guardrail_id}")
        return False 