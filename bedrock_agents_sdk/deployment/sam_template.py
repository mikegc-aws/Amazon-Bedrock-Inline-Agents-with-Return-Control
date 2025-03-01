"""
SAM template generation for Bedrock Agents SDK.
"""
import os
import yaml
import inspect
import textwrap
from typing import Dict, Any, List, Optional, Union, Callable, TYPE_CHECKING
from pathlib import Path

from bedrock_agents_sdk.models.function import Function

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from bedrock_agents_sdk.models.agent import Agent

class SAMTemplateGenerator:
    """Generates a SAM template for deploying a Bedrock Agent"""
    
    def __init__(self, agent: "Agent", output_dir: str = "./deployment"):
        """
        Initialize the SAM template generator
        
        Args:
            agent: The agent to generate a template for
            output_dir: The directory to output the SAM template and code to
        """
        self.agent = agent
        self.output_dir = output_dir
        self.lambda_dir = os.path.join(output_dir, "lambda_function")
        
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
            
            # Add parameter to the parameters dictionary
            parameters[param_name] = {
                "Description": f"Parameter {param_name}",
                "Required": param.default == inspect.Parameter.empty,
                "Type": param_type
            }
        
        # Add parameters to the function definition if they exist
        if parameters:
            function_def["Parameters"] = parameters
            
        return function_def
    
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
            
            with open(app_py_path, "w") as f:
                # Write imports and setup
                f.write('"""\n')
                f.write('Lambda function for handling Bedrock Agent requests.\n')
                f.write('Generated by Bedrock Agents SDK.\n')
                f.write('"""\n')
                f.write('import json\n')
                f.write('import logging\n')
                f.write('\n')
                f.write('# Configure logging\n')
                f.write('logger = logging.getLogger()\n')
                f.write('logger.setLevel(logging.INFO)\n')
                f.write('\n')
                f.write('# Import function dependencies\n')
                f.write('import datetime\n')
                f.write('\n')
                f.write('# Function implementations\n')
                
                # Add function implementations for this action group
                for func in functions:
                    # Get the function source code
                    source = inspect.getsource(func.function)
                    f.write('\n')
                    f.write(source)
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
                f.write('        parameters = {}\n')
                f.write('        if "parameters" in event:\n')
                f.write('            parameters = event["parameters"]\n')
                f.write('        \n')
                f.write('        # Call the appropriate function based on the function name\n')
                
                # Add function dispatch logic for this action group only
                for func in functions:
                    f.write(f'        if function_name == "{func.name}":\n')
                    
                    # Get the function signature
                    signature = inspect.signature(func.function)
                    param_list = []
                    
                    # Build the parameter list
                    for param_name in signature.parameters:
                        param_list.append(f'{param_name}=parameters.get("{param_name}")')
                    
                    # Call the function with the parameters
                    params_str = ", ".join(param_list)
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
    
    def _generate_requirements(self):
        """Generate the requirements.txt file"""
        # Group functions by action group
        action_group_map = {}
        for func in self.agent.functions:
            group_name = func.action_group or "DefaultActions"
            if group_name not in action_group_map:
                action_group_map[group_name] = []
            action_group_map[group_name].append(func)
        
        # Basic requirements
        requirements = [
            "boto3>=1.28.0",
            "pydantic>=2.0.0"
        ]
        
        # Generate requirements.txt for each action group
        for group_name, functions in action_group_map.items():
            # Create a safe name for the Lambda function directory
            safe_group_name = ''.join(c if c.isalnum() else '' for c in group_name)
            lambda_dir = os.path.join(self.lambda_dir, safe_group_name.lower())
            
            # Create requirements.txt for this action group
            requirements_path = os.path.join(lambda_dir, "requirements.txt")
            
            # Write the requirements file
            with open(requirements_path, "w") as f:
                f.write("\n".join(requirements))
    
    def _generate_readme(self):
        """Generate a README file for the deployment"""
        readme_path = os.path.join(self.output_dir, "README.md")
        
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
   sam deploy --guided --capabilities CAPABILITY_NAMED_IAM
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