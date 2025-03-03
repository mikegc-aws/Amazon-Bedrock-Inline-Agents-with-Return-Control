"""
Code Interpreter Example

This example demonstrates how to use the Code Interpreter feature of Amazon Bedrock Agents.
The Code Interpreter allows the agent to write and execute Python code to solve problems.
"""

import os
from bedrock_agents_sdk import Client, Agent, Message

def main():
    """
    Main function to demonstrate Code Interpreter functionality.
    """
    # Create an agent with Code Interpreter enabled
    agent = Agent(
        name="CodeInterpreterAgent",
        model="anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="""
        You are a helpful data analysis assistant that can write and execute Python code.
        When asked to analyze data or solve mathematical problems, use Python code to provide solutions.
        Create visualizations when appropriate to help explain your findings.
        """,
        enable_code_interpreter=True  # This enables the Code Interpreter feature
    )

    # Create a client with raw trace level to see the code being executed
    client = Client(
        verbosity="normal",
        trace_level="raw"  # Use "raw" to see the actual code being executed
    )

    # Example 1: Simple calculation
    print("\n=== Example 1: Simple Calculation ===")
    response = client.run(
        agent=agent,
        message="Calculate the first 10 Fibonacci numbers and show them in a table."
    )
    print(f"Response: {response['response']}")

    # Example 2: Data analysis with a CSV file
    print("\n=== Example 2: Data Analysis with CSV ===")
    
    # Create a sample CSV file if it doesn't exist
    csv_path = "sample_data.csv"
    if not os.path.exists(csv_path):
        with open(csv_path, "w") as f:
            f.write("Month,Sales,Expenses\n")
            f.write("January,10000,8000\n")
            f.write("February,12000,8500\n")
            f.write("March,15000,9000\n")
            f.write("April,9000,7500\n")
            f.write("May,11000,8200\n")
            f.write("June,13500,8800\n")
    
    # Add the CSV file to the agent
    agent.add_file_from_path(csv_path)
    
    # Run the agent with a data analysis request
    response = client.run(
        agent=agent,
        message="""
        Please analyze the sales data in the CSV file:
        1. Calculate the total sales and expenses
        2. Calculate the profit for each month
        3. Create a bar chart showing sales and expenses by month
        4. Which month had the highest profit margin?
        """
    )
    print(f"Response: {response['response']}")
    
    # Save any generated files
    if response.get("files"):
        print(f"\nThe agent generated {len(response['files'])} file(s)")
        saved_paths = response["save_all_files"]("output")
        print(f"Files saved to: {', '.join(saved_paths)}")

    # Example 3: Interactive chat with Code Interpreter
    print("\n=== Example 3: Interactive Chat with Code Interpreter ===")
    print("Starting interactive chat. Type 'exit' to quit.")
    
    # Start an interactive chat session
    client.chat(agent=agent)

if __name__ == "__main__":
    main() 