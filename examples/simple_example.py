"""
Simple example of using the Bedrock Agents SDK.
"""
import datetime
from bedrock_agents_sdk import BedrockAgents, Agent, Message

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
    # Create the client - handles communication with Amazon Bedrock
    client = BedrockAgents(verbosity="verbose")
    
    # Create the agent - the LLM runs in Amazon Bedrock's cloud
    agent = Agent(
        name="SimpleAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="""You are a helpful assistant that can tell the time and date, 
        and perform simple calculations. When asked about time or date, use the 
        appropriate function to get accurate information. When asked to add numbers, 
        use the add_numbers function.""",
        functions={
            "TimeActions": [get_time, get_date],
            "MathActions": [add_numbers]
        }
    )
    
    # Run the agent with a single query
    result = client.run(
        agent=agent,
        messages=[
            {
                "role": "user",
                "content": "What time is it now, and can you also add 25 and 17 for me?"
            }
        ]
    )
    
    print("\nResponse from agent:")
    print("-" * 50)
    print(result["response"])
    print("-" * 50)
    
    # Or start an interactive chat session
    print("\nStarting interactive chat session. Type 'exit' to quit.\n")
    client.chat(agent=agent)

if __name__ == "__main__":
    main() 