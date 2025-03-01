import pytest
from bedrock_agents_sdk.plugins.base import BedrockAgentsPlugin

class CustomPlugin(BedrockAgentsPlugin):
    """A custom plugin for testing"""
    
    def __init__(self, custom_param="default"):
        self.custom_param = custom_param
        self.client = None
    
    def initialize(self, client):
        """Called when the plugin is registered with the client"""
        self.client = client
    
    def pre_invoke(self, params):
        """Called before invoke_inline_agent, can modify params"""
        params["customParam"] = self.custom_param
        return params
    
    def post_invoke(self, response):
        """Called after invoke_inline_agent, can modify response"""
        # Add a custom field to the response
        if "custom" not in response:
            response["custom"] = {}
        response["custom"]["plugin"] = "CustomPlugin"
        return response
    
    def post_process(self, result):
        """Called after processing the response, can modify the final result"""
        # Add a custom field to the result
        result["custom_data"] = self.custom_param
        return result

class TestCustomPlugin:
    def test_custom_plugin_initialization(self):
        """Test that a custom plugin can be initialized"""
        plugin = CustomPlugin(custom_param="test")
        
        assert plugin.custom_param == "test"
        assert plugin.client is None
    
    def test_custom_plugin_initialize(self):
        """Test that a custom plugin can be initialized with a client"""
        plugin = CustomPlugin(custom_param="test")
        client = "mock_client"
        
        plugin.initialize(client)
        
        assert plugin.client == "mock_client"
    
    def test_custom_plugin_pre_invoke(self):
        """Test that a custom plugin can modify parameters before invocation"""
        plugin = CustomPlugin(custom_param="test")
        
        params = {}
        result = plugin.pre_invoke(params)
        
        assert result["customParam"] == "test"
    
    def test_custom_plugin_post_invoke(self):
        """Test that a custom plugin can modify the response after invocation"""
        plugin = CustomPlugin(custom_param="test")
        
        response = {}
        result = plugin.post_invoke(response)
        
        assert "custom" in result
        assert result["custom"]["plugin"] == "CustomPlugin"
    
    def test_custom_plugin_post_process(self):
        """Test that a custom plugin can modify the final result"""
        plugin = CustomPlugin(custom_param="test")
        
        result = {}
        final_result = plugin.post_process(result)
        
        assert "custom_data" in final_result
        assert final_result["custom_data"] == "test" 