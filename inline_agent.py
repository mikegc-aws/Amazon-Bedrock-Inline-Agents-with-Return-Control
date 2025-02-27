import boto3
import json
import uuid
import datetime
from botocore.exceptions import ClientError

# debug = False

# def get_current_time():
#     """Function to get the current time"""
#     now = datetime.datetime.now()
#     current_time = now.strftime("%H:%M:%S")
#     timezone = datetime.datetime.now().astimezone().tzname()
#     return {
#         "time": current_time,
#         "timezone": timezone
#     }

# def get_current_date():
#     """Function to get the current date"""
#     now = datetime.datetime.now()
#     current_date = now.strftime("%Y-%m-%d")
#     timezone = datetime.datetime.now().astimezone().tzname()
#     return {
#         "date": current_date,
#         "timezone": timezone
#     }

# def add_two_numbers(a, b):
#     """Function to add two numbers"""
#     return a + b

# def process_agent_response(response):
#     """Process the agent's response and handle any return control events"""
#     invocation_id = None
#     response_text = ""
#     function_info = None
    
#     for event in response["completion"]:
#         if "returnControl" in event:
#             function_info = event["returnControl"]
#             invocation_id = function_info["invocationId"]
#             print("\nAgent is requesting information...")
#             return invocation_id, response_text, function_info
#         elif "chunk" in event and "bytes" in event["chunk"]:
#             text = event["chunk"]["bytes"].decode('utf-8')
#             response_text += text
            
#     return invocation_id, response_text, function_info

# def get_action_groups():
#     """Define and return the action groups configuration"""
#     return [
#         {
#             "actionGroupName": "TimeActions",
#             "description": "Actions related to getting the current time",
#             "actionGroupExecutor": {
#                 "customControl": "RETURN_CONTROL"
#             },
#             "functionSchema": {
#                 "functions": [
#                     {
#                         "name": "get_time",
#                         "description": "Get the current time and date",
#                         "parameters": {},
#                         "requireConfirmation": "DISABLED"
#                     },
#                     {
#                         "name": "get_date",
#                         "description": "Get the current date",
#                         "parameters": {},
#                         "requireConfirmation": "DISABLED"
#                     }
#                 ]
#             }
#         },
#         {
#             "actionGroupName": "MathActions",
#             "description": "Actions related to mathematical operations",
#             "actionGroupExecutor": {
#                 "customControl": "RETURN_CONTROL"
#             },
#             "functionSchema": {
#                 "functions": [
#                     {
#                         "name": "add_two_numbers",
#                         "description": "Add two numbers together",  
#                         "parameters": {
#                             "a": {
#                                 "description": "The first number to add",
#                                 "required": True,
#                                 "type": "number"    
#                             },
#                             "b": {
#                                 "description": "The second number to add",
#                                 "required": True,
#                                 "type": "number"
#                             }
#                         }   
#                     }
#                 ]
#             }
#         }
#     ]

# def convert_parameters(parameters):
#     """Convert parameters from agent format to Python format"""
#     param_dict = {}
#     for param in parameters:
#         name = param.get("name")
#         value = param.get("value")
#         param_type = param.get("type")
        
#         if param_type == "number":
#             try:
#                 value = float(value)
#                 if value.is_integer():
#                     value = int(value)
#             except ValueError:
#                 print(f"\nWarning: Could not convert {value} to number")
#                 continue
        
#         param_dict[name] = value
    
#     if debug:
#         print(f"Converted parameters: {param_dict}")
#     return param_dict

# def execute_function(function_name, params):
#     """Execute the requested function with given parameters"""
#     if function_name == "get_time":
#         return get_current_time()
#     elif function_name == "get_date":
#         return get_current_date()
#     elif function_name == "add_two_numbers":
#         return add_two_numbers(params["a"], params["b"])
#     return None

# def create_return_control_result(action_group, function_name, result):
#     """Create the return control result structure"""
#     return {
#         "functionResult": {
#             "actionGroup": action_group,
#             "function": function_name,
#             "responseBody": {
#                 "application/json": {
#                     "body": json.dumps(result)
#                 }
#             }
#         }
#     }

# def handle_function_call(bedrock_agent_runtime, session_id, action_groups, instruction, foundation_model, 
#                         function_info, invocation_id):
#     """Handle the function call and return control flow"""
#     # Extract function details
#     function_input = function_info.get("invocationInputs", [])[0].get("functionInvocationInput", {})
#     function_name = function_input.get("function")
#     action_group = function_input.get("actionGroup")
#     parameters = function_input.get("parameters", [])
    
#     if debug:
#         print(f"\nRequested function: {function_name}")
    
#     # Convert and execute
#     params = convert_parameters(parameters)
#     result = execute_function(function_name, params)
    
#     if not result:
#         print(f"\nWarning: Function {function_name} did not return a result")
#         return ""
    
#     # Create and send return control result
#     return_control_result = create_return_control_result(action_group, function_name, result)
#     response = bedrock_agent_runtime.invoke_inline_agent(
#         sessionId=session_id,
#         actionGroups=action_groups,
#         instruction=instruction,
#         foundationModel=foundation_model,
#         inlineSessionState={
#             "invocationId": invocation_id,
#             "returnControlInvocationResults": [return_control_result]
#         }
#     )
    
#     # Process final response
#     _, response_text, _ = process_agent_response(response)
#     return response_text

# def chat_with_agent():
#     """Main chat loop function"""
#     # Initialize Bedrock clients
#     bedrock_runtime = boto3.client('bedrock-runtime')
#     bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
    
#     # Setup session
#     session_id = str(uuid.uuid4())
#     print(f"\nStarting new chat session (ID: {session_id})")
#     print("Type 'exit' or 'quit' to end the chat")
#     print("-" * 50)
    
#     # Get configuration
#     action_groups = get_action_groups()
#     instruction = "You are a helpful assistant that can tell the time when asked. You can also engage in general conversation."
#     foundation_model = "us.amazon.nova-pro-v1:0"
    
#     try:
#         while True:
#             # Get user input
#             user_input = input("\nYou: ").strip()
            
#             if user_input.lower() in ['exit', 'quit']:
#                 print("\nEnding chat session. Goodbye!")
#                 break
            
#             if not user_input:
#                 continue
            
#             # First invocation
#             response = bedrock_agent_runtime.invoke_inline_agent(
#                 sessionId=session_id,
#                 actionGroups=action_groups,
#                 instruction=instruction,
#                 foundationModel=foundation_model,
#                 inputText=user_input,
#                 enableTrace=True
#             )
            
#             # Process response
#             invocation_id, response_text, function_info = process_agent_response(response)
            
#             # Handle function call if needed
#             if invocation_id and function_info:
#                 response_text = handle_function_call(
#                     bedrock_agent_runtime, session_id, action_groups,
#                     instruction, foundation_model, function_info, invocation_id
#                 )
            
#             print("\nAssistant:", response_text.strip())
            
#     except ClientError as e:
#         print(f"\nError: {e}")
#     except KeyboardInterrupt:
#         print("\n\nChat session interrupted. Goodbye!")
#     except Exception as e:
#         print(f"\nUnexpected error: {e}")

class BedrockInlineAgent:
    def __init__(self, action_groups, instruction, foundation_model="us.amazon.nova-pro-v1:0", debug=False):
        """Initialize the Bedrock Inline Agent"""
        self.action_groups = action_groups
        self.instruction = instruction
        self.foundation_model = foundation_model
        self.debug = debug
        
        # Initialize Bedrock clients
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
        
        # Initialize session
        self.session_id = str(uuid.uuid4())
        
        # Store registered functions
        self.registered_functions = {}
    
    def register_function(self, function_name, function):
        """Register a function that can be called by the agent"""
        self.registered_functions[function_name] = function
        
    def process_agent_response(self, response):
        """Process the agent's response and handle any return control events"""
        invocation_id = None
        response_text = ""
        function_info = None
        
        for event in response["completion"]:
            if "returnControl" in event:
                function_info = event["returnControl"]
                invocation_id = function_info["invocationId"]
                if self.debug:
                    print("\nAgent is requesting information...")
                return invocation_id, response_text, function_info
            elif "chunk" in event and "bytes" in event["chunk"]:
                text = event["chunk"]["bytes"].decode('utf-8')
                response_text += text
                
        return invocation_id, response_text, function_info

    def convert_parameters(self, parameters):
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
            
            param_dict[name] = value
        
        if self.debug:
            print(f"Converted parameters: {param_dict}")
        return param_dict

    def execute_function(self, function_name, params):
        """Execute a registered function with given parameters"""
        if function_name in self.registered_functions:
            func = self.registered_functions[function_name]
            if params:
                return func(**params)
            return func()
        return None

    def create_return_control_result(self, action_group, function_name, result):
        """Create the return control result structure"""
        return {
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

    def handle_function_call(self, function_info, invocation_id):
        """Handle the function call and return control flow"""
        # Extract function details
        function_input = function_info.get("invocationInputs", [])[0].get("functionInvocationInput", {})
        function_name = function_input.get("function")
        action_group = function_input.get("actionGroup")
        parameters = function_input.get("parameters", [])
        
        if self.debug:
            print(f"\nRequested function: {function_name}")
        
        # Convert and execute
        params = self.convert_parameters(parameters)
        result = self.execute_function(function_name, params)
        
        if not result:
            print(f"\nWarning: Function {function_name} did not return a result")
            return ""
        
        # Create and send return control result
        return_control_result = self.create_return_control_result(action_group, function_name, result)
        response = self.bedrock_agent_runtime.invoke_inline_agent(
            sessionId=self.session_id,
            actionGroups=self.action_groups,
            instruction=self.instruction,
            foundationModel=self.foundation_model,
            inlineSessionState={
                "invocationId": invocation_id,
                "returnControlInvocationResults": [return_control_result]
            }
        )
        
        # Process final response
        _, response_text, _ = self.process_agent_response(response)
        return response_text

    def chat(self):
        """Start the chat session"""
        print(f"\nStarting new chat session (ID: {self.session_id})")
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
                
                # First invocation
                response = self.bedrock_agent_runtime.invoke_inline_agent(
                    sessionId=self.session_id,
                    actionGroups=self.action_groups,
                    instruction=self.instruction,
                    foundationModel=self.foundation_model,
                    inputText=user_input,
                    enableTrace=True
                )
                
                # Process response
                invocation_id, response_text, function_info = self.process_agent_response(response)
                
                # Handle function call if needed
                if invocation_id and function_info:
                    response_text = self.handle_function_call(function_info, invocation_id)
                
                print("\nAssistant:", response_text.strip())
                
        except ClientError as e:
            print(f"\nError: {e}")
        except KeyboardInterrupt:
            print("\n\nChat session interrupted. Goodbye!")
        except Exception as e:
            print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    chat_with_agent()