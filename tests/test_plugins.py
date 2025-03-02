import pytest
from bedrock_agents_sdk.plugins.base import BedrockAgentsPlugin
from bedrock_agents_sdk.plugins.security import SecurityPlugin
from bedrock_agents_sdk.plugins.guardrail import GuardrailPlugin
from bedrock_agents_sdk.plugins.knowledge_base import KnowledgeBasePlugin

class TestSecurityPlugin:
    def test_security_plugin_initialization(self):
        """Test that a security plugin can be initialized"""
        plugin = SecurityPlugin(customer_encryption_key_arn="test-arn")
        
        assert plugin.customer_encryption_key_arn == "test-arn"
    
    def test_security_plugin_pre_invoke(self):
        """Test that a security plugin adds the customer encryption key ARN to the parameters"""
        plugin = SecurityPlugin(customer_encryption_key_arn="test-arn")
        
        params = {}
        result = plugin.pre_invoke(params)
        
        assert result["customerEncryptionKeyArn"] == "test-arn"
    
    def test_security_plugin_pre_invoke_no_arn(self):
        """Test that a security plugin doesn't modify the parameters if no ARN is provided"""
        plugin = SecurityPlugin()
        
        params = {}
        result = plugin.pre_invoke(params)
        
        assert result == {}

class TestGuardrailPlugin:
    def test_guardrail_plugin_initialization(self):
        """Test that a guardrail plugin can be initialized"""
        plugin = GuardrailPlugin(guardrail_id="test-id", guardrail_version="1.0")
        
        assert plugin.guardrail_id == "test-id"
        assert plugin.guardrail_version == "1.0"
    
    def test_guardrail_plugin_pre_invoke(self):
        """Test that a guardrail plugin adds the guardrail configuration to the parameters"""
        plugin = GuardrailPlugin(guardrail_id="test-id", guardrail_version="1.0")
        
        params = {}
        result = plugin.pre_invoke(params)
        
        assert "guardrailConfiguration" in result
        assert result["guardrailConfiguration"]["guardrailIdentifier"] == "test-id"
        assert result["guardrailConfiguration"]["guardrailVersion"] == "1.0"
    
    def test_guardrail_plugin_pre_invoke_no_version(self):
        """Test that a guardrail plugin doesn't add the version if not provided"""
        plugin = GuardrailPlugin(guardrail_id="test-id")
        
        params = {}
        result = plugin.pre_invoke(params)
        
        assert "guardrailConfiguration" in result
        assert result["guardrailConfiguration"]["guardrailIdentifier"] == "test-id"
        assert "guardrailVersion" not in result["guardrailConfiguration"]

class TestKnowledgeBasePlugin:
    def test_knowledge_base_plugin_initialization(self):
        """Test that a knowledge base plugin can be initialized"""
        plugin = KnowledgeBasePlugin(
            knowledge_base_id="test-id",
            description="test description",
            retrieval_config={"maxResults": 5}
        )
        
        assert plugin.knowledge_base_id == "test-id"
        assert plugin.description == "test description"
        assert plugin.retrieval_config == {"maxResults": 5}
    
    def test_knowledge_base_plugin_pre_invoke(self):
        """Test that a knowledge base plugin adds the knowledge base configuration to the parameters"""
        plugin = KnowledgeBasePlugin(
            knowledge_base_id="test-id",
            description="test description",
            retrieval_config={"maxResults": 5}
        )
        
        params = {}
        result = plugin.pre_invoke(params)
        
        assert "knowledgeBases" in result
        assert len(result["knowledgeBases"]) == 1
        assert result["knowledgeBases"][0]["knowledgeBaseId"] == "test-id"
        assert result["knowledgeBases"][0]["description"] == "test description"
        assert result["knowledgeBases"][0]["retrievalConfiguration"] == {"maxResults": 5}
    
    def test_knowledge_base_plugin_pre_invoke_minimal(self):
        """Test that a knowledge base plugin works with minimal configuration"""
        plugin = KnowledgeBasePlugin(knowledge_base_id="test-id")
        
        params = {}
        result = plugin.pre_invoke(params)
        
        assert "knowledgeBases" in result
        assert len(result["knowledgeBases"]) == 1
        assert result["knowledgeBases"][0]["knowledgeBaseId"] == "test-id"
        assert "description" not in result["knowledgeBases"][0]
        assert "retrievalConfiguration" not in result["knowledgeBases"][0]
    
    def test_knowledge_base_plugin_pre_invoke_existing(self):
        """Test that a knowledge base plugin appends to existing knowledge bases"""
        plugin = KnowledgeBasePlugin(knowledge_base_id="test-id-2")
        
        params = {
            "knowledgeBases": [
                {"knowledgeBaseId": "test-id-1"}
            ]
        }
        result = plugin.pre_invoke(params)
        
        assert "knowledgeBases" in result
        assert len(result["knowledgeBases"]) == 2
        assert result["knowledgeBases"][0]["knowledgeBaseId"] == "test-id-1"
        assert result["knowledgeBases"][1]["knowledgeBaseId"] == "test-id-2" 