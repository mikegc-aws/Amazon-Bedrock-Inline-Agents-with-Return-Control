Code Interpreter
===============

The SDK supports Amazon Bedrock's Code Interpreter feature, which allows the agent to write and execute Python code to solve problems.

Enabling Code Interpreter
------------------------

To enable Code Interpreter, set the ``enable_code_interpreter`` parameter to ``True`` when creating an agent:

.. code-block:: python

    from bedrock_agents_sdk import Agent, Client

    agent = Agent(
        name="CodeAgent",
        model="anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful assistant that can write and execute code.",
        enable_code_interpreter=True
    )

    client = Client()
    client.chat(agent=agent)

When enabled, the agent can:

* Write Python code to solve complex problems
* Execute the code in a secure sandbox environment
* Return the results of the code execution
* Create and manipulate data visualizations
* Work with data analysis and numerical computations

Benefits of the Managed Code Execution Environment
-------------------------------------------------

The Code Interpreter feature provides significant advantages:

1. **Zero Setup**: No need to configure a secure Python environment - it's fully managed by Amazon Bedrock
2. **Security**: Code runs in an isolated sandbox, protecting your systems
3. **Pre-installed Libraries**: Common data science and visualization libraries are pre-installed
4. **Dynamic Problem Solving**: The agent can write and execute code on the fly to solve complex problems
5. **No Local Resources**: Code execution happens in the cloud, not consuming your local resources

Viewing Code Interpreter Output
------------------------------

To see the actual code generated and executed by the Code Interpreter, you can use the "raw" trace level:

.. code-block:: python

    # Create a client with raw trace level to see code interpreter output
    client = Client(
        verbosity="verbose",
        trace_level="raw"
    )

    # Or via command line
    # python app.py --trace raw

This will show the complete unprocessed trace data, including the code that was written and executed by the Code Interpreter.

Working with Files
-----------------

Code Interpreter is particularly useful when working with data files. You can add files to an agent using the ``add_file`` or ``add_file_from_path`` methods:

.. code-block:: python

    # Create an agent with code interpreter enabled
    agent = Agent(
        name="FileAgent",
        model="anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful assistant that can analyze data files.",
        enable_code_interpreter=True
    )

    # Add a file from a path (automatically detects media type)
    agent.add_file_from_path("data.csv")

    # Start chatting with the agent
    client = Client()
    client.chat(agent=agent)

The agent can then read, analyze, and visualize the data in the file using the Code Interpreter.

Example Use Cases
----------------

Code Interpreter is particularly useful for:

* Data analysis tasks
* Mathematical calculations
* Generating visualizations
* Solving algorithmic problems
* Processing and transforming data
* Creating reports with charts and tables 