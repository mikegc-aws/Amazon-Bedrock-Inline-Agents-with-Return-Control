import datetime, json
from bedrockInlineAgent import BedrockInlineAgent

# Create the agent instance
agent = BedrockInlineAgent(
    foundation_model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instruction="""You are a helpful assistant that can tell the time, 
perform basic math operations, search the web, and load content from URLs. 
You can also engage in general conversation.""",
    debug=False, 
    enable_code_interpreter=True
)

# Time functions
@agent.agent_function(action_group="TimeActions", description="Get the current time")
def get_time() -> dict:
    """Get the current time with timezone information"""
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    timezone = datetime.datetime.now().astimezone().tzname()
    return {
        "time": current_time,
        "timezone": timezone
    }

@agent.agent_function(action_group="TimeActions", description="Get the current date")
def get_date() -> dict:
    """Get the current date with timezone information"""
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    timezone = datetime.datetime.now().astimezone().tzname()
    return {
        "date": current_date,
        "timezone": timezone
    }

@agent.agent_function(action_group="MathActions", description="Perform a math operation")
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

def main():
    # View the action groups:
    agent.build_action_groups()
    action_groups = agent.action_groups
    print(json.dumps(action_groups, indent=4))

    # Start the chat session
    agent.chat()

if __name__ == "__main__":
    main() 