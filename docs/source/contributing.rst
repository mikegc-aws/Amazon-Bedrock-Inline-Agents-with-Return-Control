Contributing
============

We welcome contributions to the Amazon Bedrock Agents with Return Control SDK! This section provides guidelines for contributing to the project.

.. note::
   This project is maintained by Mike Chambers and is not an official AWS project.

Setting Up Development Environment
--------------------------------

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/mikegc-aws/Amazon-Bedrock-Inline-Agents-with-Return-Control.git
       cd Amazon-Bedrock-Inline-Agents-with-Return-Control

2. Create a virtual environment:

   .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install development dependencies:

   .. code-block:: bash

       pip install -e ".[dev]"

Code Style
---------

We follow the PEP 8 style guide for Python code. We use the following tools to enforce code style:

* **Black**: For code formatting
* **isort**: For import sorting
* **flake8**: For linting

You can run these tools with the following commands:

.. code-block:: bash

    black .
    isort .
    flake8

Testing
------

We use pytest for testing. You can run the tests with the following command:

.. code-block:: bash

    pytest

When adding new features, please add tests to cover your code. We aim for high test coverage to ensure code quality.

Documentation
------------

We use Sphinx for documentation. You can build the documentation with the following commands:

.. code-block:: bash

    cd docs
    make html

The documentation will be available in the ``docs/build/html`` directory.

When adding new features, please update the documentation to reflect your changes.

Pull Request Process
------------------

1. Fork the repository and create a new branch for your feature or bug fix.
2. Add your changes, including tests and documentation.
3. Run the tests to ensure they pass.
4. Run the code style tools to ensure your code follows our style guidelines.
5. Submit a pull request to the main repository.
6. The maintainers will review your pull request and provide feedback.
7. Once your pull request is approved, it will be merged into the main branch.

Reporting Issues
--------------

If you find a bug or have a feature request, please open an issue on the GitHub repository. Please include as much detail as possible, including:

* A clear and descriptive title
* A detailed description of the issue or feature request
* Steps to reproduce the issue (for bugs)
* Expected behavior
* Actual behavior
* Screenshots or code snippets (if applicable)
* Environment information (OS, Python version, etc.)

Code of Conduct
-------------

We expect all contributors to follow our code of conduct. Please be respectful and considerate of others when contributing to the project.

License
------

By contributing to this project, you agree that your contributions will be licensed under the project's license. 