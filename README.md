# Amazon Bedrock Agents with Return Control SDK

This SDK provides a simple yet powerful way to create and interact with Amazon Bedrock Agents using the Return Control pattern. It allows you to easily define function tools, organize them into action groups, and handle the entire conversation flow with minimal boilerplate code.

## Why Use This SDK?

As a developer, you want to build powerful AI agents quickly without managing complex infrastructure. This SDK lets you:

1. **Develop locally, run in the cloud** - Write and test your agent tools locally while Amazon Bedrock handles the heavy lifting of LLM orchestration and session management in the cloud.

2. **Zero conversation management** - No need to track conversation history or manage state - Amazon Bedrock Agents handles this automatically.

3. **Minimal boilerplate** - Focus on your business logic rather than agent infrastructure. Define functions, and the SDK handles parameter extraction, validation, and the entire conversation flow.

4. **Secure managed environment** - Leverage Amazon Bedrock's fully managed and secure code execution environment without additional setup.

## Benefits

### For Rapid Development
- **Quick setup**: Get an agent running in minutes, not days
- **Local testing**: Test your agent tools locally before deploying
- **Automatic documentation**: Function docstrings become parameter descriptions
- **Type inference**: Automatic parameter type detection from Python type hints

### For Production Applications
- **Cloud-scale reliability**: Amazon Bedrock manages the LLM and session storage
- **No conversation state management**: Focus on your tools, not managing dialog history
- **Secure code execution**: Use the built-in Code Interpreter for dynamic code execution in a secure sandbox
- **Flexible verbosity**: Comprehensive logging options for development and production

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

In just a few lines of code, you can create a fully functional agent that leverages Amazon Bedrock's cloud infrastructure. No need to manage conversation state, handle complex agent logic, or set up infrastructure - just define your functions and start building.

Here's a minimal example to get started:

```python
import datetime
from bedrockAgents import BedrockAgents, Agent, Message

# Define a function - this will run locally on your machine
def get_time() -> dict:
    """Get the current time"""
    now = datetime.datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

# Create the agent - the LLM runs in Amazon Bedrock's cloud
agent = Agent(
    name="TimeAgent",
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    instructions="You are a helpful assistant that can tell the time.",
    functions=[get_time]
)

# Create the client - handles communication with Amazon Bedrock
client = BedrockAgents()

# Start chatting - conversation history is managed in the cloud
if __name__ == "__main__":
    client.chat(agent=agent)
```

That's it! With this code, you have:
- A locally defined function that the agent can call
- A cloud-hosted LLM that handles the conversation
- Automatic conversation state management
- No infrastructure to set up or maintain

## Core Concepts

The SDK is built around these key components:

1. **Agent**: A class that represents a Bedrock agent configuration, including its name, model, instructions, and functions.

2. **Function**: A class that represents a function that can be called by the agent. These functions run locally on your machine, but are orchestrated by the cloud-based agent.

3. **BedrockAgents**: The main client class that manages the agent session, function execution, and conversation flow. It handles all communication with Amazon Bedrock.

4. **Action Groups**: Collections of related function tools that are presented to the agent. These help organize your functions logically.

5. **Return Control Flow**: The pattern where the agent can request information by calling your local functions and then continue the conversation with the results. This enables a seamless hybrid cloud-local architecture.

### Cloud-Local Hybrid Architecture

This SDK implements a hybrid architecture where:

- **Cloud Components (Amazon Bedrock)**:
  - LLM execution
  - Conversation state management
  - Agent orchestration
  - Code Interpreter (secure sandbox)

- **Local Components (Your Machine)**:
  - Function tools implementation
  - Business logic
  - Data access
  - Custom integrations

This architecture gives you the best of both worlds: the scalability and management of cloud services with the flexibility and control of local development.

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

### Benefits of the Managed Code Execution Environment

The Code Interpreter feature provides significant advantages:

1. **Zero Setup**: No need to configure a secure Python environment - it's fully managed by Amazon Bedrock
2. **Security**: Code runs in an isolated sandbox, protecting your systems
3. **Pre-installed Libraries**: Common data science and visualization libraries are pre-installed
4. **Dynamic Problem Solving**: The agent can write and execute code on the fly to solve complex problems
5. **No Local Resources**: Code execution happens in the cloud, not consuming your local resources

This means you can enable powerful code execution capabilities without any additional infrastructure or security concerns.

## Debugging and Running

### Verbosity and Logging

The SDK provides a unified verbosity system with multiple levels to help you debug and understand the agent's operations:

```python
# Simple unified verbosity control
client = BedrockAgents(verbosity="normal")  # Default level

# Available verbosity levels:
client = BedrockAgents(verbosity="quiet")    # No output except errors
client = BedrockAgents(verbosity="normal")   # Basic operational information
client = BedrockAgents(verbosity="verbose")  # Detailed operational information
client = BedrockAgents(verbosity="debug")    # All available information

# Advanced control (overrides specific aspects of verbosity)
client = BedrockAgents(
    verbosity="normal",     # Base verbosity level
    sdk_logs=True,          # Override to show SDK-level logs
    agent_traces=True,      # Override to show agent reasoning and decisions
    trace_level="detailed"  # Override level of trace detail
)
```

#### Verbosity Levels Explained

Each verbosity level automatically configures the appropriate combination of logging options:

- **quiet**: 
  - No SDK logs
  - No agent traces
  - Errors are still displayed

- **normal** (default): 
  - SDK logs controlled by `sdk_logs` parameter (default: False)
  - Agent traces controlled by `agent_traces` parameter (default: True)
  - Trace level controlled by `trace_level` parameter (default: "standard")

- **verbose**: 
  - SDK logs enabled
  - Agent traces enabled
  - Trace level set to at least "standard"

- **debug**: 
  - SDK logs enabled
  - Agent traces enabled
  - Trace level set to "detailed"

#### SDK Logs

SDK logs (prefixed with `[SDK LOG]`) provide information about:
- Action groups being built
- Function calls and parameters
- Agent invocations
- Function results

#### Agent Traces

Agent traces (prefixed with `[AGENT TRACE]`) provide insight into the agent's reasoning:
- Reasoning process
- Decision rationale
- Function invocation details

#### Trace Levels

- **minimal**: Only basic reasoning and decisions
- **standard**: Reasoning, decisions, and function calls (default)
- **detailed**: All available trace information

#### Backward Compatibility

For backward compatibility, you can still use the `debug` parameter:

```python
# Equivalent to sdk_logs=True
client = BedrockAgents(debug=True)
```

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

#### 2. Interactive Chat

```python
client.chat(agent=agent)
```

#### 3. Continuing a Conversation

You can maintain conversation context across multiple run() calls by passing the same session_id:

```python
# First interaction
session_id = "my-custom-session-123"  # Or use a generated UUID
response1 = client.run(
    agent=agent,
    messages=[
        {
            "role": "user",
            "content": "What time is it?"
        }
    ],
    session_id=session_id
)

print(response1)

# Continue the same conversation
response2 = client.run(
    agent=agent,
    messages=[
        {
            "role": "user",
            "content": "And what's the date today?"
        }
    ],
    session_id=session_id
)

print(response2)
```

You can also continue an existing session in the interactive chat:

```python
# Start or continue a chat session with a specific session ID
client.chat(agent=agent, session_id="my-custom-session-123")
```

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
    client = BedrockAgents(verbosity="verbose")
    
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
client = BedrockAgents(verbosity="normal", max_tool_calls=20)  # Default is 10
```

### BedrockAgents Constructor Parameters

The `BedrockAgents` class accepts the following parameters:

```python
client = BedrockAgents(
    verbosity="normal",     # Overall verbosity level (quiet, normal, verbose, debug)
    sdk_logs=False,         # Whether to show SDK-level logs
    agent_traces=True,      # Whether to show agent trace information
    trace_level="standard", # Level of agent trace detail (minimal, standard, detailed)
    max_tool_calls=10,      # Maximum number of tool calls to prevent infinite loops
    debug=None             # Deprecated: Use sdk_logs instead
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `verbosity` | str | "normal" | Overall verbosity level. Options: "quiet", "normal", "verbose", "debug" |
| `sdk_logs` | bool | False | Whether to show SDK-level logs (client operations, function calls, etc.) |
| `agent_traces` | bool | True | Whether to show agent trace information (reasoning, decisions, etc.) |
| `trace_level` | str | "standard" | Level of agent trace detail. Options: "minimal", "standard", "detailed" |
| `max_tool_calls` | int | 10 | Maximum number of tool calls to prevent infinite loops |
| `debug` | bool | None | Deprecated: Use `sdk_logs` instead |

Note that the `verbosity` parameter will override the other logging parameters unless you explicitly set them.

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

## Running Tests

The project includes a comprehensive test suite built with pytest. To run the tests:

1. Make sure you have installed the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the tests using pytest:
   ```bash
   pytest
   ```

3. For more verbose output, use:
   ```bash
   pytest -v
   ```

4. To run a specific test file:
   ```bash
   pytest test_bedrock_agents.py
   ```

5. To run a specific test function:
   ```bash
   pytest test_bedrock_agents.py::test_function_name
   ```

The test suite covers:
- Initialization of BedrockAgents and Agent classes
- Function processing and execution
- Parameter extraction and conversion
- Action group building
- Agent invocation with mocks
- Error handling
- Edge cases

---

## Conclusion

This SDK empowers developers to build sophisticated AI agents with Amazon Bedrock while maintaining a streamlined development experience:

- **Focus on Business Logic**: Write your function tools and let the SDK handle the complex orchestration
- **Hybrid Architecture**: Develop locally while leveraging the power of Amazon Bedrock's cloud infrastructure
- **Zero State Management**: No need to track conversation history or manage complex agent state
- **Rapid Development**: Get from concept to working agent in minutes, not days
- **Production Ready**: Built for both development and production use cases with flexible logging and error handling
- **Secure by Design**: Leverage Amazon's secure managed environments for both agent execution and code interpretation

By eliminating the boilerplate code for function registration, parameter extraction, and conversation flow, this SDK allows you to focus on what matters most - building valuable AI experiences for your users.

For more information, see the [Amazon Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-inline.html).

