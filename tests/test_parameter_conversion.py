import pytest
from bedrock_agents_sdk.utils.parameter_conversion import convert_parameters

class TestParameterConversion:
    def test_convert_string_parameters(self):
        """Test converting string parameters"""
        parameters = [
            {"name": "param1", "value": "value1", "type": "string"},
            {"name": "param2", "value": "value2", "type": "string"}
        ]
        
        result = convert_parameters(parameters)
        
        assert result == {
            "param1": "value1",
            "param2": "value2"
        }
    
    def test_convert_number_parameters(self):
        """Test converting number parameters"""
        parameters = [
            {"name": "int_param", "value": "123", "type": "number"},
            {"name": "float_param", "value": "123.45", "type": "number"}
        ]
        
        result = convert_parameters(parameters)
        
        assert result == {
            "int_param": 123,
            "float_param": 123.45
        }
        
        # Check that the types are correct
        assert isinstance(result["int_param"], int)
        assert isinstance(result["float_param"], float)
    
    def test_convert_boolean_parameters(self):
        """Test converting boolean parameters"""
        parameters = [
            {"name": "true_param1", "value": "true", "type": "boolean"},
            {"name": "true_param2", "value": "yes", "type": "boolean"},
            {"name": "true_param3", "value": "1", "type": "boolean"},
            {"name": "false_param1", "value": "false", "type": "boolean"},
            {"name": "false_param2", "value": "no", "type": "boolean"},
            {"name": "false_param3", "value": "0", "type": "boolean"}
        ]
        
        result = convert_parameters(parameters)
        
        assert result == {
            "true_param1": True,
            "true_param2": True,
            "true_param3": True,
            "false_param1": False,
            "false_param2": False,
            "false_param3": False
        }
    
    def test_convert_mixed_parameters(self):
        """Test converting mixed parameter types"""
        parameters = [
            {"name": "string_param", "value": "value", "type": "string"},
            {"name": "int_param", "value": "123", "type": "number"},
            {"name": "float_param", "value": "123.45", "type": "number"},
            {"name": "bool_param", "value": "true", "type": "boolean"}
        ]
        
        result = convert_parameters(parameters)
        
        assert result == {
            "string_param": "value",
            "int_param": 123,
            "float_param": 123.45,
            "bool_param": True
        }
    
    def test_convert_invalid_number(self):
        """Test converting an invalid number"""
        parameters = [
            {"name": "invalid_number", "value": "not_a_number", "type": "number"}
        ]
        
        result = convert_parameters(parameters)
        
        # The invalid number should be skipped
        assert result == {} 