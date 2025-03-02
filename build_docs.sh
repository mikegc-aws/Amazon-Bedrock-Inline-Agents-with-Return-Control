#!/bin/bash

# Script to build the documentation for the Amazon Bedrock Agents with Return Control SDK

# Install documentation dependencies if not already installed
pip install -e ".[docs]"

# Build the documentation
cd docs
make html
cd ..

# Deploy to GitHub Pages (if requested)
if [ "$1" == "--deploy" ]; then
    echo "Deploying documentation to GitHub Pages..."
    
    # Create a temporary directory for the gh-pages branch
    rm -rf temp_docs
    mkdir -p temp_docs
    
    # Clone the gh-pages branch to the temporary directory
    git clone -b gh-pages https://github.com/mikegc-aws/Amazon-Bedrock-Inline-Agents-with-Return-Control.git temp_docs 2>/dev/null || git clone https://github.com/mikegc-aws/Amazon-Bedrock-Inline-Agents-with-Return-Control.git temp_docs
    
    # Create and switch to gh-pages branch if it doesn't exist
    cd temp_docs
    git checkout gh-pages 2>/dev/null || git checkout -b gh-pages
    
    # Remove existing files (except .git directory)
    find . -maxdepth 1 ! -name .git ! -name . -exec rm -rf {} \;
    
    # Copy the new documentation
    cp -R ../docs/build/html/* .
    
    # Add a .nojekyll file to bypass Jekyll processing
    touch .nojekyll
    
    # Add, commit, and push changes
    git add .
    git commit -m "Update documentation"
    git push origin gh-pages --no-verify
    
    # Clean up
    cd ..
    rm -rf temp_docs
    
    echo "Documentation deployed successfully to GitHub Pages!"
    echo "Visit https://mikegc-aws.github.io/Amazon-Bedrock-Inline-Agents-with-Return-Control/ to view it."
else
    echo "Documentation built successfully!"
    echo "Open docs/build/html/index.html in your browser to view it."
    echo "Run './build_docs.sh --deploy' to deploy to GitHub Pages."
fi 