# Amazon Bedrock Inline Agents with Return Control SDK

This SDK provides a simple yet powerful way to create and interact with Amazon Bedrock Inline Agents using the Return Control pattern. It allows you to easily define function tools, organize them into action groups, and handle the entire conversation flow with minimal boilerplate code.

## Features

- Decorator-based function registration
- Automatic parameter type detection and validation
- Docstring-based parameter descriptions
- Action group organization
- Recursive tool calling with result accumulation
- Interactive chat interface

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
from bedrockInlineAgent import BedrockInlineAgent

# Create the agent
agent = BedrockInlineAgent(
    instruction="You are a helpful assistant that can tell the time.",
    foundation_model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
)

# Define a function tool
@agent.agent_function(action_group="TimeTools")
def get_time() -> dict:
    """Get the current time"""
    import datetime
    now = datetime.datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

# Start chatting
if __name__ == "__main__":
    agent.chat()
```

## Core Concepts

The SDK is built around these key components:

1. **BedrockInlineAgent**: The main class that manages the agent session, function registration, and conversation flow.
2. **agent_function decorator**: A decorator that registers functions as tools the agent can use.
3. **Action Groups**: Collections of related function tools that are presented to the agent.
4. **Return Control Flow**: The pattern where the agent can request information by calling functions and then continue the conversation with the results.

## Creating Function Tools

Function tools are created by decorating regular Python functions with the `@agent.agent_function` decorator:

```python
@agent.agent_function(
    action_group="MathTools",
    description="Add two numbers together"
)
def add_numbers(a: int, b: int) -> dict:
    """
    Add two numbers and return their sum.
    
    :param a: The first number to add
    :param b: The second number to add
    :return: Dictionary containing the result
    """
    return {"result": a + b}
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

Action groups organize related functions together. You can specify the action group when decorating a function:

```python
@agent.agent_function(action_group="TimeTools")
def get_time():
    # ...

@agent.agent_function(action_group="TimeTools")
def get_date():
    # ...
```

If no action group is specified, one is generated based on the function's module name.

### Action Group Descriptions

Action group descriptions are automatically generated as "Actions related to {group_name}". The "Actions" suffix is removed from the group name for cleaner descriptions.

## Debugging and Exporting

### Debug Mode

Enable debug mode to see detailed information about the agent's operations:

```python
agent = BedrockInlineAgent(
    instruction="You are a helpful assistant.",
    debug=True
)
```

### Exporting Action Groups

You can export the action groups to inspect how they're structured:

```python
agent.build_action_groups()
action_groups = agent.action_groups
import json
print(json.dumps(action_groups, indent=4))
```

This is useful for debugging and understanding how your functions are being presented to the agent.

### Starting a Chat Session

To start an interactive chat session:

```python
agent.chat()
```

This will begin a terminal-based chat where users can interact with your agent.

## Complete Example

Here's a more complete example showing various features:

```python
import datetime
from bedrockInlineAgent import BedrockInlineAgent

# Create the agent
agent = BedrockInlineAgent(
    instruction="You are a helpful assistant that can tell time and do math.",
    foundation_model="us.anthropic.claude-3-5-sonnet-20241022-v2:0"
)

# Time functions
@agent.agent_function(action_group="TimeTools")
def get_time() -> dict:
    """Get the current time with timezone information"""
    now = datetime.datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "timezone": datetime.datetime.now().astimezone().tzname()
    }

# Math functions
@agent.agent_function(action_group="MathTools")
def calculate(operation: str, a: int, b: int) -> dict:
    """
    Perform a mathematical operation on two numbers.
    
    :param operation: The operation to perform (must be one of: "add", "subtract", "multiply", "divide")
    :param a: The first number in the operation
    :param b: The second number in the operation
    :return: Dictionary containing the result of the operation
    """
    if operation == "add":
        return {"result": a + b}
    elif operation == "subtract":
        return {"result": a - b}
    elif operation == "multiply":
        return {"result": a * b}
    elif operation == "divide":
        if b == 0:
            return {"error": "Cannot divide by zero"}
        return {"result": a / b}
    else:
        return {"error": f"Unknown operation: {operation}"}

# Start the chat
if __name__ == "__main__":
    agent.chat()
```

## Advanced Usage

### Explicit Parameter Definitions

For complete control over parameter definitions, you can provide them explicitly:

```python
@agent.agent_function(
    action_group="WeatherTools",
    parameters={
        "location": {
            "description": "The city and state/country (e.g., 'Seattle, WA')",
            "required": True,
            "type": "string"
        },
        "units": {
            "description": "Temperature units ('celsius' or 'fahrenheit')",
            "required": False,
            "type": "string"
        }
    }
)
def get_weather(location, units="celsius"):
    # Implementation...
```

### Custom Function Descriptions

You can provide a custom description for the function:

```python
@agent.agent_function(
    action_group="MathTools",
    description="Calculate the square root of a number"
)
def sqrt(number: float) -> dict:
    import math
    return {"result": math.sqrt(number)}
```

### Maximum Tool Call Limit

The SDK has a safety limit to prevent infinite loops of tool calls. You can adjust this limit:

```python
agent = BedrockInlineAgent(
    instruction="You are a helpful assistant.",
    max_tool_calls=20  # Default is 10
)
```

---

This SDK simplifies the process of creating powerful agents with Amazon Bedrock. By handling the boilerplate code for function registration, parameter extraction, and conversation flow, it allows you to focus on building useful tools for your agent.

For more information, see the [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-inline.html).

