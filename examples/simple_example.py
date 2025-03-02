"""
Simple example of using the Bedrock Agents SDK.
"""
from bedrock_agents_sdk import Client, Agent, Message
import datetime

# Define a function - this will run locally on your machine
def get_time() -> dict:
    """Get the current time"""
    now = datetime.datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

def get_date() -> dict:
    """Get the current date"""
    now = datetime.datetime.now()
    return {"date": now.strftime("%Y-%m-%d")}

def add_numbers(a: int, b: int) -> dict:
    """Add two numbers together
    
    :param a: The first number
    :param b: The second number
    """
    return {"result": a + b}

def main():
    # Create the agent
    agent = Agent(
        name="SimpleAgent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can tell time and do simple math.",
        functions=[get_time, get_date, add_numbers]
    )
    
    # Create the client
    client = Client(verbosity="verbose")
    
    # Start interactive chat session
    client.chat(agent=agent)

if __name__ == "__main__":
    main() 