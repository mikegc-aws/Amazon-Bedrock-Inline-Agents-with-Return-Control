"""
SAM template generation for Bedrock Agents SDK.
"""
import os
import yaml
import inspect
import textwrap
import ast
import re
from typing import Dict, Any, List, Optional, Union, Callable, TYPE_CHECKING, Set
from pathlib import Path

from bedrock_agents_sdk.models.function import Function

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from bedrock_agents_sdk.models.agent import Agent

class SAMTemplateGenerator:
    """Generates a SAM template for deploying a Bedrock Agent"""
    
    def __init__(self, agent: "Agent", output_dir: str = None):
        """
        Initialize the SAM template generator
        
        Args:
            agent: The agent to generate a template for
            output_dir: The directory to output the SAM template and code to.
                        If None, defaults to "./[agent_name]_deployment"
        """
        self.agent = agent
        
        # If output_dir is not provided, use agent name to create a default path
        if output_dir is None:
            # Create a safe name for the directory (lowercase, alphanumeric with underscores)
            safe_name = ''.join(c.lower() if c.isalnum() else '_' for c in agent.name)
            safe_name = safe_name.strip('_')  # Remove leading/trailing underscores
            output_dir = f"./{safe_name}_deployment"
        
        self.output_dir = output_dir
        self.lambda_dir = os.path.join(output_dir, "lambda_function")
        # Dictionary to store custom dependencies provided by the developer
        self.custom_dependencies = {}
        
    def generate(self, 
                 foundation_model: Optional[str] = None,
                 parameters: Optional[Dict[str, Dict[str, str]]] = None,
                 description: Optional[str] = None) -> str:
        """
        Generate the SAM template and supporting files
        
        Args:
            foundation_model: The foundation model to use (defaults to the agent's model)
            parameters: Additional parameters to add to the template
            description: Description for the SAM template
            
        Returns:
            str: Path to the generated template file
        """
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.lambda_dir, exist_ok=True)
        
        # Generate the SAM template
        template = self._create_template(
            foundation_model=foundation_model or self.agent.model,
            parameters=parameters,
            description=description or f"SAM template for {self.agent.name}"
        )
        
        # Apply plugins to the template
        for plugin in self.agent.plugins:
            template = plugin.pre_deploy(template)
        
        # Write the template to a file
        template_path = os.path.join(self.output_dir, "template.yaml")
        with open(template_path, "w") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)
        
        # Generate the Lambda function code
        self._generate_lambda_code()
        
        # Generate requirements.txt
        self._generate_requirements()
        
        # Generate README
        self._generate_readme()
        
        # Print deployment instructions
        safe_name = ''.join(c.lower() if c.isalnum() else '-' for c in self.agent.name)
        safe_name = safe_name.strip('-')  # Remove leading/trailing hyphens
        print(f"\nDeployment files generated for {self.agent.name}!")
        print(f"SAM template: {template_path}")
        print("\nTo deploy the agent to AWS, run the following commands:")
        print(f"  cd {os.path.basename(self.output_dir)}")
        print("  sam build")
        print(f"  sam deploy --guided --capabilities CAPABILITY_NAMED_IAM --stack-name {safe_name}-agent")
        
        return template_path
    
    def _create_template(self, 
                         foundation_model: str, 
                         parameters: Optional[Dict[str, Dict[str, str]]] = None,
                         description: str = "SAM template for Bedrock Agent") -> Dict[str, Any]:
        """Create the SAM template dictionary"""
        # Remove region prefix from model ID for IAM policy
        model_for_policy = foundation_model
        if model_for_policy.startswith("us.") or model_for_policy.startswith("eu."):
            model_for_policy = model_for_policy.split(".", 1)[1]
            
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Transform": "AWS::Serverless-2016-10-31",
            "Description": description,
            "Parameters": {
                "FoundationModel": {
                    "Type": "String",
                    "Description": "Foundation model used by the agent",
                    "Default": foundation_model
                },
                "ModelForPolicy": {
                    "Type": "String",
                    "Description": "Foundation model ID used in IAM policy (without region prefix)",
                    "Default": model_for_policy
                }
            },
            "Globals": {
                "Function": {
                    "Timeout": 30,
                    "MemorySize": 128
                }
            },
            "Resources": {
                # The Bedrock Agent
                "BedrockAgent": {
                    "Type": "AWS::Bedrock::Agent",
                    "Properties": {
                        "ActionGroups": self._generate_action_groups(),
                        "AgentName": self.agent.name,
                        "AgentResourceRoleArn": {"Fn::GetAtt": ["BedrockAgentRole", "Arn"]},
                        "AutoPrepare": True,
                        "Description": f"Agent for {self.agent.name}",
                        "FoundationModel": {"Ref": "FoundationModel"},
                        "IdleSessionTTLInSeconds": 1800,
                        "Instruction": self.agent.instructions
                    }
                },
                # IAM role for the Bedrock Agent
                "BedrockAgentRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "RoleName": {"Fn::Sub": "AmazonBedrockExecutionRoleForAgents_${AWS::StackName}"},
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Principal": {"Service": "bedrock.amazonaws.com"},
                                "Action": "sts:AssumeRole"
                            }]
                        },
                        "Policies": [{
                            "PolicyName": {"Fn::Sub": "BedrockAgentFunctionPolicy-${AWS::StackName}"},
                            "PolicyDocument": {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": "bedrock:InvokeModel",
                                        "Resource": {"Fn::Sub": "arn:aws:bedrock:${AWS::Region}::foundation-model/${ModelForPolicy}"}
                                    }
                                ]
                            }
                        }]
                    }
                },
                # Alias for the Bedrock Agent
                "BedrockAgentAlias": {
                    "Type": "AWS::Bedrock::AgentAlias",
                    "Properties": {
                        "AgentAliasName": "AgentAlias",
                        "AgentId": {"Fn::GetAtt": ["BedrockAgent", "AgentId"]},
                        "Description": "Created by SAM template"
                    }
                }
            },
            "Outputs": {
                "BedrockAgent": {
                    "Description": "Bedrock Agent ARN",
                    "Value": {"Ref": "BedrockAgent"}
                }
            }
        }
        
        # Group functions by action group
        action_group_map = {}
        for func in self.agent.functions:
            group_name = func.action_group or "DefaultActions"
            if group_name not in action_group_map:
                action_group_map[group_name] = []
            action_group_map[group_name].append(func)
        
        # Create Lambda functions and permissions for each action group
        for group_name, functions in action_group_map.items():
            # Create a safe name for CloudFormation resources
            safe_group_name = ''.join(c if c.isalnum() else '' for c in group_name)
            
            # Add Lambda function for this action group
            lambda_function_name = f"{safe_group_name}Function"
            template["Resources"][lambda_function_name] = {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "CodeUri": f"lambda_function/{safe_group_name.lower()}/",
                    "Handler": "app.lambda_handler",
                    "Runtime": "python3.9",
                    "Architectures": ["x86_64"],
                    "Role": {"Fn::GetAtt": [f"{safe_group_name}FunctionRole", "Arn"]}
                }
            }
            
            # Add IAM role for the Lambda function
            template["Resources"][f"{safe_group_name}FunctionRole"] = {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "RoleName": {"Fn::Sub": f"{safe_group_name}FunctionRole-${{AWS::StackName}}"},
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Effect": "Allow",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Action": "sts:AssumeRole"
                        }]
                    },
                    "Policies": [{
                        "PolicyName": {"Fn::Sub": f"Lambda{safe_group_name}FunctionPolicy-${{AWS::StackName}}"},
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Action": [
                                    "logs:CreateLogGroup",
                                    "logs:CreateLogStream",
                                    "logs:PutLogEvents"
                                ],
                                "Resource": "arn:aws:logs:*:*:*"
                            }]
                        }
                    }]
                }
            }
            
            # Add permission for Bedrock to invoke the Lambda function
            template["Resources"][f"{safe_group_name}FunctionInvocationPermission"] = {
                "Type": "AWS::Lambda::Permission",
                "Properties": {
                    "FunctionName": {"Fn::GetAtt": [lambda_function_name, "Arn"]},
                    "Action": "lambda:InvokeFunction",
                    "Principal": "bedrock.amazonaws.com",
                    "SourceAccount": {"Ref": "AWS::AccountId"},
                    "SourceArn": {"Fn::GetAtt": ["BedrockAgent", "AgentArn"]}
                }
            }
            
            # Add Lambda ARN to Bedrock Agent Role policy
            lambda_invoke_statement = {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": {"Fn::GetAtt": [lambda_function_name, "Arn"]}
            }
            
            # Add the statement to the existing policy
            template["Resources"]["BedrockAgentRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"].append(
                lambda_invoke_statement
            )
        
        # Add user-provided parameters
        if parameters:
            template["Parameters"].update(parameters)
            
        return template
    
    def _generate_action_groups(self) -> List[Dict[str, Any]]:
        """Generate the action groups configuration for the SAM template"""
        action_groups = []
        
        # Group functions by action group
        action_group_map = {}
        
        for func in self.agent.functions:
            # Determine action group name
            group_name = func.action_group or "DefaultActions"
            
            # Create action group if it doesn't exist
            if group_name not in action_group_map:
                action_group_map[group_name] = []
            
            # Add function to action group
            action_group_map[group_name].append(func)
        
        # Create action groups
        for group_name, functions in action_group_map.items():
            # Create a safe name for CloudFormation resources
            safe_group_name = ''.join(c if c.isalnum() else '' for c in group_name)
            lambda_function_name = f"{safe_group_name}Function"
            
            action_group = {
                "ActionGroupName": group_name,
                "ActionGroupExecutor": {
                    "Lambda": {"Fn::GetAtt": [lambda_function_name, "Arn"]}
                },
                "ActionGroupState": "ENABLED",
                "Description": f"Functions related to {group_name.replace('Actions', '')}",
                "FunctionSchema": {
                    "Functions": [self._generate_function_schema(func) for func in functions]
                }
            }
            
            action_groups.append(action_group)
        
        # Add code interpreter action group if enabled
        if self.agent.enable_code_interpreter:
            code_interpreter_action = {
                'ActionGroupName': 'CodeInterpreterAction',
                'ParentActionGroupSignature': 'AMAZON.CodeInterpreter'
            }
            action_groups.append(code_interpreter_action)
        
        # Add user input action group
        user_input_action = {
            'ActionGroupName': 'UserInputAction',
            'ParentActionGroupSignature': 'AMAZON.UserInput'
        }
        action_groups.append(user_input_action)
        
        return action_groups
    
    def _generate_function_schema(self, func: Function) -> Dict[str, Any]:
        """Generate the function schema for a function"""
        # Get the function signature
        signature = inspect.signature(func.function)
        
        # Create the function definition
        function_def = {
            "Name": func.name,
            "Description": func.description
        }
        
        # Add parameters if they exist
        parameters = {}
        
        # Extract parameter descriptions from docstring
        from bedrock_agents_sdk.utils.parameter_extraction import extract_parameter_info
        param_info = extract_parameter_info(func.function)
        
        for param_name, param in signature.parameters.items():
            # Skip return annotation
            if param_name == "return":
                continue
                
            # Get parameter type
            param_type = "string"  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list or param.annotation == dict:
                    param_type = "object"
            
            # Get description from extracted parameter info if available
            param_desc = f"Parameter {param_name}"
            if param_name in param_info:
                param_desc = param_info[param_name]["description"]
            
            # Add parameter to the parameters dictionary
            parameters[param_name] = {
                "Description": param_desc,
                "Required": param.default == inspect.Parameter.empty,
                "Type": param_type
            }
        
        # Add parameters to the function definition if they exist
        if parameters:
            function_def["Parameters"] = parameters
            
        return function_def
    
    def _detect_imports(self, function: Callable) -> Set[str]:
        """
        Detect imports in a function's source code
        
        Args:
            function: The function to analyze
            
        Returns:
            Set of imported module names
        """
        # Get the source code of the function
        source = inspect.getsource(function)
        
        # Parse the source code into an AST
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # If there's a syntax error, return an empty set
            return set()
        
        # Extract imports from the AST
        imports = set()
        for node in ast.walk(tree):
            # Handle 'import x' statements
            if isinstance(node, ast.Import):
                for name in node.names:
                    # Get the top-level module name (e.g., 'pandas' from 'pandas.DataFrame')
                    module_name = name.name.split('.')[0]
                    imports.add(module_name)
            
            # Handle 'from x import y' statements
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get the top-level module name
                    module_name = node.module.split('.')[0]
                    imports.add(module_name)
        
        # Filter out standard library modules
        # This is a simplified approach - a more comprehensive solution would use importlib.util.find_spec
        std_lib_modules = {
            'os', 'sys', 'time', 'datetime', 'json', 'math', 'random', 
            're', 'collections', 'itertools', 'functools', 'logging',
            'io', 'tempfile', 'pathlib', 'uuid', 'hashlib', 'base64',
            'typing', 'enum', 'abc', 'copy', 'inspect', 'traceback'
        }
        
        # Return only non-standard library imports
        return imports - std_lib_modules
    
    def add_custom_dependency(self, action_group: str, dependency: str, version: Optional[str] = None):
        """
        Add a custom dependency for a specific action group
        
        Args:
            action_group: The action group to add the dependency to
            dependency: The name of the dependency
            version: Optional version constraint (e.g., ">=1.0.0")
        """
        if action_group not in self.custom_dependencies:
            self.custom_dependencies[action_group] = {}
        
        self.custom_dependencies[action_group][dependency] = version
    
    def _generate_requirements(self):
        """Generate the requirements.txt file"""
        # Group functions by action group
        action_group_map = {}
        for func in self.agent.functions:
            group_name = func.action_group or "DefaultActions"
            if group_name not in action_group_map:
                action_group_map[group_name] = []
            action_group_map[group_name].append(func)
        
        # Basic requirements for all Lambda functions
        base_requirements = [
            "boto3>=1.28.0",
            "pydantic>=2.0.0"
        ]
        
        # Generate requirements.txt for each action group
        for group_name, functions in action_group_map.items():
            # Create a safe name for the Lambda function directory
            safe_group_name = ''.join(c if c.isalnum() else '' for c in group_name)
            lambda_dir = os.path.join(self.lambda_dir, safe_group_name.lower())
            
            # Detect imports from all functions in this action group
            detected_imports = set()
            for func in functions:
                detected_imports.update(self._detect_imports(func.function))
            
            # Convert detected imports to requirements
            detected_requirements = []
            for module_name in detected_imports:
                detected_requirements.append(f"{module_name}")
            
            # Add custom dependencies for this action group
            custom_requirements = []
            if group_name in self.custom_dependencies:
                for dep, version in self.custom_dependencies[group_name].items():
                    if version:
                        custom_requirements.append(f"{dep}{version}")
                    else:
                        custom_requirements.append(dep)
            
            # Combine all requirements
            all_requirements = base_requirements + detected_requirements + custom_requirements
            
            # Remove duplicates while preserving order
            unique_requirements = []
            seen = set()
            for req in all_requirements:
                # Extract package name (without version)
                package_name = re.split(r'[<>=]', req)[0].strip()
                if package_name not in seen:
                    seen.add(package_name)
                    unique_requirements.append(req)
            
            # Create requirements.txt for this action group
            requirements_path = os.path.join(lambda_dir, "requirements.txt")
            
            # Write the requirements file
            with open(requirements_path, "w") as f:
                f.write("\n".join(unique_requirements))
    
    def _generate_lambda_code(self):
        """Generate the Lambda function code for each action group"""
        # Group functions by action group
        action_group_map = {}
        for func in self.agent.functions:
            group_name = func.action_group or "DefaultActions"
            if group_name not in action_group_map:
                action_group_map[group_name] = []
            action_group_map[group_name].append(func)
        
        # Generate Lambda function code for each action group
        for group_name, functions in action_group_map.items():
            # Create a safe name for the Lambda function directory
            safe_group_name = ''.join(c if c.isalnum() else '' for c in group_name)
            lambda_dir = os.path.join(self.lambda_dir, safe_group_name.lower())
            os.makedirs(lambda_dir, exist_ok=True)
            
            # Create app.py for this action group
            app_py_path = os.path.join(lambda_dir, "app.py")
            
            # Detect all imports from functions in this action group
            all_imports = set()
            for func in functions:
                all_imports.update(self._detect_imports(func.function))
            
            with open(app_py_path, "w") as f:
                # Write imports and setup
                f.write('"""\n')
                f.write('Lambda function for handling Bedrock Agent requests.\n')
                f.write('Generated by Bedrock Agents SDK.\n')
                f.write('"""\n')
                f.write('import json\n')
                f.write('import logging\n')
                f.write('import datetime\n')
                f.write('from typing import Dict, List, Any, Optional, Union\n')
                
                # Add detected imports
                for module in sorted(all_imports):
                    f.write(f'import {module}\n')
                
                f.write('\n')
                f.write('# Configure logging\n')
                f.write('logger = logging.getLogger()\n')
                f.write('logger.setLevel(logging.INFO)\n')
                f.write('\n')
                f.write('# Function implementations\n')
                
                # Add function implementations for this action group
                for func in functions:
                    # Get the function source code
                    source = inspect.getsource(func.function)
                    f.write('\n')
                    f.write(source)
                    f.write('\n')
                
                # Add parameter extraction helper function
                f.write('def extract_parameter_value(parameters, param_name, default=None):\n')
                f.write('    """\n')
                f.write('    Extract a parameter value from the parameters list or dictionary\n')
                f.write('    \n')
                f.write('    Args:\n')
                f.write('        parameters: List of parameter dictionaries or a dictionary\n')
                f.write('        param_name: Name of the parameter to extract\n')
                f.write('        default: Default value if parameter is not found\n')
                f.write('        \n')
                f.write('    Returns:\n')
                f.write('        The parameter value or default if not found\n')
                f.write('    """\n')
                f.write('    if isinstance(parameters, list):\n')
                f.write('        # Parameters is a list of dictionaries\n')
                f.write('        for param in parameters:\n')
                f.write('            if isinstance(param, dict) and param.get("name") == param_name:\n')
                f.write('                return param.get("value", default)\n')
                f.write('    elif isinstance(parameters, dict):\n')
                f.write('        # Parameters is a dictionary\n')
                f.write('        return parameters.get(param_name, default)\n')
                f.write('    \n')
                f.write('    # If we get here, parameter was not found\n')
                f.write('    return default\n')
                f.write('\n')
                
                # Add the Lambda handler
                f.write('def lambda_handler(event, context):\n')
                f.write('    """\n')
                f.write('    Lambda function handler for Bedrock Agent requests\n')
                f.write('    """\n')
                f.write('    logger.info("Received event: %s", json.dumps(event))\n')
                f.write('    \n')
                f.write('    try:\n')
                f.write('        # Extract information from the event\n')
                f.write('        message_version = event.get("messageVersion", "1.0")\n')
                f.write('        function_name = event.get("function", "")\n')
                f.write('        action_group = event.get("actionGroup", "")\n')
                f.write('        \n')
                f.write('        # Get parameters from the event if available\n')
                f.write('        parameters = event.get("parameters", [])\n')
                f.write('        logger.info(f"Parameters received: {parameters}")\n')
                f.write('        \n')
                f.write('        # Call the appropriate function based on the function name\n')
                
                # Add function dispatch logic for this action group only
                for func in functions:
                    f.write(f'        if function_name == "{func.name}":\n')
                    
                    # Get the function signature
                    signature = inspect.signature(func.function)
                    param_list = []
                    
                    # Build the parameter list with proper extraction
                    for param_name, param in signature.parameters.items():
                        # Handle different parameter types
                        if param.annotation == int:
                            # For integer parameters, convert string to int
                            f.write(f'            {param_name}_str = extract_parameter_value(parameters, "{param_name}", "{param.default if param.default != inspect.Parameter.empty else 0}")\n')
                            f.write(f'            try:\n')
                            f.write(f'                {param_name} = int({param_name}_str)\n')
                            f.write(f'            except (ValueError, TypeError):\n')
                            f.write(f'                {param_name} = {param.default if param.default != inspect.Parameter.empty else 0}\n')
                            param_list.append(param_name)
                        elif param.annotation == float:
                            # For float parameters, convert string to float
                            f.write(f'            {param_name}_str = extract_parameter_value(parameters, "{param_name}", "{param.default if param.default != inspect.Parameter.empty else 0.0}")\n')
                            f.write(f'            try:\n')
                            f.write(f'                {param_name} = float({param_name}_str)\n')
                            f.write(f'            except (ValueError, TypeError):\n')
                            f.write(f'                {param_name} = {param.default if param.default != inspect.Parameter.empty else 0.0}\n')
                            param_list.append(param_name)
                        elif param.annotation == bool:
                            # For boolean parameters, convert string to bool
                            f.write(f'            {param_name}_str = extract_parameter_value(parameters, "{param_name}", "{str(param.default).lower() if param.default != inspect.Parameter.empty else "false"}")\n')
                            f.write(f'            {param_name} = {param_name}_str.lower() in ["true", "yes", "1", "t", "y"]\n')
                            param_list.append(param_name)
                        else:
                            # For string and other parameters, use as is
                            default_value = f'"{param.default}"' if param.default != inspect.Parameter.empty else '""'
                            f.write(f'            {param_name} = extract_parameter_value(parameters, "{param_name}", {default_value})\n')
                            param_list.append(param_name)
                    
                    # Call the function with the parameters
                    params_str = ", ".join([f'{param_name}={param_name}' for param_name in param_list])
                    f.write(f'            logger.info(f"Calling {func.name} with {params_str}")\n')
                    f.write(f'            output_from_logic = {func.name}({params_str})\n')
                    f.write('            \n')
                    f.write('            # Format the response\n')
                    f.write('            response_body = {\n')
                    f.write('                "TEXT": {\n')
                    f.write('                    "body": json.dumps(output_from_logic)\n')
                    f.write('                }\n')
                    f.write('            }\n')
                    f.write('            \n')
                    f.write('            action_response = {\n')
                    f.write('                "actionGroup": action_group,\n')
                    f.write('                "function": function_name,\n')
                    f.write('                "functionResponse": {\n')
                    f.write('                    "responseBody": response_body\n')
                    f.write('                }\n')
                    f.write('            }\n')
                    f.write('            \n')
                    f.write('            function_response = {\n')
                    f.write('                "response": action_response,\n')
                    f.write('                "messageVersion": message_version\n')
                    f.write('            }\n')
                    f.write('            \n')
                    f.write('            return function_response\n')
                
                # Add error handling
                f.write('        # If we get here, the function was not found\n')
                f.write('        logger.error("Unknown function: %s", function_name)\n')
                f.write('        error_message = f"Unknown function: {function_name}"\n')
                f.write('        \n')
                f.write('        response_body = {\n')
                f.write('            "TEXT": {\n')
                f.write('                "body": json.dumps({"error": error_message})\n')
                f.write('            }\n')
                f.write('        }\n')
                f.write('        \n')
                f.write('        action_response = {\n')
                f.write('            "actionGroup": action_group,\n')
                f.write('            "function": function_name,\n')
                f.write('            "functionResponse": {\n')
                f.write('                "responseBody": response_body\n')
                f.write('            }\n')
                f.write('        }\n')
                f.write('        \n')
                f.write('        function_response = {\n')
                f.write('            "response": action_response,\n')
                f.write('            "messageVersion": message_version\n')
                f.write('        }\n')
                f.write('        \n')
                f.write('        return function_response\n')
                f.write('        \n')
                f.write('    except Exception as e:\n')
                f.write('        logger.error("Error processing request: %s", str(e))\n')
                f.write('        error_message = str(e)\n')
                f.write('        \n')
                f.write('        # Extract action group and function name from event if available\n')
                f.write('        action_group = event.get("actionGroup", "")\n')
                f.write('        function_name = event.get("function", "")\n')
                f.write('        message_version = event.get("messageVersion", "1.0")\n')
                f.write('        \n')
                f.write('        response_body = {\n')
                f.write('            "TEXT": {\n')
                f.write('                "body": json.dumps({"error": error_message})\n')
                f.write('            }\n')
                f.write('        }\n')
                f.write('        \n')
                f.write('        action_response = {\n')
                f.write('            "actionGroup": action_group,\n')
                f.write('            "function": function_name,\n')
                f.write('            "functionResponse": {\n')
                f.write('                "responseBody": response_body\n')
                f.write('            }\n')
                f.write('        }\n')
                f.write('        \n')
                f.write('        function_response = {\n')
                f.write('            "response": action_response,\n')
                f.write('            "messageVersion": message_version\n')
                f.write('        }\n')
                f.write('        \n')
                f.write('        return function_response\n')
    
    def _generate_readme(self):
        """Generate a README file for the deployment"""
        readme_path = os.path.join(self.output_dir, "README.md")
        
        # Create a safe name for the stack (lowercase, alphanumeric with hyphens)
        safe_stack_name = ''.join(c.lower() if c.isalnum() else '-' for c in self.agent.name)
        safe_stack_name = safe_stack_name.strip('-')  # Remove leading/trailing hyphens
        
        with open(readme_path, "w") as f:
            f.write(f"""# {self.agent.name} Deployment

This directory contains the AWS SAM template and supporting files for deploying the {self.agent.name} agent to AWS Bedrock.

## Deployment Instructions

1. Install the AWS SAM CLI if you haven't already:
   ```
   pip install aws-sam-cli
   ```

2. Build the SAM application:
   ```
   sam build
   ```

3. Deploy the SAM application:
   ```
   sam deploy --guided --capabilities CAPABILITY_NAMED_IAM --stack-name {safe_stack_name}-agent
   ```
   
   Note: The `CAPABILITY_NAMED_IAM` capability is required because this template creates named IAM resources.

4. Follow the prompts to complete the deployment.

## Resources Created

- Lambda function for handling agent requests
- IAM roles for the Lambda function and Bedrock Agent
- Bedrock Agent with action groups
- Bedrock Agent Alias

## Customization

You can customize the deployment by editing the `template.yaml` file.
""") 