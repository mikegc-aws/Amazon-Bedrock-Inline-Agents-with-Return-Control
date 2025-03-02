Installation
============

Prerequisites
------------

Before installing the Amazon Bedrock Agents with Return Control SDK, ensure you have:

* Python 3.8 or higher
* AWS CLI configured with appropriate credentials
* AWS SAM CLI (for deployment)

Installation
-----------

You can install the SDK directly from GitHub:

.. code-block:: bash

    pip install git+https://github.com/mikegc-aws/Amazon-Bedrock-Inline-Agents-with-Return-Control.git

Or clone the repository and install locally:

.. code-block:: bash

    git clone https://github.com/mikegc-aws/Amazon-Bedrock-Inline-Agents-with-Return-Control.git
    cd Amazon-Bedrock-Inline-Agents-with-Return-Control
    pip install -e .

For development, you can install additional dependencies:

.. code-block:: bash

    pip install -e ".[dev]"

AWS Setup
--------

To use the SDK, you need to have AWS credentials configured. You can do this by:

1. Installing the AWS CLI
2. Running ``aws configure`` and providing your AWS Access Key ID, Secret Access Key, and default region
3. Ensuring you have the necessary permissions to create and manage Amazon Bedrock Agents

For more detailed AWS setup instructions, refer to the AWS setup guides included in the repository:

* ``aws_setup_instructions.md``
* ``aws-setup-guide.md``
* ``aws-bedrock-foundation-models-guide.md`` 