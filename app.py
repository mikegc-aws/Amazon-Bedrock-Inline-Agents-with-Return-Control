import datetime
import json
import argparse
import os
from bedrock_agents_sdk import BedrockAgents, Agent, Message, SecurityPlugin, GuardrailPlugin, KnowledgeBasePlugin

# Define functions (no decorators needed)
def get_time() -> dict:
    """Get the current time with timezone information"""
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    timezone = datetime.datetime.now().astimezone().tzname()
    return {
        "time": current_time,
        "timezone": timezone
    }

def get_date() -> dict:
    """Get the current date with timezone information"""
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    timezone = datetime.datetime.now().astimezone().tzname()
    return {
        "date": current_date,
        "timezone": timezone
    }

def add_two_numbers(a: int, b: int, operation: str = "add") -> dict:
    """
    Perform a mathematical operation on two numbers.
    
    :param a: The first number in the operation
    :param b: The second number in the operation
    :param operation: The operation to perform (must be one of: "add", "subtract", "multiply")
    :return: Dictionary containing the result of the operation
    """
    if operation == "add":
        return {"result": a + b}
    if operation == "subtract":
        return {"result": a - b}
    elif operation == "multiply":
        return {"result": a * b}
    return {"result": a + b}

def save_note(content: str, filename: str = "note.txt") -> dict:
    """
    Save a note to a file.
    
    :param content: The content to save
    :param filename: The filename to save to
    :return: Dictionary containing the result of the operation
    """
    try:
        with open(filename, "w") as f:
            f.write(content)
        return {
            "success": True,
            "message": f"Note saved to {filename}",
            "filename": filename
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error saving note: {str(e)}"
        }

def main():
    parser = argparse.ArgumentParser(description="Amazon Bedrock Agents SDK Example")
    parser.add_argument("--chat", action="store_true", help="Start in interactive chat mode")
    parser.add_argument("--region", type=str, help="AWS region name")
    parser.add_argument("--profile", type=str, help="AWS profile name")
    parser.add_argument("--verbosity", type=str, default="verbose", 
                        choices=["quiet", "normal", "verbose", "debug"],
                        help="Verbosity level")
    parser.add_argument("--trace", type=str, default="none", 
                        choices=["none", "minimal", "standard", "detailed", "raw"],
                        help="Agent trace level (raw shows complete unprocessed trace data)")
    parser.add_argument("--file", type=str, help="Path to a file to send to the agent")
    parser.add_argument("--kms-key", type=str, help="Customer KMS key ARN for encryption")
    args = parser.parse_args()
    
    # Create the client with specified options
    client = BedrockAgents(
        region_name=args.region,
        profile_name=args.profile,
        verbosity=args.verbosity,
        trace_level=args.trace
    )
    
    # Register plugins if needed
    if args.kms_key:
        client.register_plugin(SecurityPlugin(customer_encryption_key_arn=args.kms_key))
    
    # Create the agent with functions directly in the definition
    agent = Agent(
        name="HelperAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="""You are a helpful and friendly assistant helping to test this new agent.
        When asked about time or date, use the appropriate function to get accurate information.
        When asked to perform calculations, use the add_two_numbers function with the appropriate operation.
        You can save notes using the save_note function.
        If provided with files, you can analyze them and explain their contents.
        Always explain your reasoning before taking actions.""",
        functions={
            "TimeActions": [get_time, get_date],
            "MathActions": [add_two_numbers],
            "NoteActions": [save_note]
        },
        enable_code_interpreter=True  # Enable code interpreter for file analysis
    )
    
    # Add a file if specified
    if args.file and os.path.exists(args.file):
        try:
            agent.add_file_from_path(args.file)
            print(f"Added file: {args.file}")
        except Exception as e:
            print(f"Error adding file: {e}")
    
    # Run in chat mode or with a single query
    if args.chat:
        client.chat(agent=agent)
    else:
        # Test with a query that will trigger function calling
        result = client.run(
            agent=agent,
            messages=[
                {
                    "role": "user",
                    "content": "What time is it now, and can you also add 25 and 17 for me?"
                }
            ]
        )
        
        print("\nFinal response from agent:")
        print("-" * 50)
        print(result["response"])
        print("-" * 50)
        
        # Handle any files returned by the agent
        if result.get("files"):
            print(f"\nThe agent generated {len(result['files'])} file(s):")
            for i, file in enumerate(result["files"]):
                print(f"  {i+1}. {file.name} ({len(file.content)} bytes, type: {file.type})")
            
            # Save the files
            save_dir = "output"
            os.makedirs(save_dir, exist_ok=True)
            saved_paths = result["save_all_files"](save_dir)
            print(f"\nFiles saved to: {', '.join(saved_paths)}")

if __name__ == "__main__":
    main() 