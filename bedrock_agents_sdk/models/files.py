"""
File models for Bedrock Agents SDK.
"""
from typing import Dict, Any
from pydantic import BaseModel

class InputFile(BaseModel):
    """Represents a file to be sent to the agent"""
    name: str
    content: bytes
    media_type: str
    use_case: str = "CODE_INTERPRETER"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API parameters format"""
        return {
            "name": self.name,
            "source": {
                "byteContent": {
                    "data": self.content,
                    "mediaType": self.media_type
                },
                "sourceType": "BYTE_CONTENT"
            },
            "useCase": self.use_case
        }

class OutputFile:
    """Represents a file received from the agent"""
    def __init__(self, name: str, content: bytes, file_type: str):
        self.name = name
        self.content = content
        self.type = file_type
    
    @classmethod
    def from_response(cls, file_data: Dict[str, Any]) -> 'OutputFile':
        """Create an OutputFile from API response data"""
        return cls(
            name=file_data.get('name', ''),
            content=file_data.get('bytes', b''),
            file_type=file_data.get('type', '')
        )
    
    def save(self, directory: str = ".") -> str:
        """Save the file to disk"""
        import os
        path = os.path.join(directory, self.name)
        with open(path, 'wb') as f:
            f.write(self.content)
        return path 