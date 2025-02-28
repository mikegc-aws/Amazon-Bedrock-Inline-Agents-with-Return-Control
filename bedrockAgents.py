import boto3
import json
import uuid
import inspect
from typing import List, Dict, Any, Optional, Union, Callable, Type
from pydantic import BaseModel, create_model, Field
from botocore.exceptions import ClientError

class Function(BaseModel):
    """Represents a function that can be called by the agent"""
    name: str
    description: str
    function: Callable
    action_group: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

class Message(BaseModel):
    """Represents a message in the conversation"""
    role: str
    content: str

class ActionGroup(BaseModel):
    """Represents an action group in the agent"""
    name: str
    description: str
    functions: List[Function]

class Agent(BaseModel):
    """Represents a Bedrock agent configuration"""
    name: str
    model: str
    instructions: str
    functions: List[Union[Function, Callable]] = []
    enable_code_interpreter: bool = False
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """Initialize the agent and process functions if provided"""
        # Handle dictionary format for functions
        if 'functions' in data and isinstance(data['functions'], dict):
            action_groups = data.pop('functions')
            processed_functions = []
            
            for action_group, funcs in action_groups.items():
                for func in funcs:
                    processed_functions.append(self._create_function(func, action_group=action_group))
            
            data['functions'] = processed_functions
        
        super().__init__(**data)
        self._process_functions()
    
    def _process_functions(self):
        """Process functions provided in the constructor"""
        processed_functions = []
        
        # Process each function
        for item in self.functions:
            if isinstance(item, Function):
                # Already a Function object, keep as is
                processed_functions.append(item)
            elif callable(item):
                # Single function without action group
                processed_functions.append(self._create_function(item))
        
        # Replace the original functions list with processed functions
        self.functions = processed_functions
    
    def _create_function(self, function: Callable, description: Optional[str] = None, action_group: Optional[str] = None) -> Function:
        """Create a Function object from a callable"""
        func_name = function.__name__
        func_desc = description or function.__doc__ or f"Execute the {func_name} function"
        
        return Function(
            name=func_name,
            description=func_desc,
            function=function,
            action_group=action_group
        )
    
    def add_function(self, function: Callable, description: Optional[str] = None, action_group: Optional[str] = None):
        """Add a function to the agent"""
        self.functions.append(self._create_function(function, description, action_group))
        return self

class BedrockAgents:
    """Client for interacting with Amazon Bedrock Agents"""
    
    def __init__(self, debug: bool = False):
        """Initialize the Bedrock Agents client"""
        self.debug = debug
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
        self.max_tool_calls = 10  # Safety limit to prevent infinite loops
    
    def _extract_parameter_info(self, function: Callable) -> Dict[str, Dict[str, Any]]:
        """Extract parameter information from a function using type hints and docstring"""
        params = {}
        sig = inspect.signature(function)
        
        for param_name, param in sig.parameters.items():
            # Skip self parameter for methods
            if param_name == 'self':
                continue
                
            # Determine parameter type from annotations or default to string
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int or param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
            
            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty
            
            # Look for parameter description in docstring
            param_desc = f"The {param_name} parameter"
            if function.__doc__:
                # Look for :param param_name: in docstring
                for line in function.__doc__.split('\n'):
                    line = line.strip()
                    if line.startswith(f":param {param_name}:"):
                        param_desc = line.split(f":param {param_name}:")[1].strip()
            
            # Add parameter definition
            params[param_name] = {
                "description": param_desc,
                "required": required,
                "type": param_type
            }
        
        return params
    
    def _build_action_groups(self, agent: Agent) -> List[Dict[str, Any]]:
        """Build action groups from agent functions"""
        # Group functions by action group
        action_group_map = {}
        
        for func in agent.functions:
            # Determine action group name
            group_name = func.action_group or "DefaultActions"
            
            # Create action group if it doesn't exist
            if group_name not in action_group_map:
                action_group_map[group_name] = []
            
            # Extract parameter information
            params = self._extract_parameter_info(func.function)
            
            # Add function to action group
            action_group_map[group_name].append({
                "name": func.name,
                "description": func.description,
                "parameters": params
            })
        
        # Create action groups
        action_groups = []
        
        # Add custom action groups from functions
        for group_name, functions in action_group_map.items():
            action_group = {
                "actionGroupName": group_name,
                "description": f"Actions related to {group_name.replace('Actions', '')}",
                "actionGroupExecutor": {
                    "customControl": "RETURN_CONTROL"
                },
                "functionSchema": {
                    "functions": []
                }
            }
            
            for func_info in functions:
                function_def = {
                    "name": func_info["name"],
                    "description": func_info["description"],
                    "requireConfirmation": "DISABLED"
                }
                
                # Add parameters if they exist
                if func_info["parameters"]:
                    function_def["parameters"] = func_info["parameters"]
                
                action_group["functionSchema"]["functions"].append(function_def)
            
            action_groups.append(action_group)
        
        # Add code interpreter action group if enabled
        if agent.enable_code_interpreter:
            code_interpreter_action = {
                'actionGroupName': 'CodeInterpreterAction',
                'parentActionGroupSignature': 'AMAZON.CodeInterpreter'
            }
            action_groups.append(code_interpreter_action)
            if self.debug:
                print("Added Code Interpreter action group")
        
        if self.debug:
            print(f"Built {len(action_groups)} action groups with {len(agent.functions)} functions")
        
        return action_groups
    
    def _convert_parameters(self, parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Convert parameters from agent format to Python format"""
        param_dict = {}
        for param in parameters:
            name = param.get("name")
            value = param.get("value")
            param_type = param.get("type")
            
            if param_type == "number":
                try:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                except ValueError:
                    print(f"\nWarning: Could not convert {value} to number")
                    continue
            elif param_type == "boolean":
                if value.lower() in ["true", "yes", "1"]:
                    value = True
                elif value.lower() in ["false", "no", "0"]:
                    value = False
            
            param_dict[name] = value
        
        if self.debug:
            print(f"Converted parameters: {param_dict}")
        return param_dict
    
    def _execute_function(self, function_map: Dict[str, Callable], function_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function with given parameters"""
        if function_name not in function_map:
            print(f"\nError: Function '{function_name}' is not registered")
            return None
            
        try:
            func = function_map[function_name]
            if params:
                return func(**params)
            return func()
        except TypeError as e:
            print(f"\nError calling function '{function_name}': {e}")
            print(f"Parameters: {params}")
            return None
        except Exception as e:
            print(f"\nUnexpected error in function '{function_name}': {e}")
            return None
    
    def _invoke_agent(self, 
                     agent: Agent, 
                     action_groups: List[Dict[str, Any]], 
                     function_map: Dict[str, Callable],
                     session_id: str,
                     input_text: Optional[str] = None, 
                     invocation_id: Optional[str] = None, 
                     return_control_result: Optional[Dict[str, Any]] = None, 
                     accumulated_text: str = "",
                     tool_call_count: int = 0) -> str:
        """
        Invoke the agent with either user input or function result
        This method handles the entire flow recursively until completion
        """
        tool_call_count += 1
        if tool_call_count > self.max_tool_calls:
            return accumulated_text + "\n\nReached maximum number of tool calls. Some tasks may be incomplete."
        
        if self.debug and tool_call_count > 1:
            print(f"\nTool call #{tool_call_count - 1}")
        
        try:
            # Determine if this is an initial call or a follow-up call
            if input_text is not None:
                # Initial call with user input
                if self.debug:
                    print(f"\nInvoking agent with user input: '{input_text[:50]}...' if len(input_text) > 50 else input_text")
                response = self.bedrock_agent_runtime.invoke_inline_agent(
                    sessionId=session_id,
                    actionGroups=action_groups,
                    instruction=agent.instructions,
                    foundationModel=agent.model,
                    inputText=input_text,
                    enableTrace=True
                )
            else:
                # Follow-up call with function result
                if self.debug:
                    print(f"\nInvoking agent with function result for invocation ID: {invocation_id}")
                response = self.bedrock_agent_runtime.invoke_inline_agent(
                    sessionId=session_id,
                    actionGroups=action_groups,
                    instruction=agent.instructions,
                    foundationModel=agent.model,
                    inlineSessionState={
                        "invocationId": invocation_id,
                        "returnControlInvocationResults": [return_control_result]
                    }
                )
            
            # Process the response
            return_control = None
            response_text = ""
            
            for event in response["completion"]:
                if "returnControl" in event:
                    return_control = event["returnControl"]
                    if self.debug:
                        print("\nAgent is requesting information...")
                    break
                elif "chunk" in event and "bytes" in event["chunk"]:
                    text = event["chunk"]["bytes"].decode('utf-8')
                    response_text += text
            
            # Update accumulated text with any new response text
            if response_text:
                # Only add a separator if we already have accumulated text
                if accumulated_text:
                    accumulated_text += "\n"
                accumulated_text += response_text
            
            # If no tool call is needed, return the accumulated response
            if not return_control:
                return accumulated_text
            
            # Extract function details
            invocation_id = return_control["invocationId"]
            function_input = return_control.get("invocationInputs", [])[0].get("functionInvocationInput", {})
            function_name = function_input.get("function")
            action_group = function_input.get("actionGroup")
            parameters = function_input.get("parameters", [])
            
            if self.debug:
                print(f"\nRequested function: {function_name}")
                print(f"Action group: {action_group}")
                print(f"Parameters: {parameters}")
            
            # Convert and execute
            params = self._convert_parameters(parameters)
            result = self._execute_function(function_map, function_name, params)
            
            if not result:
                print(f"\nWarning: Function {function_name} did not return a result")
                return accumulated_text
            
            if self.debug:
                print(f"\nFunction result: {result}")
            
            # Create return control result
            return_control_result = {
                "functionResult": {
                    "actionGroup": action_group,
                    "function": function_name,
                    "responseBody": {
                        "application/json": {
                            "body": json.dumps(result)
                        }
                    }
                }
            }
            
            # Recursive call with the function result
            return self._invoke_agent(
                agent=agent,
                action_groups=action_groups,
                function_map=function_map,
                session_id=session_id,
                input_text=None,
                invocation_id=invocation_id,
                return_control_result=return_control_result,
                accumulated_text=accumulated_text,
                tool_call_count=tool_call_count
            )
            
        except Exception as e:
            print(f"\nError in invoke_agent: {e}")
            return f"An error occurred: {str(e)}"
    
    def run(self, agent: Agent, messages: List[Union[Message, Dict[str, str]]]) -> str:
        """
        Run the agent with a list of messages
        
        Args:
            agent: The agent configuration
            messages: List of messages in the conversation
            
        Returns:
            str: The agent's response
        """
        # Create a session ID
        session_id = str(uuid.uuid4())
        
        # Build action groups
        action_groups = self._build_action_groups(agent)
        
        # Create a map of function names to functions
        function_map = {func.name: func.function for func in agent.functions}
        
        # Get the last user message
        last_message = messages[-1]
        if isinstance(last_message, dict):
            last_message = Message(**last_message)
        
        if last_message.role != "user":
            raise ValueError("The last message must be from the user")
        
        # Invoke the agent
        response = self._invoke_agent(
            agent=agent,
            action_groups=action_groups,
            function_map=function_map,
            session_id=session_id,
            input_text=last_message.content,
            tool_call_count=0
        )
        
        return response
    
    def chat(self, agent: Agent):
        """
        Start an interactive chat session with the agent
        
        Args:
            agent: The agent configuration
        """
        # Create a session ID
        session_id = str(uuid.uuid4())
        
        # Build action groups
        action_groups = self._build_action_groups(agent)
        
        # Create a map of function names to functions
        function_map = {func.name: func.function for func in agent.functions}
        
        print(f"\nStarting new chat session (ID: {session_id})")
        print("Type 'exit' or 'quit' to end the chat")
        print("-" * 50)
        
        try:
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\nEnding chat session. Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Invoke the agent
                response_text = self._invoke_agent(
                    agent=agent,
                    action_groups=action_groups,
                    function_map=function_map,
                    session_id=session_id,
                    input_text=user_input,
                    tool_call_count=0
                )
                
                # Print the agent's final response
                print("\nAssistant:", response_text.strip())
                
        except ClientError as e:
            print(f"\nError: {e}")
        except KeyboardInterrupt:
            print("\n\nChat session interrupted. Goodbye!")
        except Exception as e:
            print(f"\nUnexpected error: {e}") 