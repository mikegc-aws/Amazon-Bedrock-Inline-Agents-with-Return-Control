Command Line Interface
====================

The SDK includes a command-line interface (CLI) for testing and interacting with agents. The CLI is implemented in the ``app.py`` file that comes with the SDK.

Basic Usage
----------

.. code-block:: bash

    # Start in interactive chat mode
    python app.py --chat

    # Run with a file
    python app.py --file data.csv

    # Use a specific AWS region and profile
    python app.py --region us-west-2 --profile myprofile

Verbosity and Trace Levels
-------------------------

You can control the verbosity and trace levels using command-line arguments:

.. code-block:: bash

    # Set verbosity level
    python app.py --verbosity verbose

    # Set trace level
    python app.py --trace standard

    # Use the raw trace level to see all trace data, including code interpreter output
    python app.py --trace raw  # Shows complete unprocessed JSON trace data

    # Combine options for specific debugging needs
    python app.py --chat --verbosity quiet --trace raw  # Quiet SDK logs but full trace data

Available Options
---------------

The CLI supports the following options:

.. code-block:: bash

    --chat                 Start in interactive chat mode
    --region REGION        AWS region name
    --profile PROFILE      AWS profile name
    --verbosity {quiet,normal,verbose,debug}
                           Verbosity level
    --trace {none,minimal,standard,detailed,raw}
                           Agent trace level (raw shows complete unprocessed trace data)
    --file FILE            Path to a file to send to the agent
    --kms-key KMS_KEY      Customer KMS key ARN for encryption

Example Commands
--------------

Here are some example commands to get you started:

.. code-block:: bash

    # Start a chat session with verbose logging
    python app.py --chat --verbosity verbose

    # Start a chat session with detailed agent traces
    python app.py --chat --trace detailed

    # Start a chat session with raw trace level to see code interpreter output
    python app.py --chat --trace raw

    # Upload a file and start a chat session
    python app.py --chat --file data.csv

    # Use a customer KMS key for encryption
    python app.py --chat --kms-key "arn:aws:kms:us-west-2:123456789012:key/abcd1234-ab12-cd34-ef56-abcdef123456"

    # Combine multiple options
    python app.py --chat --region us-west-2 --profile dev --verbosity normal --trace standard 