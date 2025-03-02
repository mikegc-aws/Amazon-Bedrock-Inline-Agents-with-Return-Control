"""
Knowledge base plugin for Bedrock Agents SDK.
"""
from bedrock_agents_sdk.plugins.base import AgentPlugin

class KnowledgeBasePlugin(AgentPlugin):
    """Plugin for adding knowledge base integration to Bedrock Agents"""
    
    def __init__(self, knowledge_base_id: str, description: str = None, retrieval_config: dict = None):
        """
        Initialize the knowledge base plugin
        
        Args:
            knowledge_base_id: The ID of the knowledge base to use
            description: Optional description of the knowledge base
            retrieval_config: Optional retrieval configuration for the knowledge base
        """
        self.knowledge_base_id = knowledge_base_id
        self.description = description or f"Knowledge base {knowledge_base_id}"
        self.retrieval_config = retrieval_config
    
    def pre_invoke(self, params):
        """Add knowledge base configuration to the request parameters"""
        if "knowledgeBases" not in params:
            params["knowledgeBases"] = []
            
        # Add the knowledge base if it's not already in the list
        kb_entry = {
            "knowledgeBaseId": self.knowledge_base_id,
            "description": self.description
        }
        
        # Add retrieval configuration if provided
        if self.retrieval_config:
            kb_entry["retrievalConfiguration"] = self.retrieval_config
        
        if not any(kb.get("knowledgeBaseId") == self.knowledge_base_id for kb in params["knowledgeBases"]):
            params["knowledgeBases"].append(kb_entry)
            
        return params
    
    def pre_deploy(self, template):
        """Add knowledge base configuration to the agent in the SAM template"""
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add knowledge base configuration to the agent
            if "KnowledgeBases" not in agent_props:
                agent_props["KnowledgeBases"] = []
                
            # Add the knowledge base if it's not already in the list
            kb_entry = {
                "KnowledgeBaseId": self.knowledge_base_id,
                "Description": self.description
            }
            
            # Add retrieval configuration if provided
            if self.retrieval_config:
                kb_entry["RetrievalConfiguration"] = self.retrieval_config
            
            if not any(kb.get("KnowledgeBaseId") == self.knowledge_base_id for kb in agent_props["KnowledgeBases"]):
                agent_props["KnowledgeBases"].append(kb_entry)
            
            # Add IAM permissions for knowledge base
            if "BedrockAgentRole" in template["Resources"]:
                role_props = template["Resources"]["BedrockAgentRole"]["Properties"]
                
                # Get the policy document
                if "Policies" in role_props:
                    for policy in role_props["Policies"]:
                        if "PolicyDocument" in policy and "Statement" in policy["PolicyDocument"]:
                            statements = policy["PolicyDocument"]["Statement"]
                            
                            # Add knowledge base permissions
                            kb_statement = {
                                "Effect": "Allow",
                                "Action": [
                                    "bedrock:RetrieveAndGenerate",
                                    "bedrock:Retrieve"
                                ],
                                "Resource": {
                                    "Fn::Sub": "arn:aws:bedrock:${AWS::Region}:${AWS::AccountId}:knowledge-base/" + self.knowledge_base_id
                                }
                            }
                            
                            # Check if statement already exists
                            if not any(self._is_same_kb_resource(stmt, self.knowledge_base_id) for stmt in statements):
                                statements.append(kb_statement)
            
        return template
        
    def _is_same_kb_resource(self, statement, kb_id):
        """Check if a statement refers to the same knowledge base resource"""
        resource = statement.get("Resource")
        if isinstance(resource, dict) and "Fn::Sub" in resource:
            return resource["Fn::Sub"].endswith(f"knowledge-base/{kb_id}")
        elif isinstance(resource, str):
            return resource.endswith(f"knowledge-base/{kb_id}")
        return False 