import pytest
import os
import tempfile
from bedrock_agents_sdk.models.files import InputFile, OutputFile

class TestInputFile:
    def test_input_file_initialization(self):
        """Test that an input file can be initialized"""
        file = InputFile(
            name="test.txt",
            content=b"test content",
            media_type="text/plain"
        )
        
        assert file.name == "test.txt"
        assert file.content == b"test content"
        assert file.media_type == "text/plain"
        assert file.use_case == "CODE_INTERPRETER"
    
    def test_input_file_to_dict(self):
        """Test that an input file can be converted to a dictionary"""
        file = InputFile(
            name="test.txt",
            content=b"test content",
            media_type="text/plain"
        )
        
        file_dict = file.to_dict()
        
        assert file_dict["name"] == "test.txt"
        assert file_dict["source"]["byteContent"]["data"] == b"test content"
        assert file_dict["source"]["byteContent"]["mediaType"] == "text/plain"
        assert file_dict["source"]["sourceType"] == "BYTE_CONTENT"
        assert file_dict["useCase"] == "CODE_INTERPRETER"

class TestOutputFile:
    def test_output_file_initialization(self):
        """Test that an output file can be initialized"""
        file = OutputFile(
            name="test.txt",
            content=b"test content",
            file_type="text/plain"
        )
        
        assert file.name == "test.txt"
        assert file.content == b"test content"
        assert file.type == "text/plain"
    
    def test_output_file_from_response(self):
        """Test that an output file can be created from a response"""
        response_data = {
            "name": "test.txt",
            "bytes": b"test content",
            "type": "text/plain"
        }
        
        file = OutputFile.from_response(response_data)
        
        assert file.name == "test.txt"
        assert file.content == b"test content"
        assert file.type == "text/plain"
    
    def test_output_file_save(self):
        """Test that an output file can be saved to disk"""
        file = OutputFile(
            name="test.txt",
            content=b"test content",
            file_type="text/plain"
        )
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the file
            path = file.save(temp_dir)
            
            # Check that the file exists
            assert os.path.exists(path)
            
            # Check that the file has the correct content
            with open(path, "rb") as f:
                content = f.read()
                assert content == b"test content" 