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
    
    def pre_deploy(self, template):
        """Add knowledge base configuration to the SAM template"""
        # Add knowledge base ID to agent properties
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add KnowledgeBases property if it doesn't exist
            if "KnowledgeBases" not in agent_props:
                agent_props["KnowledgeBases"] = []
                
            # Create knowledge base configuration
            kb_config = {
                "KnowledgeBaseId": self.knowledge_base_id
            }
            
            if self.description:
                kb_config["Description"] = self.description
                
            if self.retrieval_config:
                # Convert retrieval configuration to proper format
                # The CloudFormation property names are typically PascalCase
                retrieval_config = {}
                for key, value in self.retrieval_config.items():
                    # Convert camelCase to PascalCase
                    pascal_key = key[0].upper() + key[1:]
                    retrieval_config[pascal_key] = value
                
                kb_config["RetrievalConfiguration"] = retrieval_config
                
            # Add the knowledge base configuration to the agent properties
            agent_props["KnowledgeBases"].append(kb_config)
            
            # Add IAM permissions for the knowledge base
            # Get the agent role
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
                
                # Add knowledge base permissions to the policy
                if "PolicyDocument" in policy and "Statement" in policy["PolicyDocument"]:
                    kb_statement = {
                        "Effect": "Allow",
                        "Action": [
                            "bedrock:RetrieveAndGenerate",
                            "bedrock:Retrieve"
                        ],
                        "Resource": {"Fn::Sub": f"arn:aws:bedrock:${{AWS::Region}}:${{AWS::AccountId}}:knowledge-base/{self.knowledge_base_id}"}
                    }
                    
                    # Add the statement if it doesn't already exist
                    statements = policy["PolicyDocument"]["Statement"]
                    if not any(self._is_same_kb_resource(s, self.knowledge_base_id) for s in statements):
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