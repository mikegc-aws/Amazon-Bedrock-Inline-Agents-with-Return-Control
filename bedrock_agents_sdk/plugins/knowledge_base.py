"""
Knowledge base plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import AgentPlugin

class KnowledgeBasePlugin(AgentPlugin):
    """Plugin for adding knowledge base integration to Bedrock Agents"""
    
    def __init__(self, knowledge_base_id: str, description: str = None):
        """
        Initialize the knowledge base plugin
        
        Args:
            knowledge_base_id: The ID of the knowledge base to use
            description: Optional description of the knowledge base
        """
        self.knowledge_base_id = knowledge_base_id
        self.description = description or f"Knowledge base {knowledge_base_id}"
    
    def pre_invoke(self, params):
        """Add knowledge base configuration to the request parameters"""
        if "knowledgeBases" not in params:
            params["knowledgeBases"] = []
            
        # Add the knowledge base if it's not already in the list
        kb_entry = {
            "knowledgeBaseId": self.knowledge_base_id,
            "description": self.description
        }
        
        if not any(kb.get("knowledgeBaseId") == self.knowledge_base_id for kb in params["knowledgeBases"]):
            params["knowledgeBases"].append(kb_entry)
            
        return params
    
    def pre_deploy(self, template):
        """Add knowledge base configuration to the agent in the SAM template"""
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add knowledge base configuration to the agent
            if "knowledgeBases" not in agent_props:
                agent_props["knowledgeBases"] = []
                
            # Add the knowledge base if it's not already in the list
            kb_entry = {
                "knowledgeBaseId": self.knowledge_base_id,
                "description": self.description
            }
            
            if not any(kb.get("knowledgeBaseId") == self.knowledge_base_id for kb in agent_props["knowledgeBases"]):
                agent_props["knowledgeBases"].append(kb_entry)
            
        return template 