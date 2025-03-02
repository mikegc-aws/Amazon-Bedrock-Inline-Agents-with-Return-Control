#!/bin/bash

# Script to build the documentation for the Amazon Bedrock Agents with Return Control SDK

# Install documentation dependencies if not already installed
pip install -e ".[docs]"

# Build the documentation
cd docs
make html

# Print success message
echo "Documentation built successfully!"
echo "Open docs/build/html/index.html in your browser to view it." 