# Amazon Bedrock Agents with Return Control SDK

This SDK provides a simple yet powerful way to create and interact with Amazon Bedrock Agents using the Return Control pattern. It allows you to easily define function tools, organize them into action groups, and handle the entire conversation flow with minimal boilerplate code.

## Features

- Multiple ways to register functions (direct assignment, add_function method)
- Automatic parameter type detection and validation
- Docstring-based parameter descriptions
- Action group organization
- Recursive tool calling with result accumulation
- Interactive chat interface
- Optional Code Interpreter integration

## Prerequisites

- Python 3.x
- AWS account with access to Amazon Bedrock
- Appropriate AWS credentials configured

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

Here's a minimal example to get started:

```python
import datetime
from bedrockAgents import BedrockAgents, Agent, Message

# Define a function
def get_time() -> dict:
    """Get the current time"""
    now = datetime.datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

# Create the agent
agent = Agent(
    name="TimeAgent",
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a helpful assistant that can tell the time.",
    functions=[get_time]
)

# Create the client
client = BedrockAgents()

# Start chatting
if __name__ == "__main__":
    client.chat(agent=agent)
```

## Core Concepts

The SDK is built around these key components:

1. **Agent**: A class that represents a Bedrock agent configuration, including its name, model, instructions, and functions.
2. **Function**: A class that represents a function that can be called by the agent.
3. **BedrockAgents**: The main client class that manages the agent session, function execution, and conversation flow.
4. **Action Groups**: Collections of related function tools that are presented to the agent.
5. **Return Control Flow**: The pattern where the agent can request information by calling functions and then continue the conversation with the results.

## Creating Function Tools

There are multiple ways to add functions to an agent:

### Method 1: Direct Assignment in Constructor (List Format)

```python
def get_time() -> dict:
    """Get the current time"""
    import datetime
    now = datetime.datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

def get_date() -> dict:
    """Get the current date"""
    import datetime
    now = datetime.datetime.now()
    return {"date": now.strftime("%Y-%m-%d")}

# All functions in the same action group (default)
agent = Agent(
    name="TimeAgent",
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a helpful assistant that can tell time.",
    functions=[get_time, get_date]
)
```

### Method 2: Direct Assignment in Constructor (Dictionary Format)

```python
def get_time() -> dict:
    """Get the current time"""
    import datetime
    now = datetime.datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

def add_numbers(a: int, b: int) -> dict:
    """Add two numbers together"""
    return {"result": a + b}

# Organize functions into action groups
agent = Agent(
    name="HelperAgent",
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a helpful assistant.",
    functions={
        "TimeActions": [get_time, get_date],
        "MathActions": [add_numbers]
    }
)
```

### Method 3: Using the add_function Method

```python
agent = Agent(
    name="HelperAgent",
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a helpful assistant."
)

# Add functions one by one
agent.add_function(get_time, action_group="TimeActions")
agent.add_function(get_date, action_group="TimeActions")
agent.add_function(add_numbers, action_group="MathActions")
```

### Function Requirements:

1. Functions should return a dictionary that can be serialized to JSON
2. Type hints are recommended but not required
3. Docstrings help the agent understand the function's purpose

## Parameter Handling

The SDK automatically extracts parameter information from your function definitions:

### Type Detection

Parameter types are automatically detected from type hints:
- `int` and `float` → "number"
- `bool` → "boolean"
- Other types → "string"

### Required vs Optional

Parameters without default values are marked as required:
```python
def function(required_param, optional_param="default"):
    # required_param will be marked as required
    # optional_param will be marked as optional
```

### Parameter Descriptions

Parameter descriptions are extracted from docstrings using the `:param name:` format:

```python
def calculate(operation: str, a: int, b: int) -> dict:
    """
    Perform a calculation.
    
    :param operation: The operation to perform (must be one of: "add", "subtract", "multiply")
    :param a: The first number in the operation
    :param b: The second number in the operation
    :return: Dictionary containing the result
    """
```

If no docstring is provided, a default description is generated: "The {param_name} parameter".

## Action Groups

Action groups organize related functions together. You can specify the action group in several ways:

### Using Dictionary Format

```python
agent = Agent(
    name="HelperAgent",
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a helpful assistant.",
    functions={
        "TimeActions": [get_time, get_date],
        "MathActions": [add_numbers]
    }
)
```

### Using add_function Method

```python
agent.add_function(get_time, action_group="TimeActions")
agent.add_function(add_numbers, action_group="MathActions")
```

If no action group is specified when using the list format or add_function method without an action_group parameter, functions are assigned to a default action group called "DefaultActions".

### Action Group Descriptions

Action group descriptions are automatically generated as "Actions related to {group_name}". The "Actions" suffix is removed from the group name for cleaner descriptions.

## Code Interpreter

The SDK supports Amazon Bedrock's Code Interpreter feature, which allows the agent to write and execute Python code to solve problems.

To enable Code Interpreter:

```python
agent = Agent(
    name="CodeAgent",
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a helpful assistant that can write and execute code.",
    enable_code_interpreter=True
)
```

When enabled, the agent can:
- Write Python code to solve complex problems
- Execute the code in a secure sandbox environment
- Return the results of the code execution
- Create and manipulate data visualizations
- Work with data analysis and numerical computations

This is particularly useful for:
- Data analysis tasks
- Mathematical calculations
- Generating visualizations
- Solving algorithmic problems

## Debugging and Running

### Debug Mode

Enable debug mode to see detailed information about the agent's operations:

```python
client = BedrockAgents(debug=True)
```

Debug mode provides information about:
- Action groups being built
- Function calls and parameters
- Agent invocations
- Function results

### Running the Agent

There are two ways to interact with the agent:

#### 1. Single Request

```python
response = client.run(
    agent=agent,
    messages=[
        {
            "role": "user",
            "content": "What time is it?"
        }
    ]
)

print(response)
```

#### 2. Interactive Chat Session

```python
client.chat(agent=agent)
```

This will begin a terminal-based chat where users can interact with your agent.

## Complete Example

Here's a more complete example showing various features:

```python
import datetime
from bedrockAgents import BedrockAgents, Agent, Message

# Define functions
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
    client = BedrockAgents(debug=True)
    
    # Create the agent with functions directly in the definition
    agent = Agent(
        name="HelperAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful and friendly assistant helping to test this new agent.",
        functions={
            "TimeActions": [get_time, get_date],
            "MathActions": [add_two_numbers]
        }
    )
    
    # Start interactive chat session
    client.chat(agent=agent)

if __name__ == "__main__":
    main()
```

## Advanced Usage

### Maximum Tool Call Limit

The SDK has a safety limit to prevent infinite loops of tool calls. You can adjust this limit when creating the client:

```python
client = BedrockAgents(debug=False, max_tool_calls=20)  # Default is 10
```

### Using Message Objects

Instead of dictionaries, you can use Message objects for more type safety:

```python
from bedrockAgents import Message

response = client.run(
    agent=agent,
    messages=[
        Message(role="user", content="What time is it?")
    ]
)
```

### Function Conversion

The SDK automatically converts parameter types based on the function's type hints:
- String values for parameters with `int` or `float` type hints are converted to numbers
- String values like "true", "yes", "1" for parameters with `bool` type hints are converted to boolean True
- String values like "false", "no", "0" for parameters with `bool` type hints are converted to boolean False

---

This SDK simplifies the process of creating powerful agents with Amazon Bedrock. By handling the boilerplate code for function registration, parameter extraction, and conversation flow, it allows you to focus on building useful tools for your agent.

For more information, see the [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-inline.html).

