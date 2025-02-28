import boto3
import json
import uuid
from botocore.exceptions import ClientError

class BedrockInlineAgent:
    def __init__(self, action_groups, instruction, foundation_model="us.amazon.nova-pro-v1:0", debug=False):
        """Initialize the Bedrock Inline Agent"""
        self.action_groups = action_groups
        self.instruction = instruction
        self.foundation_model = foundation_model
        self.debug = debug
        self.max_tool_calls = 10  # Safety limit to prevent infinite loops
        
        # Initialize Bedrock clients
        self.bedrock_runtime = boto3.client('bedrock-runtime')
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
        
        # Initialize session
        self.session_id = str(uuid.uuid4())
        
        # Store registered functions
        self.registered_functions = {}
        
        # Tool call counter for debugging
        self.tool_call_count = 0
    
    def register_function(self, function_name, function):
        """Register a function that can be called by the agent"""
        self.registered_functions[function_name] = function
    
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
            elif param_type == "boolean":
                if value.lower() in ["true", "yes", "1"]:
                    value = True
                elif value.lower() in ["false", "no", "0"]:
                    value = False
            
            param_dict[name] = value
        
        if self.debug:
            print(f"Converted parameters: {param_dict}")
        return param_dict

    def execute_function(self, function_name, params):
        """Execute a registered function with given parameters"""
        if function_name not in self.registered_functions:
            print(f"\nError: Function '{function_name}' is not registered")
            return None
            
        try:
            func = self.registered_functions[function_name]
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

    def invoke_agent(self, input_text=None, invocation_id=None, return_control_result=None, accumulated_text=""):
        """
        Invoke the agent with either user input or function result
        This method handles the entire flow recursively until completion
        """
        self.tool_call_count += 1
        if self.tool_call_count > self.max_tool_calls:
            return accumulated_text + "\n\nReached maximum number of tool calls. Some tasks may be incomplete."
        
        if self.debug and self.tool_call_count > 1:
            print(f"\nTool call #{self.tool_call_count - 1}")
        
        try:
            # Determine if this is an initial call or a follow-up call
            if input_text is not None:
                # Initial call with user input
                if self.debug:
                    print(f"\nInvoking agent with user input: '{input_text[:50]}...' if len(input_text) > 50 else input_text")
                response = self.bedrock_agent_runtime.invoke_inline_agent(
                    sessionId=self.session_id,
                    actionGroups=self.action_groups,
                    instruction=self.instruction,
                    foundationModel=self.foundation_model,
                    inputText=input_text,
                    enableTrace=True
                )
            else:
                # Follow-up call with function result
                if self.debug:
                    print(f"\nInvoking agent with function result for invocation ID: {invocation_id}")
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
                self.tool_call_count = 0  # Reset counter for next user input
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
            params = self.convert_parameters(parameters)
            result = self.execute_function(function_name, params)
            
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
            return self.invoke_agent(
                input_text=None,
                invocation_id=invocation_id,
                return_control_result=return_control_result,
                accumulated_text=accumulated_text
            )
            
        except Exception as e:
            print(f"\nError in invoke_agent: {e}")
            return f"An error occurred: {str(e)}"

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
                
                # Reset tool call counter for new user input
                self.tool_call_count = 0
                
                # Process the user input through the agent
                response_text = self.invoke_agent(input_text=user_input)
                
                # Print the agent's final response
                print("\nAssistant:", response_text.strip())
                
        except ClientError as e:
            print(f"\nError: {e}")
        except KeyboardInterrupt:
            print("\n\nChat session interrupted. Goodbye!")
        except Exception as e:
            print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    # This should not be called directly
    pass