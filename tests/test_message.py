import pytest
from bedrock_agents_sdk import Message

class TestMessage:
    def test_message_initialization(self):
        """Test that a message can be initialized"""
        message = Message(role="user", content="Hello, world!")
        
        assert message.role == "user"
        assert message.content == "Hello, world!"
    
    def test_message_from_dict(self):
        """Test that a message can be created from a dictionary"""
        message_dict = {"role": "user", "content": "Hello, world!"}
        message = Message(**message_dict)
        
        assert message.role == "user"
        assert message.content == "Hello, world!"
    
    def test_message_to_dict(self):
        """Test that a message can be converted to a dictionary"""
        message = Message(role="user", content="Hello, world!")
        message_dict = message.model_dump()
        
        assert message_dict == {"role": "user", "content": "Hello, world!"} 