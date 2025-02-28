import datetime
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
    # Create the client
    client = BedrockAgents(debug=False)
    
    # Create the agent with functions directly in the definition
    agent = Agent(
        name="HelperAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="""You are a helpful and friendly assistant helping to test this new agent.""",
        functions={
            "TimeActions": [get_time, get_date],
            "MathActions": [add_two_numbers]
        }
    )
    
    # Alternative: using a simple list of functions (all will be in the same default action group)
    # agent = Agent(
    #     name="HelperAgent",
    #     model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    #     instructions="""You are a helpful and friendly assistant helping to test this new agent.""",
    #     functions=[get_time, get_date, add_two_numbers]
    # )
        
    response = client.run(
        agent=agent,
        messages=[
            {
                "role": "user",
                "content": "Hello agent.  What is the time?"
            }
        ]
    )
    
    print("\nAssistant:", response)
    
    # Start interactive chat session
    # client.chat(agent=agent)

if __name__ == "__main__":
    main() 