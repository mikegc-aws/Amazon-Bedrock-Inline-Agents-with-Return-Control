"""
Message model for Bedrock Agents SDK.
"""
from pydantic import BaseModel

class Message(BaseModel):
    """Represents a message in the conversation"""
    role: str
    content: str 