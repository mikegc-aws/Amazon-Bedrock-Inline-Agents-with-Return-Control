import pytest
from unittest.mock import MagicMock, patch
from bedrock_agents_sdk import Agent
from bedrock_agents_sdk.plugins.base import BedrockAgentsPlugin
from bedrock_agents_sdk.plugins.security import SecurityPlugin
from bedrock_agents_sdk.plugins.guardrail import GuardrailPlugin
from bedrock_agents_sdk.plugins.knowledge_base import KnowledgeBasePlugin

# Sample function for testing
def sample_function() -> dict:
    """A sample function that returns a dictionary"""
    return {"status": "success"}

# Custom plugin for testing pre_deploy
class DeploymentTestPlugin(BedrockAgentsPlugin):
    """A custom plugin for testing deployment"""
    
    def __init__(self, custom_param="default"):
        self.custom_param = custom_param
    
    def pre_deploy(self, template):
        """Add custom properties to the template"""
        if "Resources" in template and "BedrockAgent" in template["Resources"]:
            agent_props = template["Resources"]["BedrockAgent"]["Properties"]
            
            # Add custom properties to the agent
            if "CustomProperties" not in agent_props:
                agent_props["CustomProperties"] = {}
                
            agent_props["CustomProperties"]["TestProperty"] = self.custom_param
            
        return template

class TestPluginDeployment:
    def test_agent_add_plugin(self):
        """Test that plugins can be added to an agent"""
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent"
        )
        
        # Initially no plugins
        assert len(agent.plugins) == 0
        
        # Add a plugin
        plugin = DeploymentTestPlugin(custom_param="test_value")
        agent.add_plugin(plugin)
        
        # Check that the plugin was added
        assert len(agent.plugins) == 1
        assert agent.plugins[0].custom_param == "test_value"
        
        # Add another plugin
        security_plugin = SecurityPlugin(customer_encryption_key_arn="test-arn")
        agent.add_plugin(security_plugin)
        
        # Check that the plugin was added
        assert len(agent.plugins) == 2
        assert agent.plugins[1].customer_encryption_key_arn == "test-arn"
    
    def test_agent_initialization_with_plugins(self):
        """Test that an agent can be initialized with plugins"""
        plugin = DeploymentTestPlugin(custom_param="test_value")
        security_plugin = SecurityPlugin(customer_encryption_key_arn="test-arn")
        
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            plugins=[plugin, security_plugin]
        )
        
        # Check that plugins were properly added
        assert len(agent.plugins) == 2
        assert agent.plugins[0].custom_param == "test_value"
        assert agent.plugins[1].customer_encryption_key_arn == "test-arn"
    
    @patch('bedrock_agents_sdk.deployment.sam_template.SAMTemplateGenerator._create_template')
    def test_security_plugin_pre_deploy(self, mock_create_template):
        """Test that the security plugin modifies the template during deployment"""
        # Set up the mock to return a template
        mock_template = {
            "Resources": {
                "BedrockAgent": {
                    "Properties": {}
                },
                "BedrockAgentRole": {
                    "Properties": {
                        "Policies": [
                            {
                                "PolicyName": {"Fn::Sub": "BedrockAgentPolicy-${AWS::StackName}"},
                                "PolicyDocument": {
                                    "Version": "2012-10-17",
                                    "Statement": []
                                }
                            }
                        ]
                    }
                }
            }
        }
        mock_create_template.return_value = mock_template
        
        # Create an agent with a security plugin
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            plugins=[SecurityPlugin(customer_encryption_key_arn="test-arn")]
        )
        
        # Mock the deployment process
        with patch('builtins.open', MagicMock()):
            with patch('os.makedirs', MagicMock()):
                # Call deploy to trigger the template generation
                agent.deploy(output_dir="test_output")
        
        # Check that the security plugin modified the template
        agent_props = mock_template["Resources"]["BedrockAgent"]["Properties"]
        assert "customerEncryptionKeyArn" in agent_props
        assert agent_props["customerEncryptionKeyArn"] == "test-arn"
        
        # Check that the IAM permissions were added
        statements = mock_template["Resources"]["BedrockAgentRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
        assert len(statements) == 1
        assert statements[0]["Resource"] == "test-arn"
        assert "kms:Decrypt" in statements[0]["Action"]
        assert "kms:GenerateDataKey" in statements[0]["Action"]
    
    @patch('bedrock_agents_sdk.deployment.sam_template.SAMTemplateGenerator._create_template')
    def test_guardrail_plugin_pre_deploy(self, mock_create_template):
        """Test that the guardrail plugin modifies the template during deployment"""
        # Set up the mock to return a template
        mock_template = {
            "Resources": {
                "BedrockAgent": {
                    "Properties": {}
                },
                "BedrockAgentRole": {
                    "Properties": {
                        "Policies": [
                            {
                                "PolicyName": {"Fn::Sub": "BedrockAgentPolicy-${AWS::StackName}"},
                                "PolicyDocument": {
                                    "Version": "2012-10-17",
                                    "Statement": []
                                }
                            }
                        ]
                    }
                }
            }
        }
        mock_create_template.return_value = mock_template
        
        # Create an agent with a guardrail plugin
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            plugins=[GuardrailPlugin(guardrail_id="test-id", guardrail_version="1.0")]
        )
        
        # Mock the deployment process
        with patch('builtins.open', MagicMock()):
            with patch('os.makedirs', MagicMock()):
                # Call deploy to trigger the template generation
                agent.deploy(output_dir="test_output")
        
        # Check that the guardrail plugin modified the template
        agent_props = mock_template["Resources"]["BedrockAgent"]["Properties"]
        assert "guardrailConfiguration" in agent_props
        assert agent_props["guardrailConfiguration"]["guardrailIdentifier"] == "test-id"
        assert agent_props["guardrailConfiguration"]["guardrailVersion"] == "1.0"
        
        # Check that the IAM permissions were added
        statements = mock_template["Resources"]["BedrockAgentRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
        assert len(statements) == 1
        assert "bedrock:ApplyGuardrail" in statements[0]["Action"]
        assert statements[0]["Resource"]["Fn::Sub"].endswith("guardrail/test-id")
    
    @patch('bedrock_agents_sdk.deployment.sam_template.SAMTemplateGenerator._create_template')
    def test_knowledge_base_plugin_pre_deploy(self, mock_create_template):
        """Test that the knowledge base plugin modifies the template during deployment"""
        # Set up the mock to return a template
        mock_template = {
            "Resources": {
                "BedrockAgent": {
                    "Properties": {}
                },
                "BedrockAgentRole": {
                    "Properties": {
                        "Policies": [
                            {
                                "PolicyName": {"Fn::Sub": "BedrockAgentPolicy-${AWS::StackName}"},
                                "PolicyDocument": {
                                    "Version": "2012-10-17",
                                    "Statement": []
                                }
                            }
                        ]
                    }
                }
            }
        }
        mock_create_template.return_value = mock_template
        
        # Create an agent with a knowledge base plugin
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            plugins=[KnowledgeBasePlugin(
                knowledge_base_id="test-kb-id",
                description="Test KB",
                retrieval_config={"maxResults": 5}
            )]
        )
        
        # Mock the deployment process
        with patch('builtins.open', MagicMock()):
            with patch('os.makedirs', MagicMock()):
                # Call deploy to trigger the template generation
                agent.deploy(output_dir="test_output")
        
        # Check that the knowledge base plugin modified the template
        agent_props = mock_template["Resources"]["BedrockAgent"]["Properties"]
        assert "knowledgeBases" in agent_props
        assert len(agent_props["knowledgeBases"]) == 1
        assert agent_props["knowledgeBases"][0]["knowledgeBaseId"] == "test-kb-id"
        assert agent_props["knowledgeBases"][0]["description"] == "Test KB"
        assert agent_props["knowledgeBases"][0]["retrievalConfiguration"]["maxResults"] == 5
        
        # Check that the IAM permissions were added
        statements = mock_template["Resources"]["BedrockAgentRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
        assert len(statements) == 1
        assert "bedrock:RetrieveAndGenerate" in statements[0]["Action"]
        assert "bedrock:Retrieve" in statements[0]["Action"]
        assert statements[0]["Resource"]["Fn::Sub"].endswith("knowledge-base/test-kb-id")
    
    @patch('bedrock_agents_sdk.deployment.sam_template.SAMTemplateGenerator._create_template')
    def test_custom_plugin_pre_deploy(self, mock_create_template):
        """Test that a custom plugin modifies the template during deployment"""
        # Set up the mock to return a template
        mock_template = {
            "Resources": {
                "BedrockAgent": {
                    "Properties": {}
                }
            }
        }
        mock_create_template.return_value = mock_template
        
        # Create an agent with a custom plugin
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            plugins=[DeploymentTestPlugin(custom_param="test_value")]
        )
        
        # Mock the deployment process
        with patch('builtins.open', MagicMock()):
            with patch('os.makedirs', MagicMock()):
                # Call deploy to trigger the template generation
                agent.deploy(output_dir="test_output")
        
        # Check that the custom plugin modified the template
        agent_props = mock_template["Resources"]["BedrockAgent"]["Properties"]
        assert "CustomProperties" in agent_props
        assert agent_props["CustomProperties"]["TestProperty"] == "test_value"
    
    @patch('bedrock_agents_sdk.deployment.sam_template.SAMTemplateGenerator._create_template')
    def test_multiple_plugins_pre_deploy(self, mock_create_template):
        """Test that multiple plugins modify the template during deployment"""
        # Set up the mock to return a template
        mock_template = {
            "Resources": {
                "BedrockAgent": {
                    "Properties": {}
                },
                "BedrockAgentRole": {
                    "Properties": {
                        "Policies": [
                            {
                                "PolicyName": {"Fn::Sub": "BedrockAgentPolicy-${AWS::StackName}"},
                                "PolicyDocument": {
                                    "Version": "2012-10-17",
                                    "Statement": []
                                }
                            }
                        ]
                    }
                }
            }
        }
        mock_create_template.return_value = mock_template
        
        # Create an agent with multiple plugins
        agent = Agent(
            name="TestAgent",
            model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            instructions="You are a test agent",
            plugins=[
                DeploymentTestPlugin(custom_param="test_value"),
                SecurityPlugin(customer_encryption_key_arn="test-arn"),
                GuardrailPlugin(guardrail_id="test-id")
            ]
        )
        
        # Mock the deployment process
        with patch('builtins.open', MagicMock()):
            with patch('os.makedirs', MagicMock()):
                # Call deploy to trigger the template generation
                agent.deploy(output_dir="test_output")
        
        # Check that all plugins modified the template
        agent_props = mock_template["Resources"]["BedrockAgent"]["Properties"]
        
        # Custom plugin
        assert "CustomProperties" in agent_props
        assert agent_props["CustomProperties"]["TestProperty"] == "test_value"
        
        # Security plugin
        assert "customerEncryptionKeyArn" in agent_props
        assert agent_props["customerEncryptionKeyArn"] == "test-arn"
        
        # Guardrail plugin
        assert "guardrailConfiguration" in agent_props
        assert agent_props["guardrailConfiguration"]["guardrailIdentifier"] == "test-id"
        
        # Check that the IAM permissions were added for both plugins
        statements = mock_template["Resources"]["BedrockAgentRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
        assert len(statements) == 2  # One for security, one for guardrail 