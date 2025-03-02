"""
Main client for Bedrock Agents SDK.
"""
import boto3
import json
import uuid
from typing import List, Dict, Any, Optional, Union, Callable
from botocore.exceptions import ClientError

from bedrock_agents_sdk.models.agent import Agent
from bedrock_agents_sdk.models.function import Function
from bedrock_agents_sdk.models.message import Message
from bedrock_agents_sdk.models.files import OutputFile
from bedrock_agents_sdk.utils.parameter_extraction import extract_parameter_info
from bedrock_agents_sdk.utils.parameter_conversion import convert_parameters
from bedrock_agents_sdk.utils.trace_processing import process_trace_data

class Client:
    """Client for interacting with Amazon Bedrock Agents"""
    
    def __init__(self, 
                 region_name: Optional[str] = None, 
                 profile_name: Optional[str] = None,
                 verbosity: str = "normal",
                 trace_level: str = "none",
                 max_tool_calls: int = 10):
        """
        Initialize the client
        
        Args:
            region_name: AWS region name (default: None, uses boto3 default)
            profile_name: AWS profile name (default: None, uses boto3 default)
            verbosity: Logging verbosity (default: "normal")
                Options: "quiet", "normal", "verbose", "debug"
            trace_level: Agent trace level (default: "none")
                Options: "none", "minimal", "standard", "detailed"
            max_tool_calls: Maximum number of tool calls per run (default: 10)
        """
        # Set up session
        session = boto3.Session(region_name=region_name, profile_name=profile_name)
        self.bedrock_agent_runtime = session.client('bedrock-agent-runtime')
        
        # Configure logging
        self.verbosity = verbosity.lower()
        self.sdk_logs = self.verbosity != "quiet"
        self.debug_logs = self.verbosity == "debug"
        
        # Configure agent traces
        self.trace_level = trace_level.lower()
        self.agent_traces = self.trace_level != "none"
        
        # Set maximum tool calls
        self.max_tool_calls = max_tool_calls
        
        if self.sdk_logs:
            print(f"[SDK LOG] Initialized Bedrock Agents client (region: {region_name or 'default'}, verbosity: {verbosity}, trace level: {trace_level})")
    
    def _build_action_groups(self, agent: Agent) -> List[Dict[str, Any]]:
        """Build action groups from agent's action_groups property or functions"""
        action_groups = []
        
        # First, use the explicitly defined action groups if they exist
        if agent.action_groups:
            for ag in agent.action_groups:
                action_group = {
                    "actionGroupName": ag.name,
                    "description": ag.description,
                    "actionGroupExecutor": {
                        "customControl": "RETURN_CONTROL"
                    },
                    "functionSchema": {
                        "functions": []
                    }
                }
                
                for func in ag.functions:
                    # Extract function info
                    if isinstance(func, Function):
                        func_obj = func
                    else:
                        # Create a Function object if it's a callable
                        func_obj = Function(
                            name=func.__name__,
                            description=func.__doc__ or f"Execute {func.__name__}",
                            function=func,
                            action_group=ag.name
                        )
                    
                    # Extract parameter information
                    params = extract_parameter_info(func_obj.function)
                    
                    function_def = {
                        "name": func_obj.name,
                        "description": func_obj.description,
                        "requireConfirmation": "DISABLED"
                    }
                    
                    # Add parameters if they exist
                    if params:
                        function_def["parameters"] = params
                    
                    action_group["functionSchema"]["functions"].append(function_def)
                
                action_groups.append(action_group)
                
            if self.sdk_logs:
                print(f"[SDK LOG] Using {len(action_groups)} action groups from agent.action_groups")
        
        # If no action groups are defined, fall back to building them from functions
        else:
            # Group functions by action group
            action_group_map = {}
            
            for func in agent.functions:
                # Determine action group name
                group_name = func.action_group or "DefaultActions"
                
                # Create action group if it doesn't exist
                if group_name not in action_group_map:
                    action_group_map[group_name] = []
                
                # Extract parameter information
                params = extract_parameter_info(func.function)
                
                # Add function to action group
                action_group_map[group_name].append({
                    "name": func.name,
                    "description": func.description,
                    "parameters": params
                })
            
            # Create action groups
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
                
            if self.sdk_logs:
                print(f"[SDK LOG] Built {len(action_groups)} action groups from agent.functions")
        
        # Add code interpreter action group if enabled
        if agent.enable_code_interpreter:
            code_interpreter_action = {
                'actionGroupName': 'CodeInterpreterAction',
                'parentActionGroupSignature': 'AMAZON.CodeInterpreter'
            }
            action_groups.append(code_interpreter_action)
            if self.sdk_logs:
                print("[SDK LOG] Added Code Interpreter action group")
        
        if self.sdk_logs:
            print(f"[SDK LOG] Configured {len(action_groups)} action groups with {len(agent.functions)} functions")
        
        return action_groups
    
    def _execute_function(self, function_map: Dict[str, Callable], function_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function with given parameters"""
        if function_name not in function_map:
            if self.sdk_logs:
                print(f"\n[SDK LOG] Error: Function '{function_name}' is not registered")
            return None
            
        try:
            func = function_map[function_name]
            if params:
                return func(**params)
            return func()
        except TypeError as e:
            if self.sdk_logs:
                print(f"\n[SDK LOG] Error calling function '{function_name}': {e}")
                print(f"[SDK LOG] Parameters provided: {params}")
            return None
        except Exception as e:
            if self.sdk_logs:
                print(f"\n[SDK LOG] Unexpected error in function '{function_name}': {e}")
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
                     tool_call_count: int = 0) -> Dict[str, Any]:
        """
        Invoke the agent with either user input or function result
        This method handles the entire flow recursively until completion
        
        Returns:
            Dict[str, Any]: Dictionary containing the response text and any files
        """
        tool_call_count += 1
        if tool_call_count > self.max_tool_calls:
            return {
                "response": accumulated_text + "\n\nReached maximum number of tool calls. Some tasks may be incomplete.",
                "files": []
            }
        
        if self.sdk_logs and tool_call_count > 1:
            print(f"\n[SDK LOG] Processing function call #{tool_call_count - 1}...")
        
        try:
            # Prepare parameters for the API call
            params = {
                "sessionId": session_id,
                "actionGroups": action_groups,
                "instruction": agent.instructions,
                "foundationModel": agent.model,
                "enableTrace": self.agent_traces
            }
            
            # Add advanced configuration if provided
            if agent.advanced_config:
                params.update(agent.advanced_config)
            
            # Determine if this is an initial call or a follow-up call
            if input_text is not None:
                # Initial call with user input
                if self.sdk_logs:
                    truncated_input = input_text[:50] + "..." if len(input_text) > 50 else input_text
                    print(f"\n[SDK LOG] Sending user query to agent: '{truncated_input}'")
                
                params["inputText"] = input_text
                
                # Add files if provided
                if agent.files:
                    if self.sdk_logs:
                        print(f"\n[SDK LOG] Sending {len(agent.files)} file(s) to agent")
                    
                    params["inlineSessionState"] = {
                        "files": [f.to_dict() for f in agent.files]
                    }
            else:
                # Follow-up call with function result
                if self.sdk_logs:
                    print(f"\n[SDK LOG] Sending function result back to agent (invocation ID: {invocation_id})")
                
                inline_session_state = {
                    "invocationId": invocation_id,
                    "returnControlInvocationResults": [return_control_result]
                }
                
                # Add files if provided
                if agent.files:
                    if self.sdk_logs:
                        print(f"\n[SDK LOG] Sending {len(agent.files)} file(s) to agent")
                    inline_session_state["files"] = [f.to_dict() for f in agent.files]
                
                params["inlineSessionState"] = inline_session_state
            
            # Apply agent plugins pre-invoke
            for plugin in agent.plugins:
                params = plugin.pre_invoke(params)
            
            # Call the API
            response = self.bedrock_agent_runtime.invoke_inline_agent(**params)
            
            # Apply agent plugins post-invoke
            for plugin in agent.plugins:
                response = plugin.post_invoke(response)
            
            # Process the response
            return_control = None
            response_text = ""
            output_files = []
            
            for event in response["completion"]:
                if "returnControl" in event:
                    return_control = event["returnControl"]
                    if self.sdk_logs:
                        print("\n[SDK LOG] Agent needs to call a function...")
                    break
                elif "chunk" in event and "bytes" in event["chunk"]:
                    text = event["chunk"]["bytes"].decode('utf-8')
                    response_text += text
                elif "files" in event:
                    # Process files from the response
                    for file_data in event["files"].get("files", []):
                        output_file = OutputFile.from_response(file_data)
                        output_files.append(output_file)
                        if self.sdk_logs:
                            print(f"\n[SDK LOG] Received file: {output_file.name} ({len(output_file.content)} bytes, type: {output_file.type})")
                elif "trace" in event:
                    # Process trace information using the helper method
                    process_trace_data(event["trace"], self.agent_traces, self.trace_level)
            
            # Update accumulated text with any new response text
            if response_text:
                # Only add a separator if we already have accumulated text
                if accumulated_text:
                    accumulated_text += "\n"
                accumulated_text += response_text
                if self.sdk_logs and not return_control:
                    print("\n[SDK LOG] Agent has completed its response")
            
            # If no tool call is needed, prepare the final result
            if not return_control:
                result = {
                    "response": accumulated_text,
                    "files": output_files
                }
                
                # Apply agent plugins post-process
                for plugin in agent.plugins:
                    result = plugin.post_process(result)
                
                return result
            
            # Extract function details
            invocation_id = return_control["invocationId"]
            function_input = return_control.get("invocationInputs", [])[0].get("functionInvocationInput", {})
            function_name = function_input.get("function")
            action_group = function_input.get("actionGroup")
            parameters = function_input.get("parameters", [])
            
            if self.sdk_logs:
                print(f"\n[SDK LOG] Function requested: {function_name}")
                print(f"[SDK LOG] From action group: {action_group}")
                if parameters:
                    print(f"[SDK LOG] With parameters: {parameters}")
                else:
                    print(f"[SDK LOG] No parameters provided")
            
            # Convert and execute
            params = convert_parameters(parameters, self.sdk_logs)
            result = self._execute_function(function_map, function_name, params)
            
            if not result:
                if self.sdk_logs:
                    print(f"\n[SDK LOG] Warning: Function {function_name} did not return a result")
                final_result = {
                    "response": accumulated_text,
                    "files": output_files
                }
                
                # Apply agent plugins post-process
                for plugin in agent.plugins:
                    final_result = plugin.post_process(final_result)
                
                return final_result
            
            if self.sdk_logs:
                print(f"\n[SDK LOG] Function executed successfully. Result: {result}")
            
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
            result = self._invoke_agent(
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
            
            # Merge files from this call with any files from recursive calls
            all_files = output_files + result.get("files", [])
            final_result = {
                "response": result.get("response", ""),
                "files": all_files
            }
            
            # Apply agent plugins post-process
            for plugin in agent.plugins:
                final_result = plugin.post_process(final_result)
            
            return final_result
            
        except Exception as e:
            error_msg = f"Error in agent invocation: {e}"
            if self.sdk_logs:
                print(f"\n[SDK LOG] {error_msg}")
            return {
                "response": f"An error occurred: {str(e)}",
                "files": []
            }
    
    def run(self, agent: Agent, message: Optional[str] = None, messages: Optional[List[Union[Message, Dict[str, str]]]] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent with either a simple message string or a list of structured messages
        
        Args:
            agent: The agent configuration
            message: A simple string message (mutually exclusive with messages)
            messages: A list of messages in the conversation (mutually exclusive with message)
            session_id: Optional session ID to continue a conversation. If not provided, a new session will be created.
            
        Returns:
            Dict[str, Any]: Dictionary containing the response text and any files
        """
        # Validate input parameters
        if message is None and messages is None:
            raise ValueError("Either 'message' or 'messages' must be provided")
        if message is not None and messages is not None:
            raise ValueError("Only one of 'message' or 'messages' should be provided, not both")
            
        # Create a session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())
            
        if self.sdk_logs:
            print(f"\n[SDK LOG] Starting new run session (ID: {session_id})")
        
        # Build action groups
        action_groups = self._build_action_groups(agent)
        
        # Create a map of function names to functions
        function_map = {func.name: func.function for func in agent.functions}
        
        # Handle simple string input by converting it to a user message
        if message is not None:
            last_message = Message(role="user", content=message)
        else:
            # Get the last user message from the list
            last_message = messages[-1]
            if isinstance(last_message, dict):
                last_message = Message(**last_message)
            
            if last_message.role != "user":
                raise ValueError("The last message must be from the user")
        
        # Invoke the agent
        result = self._invoke_agent(
            agent=agent,
            action_groups=action_groups,
            function_map=function_map,
            session_id=session_id,
            input_text=last_message.content,
            tool_call_count=0
        )
        
        if self.sdk_logs:
            print(f"\n[SDK LOG] Run session completed (ID: {session_id})")
            
            if result.get("files"):
                print(f"\n[SDK LOG] {len(result['files'])} file(s) were generated during this session")
        
        # Add helper methods for file handling
        if result.get("files"):
            # Add a method to save all files
            def save_all_files(directory="."):
                """Save all files to the specified directory"""
                saved_paths = []
                for file in result["files"]:
                    path = file.save(directory)
                    saved_paths.append(path)
                return saved_paths
            
            result["save_all_files"] = save_all_files
        
        return result
    
    def chat(self, agent: Agent, session_id: Optional[str] = None):
        """
        Start an interactive chat session with the agent
        
        Args:
            agent: The agent configuration
            session_id: Optional session ID to continue a conversation. If not provided, a new session will be created.
        """
        # Create a session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Build action groups
        action_groups = self._build_action_groups(agent)
        
        # Create a map of function names to functions
        function_map = {func.name: func.function for func in agent.functions}
        
        print(f"\n[SESSION] Starting chat session (ID: {session_id})")
        print("[SESSION] Type 'exit' or 'quit' to end the chat")
        print("[SESSION] Type 'file:path/to/file.ext' to upload a file")
        print("[SESSION] Type 'clear files' to remove all uploaded files")
        print("-" * 50)
        
        try:
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\n[SESSION] Ending chat session. Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Check for file upload command
                if user_input.startswith('file:'):
                    file_path = user_input[5:].strip()
                    try:
                        file = agent.add_file_from_path(file_path)
                        print(f"[SESSION] File '{file.name}' uploaded successfully ({len(file.content)} bytes)")
                        continue
                    except Exception as e:
                        print(f"[ERROR] Failed to upload file: {e}")
                        continue
                
                # Check for clear files command
                if user_input.lower() == 'clear files':
                    agent.files = []
                    print("[SESSION] All files have been cleared")
                    continue
                
                # Invoke the agent
                result = self._invoke_agent(
                    agent=agent,
                    action_groups=action_groups,
                    function_map=function_map,
                    session_id=session_id,
                    input_text=user_input,
                    tool_call_count=0
                )
                
                # Print the agent's final response
                print("\nAssistant:", result["response"].strip())
                
                # Handle any files returned by the agent
                if result.get("files"):
                    print(f"\n[FILES] The agent generated {len(result['files'])} file(s):")
                    for i, file in enumerate(result["files"]):
                        print(f"  {i+1}. {file.name} ({len(file.content)} bytes, type: {file.type})")
                    
                    # Ask if the user wants to save the files
                    save_choice = input("\nDo you want to save these files? (y/n): ").strip().lower()
                    if save_choice in ['y', 'yes']:
                        save_dir = input("Enter directory to save files (default is current directory): ").strip()
                        if not save_dir:
                            save_dir = "."
                        
                        # Save the files
                        saved_paths = []
                        for file in result["files"]:
                            path = file.save(save_dir)
                            saved_paths.append(path)
                        
                        print(f"\n[FILES] Files saved to: {', '.join(saved_paths)}")
                
        except ClientError as e:
            print(f"\n[ERROR] AWS Client Error: {e}")
        except KeyboardInterrupt:
            print("\n\n[SESSION] Chat session interrupted. Goodbye!")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}") 