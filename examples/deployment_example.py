"""
Example of deploying a Bedrock Agent to AWS using the Bedrock Agents SDK.
"""
import datetime
import os
from bedrock_agents_sdk import BedrockAgents, Agent, Message

# Define functions - these will run in AWS Lambda when deployed
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
        name="DeploymentExample",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="""You are a helpful assistant that can tell the time and date, 
        and perform simple calculations. When asked about time or date, use the 
        appropriate function to get accurate information. When asked to add numbers, 
        use the add_numbers function.""",
        functions={
            "TimeActions": [get_time, get_date],
            "MathActions": [add_numbers]
        }
    )
    
    # Test the agent locally before deploying
    print("Testing agent locally before deployment...")
    client = BedrockAgents(verbosity="normal")
    result = client.run(
        agent=agent,
        message="What time is it now, and can you also add 25 and 17 for me?"
    )
    print("\nLocal agent response:")
    print("-" * 50)
    print(result["response"])
    print("-" * 50)
    
    # Deploy the agent to AWS
    print("\nDeploying agent to AWS...")
    
    # Generate the SAM template and supporting files
    # The output directory will default to "./deploymentexample_deployment"
    template_path = agent.deploy(
        description="Example agent deployment",
        # Uncomment the following lines to automatically build and deploy
        # auto_build=True,
        # auto_deploy=True
    )
    
    print("\nAfter deployment, you can test your agent in the AWS Console:")
    print("1. Go to the Amazon Bedrock console")
    print("2. Navigate to Agents")
    print("3. Find your agent named 'DeploymentExample'")
    print("4. Click on the agent and use the 'Test' tab to interact with it")

if __name__ == "__main__":
    main() 