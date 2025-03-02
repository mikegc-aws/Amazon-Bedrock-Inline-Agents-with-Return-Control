"""
Example of deploying a Bedrock Agent with various parameter types.

This example demonstrates how to:
1. Define functions with different parameter types (string, int, float, bool)
2. Use type hints to ensure proper parameter conversion in Lambda functions
3. Provide default values for optional parameters
4. Deploy an agent that correctly handles parameters in Lambda
"""
import os
from bedrock_agents_sdk import BedrockAgents, Agent, Message

# Define functions with various parameter types
def calculate(operation: str, a: int, b: int) -> dict:
    """
    Perform a mathematical calculation
    
    :param operation: The operation to perform (add, subtract, multiply, divide)
    :param a: The first number
    :param b: The second number
    """
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return {"error": "Cannot divide by zero"}
        result = a / b
    else:
        return {"error": f"Unknown operation: {operation}"}
    
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result
    }

def format_text(text: str, uppercase: bool = False, max_length: int = 100) -> dict:
    """
    Format a text string
    
    :param text: The text to format
    :param uppercase: Whether to convert the text to uppercase
    :param max_length: Maximum length of the text (will be truncated if longer)
    """
    # Truncate text if needed
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # Convert to uppercase if requested
    if uppercase:
        text = text.upper()
    
    return {
        "original_length": len(text),
        "formatted_text": text,
        "uppercase": uppercase,
        "max_length": max_length
    }

def calculate_statistics(numbers: str, precision: float = 2.0) -> dict:
    """
    Calculate statistics for a list of numbers
    
    :param numbers: Comma-separated list of numbers
    :param precision: Number of decimal places for results
    """
    # Parse the numbers
    try:
        num_list = [float(n.strip()) for n in numbers.split(',')]
    except ValueError:
        return {"error": "Invalid number format. Please provide comma-separated numbers."}
    
    if not num_list:
        return {"error": "No numbers provided"}
    
    # Calculate statistics
    total = sum(num_list)
    count = len(num_list)
    mean = total / count
    
    # Sort the list for median and min/max
    sorted_nums = sorted(num_list)
    
    # Calculate median
    if count % 2 == 0:
        # Even number of elements
        median = (sorted_nums[count//2 - 1] + sorted_nums[count//2]) / 2
    else:
        # Odd number of elements
        median = sorted_nums[count//2]
    
    # Round results to specified precision
    mean = round(mean, int(precision))
    median = round(median, int(precision))
    
    return {
        "count": count,
        "sum": round(total, int(precision)),
        "mean": mean,
        "median": median,
        "min": round(min(num_list), int(precision)),
        "max": round(max(num_list), int(precision)),
        "precision": int(precision)
    }

def main():
    # Create the agent
    agent = Agent(
        name="ParameterDemoAgent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="""You are a helpful assistant that demonstrates parameter handling.
        
        You can:
        1. Perform calculations using the calculate function
        2. Format text using the format_text function
        3. Calculate statistics for a list of numbers using the calculate_statistics function
        
        Please use these functions to help users with their requests.
        """,
        functions={
            "MathActions": [calculate],
            "TextActions": [format_text],
            "StatisticsActions": [calculate_statistics]
        }
    )
    
    # Test the agent locally before deploying
    print("Testing agent locally before deployment...")
    client = BedrockAgents(verbosity="normal")
    
    # Test with different parameter types
    test_messages = [
        "Calculate 25 + 17",
        "Format this text in uppercase: Hello, world!",
        "Calculate statistics for these numbers: 10, 15, 7, 22, 18, 5, 12, 30, 25, 20"
    ]
    
    for message in test_messages:
        print(f"\nTesting: {message}")
        result = client.run(agent=agent, message=message)
        print("-" * 50)
        print(result["response"])
        print("-" * 50)
    
    # Deploy the agent to AWS
    print("\nDeploying agent to AWS...")
    
    # Generate the SAM template and supporting files
    # The output directory will default to "./parameterdemoagent_deployment"
    template_path = agent.deploy(
        description="Parameter handling demonstration agent",
        # Uncomment the following lines to automatically build and deploy
        # auto_build=True,
        # auto_deploy=True
    )
    
    print("\nAfter deployment, you can test your agent in the AWS Console:")
    print("1. Go to the Amazon Bedrock console")
    print("2. Navigate to Agents")
    print("3. Find your agent named 'ParameterDemoAgent'")
    print("4. Click on the agent and use the 'Test' tab to interact with it")
    
    print("\nTry these test messages:")
    for message in test_messages:
        print(f"- {message}")

if __name__ == "__main__":
    main() 