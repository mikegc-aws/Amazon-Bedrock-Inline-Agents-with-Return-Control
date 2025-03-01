import datetime
import json
import argparse
from bedrockAgents import BedrockAgents, Agent, Message

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

def main():
    
    # Create the client with verbose mode for detailed logs
    # Verbosity options: "quiet", "normal", "verbose", "debug"
    client = BedrockAgents(verbosity="verbose") 
    
    # Create the agent with functions directly in the definition
    agent = Agent(
        name="HelperAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="""You are a helpful and friendly assistant helping to test this new agent.
        When asked about time or date, use the appropriate function to get accurate information.
        When asked to perform calculations, use the add_two_numbers function with the appropriate operation.
        Always explain your reasoning before taking actions.""",
        functions={
            "TimeActions": [get_time, get_date],
            "MathActions": [add_two_numbers]
        }
    )
    
    ###### Test with interactive chat mode:
    # client.chat(agent=agent)

    ###### Test with a query that will trigger function calling and show trace information
    response = client.run(
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
    print(response)
    print("-" * 50)

if __name__ == "__main__":
    main() 