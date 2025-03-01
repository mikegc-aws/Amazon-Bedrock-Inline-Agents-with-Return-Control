"""
Knowledge Base plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import BedrockAgentsPlugin

class KnowledgeBasePlugin(BedrockAgentsPlugin):
    """Plugin for knowledge base integration"""
    
    def __init__(self, knowledge_base_id, description=None, retrieval_config=None):
        """Initialize the knowledge base plugin"""
        self.knowledge_base_id = knowledge_base_id
        self.description = description
        self.retrieval_config = retrieval_config or {}
    
    def pre_invoke(self, params):
        """Add knowledge base configuration before invocation"""
        kb_config = {
            "knowledgeBaseId": self.knowledge_base_id
        }
        
        if self.description:
            kb_config["description"] = self.description
            
        if self.retrieval_config:
            kb_config["retrievalConfiguration"] = self.retrieval_config
        
        if "knowledgeBases" not in params:
            params["knowledgeBases"] = []
            
        params["knowledgeBases"].append(kb_config)
        return params 